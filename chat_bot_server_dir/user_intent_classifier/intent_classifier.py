import spacy
import os
import configparser
from slacker import Slacker
from pathlib import Path
from server_dir.slack_message_sender import send_channel_message
from chat_bot_server_dir.project_parser import project_parser
from chat_bot_server_dir.user_intent_classifier.sentence_type_finder import require_something_sentence
from chat_bot_server_dir.work_database import work_database

# You can download this file : https://spacy.io/usage/vectors-similarity

nlp = spacy.load('C:\\Users\\learn\\PycharmProjects\\conflict-detector\\venv\\Lib\\site-packages\\en_core_web_lg\\en_core_web_lg-2.0.0')


# bot's feature
# 1. ignore_file : It functions like gitignore. A user can customize his/her ignore files.
# 2. lock_file : A user can lock his/her files. If other users try to modify the related file of the lock_file, chatbot gives them a warning.
# 3. code_history : A user can ask who wrote certain code lines.
# 4. ignore_alarm : A user can ignore direct and indirect conflicts.
# 5. check_conflict : Before a user starts to work, the user can check if he/she generates conflict or not on the working file
# 6. working_status : A user can ask about other user's working status
# 7. channel_message : A user can let chatbot give a message to channel.
# 8. user_message : A user can let chatbot give a message to other users.
# 9. recommend : A user can ask chatbot to recommend reaction to conflict.
# 10. user_recognize : Chatbot knows when last time a user connected is, so bot can greet the user with time information. ex) It's been a while~
# 11. greeting : Chatbot can greet users.
# 12. complimentary_close : Chatbot can say good bye.
# 13. detect_direct_conflict : Chatbot can detect direct conflict and severity.
# 14. detect_indirect_conflict : Chatbot can detect indirect conflict and severity.

question_sentence_list = ["Can you not notify me about hello.py?", "Can you lock hello.py?",
                          "Can you tell me who wrote line14 to line 18 at file1.py?", "Can you not notify me about indirect conflict?",
                          "Do you think this is gonna make a conflict?", "Can you tell me user2's working status?",
                          "Can you tell everyone that I'm working on File1.py?",
                          "Can you chat to User2 that I will check and solve the problem?",
                          "Can you recommend what should I do to fix the conflict?"]
command_sentence_list = ["Don't alert me about File1.py again.", "Lock hello.py file.", "Tell me who wrote line 70 to line 90 in file1.py.",
                         "Don't alert me about indirect conflict.",
                         "Check File1.py whether it will make conflict or not.",
                         "Tell everyone that I'm working on File1.py to conflict detect channel.",
                         "Send user2 a message that I'm working on class1.",
                         "Give me some recommendation about how to solve the conflict of File1.py."]
suggestion_sentence_list = ["You should not give me notification about File1.py", "You should lock File.py.",
                            "Sayme, you should let me know who wrote code line 1 to line9 at file1.py.",
                            "You should not alert me about direct conflict.",
                            "Sayme, you should check File1.py if this is gonna make a conflict.",
                            "You should tell me user1's working status.",
                            "You should announce that don't touch File1.py to conflict detect channel.",
                            "You have to send message to User2 that I will check and solve the confilct.",
                            "You would tell me how I can solve the conflict in File1.py"]
desire_sentence_list = ["I want to ignore any alarm about File1.py.", "I want to lock File1.py.",
                        "I want to know who wrote line 70 to line 90 in File1.py.", "I don't want you to alert about direct conflict",
                        "I want to know that this is gonna make a conflict in File1.py.",
                        "I want to know user1's working status.",
                        "I want to send the message in conflict detector channel that don't modify File1.py.",
                        "I want to send a direct message to user1 that don't modify File1.py.",
                        "I want to get recommendation how I can solve the conflict in File1.py."]

def load_token() :
    file_path = os.path.join(Path(os.getcwd()).parent, "all_server_config.ini")

    if not os.path.isfile(file_path) :
        print("ERROR :: There is no all_server_config.ini")
        exit(2)
    else :
        config = configparser.ConfigParser()
        config.read(file_path)
        try :
            token=config["SLACK"]["TOKEN"]
        except :
            print("ERROR :: It is all_server_config.ini")
            exit(2)
    return token

token = load_token()
slack = Slacker(token)

def get_slack_name_list():
    try:
        user_list = list()
        # Get users list
        response = slack.users.list()
        users = response.body['members']
        for user in users:
            if user.get('profile').get('display_name') != '':
                user_list.append(user.get('profile').get('display_name'))
            else:
                user_list.append(user.get('profile').get('real_name'))
    except KeyError as ex:
        print('Invalid key : %s' % str(ex))
    return user_list

def calcue_max(sentence, list):
    user_input = nlp(sentence)
    max = 0
    max_idx = 10
    for idx in range(len(list)):
        sample_input = nlp(list[idx])
        rate = user_input.similarity(sample_input)
        if rate > max and rate > 0.70:
            max_idx = idx + 1
            max = rate
        if max_idx == 1 or max_idx == 4:
            if 'direct' in sentence or 'indirect' in sentence:
                max_idx = 4
            else:
                max_idx = 1

    return max_idx

def intent_classifier(sentence):
    if "this" in sentence:
        sentence = sentence.replace("this","xvxv.py")
    sentence_type = require_something_sentence(sentence)

    # Question
    if sentence_type == 1 :
        max_idx = calcue_max(sentence, question_sentence_list)
        return max_idx

    # Command
    elif sentence_type == 2 :
        max_idx = calcue_max(sentence, command_sentence_list)
        return max_idx

    # Suggestion
    elif sentence_type == 3 :
        max_idx = calcue_max(sentence, suggestion_sentence_list)
        return max_idx

    # Desire
    elif sentence_type == 4 :
        max_idx = calcue_max(sentence, desire_sentence_list)
        return max_idx
    else:
        return 10

def get_file_path(file_list):
    result_file_list = []
    for fl in file_list:
        r = fl.split("/")[-1]
        result_file_list.append(" " + r)
    return result_file_list


def extract_attention_word(sentence, github_email):
    import re

    work_db = work_database()
    file_list = project_parser("UCNLP", "client")["file"]

    name_list = get_slack_name_list()

    try:
        recent_data = work_db.get_recent_data(github_email)
        recent_file = recent_data[0].split('|')[0]
    except:
        recent_data = "no recent data"
        recent_file = "no recent file"
    intent_type = intent_classifier(sentence)
    print("Intent_type : ", intent_type)

    if intent_type == 1:

        result_file_list = list()
        remove_list = list()
        approve_set = set()

        print(file_list)

        for fl in file_list:
            r = fl.split("/")[-1]
            # result_file_list.append(" "+r)
            result_file_list.append(str(r))

        print(result_file_list)
        for rfl in result_file_list:
            print(rfl)
            if rfl in sentence:
                print (sentence)
                if (('not' in sentence) or ("n’t" in sentence) or ('un' in sentence)):
                    remove_list.append(file_list[result_file_list.index(rfl)])
                    print(rfl)
                    print(file_list[result_file_list.index(rfl)])
                else:
                    print(rfl)
                    print(file_list[result_file_list.index(rfl)])
                    approve_set.add(file_list[result_file_list.index(rfl)])
            elif "this" in sentence:
                    recent_file = work_db.get_recent_data(github_email)
                    approve_set.add(recent_file)
                    break



        print(remove_list)
        print(approve_set)

        if remove_list == [] and approve_set == set():
            if 'not' in sentence or "n’t" in sentence or 'un' in sentence:
                remove_list.append(recent_file)
            else:
                approve_set.add(recent_file)

        print("remove_list : ", remove_list)
        print("approve_set : ", approve_set)
        work_db.close()
        return 1, approve_set, remove_list, None


    elif intent_type == 2:

        lock_time = 0
        result_file_list = list()
        request_lock_set = set()
        remove_lock_list = list()

        for fl in file_list:
            r = fl.split("/")[-1]
            result_file_list.append(" " + r)

        for rfl in result_file_list:
            if rfl in sentence:
                if 'not' in sentence or "n’t" in sentence or 'un' in sentence:
                    remove_lock_list.append(file_list[result_file_list.index(rfl)])
                else:
                    try:
                        lock_time = int(re.findall('\d+', sentence)[0])
                    except:
                        lock_time = 1
                    request_lock_set.add(file_list[result_file_list.index(rfl)])

        if remove_lock_list == [] and request_lock_set == set():
            if 'not' in sentence or "n’t" in sentence or 'un' in sentence:
                remove_lock_list.append(recent_file)
            else :
                request_lock_set.add(recent_file)

        print("remove_lock_list : ", remove_lock_list)
        print("request_lock_set : ", request_lock_set)
        work_db.close()
        return 2, request_lock_set, remove_lock_list, lock_time


    elif intent_type == 3:
        result_file_list = get_file_path(file_list)
        file_path = ""

        for rfl in result_file_list:
            if rfl in sentence:
                file_path = file_list[result_file_list.index(rfl)]

        pattern = re.compile("\d+")
        num_list = re.findall(pattern, sentence)

        if len(num_list) > 1:
            if num_list[0] < num_list[1]:
                work_db.close()
                return 3, file_path, num_list[0], num_list[1]
            else:
                work_db.close()
                return 3, file_path, num_list[1], num_list[0]
        elif len(num_list) == 1:
            work_db.close()
            return 3, file_path, num_list[0], num_list[0]

        else:
            work_db.close()
            return 3, recent_file, 1, 1


    elif intent_type == 4:
        if 'not' in sentence or "n’t" in sentence or 'un' in sentence:
            if 'indirect' in sentence:
                work_db.close()
                return 4, 2, 1, None
            else:
                work_db.close()
                return 4, 1, 2, None
        else:
            if 'indirect' in sentence:
                work_db.close()
                return 4, 2, 0, None
            else:
                work_db.close()
                return 4, 0, 2, None


    elif intent_type == 5:
        result_file_list = get_file_path(file_list)
        file_path = ""

        for rfl in result_file_list:
            if rfl in sentence:
                file_path = file_list[result_file_list.index(rfl)]
        work_db.close()
        return 5, file_path, None, None


    elif intent_type == 6:

        target_user_name = ""

        for name in name_list:
            if name in sentence:
                target_user_name = name
                break

        if target_user_name == "":
            work_db.close()
            return 6, recent_data[2], None, None
        else:
            target_user_email = work_db.slack_name_to_git_email(target_user_name)
            work_db.close()
            return 6, target_user_name ,target_user_email, None


    elif intent_type == 7:

        msg = ""
        channel = ""

        to_channel_regex = r'to [a-zA-Z\s]+channel'
        in_channel_regex = r'in [a-zA-Z\s]+channel'

        to_channel_p = re.compile(to_channel_regex)
        in_channel_p = re.compile(in_channel_regex)

        in_result = in_channel_p.findall(sentence)
        to_result = to_channel_p.findall(sentence)

        if in_result != [] and to_result != []:
            if len(in_result[0]) < len(to_result[0]):
                channel = in_result[0][2:-7].strip()
                start_that = sentence.find('that') + 4
                msg = sentence[start_that:].replace('in {} channel'.format(channel), '').strip()
            else:
                channel = to_result[0][2:-7].strip()
                start_that = sentence.find('that') + 4
                msg = sentence[start_that:].replace('to {} channel'.format(channel), '').strip()

        elif in_result != []:
            channel = in_result[0][2:-7].strip()
            start_that = sentence.find('that') + 4
            msg = sentence[start_that:].replace('in {} channel'.format(channel), '').strip()

        elif to_result != []:
            channel = to_result[0][2:-7].strip()
            start_that = sentence.find('that') + 4
            msg = sentence[start_that:].replace('to {} channel'.format(channel), '').strip()

        else:
            channel = "code-conflict-chatbot"
            start_that = sentence.find('that') + 4
            msg = sentence[start_that:].replace('to {} channel'.format(channel), '').strip()
        work_db.close()
        return 7, channel, msg, None

    elif intent_type == 8:
        target_user_name = ""
        slack_code = ""
        for name in name_list:
            if name in sentence:
                target_user_name = name
                break
        if target_user_name == "":
            slack_code = work_db.convert_git_id_to_slack_code(recent_data[2])[0]
        else:
            slack_code = work_db.slack_name_to_slack_code(target_user_name)

        start_that = sentence.find('that') + 4
        msg = sentence[start_that:]
        work_db.close()
        return 8, slack_code, msg, None

    elif intent_type == 9:
        work_db.close()
        return 9, github_email, recent_data[2], None
    else:
        if "hi" in sentence or "Hi" in sentence or "Hello" in sentence or "hello" in sentence :
            print("greeting shell")
            return 10, "greeting", None, None
        elif "bye" or "Bye" or "See you" or "see you":
            return 11, "bye", None, None
        else:
            return 12, "no_response", None, None

if __name__ == '__main__':
    print(extract_attention_word("hi",'a'))


token = load_token()
slack = Slacker(token)

