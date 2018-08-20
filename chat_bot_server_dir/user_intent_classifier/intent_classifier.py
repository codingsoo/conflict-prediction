import spacy
from server_dir.slack_message_sender import send_channel_message
from chat_bot_server_dir.project_parser import project_parser
from chat_bot_server_dir.bot_server import get_slack_name_list
from chat_bot_server_dir.user_intent_classifier.sentence_type_finder import require_something_sentence
from chat_bot_server_dir.work_database import work_database

# You can download this file : https://spacy.io/usage/vectors-similarity
nlp = spacy.load('C:\\Users\\learn\\PycharmProjects\\conflict-detector2\\venv\\Lib\\site-packages\\en_core_web_lg\\en_core_web_lg-2.0.0')

# bot's feature
# 1. ignore_file : It is like gitignore. User can customize their ignore files.
# 2. lock_file : User can lock their files. If other users try to modify lock_files' related file, chatbot gives them warning.
# 3. code_history : User can ask about code who wrote.
# 4. ignore_alarm : User can ignore direct and indirect conflict.
# 5. check_conflict : Before user works, user can check if he generates conflict or not with user's working file.
# 6. working_status : User can ask about other user's working status
# 7. channel_message : User can let chatbot give message to channel.
# 8. user_message : User can let chatbot give message to other users.
# 9. recommend : User can ask recommend behavior about conflict.
# 10. user_recognize : Bot knows when user connected last time, so bot can greet person with time information. ex) It's been a while~
# 11. greeting : Bot can greet users.
# 12. complimentary_close : Bot can say good bye.
# 13. detect_direct_conflict : Bot can detect direct conflict and severity.
# 14. detect_indirect_conflict : Bot can detect indirect conflict and severity.

question_sentence_list = ["Can you not notify me about hello.py?", "Can you lock hello.py?",
                          "Can you tell me who wrote line14?", "Can you not notify me about indirect conflict?",
                          "Do you think this is gonna make a conflict?", "Can you tell me user2's working status?",
                          "Can you tell everyone that I'm working on File1.py?",
                          "Can you chat to User2 that I will check and solve the problem?",
                          "Can you recommend what should I do to fix the conflict?"]
command_sentence_list = ["Don't alert me about File1.py again.", "Lock hello.py file.", "Tell me who wrote def1().",
                         "Don't alert me about indirect conflict.",
                         "Check File1.py whether it will make conflict or not.",
                         "Tell everyone that I'm working on File1.py to conflict detect channel.",
                         "Send user2 a message that I'm working on class1.",
                         "Give me some recommendation about how to solve the conflict of File1.py."]
suggestion_sentence_list = ["You should not give me notification about File1.py", "You should lock File.py.",
                            "Sayme, you should let me know who wrote code line 1.",
                            "You should not alert me about direct conflict.",
                            "Sayme, you should check File1.py if this is gonna make a conflict.",
                            "You should tell me user1's working status.",
                            "You should announce that don't touch File1.py to conflict detect channel.",
                            "You have to send message to User2 that I will check and solve the confilct.",
                            "You would tell me how I can solve the conflict in File1.py"]
desire_sentence_list = ["I want to ignore any alarm about File1.py.", "I want to lock File1.py.",
                        "I want to know who wrote def1 in File1.py.", "I don't want you to alert about direct conflict",
                        "I want to know that this is gonna make a conflict in File1.py.",
                        "I want to know user1's working status.",
                        "I want to send the message in conflict detector channel that don't modify File1.py.",
                        "I want to send a direct message to user1 that don't modify File1.py.",
                        "I want to get recommendation how I can solve the conflict in File1.py."]


file_list = project_parser("UCNLP", "conflict-detector")["file"]
user_list = get_slack_name_list()


def calcue_max(sentence, list):
    user_input = nlp(sentence)
    max = 0
    for idx in range(len(list)):
        sample_input = nlp(list[idx])
        rate = user_input.similarity(sample_input)
        if rate > max and rate > 0.85:
            max_idx = idx + 1
            max = rate
        if max_idx == 1 or max_idx == 4:
            if 'direct' in sentence or 'indirect' in sentence:
                max_idx = 4
            else:
                max_idx = 1

    return max_idx


def load_token() :
    file_path = os.path.join(Path(os.getcwd()).parent.parent, "all_server_config.ini")

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
# slack = Slacker(token)

def intent_classifier(sentence):
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


def extract_attention_word(sentence):
    import re
    file_list = project_parser("UCNLP", "client")["file"]

    name_list = get_slack_name_list()
    work_db = work_database()
    intent_type = intent_classifier(sentence)
    print(intent_type)

    if intent_type == 1:
        i_file_list = project_parser("UCNLP", "conflict-detector")["file"]

        result_file_list = list()
        remove_list = list()
        approve_set = set()

        for fl in i_file_list:
            r = fl.split("/")[-1]
            result_file_list.append(" "+r)

        for rfl in result_file_list:
            if rfl in sentence:
                if 'not' in sentence or 'n\'t' in sentence or 'un' in sentence:
                    remove_list.append(i_file_list[result_file_list.index(rfl)])
                else:
                    approve_set.add(i_file_list[result_file_list.index(rfl)])

        if len(remove_list) > 0:
            work_db.remove_approved_list("slack_code", remove_list)
            print(remove_list)
        elif len(approve_set) > 0:
            work_db.add_approved_list("slack_code", approve_set)
            print(approve_set)

        return approve_set, remove_list


    elif intent_type == 2:
        file_list = project_parser("UCNLP", "conflict-detector")["file"]

        result_file_list = list()
        request_lock_set = set()
        remove_lock_list = list()

        for fl in file_list:
            r = fl.split("/")[-1]
            result_file_list.append(" " + r)

        for rfl in result_file_list:
            if rfl in sentence:
                if 'not' in sentence or 'nt' in sentence or 'un' in sentence:
                    remove_lock_list.append(file_list[result_file_list.index(rfl)])
                else:
                    try:
                        lock_time = int(re.findall('\d+', sentence)[0])
                    except:
                        lock_time = 1
                    request_lock_set.add(file_list[result_file_list.index(rfl)])

        if len(remove_lock_list) >0 :
            print(remove_lock_list)
        elif len(request_lock_set) >0:
            print(remove_lock_list)

        return request_lock_set, remove_lock_list


    elif intent_type == 3:
        file_list
        result_file_list = get_file_path(file_list)
        file_path = ""

        for rfl in result_file_list:
            if rfl in sentence:
                file_path = file_list[result_file_list.index(rfl)]

        pattern = re.compile("\d+")
        num_list = re.findall(pattern, sentence)

        if len(num_list) > 1:
            if num_list[0] < num_list[1]:
                work_db.get_user_email("conflict-detector", file_path, num_list[0], num_list[1])
            else:
                work_db.get_user_email("conflict-detector", file_path, num_list[1], num_list[0])
        elif len(num_list) == 1:
            work_db.get_user_email("conflict-detector", file_path, num_list[0], num_list[0])


    elif intent_type == 4:
        # if 'not' in sentence or 'n\'t' in sentence or 'un' in sentence:
        if 'indirect' in sentence:
            work_db.add_update_ignore("conflict-detector", [0, 1], "slack_code")
        else:
            work_db.add_update_ignore("conflict-detector", [1, 0], "slack_code")


    elif intent_type == 5:
        # is conflict
        pass


    elif intent_type == 6:
        target_user_name = ""

        for name in name_list:
            if name in sentence:
                target_user_name = name

        if target_user_name == "":
            print("There's no user")
        else:
            user_db.match_user_git_id_code(target_user_name)
            #print(remove_list)

        if len(remove_list) > 0:
            work_db.remove_approved_list(slack_code, remove_list)
            print(remove_list)
        elif len(approve_set) > 0:
            work_db.add_approved_list(slack_code, approve_set)
            print(approve_set)

    elif intent_type == 7:
        import re

        to_channel_regex = r'to [a-zA-Z\s]+channel'
        in_channel_regex = r'in [a-zA-Z\s]+channel'

        to_channel_p = re.compile(to_channel_regex)
        in_channel_p = re.compile(in_channel_regex)

        in_result = in_channel_p.findall(sentence)
        to_result = to_channel_p.findall(sentence)

        if in_result != [] and to_result != []:
            if len(in_result[0]) < len(to_result[0]):
                chaanel = in_result[0][2:-7].strip()
                start_that = sentence.find('that') + 4
                msg = sentence[start_that:].replace('in {} channel'.format(chaanel), '').strip()
            else:
                chaanel = to_result[0][2:-7].strip()
                start_that = sentence.find('that') + 4
                msg = sentence[start_that:].replace('to {} channel'.format(chaanel), '').strip()
            send_channel_message(chaanel, msg)

        elif in_result != []:
            chaanel = in_result[0][2:-7].strip()
            start_that = sentence.find('that') + 4
            msg = sentence[start_that:].replace('in {} channel'.format(chaanel), '').strip()
            send_channel_message(chaanel, msg)

        elif to_result != []:
            chaanel = to_result[0][2:-7].strip()
            start_that = sentence.find('that') + 4
            msg = sentence[start_that:].replace('to {} channel'.format(chaanel), '').strip()
            send_channel_message(chaanel, msg)

        else:
            pass


    elif intent_type == 8:
        pass


    elif intent_type == 9:
        pass

    work_db.close()


# similarity test
# user_input = "I want to stop ignoring File1.py"
# input1 = nlp(user_input)
#
# max = 0
# for idx in range(len(desire_sentence_list)):
#     sample = nlp(desire_sentence_list[idx])
#     rate = input1.similarity(sample)
#     print(rate)
#     if rate > max and rate > 0.85:
#         max_idx = idx+1
#         max = rate
# print(max_idx)

extract_attention_word("Don't ignore File1.py")

if __name__ == '__main__':
    extract_attention_word("Don't alert me about File1.py again.", "jc")