from chat_bot_server_dir.work_database import work_database
from chat_bot_server_dir.intent_func import get_user_email
from server_dir.slack_message_sender import send_channel_message
from server_dir.slack_message_sender import send_direct_message
from chat_bot_server_dir.user_intent_classifier.intent_classifier import convert_git_id_to_slack_id_from_slack, CONST_ERROR
import os, random

def sentence_processing_main(intent_type, slack_code, param0, param1, param2):
    message = "default"

    if(intent_type == 1):
        message = approved_file_logic(slack_code, param0, param1)

    elif(intent_type == 2):
        message = lock_file_logic(slack_code, param0, param1, param2)

    elif(intent_type == 3):
        message = code_history_logic(slack_code, param0, param1, param2)

    elif(intent_type == 4):
        message = ignore_file_logic(slack_code, param0, param1)

    elif(intent_type == 5):
        message = check_conflict_logic(slack_code, param0)

    elif(intent_type == 6):
        message = other_working_status_logic(slack_code, param0, param1)

    elif(intent_type == 7):
        message = send_message_channel_logic(param0, param1, param2)

    elif(intent_type == 8):
        message = send_message_direct_logic(param0, param1, param2)

    elif(intent_type == 9):
        message = recommend_solve_conflict_logic(param0, param1)

    elif(intent_type == 10):
        message = find_locker_logic(slack_code, param0)

    elif(intent_type == 11):
        message = find_severity_logic(slack_code, param0)

    elif(intent_type == 12):
        message = response_logic(slack_code, param0)

    elif(intent_type == CONST_ERROR - 2):
        message = greeting_logic(slack_code)

    elif (intent_type == CONST_ERROR - 1):
        message = bye_logic()

    elif(intent_type == CONST_ERROR):
        if param0 == "no_response":
            message = """I don't know what are you talking about. I am conflict detect chatbot, and I have 12 talking features : 
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
            """
        elif param0 == "no_file":
            message = "There is no such file. Please say it again."
        elif param0 == "no_channel":
            message = "There is no such channel. Please say it again."

    return message

def approved_file_logic(slack_code, approved_set, removed_list):
    w_db = work_database()
    user_name = w_db.convert_slack_code_to_slack_id(slack_code)
    project_name = w_db.get_repository_name(slack_code)

    approved_list = list(approved_set)

    print(slack_code)
    print("approve !! : " + str(approved_list))
    print("remove !! : " + str(removed_list))

    message = ""
    ch_message = ""
    if approved_list:
        diff_approved_set = w_db.add_approved_list(project_name=project_name,
                               req_approved_set=approved_set)

        if diff_approved_set:
            for al in approved_list:
                ch_message += random.choice(shell_dict['feat_ignore_channel'])
                ch_message = ch_message.format(user_name, al)

            send_channel_message("code-conflict-chatbot", ch_message)

            message += random.choice(shell_dict['feat_ignore_file'])
            message = message.format(approved_list[0])

        else:
            for al in approved_list:
                message += "You already ignored {} file!".format(al)

    if removed_list:
        success_list, fail_list = w_db.remove_approved_list(project_name=project_name,
                                 remove_approved_list=removed_list)

        if success_list:
            for sl in success_list:
                ch_message += random.choice(shell_dict['feat_unignore_channel'])
                ch_message = ch_message.format(user_name, sl)
            send_channel_message("code-conflict-chatbot", ch_message)

            for sl in success_list:
                message += random.choice(shell_dict['feat_unignore_file'])
                message = message.format(sl)

        if fail_list:
            for fl in fail_list:
                message += "{} is not in approved list.\n".format(fl)

    w_db.close()

    return message


def lock_file_logic(slack_code, request_lock_set, remove_lock_list, lock_time):
    w_db = work_database()

    project_name = w_db.get_repository_name(slack_code)
    message = ""

    m1 = ""
    m2 = ""

    if request_lock_set:
        lock_file_list, already_lock_list = list(w_db.add_lock_list(slack_code, request_lock_set, lock_time))
        if already_lock_list:
            for file_name in already_lock_list:
                slack_code, remain_time_str = w_db.check_user_and_remain_time_of_lock_file(project_name, file_name)
                user_name = w_db.convert_slack_code_to_slack_id(slack_code)

                message += random.choice(shell_dict['feat_lock_overlap'])
                message = message.format(user_name, file_name, remain_time_str)

        if lock_file_list:
            ch_message = ""
            user_name = w_db.convert_slack_code_to_slack_id(slack_code)
            for file_name in lock_file_list:
                ch_message += "{} locked {} file for {} hour(s).".format(user_name, file_name, lock_time)
            send_channel_message("code-conflict-chatbot", ch_message)

            message += random.choice(shell_dict['feat_lock_file'])
            ele = ', '.join(list(lock_file_list))
            message = message.format(ele)

    if remove_lock_list:
        ch_message = ""

        lock_list = w_db.read_lock_list_of_slack_code(slack_code, project_name)
        if lock_list:
            user_name = w_db.convert_slack_code_to_slack_id(slack_code)
            for file_name in remove_lock_list:
                ch_message = random.choice(shell_dict['unlock_announce'])
                ch_message = ch_message.format(user_name, file_name)

            send_channel_message("code-conflict-chatbot", ch_message)

            message += random.choice(shell_dict['feat_unlock_file'])
            w_db.remove_lock_list(slack_code, remove_lock_list)

            inform_unlock_list = w_db.read_oldest_lock_history_list(remove_lock_list)

            for file in inform_unlock_list:
                msg = "{} just unlocked. Do you want me to lock it for {} hours? [yes/no]".format(file[1], file[3])
                send_direct_message(file[2], msg)

            ele = ','.join(remove_lock_list)
            message = message.format(ele)

        else:
            message = "You didn't lock this file, so you cannot lock this file"

    # message = m1 + " / " + m2
    w_db.close()
    return message


def code_history_logic(slack_code, file_path, start_line, end_line):
    w_db = work_database()

    project_name = w_db.get_repository_name(slack_code)
    engaging_user_email_list = get_user_email(project_name, file_path, start_line, end_line)

    message = ""
    user_name_list = []
    user_name_fail_list = []

    for user_email in engaging_user_email_list:
        user_name = w_db.convert_git_id_to_slack_id(git_id=user_email)
        if user_name == "":
            print("{} is not in db.".format(user_email))
            user_name = convert_git_id_to_slack_id_from_slack(git_id=user_email)
        if user_name == "":
            user_name_fail_list.append(user_email)
        else:
            user_name_list.append(user_name)

    if user_name_list:
        message = random.choice(shell_dict['feat_history_logic']).format(",".join(user_name_list), start_line, end_line)

    if user_name_fail_list:
        message += random.choice(shell_dict['feat_history_fail']).format(",".join(user_name_fail_list))

    w_db.close()
    return message

def ignore_file_logic(slack_code, ignore_list, approval):
    w_db = work_database()
    print("ignore : " + str(ignore_list))
    project_name = w_db.get_repository_name(slack_code)
    already_ignore_tuple = w_db.read_ignore(project_name, slack_code)
    message = ""

    # Ignore
    if approval == 1:
        if already_ignore_tuple is not None and already_ignore_tuple[ignore_list - 1] == 1: # (1,0) (1,1) / (0,1) (1,1)
            if ignore_list == 1:
                message = "You have already ignored direct message."
            elif ignore_list == 2:
                message = "You have already ignored indirect message."
        else:
            if already_ignore_tuple is None:
                w_db.add_ignore(project_name, ignore_list, slack_code)
            else: # (0,0) (0,1) / (0,0) (1,0)
                w_db.update_ignore(project_name, ignore_list, slack_code, approval)
            if ignore_list == 1:
                message = random.choice(shell_dict['feat_ignore_alarm_direct'])
            elif ignore_list == 2:
                message = random.choice(shell_dict['feat_ignore_alarm_indirect'])

    # Unignore
    elif approval == 0:
        if already_ignore_tuple is None or already_ignore_tuple[ignore_list - 1] == 0 : #(0,1) (0,0) / (1,0) (0,0)
            if ignore_list == 1:
                message = "You didn't ignore direct message. So you get notified of direct message!"
            elif ignore_list == 2:
                message = "You didn't ignore indirect message. So you get notified of indirect message!"
        else:
            if already_ignore_tuple == (1, 1): # (1,1)
                w_db.update_ignore(project_name, ignore_list, slack_code, approval)
            else: # (1,0) / (0,1)
                w_db.remove_ignore(project_name, slack_code)
            if ignore_list == 1:
                message = random.choice(shell_dict['feat_unignore_alarm_direct'])
            elif ignore_list == 2:
                message = random.choice(shell_dict['feat_unignore_alarm_indirect'])

    w_db.close()
    return message


def check_conflict_logic(slack_code, file_name):
    w_db = work_database()
    message = ""

    project_name = w_db.get_repository_name(slack_code)
    print("project_ name test : ", project_name)
    direct_conflict_flag, indirect_conflict_flag = w_db.is_conflict(project_name, slack_code, file_name)

    if((direct_conflict_flag == True) and (indirect_conflict_flag == True)):
        message = random.choice(shell_dict['feat_conflict_di'])
    elif((direct_conflict_flag == True) and (indirect_conflict_flag == False)):
        message = random.choice(shell_dict['feat_conflict_d'])
    elif((direct_conflict_flag == False) and (indirect_conflict_flag == True)):
        message = random.choice(shell_dict['feat_conflict_i'])
    else:
        message = "I think it'll not cause any conflict." 

    w_db.close()
    return message


def other_working_status_logic(slack_code, target_slack_code, git_id):
    w_db = work_database()
    message = ""
    if git_id == "":
        message = "This user is not working on the project."
    else:
        project_name = w_db.get_repository_name(target_slack_code)
        if project_name == -2:
            message = "This user is not in our database."
        elif project_name == -1:
            message = "This user is not working on the project"
        else:
            db_lock_set = set(w_db.read_lock_list_of_slack_code(target_slack_code, project_name))
            print(db_lock_set)

            slack_name = w_db.convert_slack_code_to_slack_id(target_slack_code)
            working_data = w_db.get_user_working_status(git_id)

            message = random.choice(shell_dict['feat_working_status'])
            message = message.format(slack_name, working_data)

            # add lock file information.
            if db_lock_set:
                locked_file = ', '.join(list(db_lock_set))
                message += "\n{} locked '{}' files.".format(slack_name, locked_file)

    w_db.close()
    return message


def send_message_channel_logic(channel, msg, user_name):

    if msg == '':
        message = 'You must write your message between two double quotations like "message"'
        return message

    channel_msg = user_name + " announce : " + msg
    ret_scm = send_channel_message(channel, channel_msg)

    if ret_scm == 2:
        message = random.choice(shell_dict['feat_announce'])
        message = message.format(channel)
    elif ret_scm == 1:
        message = "I'm not in {} channel. If you want to send message to that channel, please invite me.".format(channel)
    elif ret_scm == 0:
        message = "There is no {} channel in Slack workspace, please check channel list.".format(channel)
    else:
        message = ''
    return message


def send_message_direct_logic(slack_code, msg, user_name):

    if msg == '':
        message = 'You must write your message between two double quotations like "message"'
        return message

    w_db = work_database()
    target_user = w_db.convert_slack_code_to_slack_id(slack_code)

    msg = user_name + " gives message : " + msg
    send_direct_message(slack_code, msg)
    message = random.choice(shell_dict['feat_send_message_user'])
    message = message.format(target_user)
    w_db.close()
    return message

def recommend_solve_conflict_logic(user1_git_id, user2_git_id):
    w_db = work_database()

    if user2_git_id != " " :
        u1, w1, u2, w2 = w_db.recommendation(user1_git_id, user2_git_id)
        user1_slack_id = w_db.convert_git_id_to_slack_id(u1)
        user2_slack_id = w_db.convert_git_id_to_slack_id(u2)

        if u1 == user1_git_id:
            message = random.choice(shell_dict['feat_recommend_change'])
            message = message.format(user2_slack_id, user2_slack_id)
        else:
            message = random.choice(shell_dict['feat_recommend_not_change'])
            message = message.format(user1_slack_id, user1_slack_id)

        w_db.close()

    else:
        message = random.choice(shell_dict['feat_recommend_no_conflict'])
        w_db.close()
    return message


def find_locker_logic(slack_code, file_path):
    w_db = work_database()
    message = ""

    project_name = w_db.get_repository_name(slack_code)

    locker_slack_code = w_db.get_locker_slack_code(project_name, file_path)

    if locker_slack_code == "":
        message = "There is no locker of {}".format(file_path)
    else:
        locker_name = w_db.convert_slack_code_to_slack_id(locker_slack_code)
        message = "The locker of {} is {}".format(file_path, locker_name)

    w_db.close()
    return message

def find_severity_logic(slack_code, file_path):
    w_db = work_database()
    message = ""

    project_name = w_db.get_repository_name(slack_code)
    severity_set = w_db.get_severity_set(project_name, file_path)

    if severity_set:
        message += "Direct Conflict\n"
        for ss in severity_set:
            logic1_name = ss[0][0]
            user1_name = w_db.convert_git_id_to_slack_id(ss[0][1])
            logic2_name = ss[1][0]
            user2_name = w_db.convert_git_id_to_slack_id(ss[1][1])
            severity = ss[2]
            message += "{} in '{}' & {} in '{}' : severity {}.\n".format(user1_name, logic1_name, user2_name, logic2_name, severity)

    else:
        message += "There is no direct conflict in {}. ".format(file_path)

    w_db.close()
    return message


def response_logic(slack_code, msg_type):
    w_db = work_database()

    request_lock_set = set()

    message = ""
    project_name = w_db.get_repository_name(slack_code)
    remove_file_list = list(set(w_db.read_lock_history_list(project_name)) - set(w_db.read_lock_list(project_name)))

    target_list = w_db.read_oldest_lock_history_list(remove_file_list)
    for target_file in target_list:
        if(target_file[2] == slack_code):
            if(msg_type == "yes"):
                request_lock_set.add(target_file[1])
                lock_file_list, already_lock_set = list(w_db.add_lock_list(slack_code, request_lock_set, target_file[3]))
                ch_message = ""
                user_name = w_db.convert_slack_code_to_slack_id(slack_code)

                for file_name in lock_file_list:
                    ch_message += "{} locked {} file for {} hour(s).".format(user_name, file_name, target_file[3])
                send_channel_message("code-conflict-chatbot", ch_message)

                message += random.choice(shell_dict['feat_lock_file'])
                ele = ','.join(list(lock_file_list))
                message = message.format(ele)

                w_db.delete_lock_history(target_file[1], slack_code)
            else:
                w_db.delete_lock_history(target_file[1], slack_code)
                message = "Okay, I'll not lock it"
        else:
            message = "I think you enter the wrong one."

    w_db.close()
    return message

def greeting_logic(slack_code):
    w_db = work_database()
    message = ""

    last_connection = w_db.user_recognize(slack_code)

    if(last_connection == 1):
        message = random.choice(shell_dict['feat_greetings'])

    # Finn can not
    elif(last_connection == 2):
        message = random.choice(shell_dict['feat_greetings2'])
    elif(last_connection == 3):
        message = random.choice(shell_dict['feat_greetings3'])
    else:
        message = random.choice(shell_dict['feat_greetings'])

    w_db.close()
    return message

def bye_logic():
    message = random.choice(shell_dict['feat_goodbye'])
    return message


shell_dict = dict()


for path, dirs, files in os.walk('../situation_shell') :
    for file in files :
        file_name, ext = os.path.splitext(file)
        if ext == '.txt' :
            shell_dict[file_name] = list()
            with open(os.path.join(path, file) , 'r', encoding="UTF-8") as f :
                for line in f.readlines() :
                    shell_dict[file_name].append(line.strip())

