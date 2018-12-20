from chat_bot_server_dir.work_database import work_database
from chat_bot_server_dir.intent_func import get_code_history_info
from server_dir.slack_message_sender import send_lock_request_button_message
from server_dir.slack_message_sender import send_all_user_message
from server_dir.slack_message_sender import send_direct_message
from server_dir.slack_message_sender import send_feature_button_message
from chat_bot_server_dir.user_intent_classifier.intent_classifier import convert_git_id_to_slack_id_from_slack
from chat_bot_server_dir.constants import *
import os
import random


def sentence_processing_main(intent_type, slack_code, param0, param1, param2):
    message = "default"

    if intent_type == 1:
        message = approved_file_logic(slack_code, param0, param1)

    elif intent_type == 2:
        message = lock_file_logic(slack_code, param0, param1, param2)

    elif intent_type == 3:
        message = code_history_logic(slack_code, param0, param1, param2)

    elif intent_type == 4:
        message = ignore_alarm_logic(slack_code, param0, param1)

    elif intent_type == 5:
        message = check_conflict_logic(slack_code, param0, param1)

    elif intent_type == 6:
        message = other_working_status_logic(slack_code, param0, param1)

    elif intent_type == 7:
        message = send_message_direct_logic(slack_code, param0, param1)

    elif intent_type == 8:
        message = recommend_solve_conflict_logic(slack_code, param0, param1)

    elif intent_type == 9:
        message = check_ignored_file_logic(slack_code, param0)

    elif intent_type == 10:
        message = check_locker_logic(slack_code, param0)

    elif intent_type == 11:
        message = check_severity_logic(slack_code, param0)

    elif intent_type == 13:
        message = file_status_logic(slack_code, param0)

    elif intent_type == ERROR - 2:
        message = greeting_logic(slack_code)

    elif intent_type == ERROR - 1:
        message = bye_logic(slack_code)

    elif intent_type == ERROR:
        if param0 == "no_response":
            message = no_response(slack_code)
        elif param0 == "same_named_file":
            message = ""
        elif param0 == "typo_error_file":
            message = ""
        elif param0 == "no_file":
            message = random.choice(shell_dict['sentence_process_no_file'])
        elif param0 == "many_files":
            message = random.choice(shell_dict['sentence_process_many_files'])

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
            message += random.choice(shell_dict['feat_ignore_file'])
            message = message.format(filename=", ".join(diff_approved_list))

        if already_approved_list:
            message += random.choice(shell_dict['feat_already_ignored'])
            message = message.format(filename=", ".join(already_approved_list))

    if removed_list:
        success_list, fail_list = w_db.remove_approved_list(slack_code=slack_code, remove_approved_list=removed_list)
        if success_list:
            message += random.choice(shell_dict['feat_unignore_file'])
            message = message.format(filename=", ".join(success_list))

        if fail_list:
            message += random.choice(shell_dict['feat_already_notify'])
            message = message.format(filename=", ".join(fail_list))

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
                    message += random.choice(shell_dict['feat_already_locked'])
                    message = message.format(filename=file_name)
                else:
                    message += random.choice(shell_dict['feat_lock_overlap'])
                    message = message.format(user2=other_slack_code, filename=file_name, remaining_time=remain_time_str)

        if lock_file_list:
            for file_name in lock_file_list:
                ch_message += random.choice(shell_dict['feat_send_all_user_lock'])
                ch_message = ch_message.format(user=slack_code, file_name=file_name,lock_time=lock_time)

            send_all_user_message(ch_message, slack_code)

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
                ch_message = random.choice(shell_dict['feat_send_all_user_unlock'])
                ch_message = ch_message.format(user2=slack_code, filename=file_name)
            send_all_user_message(ch_message, slack_code)

            message += random.choice(shell_dict['feat_unlock_file'])
            ele = ','.join(remove_lock_list)
            message = message.format(filename=ele)

            w_db.remove_lock_list(project_name, slack_code, remove_lock_set)

            inform_unlock_list = w_db.read_oldest_lock_history_list(slack_code, remove_lock_list)

            for file in inform_unlock_list:
                print("inform_unlock_list : ", file)
                if(file[2] != slack_code):
                    send_lock_request_button_message(slack_code=file[2], lock_file=file[1], lock_time=file[3])

        else:
            message += random.choice(shell_dict['feat_unlock_fail'])

    w_db.close()
    return message


def code_history_logic(slack_code, file_abs_path, start_line, end_line):
    w_db = work_database()
    message = ""

    project_name = w_db.get_repository_name(slack_code)
    file_end_line, code_history_info_dict = get_code_history_info(project_name, file_abs_path, start_line, end_line)
    user_email_list = list(code_history_info_dict)
    user_name_fail_list = []
    user_name_list = []

    if end_line != file_end_line and end_line > 0:
        message += random.choice(shell_dict['feat_history_line_info']).format(end_line=file_end_line) + "\n"

    # Find user_name
    for user_email in user_email_list:
        user_name = "<@" + w_db.convert_git_id_to_slack_code(git_id=user_email) + ">"
        if user_name == "<@>":
            print("{} is not in db.".format(user_email))
            user_name = convert_git_id_to_slack_id_from_slack(git_id=user_email)
        if user_name == "":
            user_name_fail_list.append(user_email)
        else:
            user_name_list.append(user_name)

    # case 1: Single User
    if len(user_name_list) == 1:
        message += random.choice(shell_dict['feat_history_single_user']).format(user2=user_name_list[0],
                                                                                filename=file_abs_path,
                                                                                start_line=start_line,
                                                                                end_line=end_line)
    # case 2: Multiple Users
    else:
        message_idx = random.randrange(len(shell_dict['feat_history_multiple_users']))
        message += format_code_history_multiple_users(message_idx, user_name_list, code_history_info_dict)

    # case 3: User Name is not in DB
    for user_email in user_name_fail_list:
        line_info = "line " + ", ".join(code_history_info_dict[user_email])
        message += random.choice(shell_dict['feat_history_fail']) + "\n" + user_email + " : " + line_info

    w_db.close()
    return message


def format_code_history_multiple_users(message_idx, user_name_list, code_history_info_dict):
    # Multiple developers touched these lines of code last: {user1} line {line1}, and {user2} line {line2}.
    # Line {line1} were edited by {user1}, and {line2} by {user2}.
    # GitHub reports that {user1} last edited line {line1}, and {user2} line {line2}.
    # {user1} is the last person to edit line {line1}, and {user2} line {line2}.
    # {user1}: line {line1}, {user2}: line {line2}

    code_history_info_list = list(code_history_info_dict.values())
    message = shell_dict['feat_history_multiple_users'][message_idx].format(user1=user_name_list[0], line1=", ".join(code_history_info_list[0]))

    if message_idx in [0, 2, 3]:
        for user_idx, user_name in enumerate(user_name_list[1:]):
            line_info = ", ".join(code_history_info_list[user_idx + 1])
            history_info = user_name + " line " + line_info

            if user_idx == len(user_name_list[1:]) - 1:
                message += ", and " + history_info + "."
            else:
                message += ", " + history_info

    elif message_idx == 1:
        for user_idx, user_name in enumerate(user_name_list[1:]):
            line_info = ", ".join(code_history_info_list[user_idx + 1])
            history_info = line_info + " by " + user_name

            if user_idx == len(user_name_list[1:]) - 1:
                message += ", and " + history_info + "."
            else:
                message += ", " + history_info

    elif message_idx == 4:
        for user_idx, user_name in enumerate(user_name_list[1:]):
            line_info = ", ".join(code_history_info_list[user_idx + 1])
            history_info = user_name + " : " + line_info

            if user_idx == len(user_name_list[1:]) - 1:
                message += ", " + history_info + "."
            else:
                message += ", " + history_info

    return message


def ignore_alarm_logic(slack_code, ignore_list, approval):
    w_db = work_database()
    print("ignore : " + str(ignore_list))
    project_name = w_db.get_repository_name(slack_code)
    already_ignore_list = w_db.read_ignore_list(project_name, slack_code)
    if not already_ignore_list:
        w_db.insert_ignore(project_name, slack_code)
    message = ""

    # Ignore
    if approval == IGNORE:
        # already set
        if already_ignore_list and already_ignore_list[ignore_list - 1] == IGNORE:
            if ignore_list == DIRECT:
                message = random.choice(shell_dict['feat_already_ignore_direct'])
            elif ignore_list == INDIRECT:
                message = random.choice(shell_dict['feat_already_ignore_indirect'])
            elif ignore_list == PREDICTION:
                message = random.choice(shell_dict['feat_already_ignore_prediction'])
        # not set yet
        else:
            w_db.update_ignore(project_name, ignore_list, slack_code, approval)
            if ignore_list == DIRECT:
                message = random.choice(shell_dict['feat_ignore_alarm_direct'])
            elif ignore_list == INDIRECT:
                message = random.choice(shell_dict['feat_ignore_alarm_indirect'])
            elif ignore_list == PREDICTION:
                message = random.choice(shell_dict['feat_ignore_alarm_prediction'])

    # Unignore
    elif approval == UNIGNORE:
        if not already_ignore_list or already_ignore_list[ignore_list - 1] == UNIGNORE:
            if ignore_list == DIRECT:
                message = random.choice(shell_dict['feat_can_get_direct_alarm'])
            elif ignore_list == INDIRECT:
                message = random.choice(shell_dict['feat_can_get_indirect_alarm'])
            elif ignore_list == PREDICTION:
                message = random.choice(shell_dict['feat_can_get_prediction_alarm'])
        else:
            w_db.update_ignore(project_name, ignore_list, slack_code, approval)
            if ignore_list == DIRECT:
                message = random.choice(shell_dict['feat_unignore_alarm_direct'])
            elif ignore_list == INDIRECT:
                message = random.choice(shell_dict['feat_unignore_alarm_indirect'])
            elif ignore_list == PREDICTION:
                message = random.choice(shell_dict['feat_unignore_alarm_prediction'])

    w_db.close()
    return message


def check_conflict_logic(slack_code, user_git_id, file_name):
    w_db = work_database()
    message = ""
    additional_message = ""

    project_name = w_db.get_repository_name(slack_code)

    dir_conflict_git_id_list = w_db.get_direct_conflict_user_list(project_name, user_git_id, file_name)
    indir_conflict_git_id_list, indir_conflict_file_list = w_db.get_indirect_conflict_user_list(project_name, user_git_id, file_name)

    dir_conflict_slack_code_list = w_db.convert_git_id_list_to_slack_code_list(dir_conflict_git_id_list)
    indir_conflict_slack_code_list = w_db.convert_git_id_list_to_slack_code_list(indir_conflict_git_id_list)

    if len(indir_conflict_slack_code_list) > 1:
        indir_conflict_info = ""
        for user_idx, user_name in enumerate(indir_conflict_slack_code_list[1:-1]):
            indir_conflict_info += "*" + ", ".join(indir_conflict_file_list[user_idx + 1]) + "*" + " by <@" + user_name + ">, "
        indir_conflict_info += "*" + ", ".join(indir_conflict_file_list[-1]) + "* by " + indir_conflict_slack_code_list[-1]
        additional_message = " Also, {} may cause indirect conflicts.".format(indir_conflict_info)

    print("direct_user_list : ", dir_conflict_slack_code_list)
    print("indirect_user_list : ", indir_conflict_slack_code_list)
    print("indirect_file_list : ", indir_conflict_file_list)

    if dir_conflict_slack_code_list and indir_conflict_slack_code_list:
        message = random.choice(shell_dict['feat_conflict_di']).format(user2=", ".join(dir_conflict_slack_code_list),
                                                                       user3=indir_conflict_slack_code_list[0],
                                                                       filename2=file_name,
                                                                       filename3=", ".join(indir_conflict_file_list[0]))
        message += additional_message

    elif not dir_conflict_slack_code_list and indir_conflict_slack_code_list:
        message = random.choice(shell_dict['feat_conflict_indirect']).format(user2=indir_conflict_slack_code_list[0],
                                                                      filename1=file_name,
                                                                      filename2=", ".join(indir_conflict_file_list[0]))
        message += additional_message

    elif dir_conflict_slack_code_list and not indir_conflict_slack_code_list:
        message = random.choice(shell_dict['feat_conflict_direcc']).format(user2=", ".join(dir_conflict_slack_code_list),
                                                                      filename=file_name)

    else:
        message = random.choice(shell_dict['feat_conflict_nothing'])

    w_db.close()
    return message


def other_working_status_logic(slack_code, target_slack_code, target_git_id):
    w_db = work_database()
    message = ""

    project_name = w_db.get_repository_name(target_slack_code)
    if project_name == "":
        message = random.choice(shell_dict['feat_working_status_no_user'])
    else:
        working_status = w_db.get_user_working_status(target_git_id)
        percentage = w_db.get_severity_percentage(project_name, working_status[0])
        if not working_status:
            message = random.choice(shell_dict['feat_no_working_status']).format(user = slack_code)
        else:
            message = random.choice(shell_dict['feat_working_status'])
            message = message.format(user2=target_slack_code, working_status=working_status, severity = percentage + "%")

        # add lock file information.
        db_lock_set = set(w_db.read_lock_list_of_slack_code(project_name, target_slack_code))
        print("working_status : ", db_lock_set)
        if db_lock_set:
            locked_file = ', '.join(list(db_lock_set))
            remain_time_list = w_db.check_user_and_remain_time_of_lock_file(project_name, file_name)
            remain_time = ', '.join(remain_time_list)
            message += random.choice(shell_dict['feat_working_status_lock_info']).format(user=target_slack_code,
                                                                                         file_name=locked_file,
                                                                                         remaining_time = remain_time)

    w_db.close()
    return message


def send_message_channel_logic(target_channel, msg, user_slack_id):
    if msg == '':
        message = random.choice(shell_dict['feat_send_message_error'])
        return message

    channel_msg = user_slack_id + " announce : " + msg
    send_all_user_message(message=channel_msg)

    message = random.choice(shell_dict['feat_announce'])
    message = message.format(target_channel)

    return message


def send_message_direct_logic(user_slack_code, target_slack_code, msg):
    if msg == '':
        message = random.choice(shell_dict['feat_send_message_error'])
        return message

    w_db = work_database()

    msg = random.choice(shell_dict['feat_send_message_target_user']).format(user1=user_slack_code, message=msg)
    send_direct_message(target_slack_code, msg)

    if not target_slack_code:
        message = random.choice(shell_dict['feat_send_message_user'][0:3])
    else:
        message = random.choice(shell_dict['feat_send_message_user'][3:5])
        message = message.format(user2=target_slack_code)
    w_db.close()
    return message


def recommend_solve_conflict_logic(slack_code, user_git_id, file_name):
    w_db = work_database()
    message = ""
    project_name = w_db.get_repository_name(slack_code)
    user_percentage, other_percentage, other_git_id = w_db.get_working_amount_percentage(project_name, user_git_id, file_name)

    if other_git_id == "NO_ONE":
        message = random.choice(shell_dict['feat_recommend_no_conflict']).format(file_name=file_name)

    else:
        other_name = w_db.convert_git_id_to_slack_code(other_git_id)

        percentage_gap = abs(user_percentage - other_percentage)

        if user_percentage > other_percentage:
            message = random.choice(shell_dict['feat_recommend_change'])
        elif user_percentage < other_percentage:
            message = random.choice(shell_dict['feat_recommend_no_change'])
        else:
            message = random.choice(shell_dict['feat_recommend_same_severity'])

        message = message.format(user2= other_name,
                                 severity_gap=percentage_gap,
                                 user1_severity=user_percentage,
                                 user2_severity=other_percentage)

    w_db.close()
    return message


def check_ignored_file_logic(slack_code, other_user_code):
    w_db = work_database()
    message = "\n"

    if other_user_code == None:
        ignored_file_list = w_db.get_ignored_file_list(slack_code)
    else:
        ignored_file_list = w_db.get_ignored_file_list(other_user_code)

    print("ignored_file_list : ", ignored_file_list)
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
        message = random.choice(shell_dict['feat_locked_nonexistence'])
        message = message.format(filename=file_abs_path)

    else:
        message = random.choice(shell_dict['feat_locked_existence'])
        message = message.format(user2=locker_slack_code, filename=file_abs_path)

    w_db.close()
    return message


def check_severity_logic(slack_code, file_abs_path):
    w_db = work_database()
    message = ""

    project_name = w_db.get_repository_name(slack_code)
    severity_list = w_db.get_severity_percentage(project_name, file_abs_path) # (user_slack_code, severity)

    if severity_list:
        for sl_idx, sl in enumerate(severity_list):
            user_name = w_db.convert_git_id_to_slack_code(sl[0])
            message += "<@{}> works {:.2f}%, ".format(user_name, sl[1])
        message += "in *{}*".format(file_abs_path)
    else:
        message = random.choice(shell_dict['feat_check_severity_no_direct_conflict'])
        message = message.format(filename=file_abs_path)

    w_db.close()
    return message


def file_status_logic(slack_code, file_abs_path):
    w_db = work_database()
    message = ""

    project_name = w_db.get_repository_name(slack_code)
    user_list = w_db.get_working_users_on_file(project_name, file_abs_path)

    if user_list:
        user_list = w_db.convert_git_id_list_to_slack_code_list(user_list)
        message = random.choice(shell_dict['feat_file_status_users_existence']).format(filename=file_abs_path, user_list=",".join(user_list))
    else:
        message = random.choice(shell_dict['feat_file_status_users_nonexistence']).format(filename=file_abs_path)

    w_db.close()

    return message

def lock_response_logic(slack_code, msg_type, target_file, lock_time):
    w_db = work_database()
    project_name, user_name = w_db.get_repository_and_user_name(slack_code)

    if msg_type == "YES" and target_file in w_db.read_lock_history_list(project_name, slack_code):
        print("lock_respond_file : ", target_file)
        lock_file_list, already_lock_set = list(w_db.add_lock_list(project_name, slack_code, set([target_file]), lock_time))
        ch_message = ""
        if target_file in lock_file_list:
            ch_message += random.choice(shell_dict['feat_send_all_user_lock']).format(user=slack_code, file_name=target_file, lock_time=lock_time)

        send_all_user_message(ch_message, slack_code)
        w_db.delete_lock_history(project_name, slack_code, target_file)
    else:
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


def bye_logic(slack_code):
    w_db = work_database()
    user_name = w_db.convert_slack_code_to_slack_id(slack_code)

    message = random.choice(shell_dict['feat_goodbye']).format(user=user_name)
    return message

def no_response(slack_code):

    message = random.choice(shell_dict['sentence_process_no_response'])
    send_feature_button_message(slack_code,message)
    return ""

####################################################
'''
other functions
'''

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

