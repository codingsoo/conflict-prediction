import spacy
from chat_bot_server_dir.project_parser import project_parser
from chat_bot_server_dir.user_intent_classifier.sentence_type_finder import require_something_sentence
from server_dir.slack_message_sender import *

# You can download this file : https://spacy.io/usage/vectors-similarity

# nlp = spacy.load('/Users/seonkyukim/Desktop/UCI/Chatbot/conflict-detector/venv/lib/python3.6/site-packages/en_core_web_lg/en_core_web_lg-2.0.0')
nlp = spacy.load('/Users/Kathryn/Documents/GitHub/conflict-detector/venv/lib/python3.6/site-packages/en_core_web_lg/en_core_web_lg-2.0.0')
#nlp = spacy.load('/Users/sooyoungbaek/conflict-detector/venv/lib/python3.6/site-packages/en_core_web_lg/en_core_web_lg-2.0.0')

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
# 10. check_ignored_file : A user can ask chatbot which files are ignored.
# 11. check_locker : A user can ask chatbot about who locked the file.
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
                            "You should lock File.py.",
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



def load_token() :
    file_path = os.path.join(Path(os.getcwd()).parent, "all_server_config.ini")
    token = ''
    if not os.path.isfile(file_path) :
        print("ERROR :: There is no all_server_config.ini")
        exit(2)
    else :
        config = configparser.ConfigParser()
        config.read(file_path)
        try :
            token = config["SLACK"]["TOKEN"]
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


def get_file_name_list(file_abs_path_list):
    file_name_list = []
    for fapl in file_abs_path_list:
        r = fapl.split("/")[-1]
        file_name_list.append(" " + r)
    return file_name_list


def calcue_max(sentence, list):
    user_input = nlp(sentence.strip())
    max = 0
    max_idx = ERROR
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

    if max_idx == 1 or max_idx == 10:
        if ".py" in sentence:
            max_idx = 1
        else:
            max_idx = 10

    if max_idx == 7 or max_idx == 8:
        if " <@" in sentence:
            max_idx = 8
        else:
            max_idx = 7

    if max_idx in [1, 2, 3, 5, 9, 11, 12] and ".py" not in sentence:
        return ERROR

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
        return ERROR, sentence


def extract_attention_word(owner_name, project_name,_sentence, github_email, intent_type):
    import re

    work_db = work_database()

    sentence = " " + _sentence + " "
    yes_list = ["y","yes","affirmative", "amen","fine","good","okay","true","yea","all right","aye","beyond a doubt","by all means","certainly","definitely","even so","exctly","gladly","good enough","granted","indubitably","just so","most assuredly","naturally","of course","positively","precisely","sure thing","surely","undoubtedly","unquestionably","very well","willingly","without fail","yep"]
    no_list = ["n","no", "nay", "nix", "never"]

    for yes in yes_list:
        if " " + yes + " " in sentence:
            work_db.close()
            return 13, "yes", None, None
    for no in no_list:
        if " " + no + " " in sentence:
            work_db.close()
            return 13, "no", None, None

    if intent_type == -1:
        intent_type, sentence = intent_classifier(_sentence)

        print("Intent_type", intent_type)

        # help classification about intent_type 5 and 9
        # if conflict_file in sentence, we can think user wants to recommendation.
        is_found = 0
        if intent_type in [5, 9]:
            conflict_file_list = work_db.all_conflict_list(github_email)
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

    if intent_type in [1, 2, 3, 5, 9, 11, 12]:
        file_simp_path_list = project_parser(owner_name, project_name)["file"]
        file_abs_path_list = []
        called_file_abs_path_list = []

        for fspl in file_simp_path_list:
            fapl = owner_name + "/" + project_name + "/" + fspl
            file_abs_path_list.append(fapl)

        print("file_simp_path_list", file_simp_path_list)
        print("file_abs_path_list", file_abs_path_list)

        # If the format of called file is already absolute path, just pass.
        for fapl in file_abs_path_list:
            if fapl in sentence:
                called_file_abs_path_list.append(fapl)

        # If not, find called file in sentence.
        if not called_file_abs_path_list:
            file_name_dict = dict()
            called_same_named_file_dict = dict()
            file_name_list = get_file_name_list(file_abs_path_list)

            # Create the total of file information.
            for fnl_idx, fnl in enumerate(file_name_list):
                try:
                    file_name_dict[fnl].append(fnl_idx)
                except:
                    file_name_dict[fnl] = [fnl_idx]
            print("file_name_dict", file_name_dict)

            # Find called files in sentence & decide whether file is same named file
            for file_name, fn_idx_list in file_name_dict.items():
                if file_name in sentence:
                    if len(fn_idx_list) == 1:
                        print("only one")
                        called_file_abs_path_list.append(file_abs_path_list[fn_idx_list[0]])
                    else:
                        # duplicate
                        print("duplicate")
                        same_named_file_list = []
                        for idx in fn_idx_list:
                            same_named_file_list.append(file_abs_path_list[idx])
                        called_same_named_file_dict[file_name] = same_named_file_list

            # If there are same named files
            if called_same_named_file_dict:
                print("called_same_named_file_dict", called_same_named_file_dict)
                user_slack_code = work_db.convert_git_id_to_slack_code(github_email)
                send_button_message(user_slack_code, called_same_named_file_dict, sentence, intent_type)
                if not called_file_abs_path_list:
                    work_db.close()
                    return ERROR, "same_named_file", None, None

            if not called_file_abs_path_list:
                work_db.close()
                return ERROR, "no_file", None, None

            if intent_type in [3, 5, 9, 11, 12] and len(called_file_abs_path_list) != 1:
                work_db.close()
                return ERROR, "many_files", None, None

        print("called_file_abs_path_list", called_file_abs_path_list)


    if intent_type == 1:
        remove_list = []
        approve_set = set()
        approve_word = ["advise", "notify", "give_notice", "send_word", "apprise", "apprize", "alert", "see", "hear", "bulletin", "notification", "notice", "proclamation", "warning", "advertisement", "advisory","alert","communication","communique","declaration","information","message","news","release","report","statement"]

        found = 0
        for file_abs_path in called_file_abs_path_list:
            sentence = sentence.replace(file_abs_path, " ")
            for word in approve_word:
                if word in sentence:
                    found = 1
                    if " not " in sentence or " un" in sentence:
                        approve_set.add(file_abs_path)
                    else:
                        remove_list.append(file_abs_path)

            if found == 0:
                if " not " in sentence or " un" in sentence:
                    remove_list.append(file_abs_path)
                else:
                    approve_set.add(file_abs_path)

        print("remove_list : ", remove_list)
        print("approve_set : ", approve_set)

        work_db.close()

        return 1, approve_set, remove_list, None

    # About lock
    elif intent_type == 2:
        remove_lock_list = []
        request_lock_set = set()
        lock_time = 0

        for file_abs_path in called_file_abs_path_list:
            sentence = sentence.replace(file_abs_path, " ")
            if " not " in sentence or " unlock " in sentence:
                remove_lock_list.append(file_abs_path)
            else:
                try:
                    lock_time = int(re.findall('\d+', sentence)[0])
                except:
                    lock_time = 1
                request_lock_set.add(file_abs_path)

        print("remove_lock_list : ", remove_lock_list)
        print("request_lock_set : ", request_lock_set)

        work_db.close()
        return 2, request_lock_set, remove_lock_list, lock_time

    # About code history
    elif intent_type == 3:
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
        return 3, called_file_abs_path_list[0], start_line, end_line

    # About direct or indirect ignore
    elif intent_type == 4:
        approve_word = ["advise", "notify", "give_notice", "send_word", "apprise", "apprize", "alert", "see", "hear"]
        found = 0

        for word in approve_word:
            if word in sentence:
                found = 1
                # ignore
                if " not " in sentence or " un" in sentence:
                    if " indirect " in sentence:
                        work_db.close()
                        return 4, INDIRECT, IGNORE, None
                    else:
                        work_db.close()
                        return 4, DIRECT, IGNORE, None
                # unignore
                else:
                    if " indirect " in sentence:
                        work_db.close()
                        return 4, INDIRECT, UNIGNORE, None
                    else:
                        work_db.close()
                        return 4, INDIRECT, UNIGNORE, None
        if found == 0:
            if " not " in sentence or " un" in sentence:
                if " indirect " in sentence:
                    work_db.close()
                    return 4, INDIRECT, UNIGNORE, None
                else:
                    work_db.close()
                    return 4, DIRECT, UNIGNORE, None
            else:
                if " indirect " in sentence:
                    work_db.close()
                    return 4, INDIRECT, IGNORE, None
                else:
                    work_db.close()
                    return 4, INDIRECT, IGNORE, None

    # About check conflict
    elif intent_type == 5:
        work_db.close()
        return 5, called_file_abs_path_list[0], None, None

    # About working status
    elif intent_type == 6:
        target_slack_code = ""

        slack_code_list = get_slack_code_list()
        for code in slack_code_list:
            if code in sentence:
                target_slack_code = code
                break

        if target_slack_code == "":
            recent_data = work_db.get_recent_data(github_email)
            target_slack_code = work_db.convert_git_id_to_slack_code(recent_data[2])
            work_db.close()
            return 6, target_slack_code, recent_data[2], None

        else:
            target_git_id = work_db.convert_slack_code_to_git_id(target_slack_code)
            work_db.close()
            return 6, target_slack_code, target_git_id, None

    # About channel message
    elif intent_type == 7:

        user_slack_id = work_db.convert_git_id_to_slack_id(github_email)

        # We should use unmodified sentence.
        _sentence = _sentence.replace('“','"')
        _sentence = _sentence.replace('”','"')
        word_list = _sentence.split(" ")

        print("word_list", word_list)
        try:
            channel_idx = word_list.index("channel")
            if channel_idx != 0:
                target_channel = word_list[channel_idx - 1].strip()
                # msg = " ".join(word_list[channel_idx + 1:]).strip()
                start_quot_idx = _sentence.find('"')
                end_quot_idx = _sentence.rfind('"')
                if start_quot_idx == -1 or end_quot_idx == -1 or start_quot_idx == end_quot_idx:
                    print('You must write your message between two double quotation like "message"')
                    msg = ""
                else:
                    msg = _sentence[start_quot_idx + 1:end_quot_idx].strip()
            else:
                work_db.close()
                return ERROR, "no_channel", None, None

        except IndexError:
            work_db.close()
            return ERROR, "no_channel", None, None

        work_db.close()
        return 7, target_channel, msg, user_slack_id

    # About user message
    elif intent_type == 8:

        user_slack_id = work_db.convert_git_id_to_slack_id(github_email)
        target_slack_code = ""

        slack_code_list = get_slack_code_list()
        for code in slack_code_list:
            if code in _sentence:
                target_slack_code = code
                break

        if target_slack_code == "":
            recent_data = work_db.get_recent_data(github_email)
            target_slack_code = work_db.convert_git_id_to_slack_code(recent_data[2])[0]

        # We should use unmodified sentence
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
        return 8, target_slack_code, msg, user_slack_id

    # About recommend
    elif intent_type == 9:
        recent_data = work_db.get_recent_data(github_email)
        work_db.close()
        return 9, github_email, recent_data[2], None

    # About check ignored file
    elif intent_type == 10:
        work_db.close()
        return 10, None, None, None

    # About locker of file
    elif intent_type == 11:
        work_db.close()
        return 11, called_file_abs_path_list[0], None, None

    # About severity
    elif intent_type == 12:
        work_db.close()
        return 12, called_file_abs_path_list[0], None, None

    else:
        work_db.close()
        if " hi " in sentence or " hello " in sentence:
            return ERROR - 2, "greeting", None, None
        elif " bye " in sentence or " see you " in sentence:
            return ERROR - 1, "bye", None, None
        else:
            return ERROR, "no_response", None, None


if __name__ == '__main__':
    print(extract_attention_word("hi", 'a'))
