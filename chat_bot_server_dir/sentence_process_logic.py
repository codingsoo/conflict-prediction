from chat_bot_server_dir.work_database import work_database
from chat_bot_server_dir.intent_func import get_user_email
from server_dir.slack_message_sender import send_channel_message
from server_dir.slack_message_sender import send_lock_button_message
from server_dir.slack_message_sender import send_all_user_message
from server_dir.slack_message_sender import send_direct_message
from chat_bot_server_dir.user_intent_classifier.intent_classifier import convert_git_id_to_slack_id_from_slack
from chat_bot_server_dir.constants import *
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
        message = check_ignored_file_logic(slack_code)

    elif(intent_type == 11):
        message = check_locker_logic(slack_code, param0)

    elif(intent_type == 12):
        message = check_severity_logic(slack_code, param0)

    elif(intent_type == ERROR - 2):
        message = greeting_logic(slack_code)

    elif (intent_type == ERROR - 1):
        message = bye_logic()

    elif(intent_type == ERROR):
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
            # 10. check_ignored_file : A user can ask chatbot which files are ignored.
            # 11. check_locker : A user can ask chatbot about who locked the file.
            # 12. check_severity : A user can ask chatbot about how severe conflict is.
            # 13. user_recognize : Chatbot knows when last time a user connected is, so bot can greet the user with time information. ex) It's been a while~
            # 14. greeting : Chatbot can greet users.
            # 15. complimentary_close : Chatbot can say good bye.
            # 16. detect_direct_conflict : Chatbot can detect direct conflict and severity.
            # 17. detect_indirect_conflict : Chatbot can detect indirect conflict and severity.
            """
        elif param0 == "same_named_file":
            message = ""
        elif param0 == "no_file":
            message = "There is no such file. Please say it again."
        elif param0 == "many_files":
            message = "Please write just one file"
        elif param0 == "no_channel":
            message = "There is no such channel. Please say it again."

    return message

def approved_file_logic(slack_code, approved_set, removed_list):
    w_db = work_database()
    project_name, user_name = w_db.get_repository_and_user_name(slack_code)

    approved_list = list(approved_set)

    print("approve !! : " + str(approved_list))
    print("remove !! : " + str(removed_list))

    message = ""
    if approved_list:
        diff_approved_list, db_approved_set = w_db.add_approved_list(slack_code=slack_code, req_approved_set=approved_set)
        already_approved_list = list(db_approved_set & approved_set)
        if diff_approved_list:

            # ch_message += random.choice(shell_dict['feat_ignore_channel'])
            # ch_message = ch_message.format(user_name, ", ".join(diff_approved_list))
            # send_channel_message("code-conflict-chatbot", ch_message)

            message += random.choice(shell_dict['feat_ignore_file'])
            message = message.format(filename=", ".join(diff_approved_list))

        if already_approved_list:
            message += "You already ignored *{}* file!".format(", ".join(already_approved_list))

    if removed_list:
        success_list, fail_list = w_db.remove_approved_list(slack_code=slack_code, remove_approved_list=removed_list)
        if success_list:

            # ch_message += random.choice(shell_dict['feat_unignore_channel'])
            # ch_message = ch_message.format(user_name, ", ".join(success_list))
            # send_channel_message("code-conflict-chatbot", ch_message)

            message += random.choice(shell_dict['feat_unignore_file'])
            message = message.format(filename=", ".join(success_list))

        if fail_list:
            message += "You already get notified of *{}*\n".format(", ".join(fail_list))

    w_db.close()

    return message


def lock_file_logic(slack_code, request_lock_set, remove_lock_set, lock_time):
    w_db = work_database()

    project_name, user_name = w_db.get_repository_and_user_name(slack_code)
    message = ""

    if request_lock_set:
        ch_message = ""
        lock_file_list, already_lock_list = list(w_db.add_lock_list(project_name, slack_code, request_lock_set, lock_time))

        if already_lock_list:
            for file_name in already_lock_list:
                other_slack_code, remain_time_str = w_db.check_user_and_remain_time_of_lock_file(project_name, file_name)
                if slack_code == other_slack_code:
                    message = "You've already locked *{}* file.".format(file_name)
                else:
                    other_user_name = w_db.convert_slack_code_to_slack_id(other_slack_code)
                    message += random.choice(shell_dict['feat_lock_overlap'])
                    message = message.format(user2=other_user_name, filename=file_name)

        if lock_file_list:
            for file_name in lock_file_list:
                ch_message += "{} locked *{}* file for {} hour(s).".format(user_name, file_name, lock_time)
            send_all_user_message(ch_message, slack_code)
            # send_channel_message("code-conflict-chatbot", ch_message)

            message += random.choice(shell_dict['feat_lock_file'])
            ele = ', '.join(lock_file_list)
            message = message.format(filename=ele)

    if remove_lock_set:
        ch_message = ""
        already_lock_list = w_db.read_lock_list_of_slack_code(project_name, slack_code)
        remove_lock_set = set(already_lock_list).intersection(set(remove_lock_set))
        remove_lock_list = list(remove_lock_set)

        if remove_lock_set:
            for file_name in remove_lock_set:
                ch_message = random.choice(shell_dict['unlock_announce'])
                ch_message = ch_message.format(user2=user_name, filename=file_name)
            send_all_user_message(ch_message, slack_code)
            # send_channel_message("code-conflict-chatbot", ch_message)

            message += random.choice(shell_dict['feat_unlock_file'])
            ele = ','.join(remove_lock_list)
            message = message.format(filename=ele)

            w_db.remove_lock_list(project_name, slack_code, remove_lock_set)

            inform_unlock_list = w_db.read_oldest_lock_history_list(remove_lock_list)

            for file in inform_unlock_list:
                print("inform_unlock_list", file)
                send_lock_button_message(slack_code=file[2], lock_file=file[1], lock_time=file[3])

        else:
            message = "You didn't lock this file, so you cannot lock this file. "

    w_db.close()
    return message


def code_history_logic(slack_code, file_abs_path, start_line, end_line):
    w_db = work_database()

    message = ""
    project_name = w_db.get_repository_name(slack_code)
    file_end_line, engaging_user_email_list = get_user_email(project_name, file_abs_path, start_line, end_line)

    if file_end_line != end_line:
        message += "This file's total amount of lines is *{}*.\n".format(file_end_line)
        w_db.close()
        return message

    user_email_list = list(engaging_user_email_list)
    user_name_fail_list = []

    for user_email in user_email_list:
        user_name = w_db.convert_git_id_to_slack_id(git_id=user_email)
        if user_name == "":
            print("{} is not in db.".format(user_email))
            user_name = convert_git_id_to_slack_id_from_slack(git_id=user_email)
        if user_name == "":
            user_name_fail_list.append(user_email)
        else:
            if len(user_email_list) == 1:
                message += random.choice(shell_dict['feat_history_logic']).format(user2=user_name,
                                                                                  file_name=file_abs_path,
                                                                                  start_line=start_line,
                                                                                  end_line=end_line)
            else:
                message += "{} edited ".format(user_name)
                for ele in engaging_user_email_list[user_email]:
                    message += "{}".format(ele)
                message += ". \n"


    # if user_name_fail_list:
    #     message += random.choice(shell_dict['feat_history_fail']).format(",".join(user_name_fail_list))

    for user_email in user_name_fail_list:
        line_info = ""
        for ele in engaging_user_email_list[user_email]:
            line_info = line_info + "{}".format(ele)
        message += random.choice(shell_dict['feat_history_fail']).format(user_email, user_email, ele)
        message += "\n"

    w_db.close()
    return message

def ignore_file_logic(slack_code, ignore_list, approval):
    w_db = work_database()
    print("ignore : " + str(ignore_list))
    project_name = w_db.get_repository_name(slack_code)
    already_ignore_tuple = w_db.read_ignore(project_name, slack_code)
    message = ""

    # Ignore
    if approval == IGNORE:
        if already_ignore_tuple and already_ignore_tuple[ignore_list - 1] == IGNORE: # (1,0) (1,1) / (0,1) (1,1)
            if ignore_list == DIRECT:
                message = "You have already ignored direct message."
            elif ignore_list == INDIRECT:
                message = "You have already ignored indirect message."
        else:
            if not already_ignore_tuple:
                w_db.add_ignore(project_name, ignore_list, slack_code)
            else: # (0,0) (0,1) / (0,0) (1,0)
                w_db.update_ignore(project_name, ignore_list, slack_code, approval)
            if ignore_list == DIRECT:
                message = random.choice(shell_dict['feat_ignore_alarm_direct'])
            elif ignore_list == INDIRECT:
                message = random.choice(shell_dict['feat_ignore_alarm_indirect'])

    # Unignore
    elif approval == UNIGNORE:
        if not already_ignore_tuple or already_ignore_tuple[ignore_list - 1] == UNIGNORE : #(0,1) (0,0) / (1,0) (0,0)
            if ignore_list == DIRECT:
                message = "You didn't ignore direct message. So you get notified of direct message!"
            elif ignore_list == INDIRECT:
                message = "You didn't ignore indirect message. So you get notified of indirect message!"
        else:
            if already_ignore_tuple == (IGNORE, IGNORE): # (1,1)
                w_db.update_ignore(project_name, ignore_list, slack_code, approval)
            else: # (1,0) / (0,1)
                w_db.remove_ignore(project_name, slack_code)
            if ignore_list == DIRECT:
                message = random.choice(shell_dict['feat_unignore_alarm_direct'])
            elif ignore_list == INDIRECT:
                message = random.choice(shell_dict['feat_unignore_alarm_indirect'])

    w_db.close()
    return message


def check_conflict_logic(slack_code, file_name):
    w_db = work_database()
    message = ""

    project_name = w_db.get_repository_name(slack_code)
    print("project_ name test : ", project_name)
    direct_conflict_flag, indirect_conflict_flag = w_db.is_conflict(project_name, slack_code, file_name)

    if direct_conflict_flag == True and indirect_conflict_flag == True:
        message = random.choice(shell_dict['feat_conflict_di']).format(user2="d_user", user3="in_user", filename2="d_file", filename3="in_file")
    elif direct_conflict_flag == True and indirect_conflict_flag == False:
        message = random.choice(shell_dict['feat_conflict_d']).format(user2="d_user", filename=file_name)
    elif direct_conflict_flag == False and indirect_conflict_flag == True:
        message = random.choice(shell_dict['feat_conflict_i']).format(user2="in_user", filename1=file_name, filename2="in_file")
    else:
        message = "I think it'll not cause any conflict." 

    w_db.close()
    return message


def other_working_status_logic(slack_code, target_slack_code, target_git_id):
    w_db = work_database()
    message = ""

    project_name = w_db.read_project_name(target_slack_code)
    if project_name == "":
        message = "This user is not working on our project."
    else:
        target_slack_id = w_db.convert_slack_code_to_slack_id(target_slack_code)
        working_status = w_db.get_user_working_status(target_git_id)

        message = random.choice(shell_dict['feat_working_status'])
        message = message.format(user2=target_slack_id, working_status=working_status)

        # add lock file information.
        db_lock_set = set(w_db.read_lock_list_of_slack_code(project_name, target_slack_code))
        print(db_lock_set)
        if db_lock_set:
            locked_file = ', '.join(list(db_lock_set))
            message += "\nAnd {} locked *{}* files.".format(target_slack_id, locked_file)

    w_db.close()
    return message

def send_message_channel_logic(target_channel, msg, user_slack_id):
    if msg == '':
        message = 'You must write your message between two double quotations like "message"'
        return message

    channel_msg = user_slack_id + " announce : " + msg
    ret_scm = send_channel_message(target_channel, channel_msg)

    if ret_scm == CHANNEL_WITH_SAYME:
        message = random.choice(shell_dict['feat_announce'])
        message = message.format(target_channel)
    elif ret_scm == CHANNEL_WITHOUT_SAYME:
        message = "I'm not in {} channel. If you want to send message to that channel, please invite me.".format(target_channel)
    elif ret_scm == CHANNEL_NONEXISTENCE:
        message = "There is no {} channel in Slack workspace, please check channel list.".format(target_channel)
    else:
        message = ''
    return message


def send_message_direct_logic(target_slack_code, msg, user_slack_id):
    if msg == '':
        message = 'You must write your message between two double quotations like "message"'
        return message

    w_db = work_database()
    target_slack_id = w_db.convert_slack_code_to_slack_id(target_slack_code)

    msg = user_slack_id + " gives message : " + msg
    send_direct_message(target_slack_code, msg)

    message = random.choice(shell_dict['feat_send_message_user'])
    message = message.format(user2=target_slack_id)
    w_db.close()
    return message

def recommend_solve_conflict_logic(user_git_id, file_name):
    w_db = work_database()
    message = ""
    project_name = w_db.get_repository_name_by_git_id(user_git_id)
    user_percentage, other_percentage, other_git_id = w_db.get_working_amount_percentage(project_name, user_git_id, file_name)

    if other_git_id == "NO_ONE":
        message = random.choice(shell_dict['feat_recommend_no_conflict'])

    else:
        other_name = w_db.convert_git_id_to_slack_id(other_git_id)
        percentage_gap = abs(user_percentage - other_percentage)

        if user_percentage >= other_percentage:
            message = random.choice(shell_dict['feat_recommend_change'])
        else:
            message = random.choice(shell_dict['feat_recommend_not_change'])

        message = message.format(user2=other_name,
                                 severity_gap=percentage_gap,
                                 user1_severity=user_percentage,
                                 user2_severity=other_percentage)

    # working_amt_dict = w_db.get_working_amount_dict(user_git_id, file_name)
    #
    # working_amt_list = sorted(working_amt_dict, key=lambda w: working_amt_dict[w], reverse=True)
    # print("working_amt_list", working_amt_list)
    #
    # try:
    #     user_idx = working_amt_list.index(user_git_id)
    #     if user_git_id == working_amt_list[0]:
    #         message = random.choice(shell_dict['feat_recommend_change'])
    #         ele = ", ".join(working_amt_list[1:])
    #         message = message.format(user2=ele)
    #     else:
    #         message = random.choice(shell_dict['feat_recommend_not_change'])
    #         ele = ", ".join(working_amt_list[:user_idx])
    #         message = message.format(user2=ele)
    #
    # except:
    #     message = random.choice(shell_dict['feat_recommend_no_conflict'])

    w_db.close()
    return message

def check_ignored_file_logic(slack_code):
    w_db = work_database()
    message = "\n"

    ignored_file_list = w_db.get_ignored_file_list(slack_code)
    print("ignored_file_list", ignored_file_list)

    if not ignored_file_list:
        message = random.choice(shell_dict['feat_ignored_file_nonexistence'])
    else:
        message += random.choice(shell_dict['feat_ignored_file_existence'])
        message = message.format(filename=",\n".join(ignored_file_list))

    w_db.close()
    return message


def check_locker_logic(slack_code, file_abs_path):
    w_db = work_database()
    message = ""

    project_name = w_db.get_repository_name(slack_code)

    locker_slack_code = w_db.get_locker_slack_code(project_name, file_abs_path)

    if locker_slack_code == "":
        message = random.choice(shell_dict['feat_locker_nonexistence'])
        message = message.format(filename=file_abs_path)
    else:
        locker_name = w_db.convert_slack_code_to_slack_id(locker_slack_code)
        message = random.choice(shell_dict['feat_locker_existence'])
        message = message.format(user2=locker_name, filename=file_abs_path)

    w_db.close()
    return message

def check_severity_logic(slack_code, file_abs_path):
    w_db = work_database()
    message = ""

    project_name = w_db.get_repository_name(slack_code)
    severity_set = w_db.get_severity_set(project_name, file_abs_path)

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
        message += "There is no direct conflict in {}. ".format(file_abs_path)

    w_db.close()
    return message


# def response_logic(slack_code, msg_type):
#     w_db = work_database()
#
#     request_lock_set = set()
#
#     message = ""
#     project_name = w_db.get_repository_name(slack_code)
#     remove_file_list = list(set(w_db.read_lock_history_list(project_name)) - set(w_db.read_lock_list(project_name)))
#     print("read_lock_history_list", set(w_db.read_lock_history_list(project_name)))
#     print("read_lock_list", set(w_db.read_lock_list(project_name)))
#
#     target_list = w_db.read_oldest_lock_history_list(remove_file_list)
#     print("target_list", target_list)
#     for target_file in target_list:
#         if(target_file[2] == slack_code):
#             if(msg_type == "yes"):
#                 request_lock_set.add(target_file[1])
#                 lock_file_list, already_lock_set = list(w_db.add_lock_list(slack_code, project_name, request_lock_set, target_file[3]))
#                 print("lock_file_list", lock_file_list)
#                 print("already_lock_set", already_lock_set)
#                 ch_message = ""
#                 user_name = w_db.convert_slack_code_to_slack_id(slack_code)
#
#                 for file_name in lock_file_list:
#                     ch_message += "{} locked {} file for {} hour(s).".format(user_name, file_name, target_file[3])
#                 send_channel_message("code-conflict-chatbot", ch_message)
#
#                 message += random.choice(shell_dict['feat_lock_file'])
#                 ele = ','.join(list(lock_file_list))
#                 message = message.format(ele)
#
#                 w_db.delete_lock_history(target_file[1], slack_code)
#             else:
#                 w_db.delete_lock_history(target_file[1], slack_code)
#                 message = "Okay, I'll not lock it"
#         else:
#             message = "I think you enter the wrong one."
#
#     w_db.close()
#     return message


def lock_response_logic(slack_code, msg_type, target_file, lock_time):
    w_db = work_database()
    project_name, user_name = w_db.get_repository_and_user_name(slack_code)

    if msg_type == "YES" and target_file in w_db.read_lock_history_list(project_name, slack_code):
        lock_file_list, already_lock_set = list(w_db.add_lock_list(project_name, slack_code, set([target_file]), lock_time))
        ch_message = ""
        if target_file in lock_file_list:
            ch_message += "{} locked {} file for {} hour(s).".format(user_name, target_file, lock_time)
        # send_channel_message("code-conflict-chatbot", ch_message)
        send_all_user_message(ch_message, slack_code)
        print("YES")
        w_db.delete_lock_history(project_name, slack_code, target_file)
    else:
        print("NO")
        w_db.delete_lock_history(project_name, slack_code, target_file)

    w_db.close()


def greeting_logic(slack_code):
    w_db = work_database()
    message = ""

    last_connection = w_db.user_recognize(slack_code)
    user_name = w_db.convert_slack_code_to_slack_id(slack_code)

    if(last_connection == 1):
        message = random.choice(shell_dict['feat_greetings'])
    # Finn can not
    elif(last_connection == 2):
        message = random.choice(shell_dict['feat_greetings2'])
    else:
        message = random.choice(shell_dict['feat_greetings'])
    message = message.format(user=user_name)

    w_db.close()
    return message

def bye_logic():
    message = random.choice(shell_dict['feat_goodbye'])
    return message

def remove_project_name(file_full_path_list, project_name):
    file_list = []
    for ffpl in file_full_path_list:
        file_list.append(ffpl.replace(project_name, "", 1))
    return file_list


shell_dict = dict()
for path, dirs, files in os.walk('../situation_shell') :
    for file in files :
        file_name, ext = os.path.splitext(file)
        if ext == '.txt' :
            shell_dict[file_name] = list()
            with open(os.path.join(path, file) , 'r', encoding="UTF-8") as f :
                for line in f.readlines() :
                    shell_dict[file_name].append(line.strip())

