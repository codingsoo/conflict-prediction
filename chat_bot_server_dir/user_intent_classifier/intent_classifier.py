from chat_bot_server_dir.project_parser import project_parser
from chat_bot_server_dir.user_intent_classifier.sentence_type_finder import require_something_sentence
from server_dir.slack_message_sender import *
import uuid
import dialogflow_v2 as dialogflow


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
        print("get_slack_code_list", user_list)
    except KeyError as ex:
        print('Invalid key : %s' % str(ex))
    return user_list


def get_file_name_list(file_abs_path_list):
    file_name_list = []
    for fapl in file_abs_path_list:
        r = fapl.split("/")[-1]
        file_name_list.append(" " + r)
    return file_name_list


def detect_intent_texts(project_id, session_id, text, language_code):
    """Returns the result of detect intent with texts as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversation."""

    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    print('Session path: {}\n'.format(session))


    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)

    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(session=session, query_input=query_input)

    print('=' * 20)
    print('Query text: {}'.format(response.query_result.query_text))
    print('Detected intent: {} (confidence: {})\n'.format(
        response.query_result.intent.display_name,
        response.query_result.intent_detection_confidence))
    print('Fulfillment text: {}\n'.format(
        response.query_result.fulfillment_text))

    return response.query_result.intent.display_name


def get_typo_error_cost(user_input, no_typo_error):
    x_length = len(user_input)+1
    y_length = len(no_typo_error)+1

    arr = [[0 for i in range(y_length)] for j in range(x_length)]

    for i in range(x_length-1):
        arr[i+1][0] = i+1
    for j in range(y_length-1):
        arr[0][j+1] = j+1

    for j in range(y_length-1):
        for i in range(x_length-1):
            if user_input[i] == no_typo_error[j]:
                arr[i+1][j+1] = arr[i][j]
            else:
                arr[i+1][j+1] = min(arr[i][j]+1, min(arr[i+1][j]+1,arr[i][j+1]+1))

    return arr[x_length-1][y_length-1]


def extract_attention_word(owner_name, project_name, sentence, github_email, intent_type, msg_type):

    import re
    work_db = work_database()
    sentence = " " + sentence + " "
    called_file_abs_path_list = []

    # Before classifying intent
    if intent_type == -1:
       # intent_type, sentence = intent_classifier(_sentence)
        intent_type = detect_intent_texts('sayme-9614e',str(uuid.uuid4()),sentence,'en-US')
        print("Intent_type", intent_type)

    # After classifying intent
    if intent_type in ["1_0","1_1", "2_0","2_1", "3", "5", "8", "10", "11", "13"]:
        file_simp_path_list = project_parser(owner_name, project_name)["file"]
        file_abs_path_list = []

        for fspl in file_simp_path_list:
            fapl = owner_name + "/" + project_name + "/" + fspl
            file_abs_path_list.append(fapl)

        print("file_simp_path_list : ", file_simp_path_list)
        print("file_abs_path_list : ", file_abs_path_list)

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
            print("file_name_dict : ", file_name_dict)

            if(msg_type == "message"):
                typo_error_check = 1

                for file_name, fn_idx_list in file_name_dict.items():
                    if file_name in sentence or file_name.split(".")[0] in sentence:
                        typo_error_check = 0

                sentence_split = sentence.split()
                user_file_name = " "
                for i in range(len(sentence_split)):
                    if ".py" in sentence_split[i]:
                        user_file_name = sentence_split[i]
                        break

                if typo_error_check == 1:
                    no_error_file_name = " "
                    min_rate = 1000
                    for file_name, fn_idx_list in file_name_dict.items():
                        typo_rate = get_typo_error_cost(user_file_name, file_name)
                        if(typo_rate < min_rate):
                            min_rate = typo_rate
                            no_error_file_name = file_name

                    user_slack_code = work_db.convert_git_id_to_slack_code(github_email)
                    send_typo_error_button_message(user_slack_code,user_file_name, no_error_file_name , sentence, intent_type)
                    work_db.close()
                    return ERROR, "typo_error_file", None, None

            if(msg_type == "message"):
                typo_error_check = 1

                for file_name, fn_idx_list in file_name_dict.items():
                    if file_name in sentence:
                        typo_error_check = 0

                sentence_split = sentence.split()
                user_file_name = " "
                for i in range(len(sentence_split)):
                    if ".py" in sentence_split[i]:
                        user_file_name = sentence_split[i]
                        break

                if typo_error_check == 1:
                    no_error_file_name = " "
                    min_rate = 1000
                    for file_name, fn_idx_list in file_name_dict.items():
                        typo_rate = get_typo_error_cost(user_file_name, file_name)
                        if(typo_rate < min_rate):
                            min_rate = typo_rate
                            no_error_file_name = file_name

                    user_slack_code = work_db.convert_git_id_to_slack_code(github_email)
                    send_typo_error_button_message(user_slack_code,user_file_name, no_error_file_name , sentence, intent_type)
                    work_db.close()
                    return ERROR, "typo_error_file", None, None

            # Find called files in sentence & decide whether file is same named file
            for file_name, fn_idx_list in file_name_dict.items():
                if file_name in sentence or file_name.split(".")[0] in sentence:
                    # Distinct file
                    if len(fn_idx_list) == 1:
                        called_file_abs_path_list.append(file_abs_path_list[fn_idx_list[0]])
                    # Same named file
                    else:
                        same_named_file_list = []
                        for idx in fn_idx_list:
                            same_named_file_list.append(file_abs_path_list[idx])
                        called_same_named_file_dict[file_name] = same_named_file_list

            # If there are same named files
            if called_same_named_file_dict:
                print("called_same_named_file_dict : ", called_same_named_file_dict)
                user_slack_code = work_db.convert_git_id_to_slack_code(github_email)
                send_file_selection_button_message(user_slack_code, called_same_named_file_dict, sentence, intent_type)
                if not called_file_abs_path_list:
                    work_db.close()
                    return ERROR, "same_named_file", None, None

            if not called_file_abs_path_list:
                work_db.close()
                return ERROR, "no_file", None, None

            if intent_type in ["3", "5", "8", "10", "11", "13"] and len(called_file_abs_path_list) != 1:
                work_db.close()
                return ERROR, "many_files", None, None

        print("called_file_abs_path_list : ", called_file_abs_path_list)

    # About ignore
    if intent_type == "1_0" or intent_type == "1_1"  :
        remove_list = []
        approve_set = set()

        for file_abs_path in called_file_abs_path_list:
            sentence = sentence.replace(file_abs_path, " ")
            if intent_type == "1_0":
                approve_set.add(file_abs_path)
            else:
                remove_list.append(file_abs_path)

        print("remove_list : ", remove_list)
        print("approve_set : ", approve_set)

        work_db.close()
        return 1, approve_set, remove_list, None

    # About lock
    elif intent_type == "2_0" or intent_type == "2_1":
        request_lock_set = set()
        remove_lock_set = set()
        lock_time = 0

        for file_abs_path in called_file_abs_path_list:
            sentence = sentence.replace(file_abs_path, " ")
           # if " not " in sentence or " unlock " in sentence or " stop " in sentence:
            if intent_type == "2_1":
                remove_lock_set.add(file_abs_path)
            else:
                try:
                    lock_time = int(re.findall('\d+', sentence)[0])
                except:
                    lock_time = 1
                request_lock_set.add(file_abs_path)

        print("remove_lock_set : ", remove_lock_set)
        print("request_lock_set : ", request_lock_set)

        work_db.close()
        return 2, request_lock_set, remove_lock_set, lock_time

    # About code history
    elif intent_type == "3":
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
            # Check the total history of file
            start_line = end_line = -1

        work_db.close()
        return 3, called_file_abs_path_list[0], start_line, end_line

    # About direct or indirect ignore
    elif intent_type == "4_0" or intent_type == "4_1":
        # ignore
        if intent_type == "4_0":
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
                return 4, DIRECT, UNIGNORE, None

    # About check conflict
    elif intent_type == "5":
        work_db.close()
        return 5, github_email, called_file_abs_path_list[0], None

    # About working status
    elif intent_type == "6":
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

    # About user message
    elif intent_type == "7":

        target_slack_code = ""

        slack_code_list = get_slack_code_list()
        for code in slack_code_list:
            if code in sentence:
                target_slack_code = code
                break

        if target_slack_code == "":
            recent_data = work_db.get_recent_data(github_email)
            target_slack_code = work_db.convert_git_id_to_slack_code(recent_data[2])[0]

        # We should use unmodified sentence
        sentence = sentence.replace('“','"')
        sentence = sentence.replace('”','"')

        start_quot_idx = sentence.find('"')
        end_quot_idx = sentence.rfind('"')
        if start_quot_idx == -1 or end_quot_idx == -1 or start_quot_idx == end_quot_idx:
            print('You must write your message between two double quotation like "message"')
            msg = ''
        else:
            msg = sentence[start_quot_idx + 1:end_quot_idx].strip()

        work_db.close()
        return 7, target_slack_code, msg, None

    # About recommend
    elif intent_type == "8":
        work_db.close()
        return 8, github_email, called_file_abs_path_list[0], None

    # About check ignored file
    elif intent_type == "9":
        work_db.close()
        if '@' in sentence:
            idx = sentence.find('@')
            other_user_code = sentence[idx+1:idx+9]
            return 9, other_user_code, None, None
        return 9, None, None, None

    # About locker of file
    elif intent_type == "10":
        work_db.close()
        return 10, called_file_abs_path_list[0], None, None

    # About severity
    elif intent_type == "11":
        work_db.close()
        return 11, called_file_abs_path_list[0], None, None

    # About prediction alarm
    elif intent_type == "12_0" or intent_type == "12_1":
        work_db.close()
        if intent_type == "12_0":
            return 4, PREDICTION, IGNORE, None
        else:
            return 4, PREDICTION, UNIGNORE, None

    elif intent_type == "13":
        work_db.close()
        return 13, called_file_abs_path_list[0], None, None

    else:
        work_db.close()
        if intent_type == "14" :
            return ERROR - 2, "greeting", None, None
        elif intent_type == "15":
            return ERROR - 1, "bye", None, None
        else:
            return ERROR, "no_response", None, None


if __name__ == '__main__':
    print(extract_attention_word("hi", 'a'))
