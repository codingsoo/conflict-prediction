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

#nlp = spacy.load('/Users/seonkyukim/Desktop/UCI/Chatbot/conflict-detector/venv/lib/python3.6/site-packages/en_core_web_lg/en_core_web_lg-2.0.0')
#nlp = spacy.load('/Users/Kathryn/Documents/GitHub/conflict-detector/venv/lib/python3.6/site-packages/en_core_web_lg/en_core_web_lg-2.0.0')
nlp = spacy.load('/Users/sooyoungbaek/conflict-detector/venv/lib/python3.6/site-packages/en_core_web_lg/en_core_web_lg-2.0.0')


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
                          "Do you think hello.py is gonna make a conflict?",  "Can you tell me <@UCFNMU2ED>'s working status?",
                          "Can you tell everyone that I'm working on File1.py?",
                          "Can you chat to <@UCFNMU2ED> that I will check and solve the problem?",
                          "Can you recommend what should I do to fix the conflict in File.py?"]
command_sentence_list = ["Don't notify me about File1.py again.", "Lock hello.py file.", "Tell me who wrote line 70 to line 90 in file1.py.",
                         "Don't alert me about indirect conflict.",
                         "Check File1.py whether it will make a conflict or not.",
                         "Tell me where <@UCFNMU2ED>'s working status",
                         "Tell everyone that I'm working on File1.py to conflict detect channel.",
                         "Send <@UCFNMU2ED> a message that I'm working on class1.",
                         "Give me some recommendation about how to solve the conflict of File1.py."]
suggestion_sentence_list = ["You should not give me notification about File1.py", "You should lock File.py.",
                            "Sayme, you should let me know who wrote code line 1 to line9 at file1.py.",
                            "You should not alert me about direct conflict.",
                            "Sayme, you should check File1.py if this is gonna make a conflict.",
                            "You should tell me <@UCFNMU2ED>'s working status.",
                            "You should announce that don't touch File1.py to conflict detect channel.",
                            "You have to send message to <@UCFNMU2ED> that I will check and solve the confilct.",
                            "You would tell me how I can solve the conflict in File1.py"]
desire_sentence_list = ["I want to ignore any alarm about File1.py.", "I want to lock File1.py.",
                        "I want to know who wrote line 70 to line 90 in File1.py.", "I don't want you to alert about direct conflict",
                        "I want to know that this is gonna make a conflict in File1.py.",
                        "I want to know <@UCFNMU2ED>'s working status.",
                        "I want to send the message in conflict detector channel that don't modify File1.py.",
                        "I want to send a direct message to <@UCFNMU2ED> that don't modify File1.py.",
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

def get_slack_id_list():
    try:
        user_list = list()
        # Get users list
        response = slack.users.list()
        users = response.body['members']
        for user in users:
            user_list.append(user.get('id'))
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
        if rate > max and rate > 0.35:
            max_idx = idx + 1
            max = rate

    if max_idx == 1 or max_idx == 4:
        if (" direct " in sentence or " indirect " in sentence) and (".py" not in sentence):
            max_idx = 4
        else:
            max_idx = 1

    if max_idx == 7 or max_idx == 8:
        if " <@" in sentence:
            max_idx = 8
        else:
            max_idx = 7

    if max_idx in [1, 2, 3, 5] and ".py" not in sentence:
        return 10

    return max_idx

def intent_classifier(_sentence):
    if " this file " in _sentence :
        _sentence = _sentence.replace("this file", ":.py")
    sentence_type, sentence = require_something_sentence(_sentence)

    # Question
    if sentence_type == 1 :
        max_idx = calcue_max(sentence, question_sentence_list)

        return max_idx, sentence


    # Command
    elif sentence_type == 2 :
        max_idx = calcue_max(sentence, command_sentence_list)

        return max_idx, sentence


    # Suggestion
    elif sentence_type == 3 :
        max_idx = calcue_max(sentence, suggestion_sentence_list)

        return max_idx, sentence


    # Desire
    elif sentence_type == 4 :
        max_idx = calcue_max(sentence, desire_sentence_list)

        return max_idx, sentence

    else:
        return 10, sentence

def get_file_path(file_list):
    result_file_list = []
    for fl in file_list:
        r = fl.split("/")[-1]
        result_file_list.append(" " + r)
    return result_file_list


def extract_attention_word(_sentence, github_email):
    import re

    work_db = work_database()
    onlyFile_list = project_parser("UCNLP", "conflict_test")["file"]
    file_list = list()

    for ofl in onlyFile_list:
        fl = "UCNLP" + "/" + "conflict_test" + "/" + ofl
        file_list.append(fl)

    # name_list = get_slack_name_list()
    slack_id_list = get_slack_id_list()

    # recent_data = ""
    # remove_file = ""

    try:
        recent_data = work_db.get_recent_data(github_email)
        recent_file = recent_data[0].split('|')[0]
    except:
        recent_data = "no recent data"
        recent_file = "no recent file"

    intent_type, sentence = intent_classifier(_sentence)

    print("Intent_type : ", intent_type)

    conflict_file_list = work_db.all_conflict_list(github_email)

    # help classification about intent_type 5 and 9
    # if conflict_file in sentence, we can think user wants to recommendation.
    is_found = 0
    if intent_type == 5 or intent_type == 9:
        if conflict_file_list:
            for cfl in conflict_file_list:
                file_name = cfl.split("/")[-1]
                if is_found == 0:
                    if file_name in sentence:
                        is_found = 1
                        intent_type = 9
                    else:
                        intent_type = 5
        else:
            intent_type = 5

    # About approve
    if intent_type == 1:

        result_file_list = []
        remove_list = []
        approve_set = set()
        found = 0
        print(file_list)

        approve_word = ["advise", "notify", "give_notice", "send_word", "apprise", "apprize"]

        for fl in file_list:
            r = fl.split("/")[-1]
            result_file_list.append(str(r))
        print(result_file_list)

        for rfl in result_file_list:
            print(rfl)
            if rfl in sentence:
                sentence = sentence.replace(rfl, "")
                print(sentence)
                for word in approve_word:
                    if word in sentence:
                        found = 1
                        if " not " in sentence or " un" in sentence:
                            approve_set.add(file_list[result_file_list.index(rfl)])
                            print(rfl)
                            print(file_list[result_file_list.index(rfl)])
                        else:
                            remove_list.append(file_list[result_file_list.index(rfl)])
                            print(rfl)
                            print(file_list[result_file_list.index(rfl)])

                if found == 0:
                    if " not " in sentence or " un" in sentence:
                        remove_list.append(file_list[result_file_list.index(rfl)])
                        print(rfl)
                        print(file_list[result_file_list.index(rfl)])
                    else:
                        approve_set.add(file_list[result_file_list.index(rfl)])
                        print(rfl)
                        print(file_list[result_file_list.index(rfl)])

            elif " this " in sentence:
                recent_file = work_db.get_recent_data(github_email)
                for word in approve_word:
                    if word in sentence:
                        found = 1
                        if " not " in sentence or " un" in sentence:
                            approve_set.add(recent_file)
                            print(recent_file)
                        else:
                            remove_list.append(recent_file)
                            print(recent_file)

                if found == 0:
                    if " not " in sentence or " un" in sentence:
                        remove_list.append(recent_file)
                        print(recent_file)
                    else:
                        approve_set.add(recent_file)
                        print(recent_file)
                break


        if not remove_list and not approve_set:
            work_db.close()
            return 12, "no_file", None, None

        print("remove_list : ", remove_list)
        print("approve_set : ", approve_set)

        work_db.close()

        return 1, approve_set, remove_list, None

    # About lock
    elif intent_type == 2:

        lock_time = 0
        result_file_list = []
        request_lock_set = set()
        remove_lock_list = []

        for fl in file_list:
            r = fl.split("/")[-1]
            result_file_list.append(" " + r)

        for rfl in result_file_list:
            if rfl in sentence:
                sentence = sentence.replace(rfl, "")
                if " not " in sentence or " unlock " in sentence:
                    remove_lock_list.append(file_list[result_file_list.index(rfl)])
                else:
                    try:
                        lock_time = int(re.findall('\d+', sentence)[0])
                    except:
                        lock_time = 1
                    request_lock_set.add(file_list[result_file_list.index(rfl)])

        if not remove_lock_list and not request_lock_set:
            if " not " in sentence or " unlock " in sentence:
                remove_lock_list.append(recent_file)
            elif " this file " in sentence:
                request_lock_set.add(recent_file)
            else:
                work_db.close()
                return 12, "no_file", None, None

        print("remove_lock_list : ", remove_lock_list)
        print("request_lock_set : ", request_lock_set)
        work_db.close()
        return 2, request_lock_set, remove_lock_list, lock_time

    #About history
    elif intent_type == 3:

        result_file_list = get_file_path(file_list)
        file_path = ""

        for rfl in result_file_list:
            name = rfl
            if str(os.sep) in rfl:
                name = rfl.split(os.sep)[-1]
            if name in sentence:
                file_path = rfl

        pattern = re.compile("\d+")
        num_list = re.findall(pattern, sentence)
        num_list[0] = int(num_list[0])
        num_list[1] = int(num_list[1])

        if len(num_list) > 1:
            if num_list[0] < num_list[1]:
                work_db.close()
                return 3, file_list[result_file_list.index(file_path)], num_list[0], num_list[1]
            else:
                work_db.close()
                file_path = file_path.replace(" ", "")
                return 3, file_list[result_file_list.index(file_path)], num_list[1], num_list[0]
        elif len(num_list) == 1:
            work_db.close()
            file_path = file_path.replace(" ", "")
            return 3, file_list[result_file_list.index(file_path)] , num_list[0], num_list[0]

        else:
            recent_file = recent_file.split('/')[-1]
            result_file_list = get_file_path(file_list)
            file_path = ""

            for rfl in result_file_list:
                if recent_file in sentence:
                    file_path = rfl

            if file_path == "":
                work_db.close()
                return 12, "no_file", None, None

            work_db.close()
            file_path = file_path.replace(" ", "")
            return 3, file_list[result_file_list.index(file_path)], 1, 1

    #About direct or indirect ignore
    elif intent_type == 4:

        if " not " in sentence or " unlock " in sentence:
            # 알람 해제
            if " indirect " in sentence:
                work_db.close()
                return 4, 2, 0, None
            else:
                work_db.close()
                return 4, 1, 0, None
        else:
            # 알람 설정
            if " indirect " in sentence:
                work_db.close()
                return 4, 2, 1, None
            else:
                work_db.close()
                return 4, 1, 1, None

    #About check conflict
    elif intent_type == 5:

        result_file_list = get_file_path(file_list)
        file_path = ""

        for rfl in result_file_list:
            if rfl in sentence:
                file_path = file_list[result_file_list.index(rfl)]

        if file_path == "":
            work_db.close()
            return 12, "no_file", None, None

        work_db.close()
        return 5, file_path, None, None

    #About working status
    elif intent_type == 6:

        target_user_id = ""

        for id in slack_id_list:
            if id in sentence:
                target_user_id = id
                break

        if target_user_id == "":
            slack_id = work_db.convert_git_id_to_slack_code(recent_data[2])
            work_db.close()
            return 6, slack_id, recent_data[2], None
        else:
            target_user_email = work_db.convert_slack_code_to_git_id(target_user_id)
            work_db.close()
            return 6, target_user_id, target_user_email, None

    #About channel message
    elif intent_type == 7:

        user_name = work_db.convert_git_id_to_slack_id(github_email)
        word_list = sentence.split()

        try:
            channel_idx = word_list.index("channel") - 1
            if channel_idx != 0:
                channel = word_list[channel_idx].strip()
                start_that = sentence.find(" that ") + 4
                msg = sentence[start_that:].strip()

            else:
                print("There is no channel")
                work_db.close()
                return 12, "no_file", None, None

        except IndexError:
            print("There is no channel")
            work_db.close()
            return 12, "no_file", None, None

        work_db.close()
        return 7, channel, msg, user_name

    #About user message
    elif intent_type == 8:

        user_name = work_db.convert_git_id_to_slack_id(github_email)
        target_user_slack_code = ""

        for id in slack_id_list:
            if id in sentence:
                target_user_slack_code = id
                break

        if target_user_slack_code == "":
            target_user_slack_code = work_db.convert_git_id_to_slack_code(recent_data[2])[0]

        start_that = sentence.find(" that ") + 4
        msg = sentence[start_that:]
        work_db.close()
        return 8, target_user_slack_code, msg, user_name

    #About recommend
    elif intent_type == 9:

        work_db.close()
        return 9, github_email, recent_data[2], None

    #About others
    else:

        if " hi " in sentence or " hello " in sentence :
            print("greeting shell")
            return 10, "greeting", None, None
        elif " bye " in sentence or " see you " in sentence:
            return 11, "bye", None, None
        else:
            return 12, "no_response", None, None


if __name__ == '__main__':
    print(extract_attention_word("hi", 'a'))


token = load_token()
slack = Slacker(token)