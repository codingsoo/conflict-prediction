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



# nlp = spacy.load('/Users/seonkyukim/Desktop/UCI/Chatbot/conflict-detector/venv/lib/python3.6/site-packages/en_core_web_lg/en_core_web_lg-2.0.0')
# nlp = spacy.load('/Users/Kathryn/Documents/GitHub/conflict-detector/venv/lib/python3.6/site-packages/en_core_web_lg/en_core_web_lg-2.0.0')
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
# 10. check_ignore : A user can ask chatbot which files are ignored.
# 11. check_lock : A user can ask chatbot about who locked the file.
# 12. check_severity : A user can ask chatbot about how severe conflict is.
# 13. user_recognize : Chatbot knows when last time a user connected is, so bot can greet the user with time information. ex) It's been a while~
# 14. greeting : Chatbot can greet users.
# 15. complimentary_close : Chatbot can say good bye.
# 16. detect_direct_conflict : Chatbot can detect direct conflict and severity.
# 17. detect_indirect_conflict : Chatbot can detect indirect conflict and severity.

question_sentence_list = ["Can you not notify me about hello.py?",
                          "Can you lock hello.py?",
                          "Can you tell me who wrote line 14 to line 18 at file1.py?",
                          "Can you not notify me about indirect conflict?",
                          "Do you think hello.py is gonna make a conflict?",
                          "Can you tell me <@UCFNMU2ED>'s working status?",
                          'Can you tell code-conflict-chatbot channel that “I am working on File1.py”',
                          'Can you chat to <@UCFNMU2ED> "I will check and solve the problem"?',
                          "Can you recommend what I should do to fix the conflict in File.py?",
                          "Can you tell me which files are ignored?"
                          "Can you tell me who locked file1.py?",
                          "Can you tell me who ignored file1.py?"
                          ]
command_sentence_list = ["Do not notify me about File1.py again.",
                         "Don't lock hello.py.",
                         "Tell me who wrote line 70 to line 90 in file1.py.",
                         "Do not alert me about indirect conflict.",
                         "Check File1.py whether it will make a conflict or not.",
                         "Tell me where <@UCFNMU2ED>'s working status.",
                         'Tell code-conflict-chatbot channel that “I am working on File1.py”',
                         'Send a message to <@UCFNMU2ED> "I am working on class1".',
                         "Give me some recommendation about how to solve the conflict of File1.py.",
                         "Tell me which files are ignored.",
                         "Tell me who lock file1.py.",
                         "Tell me the severity of the conflict in file1.py."
                         ]
suggestion_sentence_list = ["You should not give me notification about File1.py.",
                            "You should lock File.pwy.",
                            "You should let me know who wrote code line 1 to line 9 at file1.py.",
                            "You should not alert me about direct conflict.",
                            "You should check File1.py if this is gonna make a conflict.",
                            "You should tell me <@UCFNMU2ED>'s working status.",
                            'You should announce to code-conflict-chatbot channel that "Do not touch File1.py".',
                            'You have to send a message to <@UCFNMU2ED> "I will check and solve the conflict".',
                            "You would tell me how I can solve the conflict in File1.py",
                            "You should tell me which files are ignored."
                            "You should tell me who lock file1.py.",
                            "You should tell me the severity of the conflict in file.py."]

desire_sentence_list = ["I want to ignore any alarm about File1.py.",
                        "I want to lock File1.py.",
                        "I want to know who wrote line 70 to line 90 in File1.py.",
                        "I do not want to get alert about direct conflict.",
                        "I want to know that this is gonna make a conflict in File1.py.",
                        "I want to know <@UCFNMU2ED>'s working status.",
                        'I want to send the message to conflict detector channel that "Do not modify File1.py".',
                        'I want to send a direct message to <@UCFNMU2ED> "Do not modify File1.py".',
                        "I want to get recommendation how I can solve the conflict in File1.py.",
                        "I want to know which files are ignored.",
                        "I want to know who lock file1.py.",
                        "I want to know the severity of the conflict in file.py"]

CONST_ERROR = 16

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

def convert_git_id_to_slack_id_from_slack(git_id):
    user_list = get_slack_id_and_git_email_list()
    slack_id = ""
    for user in user_list:
        if user[1] == git_id:
            slack_id = user[0]

    return slack_id

def get_slack_id_and_git_email_list():
    try:
        user_list = list()
        # Get users list
        response = slack.users.list()
        users = response.body['members']
        for user in users:
            display_name = user.get('profile').get('display_name')
            git_email = user.get('profile').get('email')
            if display_name != '':
                user_list.append((display_name, git_email))
            else:
                user_list.append((user.get('profile').get('real_name'), git_email))
    except KeyError as ex:
        print('Invalid key : %s' % str(ex))
    return user_list

def get_slack_code_list():
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
    user_input = nlp(sentence.strip())
    max = 0
    max_idx = CONST_ERROR
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

    if max_idx in [1, 2, 3, 5, 11, 12] and ".py" not in sentence:
        return CONST_ERROR

    print ("max rate : ", max)
    return max_idx

def intent_classifier(_sentence):
    if " this file " in _sentence :
        _sentence = _sentence.replace("this file", ":.py")
    sentence_type, sentence = require_something_sentence(_sentence)

    print("sentence_type", sentence_type)
    # Question
    if sentence_type == 1:
        max_idx = calcue_max(sentence, question_sentence_list)
        return max_idx, sentence


    # Command
    elif sentence_type == 2:
        max_idx = calcue_max(sentence, command_sentence_list)
        return max_idx, sentence


    # Suggestion
    elif sentence_type == 3:
        max_idx = calcue_max(sentence, suggestion_sentence_list)
        return max_idx, sentence


    # Desire
    elif sentence_type == 4:
        max_idx = calcue_max(sentence, desire_sentence_list)
        return max_idx, sentence

    else:
        return CONST_ERROR, sentence

def get_file_path(file_list):
    result_file_list = []
    for fl in file_list:
        r = fl.split("/")[-1]
        result_file_list.append(" " + r)
    return result_file_list


def extract_attention_word(owner_name, project_name,_sentence, github_email):
    import re

    work_db = work_database()
    onlyFile_list = project_parser(owner_name, project_name)["file"]
    file_list = list()

    for ofl in onlyFile_list:
        fl = owner_name + "/" + project_name + "/" + ofl
        file_list.append(fl)

    slack_code_list = get_slack_code_list()

    recent_data = work_db.get_recent_data(github_email)
    if recent_data:
        recent_file = recent_data[0].split('|')[0]
    else:
        recent_data = "no recent data"
        recent_file = "no recent file"
    print("recent_data", recent_data)
    print("recent file", recent_file)

    sentence = " " + _sentence + " "
    yes_list = ["y","yes","affirmative", "amen","fine","good","okay","true","yea","all right","aye","beyond a doubt","by all means","certainly","definitely","even so","exctly","gladly","good enough","granted","indubitably","just so","most assuredly","naturally","of course","positively","precisely","sure thing","surely","undoubtedly","unquestionably","very well","willingly","without fail","yep"]
    no_list = ["n","no", "nay", "nix", "never"]

    for yes in yes_list:
        if " " + yes + " " in sentence:
            work_db.close()
            return 12, "yes", None, None
    for no in no_list:
        if " " + no + " " in sentence:
            work_db.close()
            return 12, "no", None, None

    intent_type, sentence = intent_classifier(_sentence)

    print("Intent_type", intent_type)

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
        remove_list = []
        approve_set = set()
        found = 0

        approve_word = ["advise", "notify", "give_notice", "send_word", "apprise", "apprize", "alert", "see", "hear", "bulletin", "notification", "notice", "proclamation", "warning", "advertisement", "advisory","alert","communication","communique","declaration","information","message","news","release","report","statement"]

        result_file_list = get_file_path(file_list)

        for rfl in result_file_list:
            print(rfl)
            if rfl in sentence:
                sentence = sentence.replace(rfl, " ")
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
                if recent_file:
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
            return CONST_ERROR, "no_file", None, None

        print("remove_list : ", remove_list)
        print("approve_set : ", approve_set)

        work_db.close()

        return 1, approve_set, remove_list, None

    # About lock
    elif intent_type == 2:

        lock_time = 0
        request_lock_set = set()
        remove_lock_list = []

        result_file_list = get_file_path(file_list)

        for rfl in result_file_list:
            if rfl in sentence:
                sentence = sentence.replace(rfl, " ")
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
                return CONST_ERROR, "no_file", None, None

        print("remove_lock_list : ", remove_lock_list)
        print("request_lock_set : ", request_lock_set)
        work_db.close()
        return 2, request_lock_set, remove_lock_list, lock_time

    # About code history
    elif intent_type == 3:
        result_file_list = get_file_path(file_list)
        file_path = ""

        for rfl in result_file_list:
            if rfl in sentence:
                file_path = file_list[result_file_list.index(rfl)]

        if file_path == "":
            work_db.close()
            return CONST_ERROR, "no_file", None, None

        pattern = re.compile("\d+")
        num_list = re.findall(pattern, sentence)

        if len(num_list) >= 2:
            num_list[0] = int(num_list[0])
            num_list[1] = int(num_list[1])
            if num_list[0] < num_list[1]:
                start_line = num_list[0]
                end_line = num_list[1]
            else:
                start_line = num_list[1]
                end_line = num_list[0]

        elif len(num_list) == 1:
            start_line = end_line = int(num_list[0])

        else:
            start_line = end_line = 1

        work_db.close()
        return 3, file_path, start_line, end_line

    # About direct or indirect ignore
    elif intent_type == 4:
        found = 0
        approve_word = ["advise", "notify", "give_notice", "send_word", "apprise", "apprize", "alert", "see", "hear"]

        for word in approve_word:
            if word in sentence:
                found = 1
                # ignore
                if " not " in sentence or " un" in sentence:
                    if " indirect " in sentence:
                        work_db.close()
                        return 4, 2, 1, None
                    else:
                        work_db.close()
                        return 4, 1, 1, None
                # unignore
                else:
                    if " indirect " in sentence:
                        work_db.close()
                        return 4, 2, 0, None
                    else:
                        work_db.close()
                        return 4, 1, 0, None
        if found == 0:
            if " not " in sentence or " un" in sentence:
                if " indirect " in sentence:
                    work_db.close()
                    return 4, 2, 0, None
                else:
                    work_db.close()
                    return 4, 1, 0, None
            else:
                if " indirect " in sentence:
                    work_db.close()
                    return 4, 2, 1, None
                else:
                    work_db.close()
                    return 4, 1, 1, None

    # About check conflict
    elif intent_type == 5:
        result_file_list = get_file_path(file_list)
        file_path = ""

        for rfl in result_file_list:
            if rfl in sentence:
                file_path = file_list[result_file_list.index(rfl)]

        if file_path == "":
            work_db.close()
            return CONST_ERROR, "no_file", None, None

        work_db.close()
        return 5, file_path, None, None

    # About working status
    elif intent_type == 6:
        target_user_slack_code = ""

        for code in slack_code_list:
            if code in sentence:
                target_user_slack_code = code
                break

        if target_user_slack_code == "":
            slack_id = work_db.convert_git_id_to_slack_code(recent_data[2])
            work_db.close()
            return 6, slack_id, recent_data[2], None
        else:
            target_user_email = work_db.convert_slack_code_to_git_id(target_user_slack_code)
            work_db.close()
            return 6, target_user_slack_code, target_user_email, None

    # About channel message
    elif intent_type == 7:

        user_name = work_db.convert_git_id_to_slack_id(github_email)

        # We should use unmodified sentence.
        _sentence = _sentence.replace('“','"')
        _sentence = _sentence.replace('”','"')
        word_list = _sentence.split(" ")

        print("word_list", word_list)
        try:
            channel_idx = word_list.index("channel")
            if channel_idx != 0:
                channel = word_list[channel_idx - 1].strip()
               # msg = " ".join(word_list[channel_idx + 1:]).strip()
                start_quot_idx = _sentence.find('"')
                end_quot_idx = _sentence.rfind('"')
                if start_quot_idx == -1 or end_quot_idx == -1 or start_quot_idx == end_quot_idx:
                    print('You must write your message between two double quotation like "message"')
                    msg = ""
                else:
                    msg = _sentence[start_quot_idx + 1:end_quot_idx].strip()
            else:
                print("There is no channel")
                work_db.close()
                return CONST_ERROR, "no_file", None, None

        except IndexError:
            print("There is no channel")
            work_db.close()
            return CONST_ERROR, "no_file", None, None

        work_db.close()
        return 7, channel, msg, user_name

    # About user message
    elif intent_type == 8:

        user_name = work_db.convert_git_id_to_slack_id(github_email)
        target_user_slack_code = ""

        # We should use unmodified sentence

        _sentence = _sentence.replace('“','"')
        _sentence = _sentence.replace('”','"')

        for code in slack_code_list:
            if code in _sentence:
                target_user_slack_code = code
                break

        if target_user_slack_code == "":
            target_user_slack_code = work_db.convert_git_id_to_slack_code(recent_data[2])[0]

        _sentence = _sentence.replace('“','"')
        _sentence = _sentence.replace('”','"')

        start_quot_idx = _sentence.find('"')
        end_quot_idx = _sentence.rfind('"')
        if start_quot_idx == -1 or end_quot_idx == -1 or start_quot_idx == end_quot_idx:
            print('You must write your message between two double quotation like "message"')
            msg = ''
        else:
            msg = _sentence[start_quot_idx + 1:end_quot_idx].strip()

        work_db.close()
        return 8, target_user_slack_code, msg, user_name

    # About recommend
    elif intent_type == 9:
        work_db.close()
        return 9, github_email, recent_data[2], None

    # About check ignored file
    elif intent_type == 10:
        work_db.close()
        return 10, None, None, None

    # About locker of file
    elif intent_type == 11:
        result_file_list = get_file_path(file_list)
        file_path = ""

        for rfl in result_file_list:
            if rfl in sentence:
                file_path = file_list[result_file_list.index(rfl)]

        if file_path == "":
            work_db.close()
            return CONST_ERROR, "no_file", None, None

        work_db.close()
        return 11, file_path, None, None

    # About severity
    elif intent_type == 12:
        result_file_list = get_file_path(file_list)
        file_path = ""

        for rfl in result_file_list:
            if rfl in sentence:
                file_path = file_list[result_file_list.index(rfl)]

        if file_path == "":
            work_db.close()
            return CONST_ERROR, "no_file", None, None

        work_db.close()
        return 12, file_path, None, None

    else:
        work_db.close()
        if " hi " in sentence or " hello " in sentence:
            print("greeting shell")
            return CONST_ERROR - 2, "greeting", None, None
        elif " bye " in sentence or " see you " in sentence:
            return CONST_ERROR - 1, "bye", None, None
        else:
            return CONST_ERROR, "no_response", None, None


if __name__ == '__main__':
    print(extract_attention_word("hi", 'a'))


token = load_token()
slack = Slacker(token)
