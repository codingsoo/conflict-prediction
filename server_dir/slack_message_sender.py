"""
    @file   slack_message_sender.py
    @brief
        Handling all the message related to conflict and prediction.(All the message except messages related to features.)
"""

from slacker import Slacker
import os
from pathlib import Path
import random
import configparser
from datetime import datetime, timedelta
from server_dir.conflict_flag_enum import Conflict_flag
from server_dir.user_database import user_database
from chat_bot_server_dir.work_database import work_database
from chat_bot_server_dir.constants import *


def get_slack():
    token = ''
    file_path = os.path.join(Path(os.getcwd()).parent, "all_server_config.ini")
    if not os.path.isfile(file_path):
        print("ERROR :: There is no server_config.ini")
        exit(2)
    else:
        config = configparser.ConfigParser()
        config.read(file_path)
        try:
            token = config["SLACK"]["TOKEN"]
        except:
            print("ERROR :: It is server_config.ini")
            exit(2)
    slack = Slacker(token)
    return slack


def make_shell_list(file):
    f = open(file, "r", encoding="UTF8")
    text = f.read()
    text = text.split("\n")
    return text


def get_message(shell_file):
    shell_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", shell_file))
    message = random.choice(shell_list)
    return message


def get_git_diff_code(user_name, project_name, file_name):
    w_db = work_database()
    git_diff_code = w_db.get_git_diff_code(user_name, project_name, file_name)
    if not git_diff_code:
        git_diff_code = ""
    git_diff_code = git_diff_code.replace("|||", "\n")
    print("get_git_diff_code", git_diff_code)
    print("hi")
    return git_diff_code


# Get user slack id
def get_user_slack_id_and_code(git_id):
    u_db = user_database("parent")
    return u_db.search_user_slack_id_and_code(git_id)


def send_lock_message(lock_file_list, user_name):
    w_db = work_database()
    user_slack_id_code = get_user_slack_id_and_code(user_name)
    message = ""
    for lfl in lock_file_list:
        # lock_user = w_db.convert_slack_code_to_slack_id(lfl[2])
        lock_user =lfl[2]

        end_time = lfl[4] + timedelta(hours=lfl[3])
        remain_time = end_time - datetime.now()
        remain_time_str = str(int(remain_time.seconds / 3600)).zfill(2) + " : " + str(int((remain_time.seconds % 3600) / 60)).zfill(2) + " : " + str(int(remain_time.seconds % 60)).zfill(2)

        message += get_message('feat_lock_alarm.txt').format(user2=lock_user,
                                                             filename=str(lfl[1]),
                                                             remaining_time=remain_time_str)
    send_direct_message(user_slack_id_code[1], message)
    w_db.close()


def send_direct_conflict_message(conflict_flag, conflict_project, conflict_file, conflict_logic, user1_name,
                                 user2_name, user1_percentage=0, user2_percentage=0, previous_percentage=0,
                                 current_severity=0, severity_flag=0):

    if conflict_logic == "in":
        conflict_logic = ""

    # Get user slack nickname
    user1_slack_id_code = get_user_slack_id_and_code(user1_name)
    user2_slack_id_code = get_user_slack_id_and_code(user2_name)
    print("user1_slack_id_code", user1_slack_id_code)
    print("user2_slack_id_code", user2_slack_id_code)

    current_percentage = round((user1_percentage + user2_percentage) / 2, 2)

    w_db = work_database()
    direct_ignore_flag = w_db.read_direct_ignore(conflict_project, user1_slack_id_code[1])

    approve_set = w_db.read_approved_list(user1_slack_id_code[1])
    print("approve_set : ", approve_set)
    print("conflict_file : ", conflict_file)
    w_db.close()

    if direct_ignore_flag == 1:
        print("IGNORE MESSAGE BY DIRECT")
        return
    elif conflict_file in approve_set:
        print("IGNORE MESSAGE BY FILE")
        return

    message = ""

    # Already conflict
    if conflict_flag == Conflict_flag.getting_severity_percentage.value \
        or conflict_flag == Conflict_flag.lower_severity_percentage.value \
        or conflict_flag == Conflict_flag.same_severity_percentage.value:

        if conflict_flag == Conflict_flag.getting_severity_percentage.value:
            # get severity_percentage

            message += get_message('get_severe_percentage.txt').format(user2=user2_slack_id_code[1],
                                                                       filename=conflict_file,
                                                                       severity=current_percentage,
                                                                       old_severity=previous_percentage,
                                                                       severity_subtraction=round(
                                                                           current_percentage - previous_percentage, 2))

            message += "\n"

            if severity_flag == Conflict_flag.getting_severity.value:
                # get severity
                message += get_message('adverb2.txt') + " "

                if current_severity == 2:
                    message += get_message('get_severe2_add.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 3:
                    message += get_message('get_severe3_add.txt').format(user2=user2_slack_id_code[1])

            elif severity_flag == Conflict_flag.same_severity.value:
                # same severity
                message += get_message('adverb1.txt') + " "

                if current_severity == 1:
                    message += get_message('same_severity1_add.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 2:
                    message += get_message('same_severity2_add.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 3:
                    message += get_message('same_severity3_add.txt').format(user2=user2_slack_id_code[1])

            elif severity_flag == Conflict_flag.lower_severity.value:
                # lower severity
                message += get_message('adverb1.txt') + " "

                if current_severity == 1:
                    message += get_message('alleviated1_add.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 2:
                    message += get_message('alleviated2_add.txt').format(user2=user2_slack_id_code[1])

        elif conflict_flag == Conflict_flag.lower_severity_percentage.value:
            # lower_severity_percentage
            message = get_message('alleviated_percentage.txt').format(user2=user2_slack_id_code[1],
                                                                      filename=conflict_file,
                                                                      severity=current_percentage,
                                                                      old_severity=previous_percentage,
                                                                      severity_subtraction=round(
                                                                          previous_percentage - current_percentage, 2))

            message += "\n"

            if severity_flag == Conflict_flag.getting_severity.value:
                # get severity
                message += get_message('adverb1.txt') + " "

                if current_severity == 2:
                    message += get_message('get_severe2_add.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 3:
                    message += get_message('get_severe3_add.txt').format(user2=user2_slack_id_code[1])

            elif severity_flag == Conflict_flag.same_severity.value:
                # same severity
                message += get_message('adverb1.txt') + " "

                if current_severity == 1:
                    message += get_message('same_severity1_add.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 2:
                    message += get_message('same_severity2_add.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 3:
                    message += get_message('same_severity3_add.txt').format(user2=user2_slack_id_code[1])

            elif severity_flag == Conflict_flag.lower_severity.value:
                # lower severity
                message += get_message('adverb2.txt') + " "

                if current_severity == 1:
                    message += get_message('alleviated1_add.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 2:
                    message += get_message('alleviated2_add.txt').format(user2=user2_slack_id_code[1])

        elif conflict_flag == Conflict_flag.same_severity_percentage.value:
            # lower_severity_percentage
            message = ""
            if severity_flag == Conflict_flag.getting_severity.value:
                # get severity
                if current_severity == 2:
                    message += get_message('get_severe2.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 3:
                    message += get_message('get_severe3.txt').format(user2=user2_slack_id_code[1])

            elif severity_flag == Conflict_flag.same_severity.value:
                # same severity
                message += ""

            elif severity_flag == Conflict_flag.lower_severity.value:
                # lower severity
                if current_severity == 1:
                    message += get_message('alleviated1.txt').format(user2=user2_slack_id_code[1])

                elif current_severity == 2:
                    message += get_message('alleviated2.txt').format(user2=user2_slack_id_code[1])

    # First conflict
    elif conflict_flag == Conflict_flag.same_function.value:
        # same function
        message = get_message('direct_conflict.txt').format(user1=user1_slack_id_code[1],
                                                            user2=user2_slack_id_code[1],
                                                            filename=conflict_logic)

        message += " " + get_message('direct_conflict_init_severity_2.txt').format(user2=user2_slack_id_code[1])

    elif conflict_flag == Conflict_flag.same_class.value:
        # same class
        logic_list = conflict_logic.split(':')[:-1]
        con_logic_for_class = ""
        for logic in logic_list:
            con_logic_for_class = con_logic_for_class + logic + ' '
        print(con_logic_for_class)

        message = get_message('direct_conflict.txt').format(user1=user1_slack_id_code[1],
                                                            user2=user2_slack_id_code[1],
                                                            filename=con_logic_for_class)
        message += " " + get_message('direct_conflict_init_severity_1.txt').format(user2=user2_slack_id_code[1])

    elif conflict_flag == Conflict_flag.file_in.value:
        # just in
        message = get_message('direct_conflict.txt').format(user1=user1_slack_id_code[1],
                                                            user2=user2_slack_id_code[1],
                                                            filename=conflict_file)

    elif conflict_flag == Conflict_flag.direct_conflict_finished.value:
        # direct conflict solved
        if user2_slack_id_code[1] == user1_slack_id_code[1]:
            pass
        else:
            message = get_message('direct_conflict_finished.txt').format(user1=user1_slack_id_code[1],
                                                                         user2=user2_slack_id_code[1],
                                                                         filename=conflict_file)

    if message != "":
        if conflict_flag == Conflict_flag.direct_conflict_finished.value:
            send_direct_message(user1_slack_id_code[1], message, "good")
        else:
            send_conflict_button_message(user1_slack_id_code[1], message, user2_name, conflict_project, conflict_file)

    return


def send_indirect_conflict_message(conflict_flag, conflict_project, conflict_file1="", conflict_file2="", conflict_logic1="", conflict_logic2="", user1_name="", user2_name="", type = None):

    # Get user slack nickname
    user1_slack_id_code = get_user_slack_id_and_code(user1_name)
    user2_slack_id_code = get_user_slack_id_and_code(user2_name)
    print("user1_slack_id_code", user1_slack_id_code)
    print("user2_slack_id_code", user2_slack_id_code)

    w_db = work_database()
    indirect_ignore_flag = w_db.read_indirect_ignore(conflict_project, user1_slack_id_code[1])

    approve_set = w_db.read_approved_list(user1_slack_id_code[1])
    print("approve_set : ", approve_set)
    print("conflict_file : ", conflict_file1)
    w_db.close()

    if conflict_file1 in approve_set:
        print("IGNORE MESSAGE BY FILE")
        return

    if indirect_ignore_flag == 1:
        print("IGNORE MESSAGE BY INDIRECT")
        return

    message = ""

    if conflict_flag == Conflict_flag.indirect_conflict_finished.value:
        # indirect conflict solved
        if user2_slack_id_code[1] == user1_slack_id_code[1]:
            pass
        else:
            message = get_message('indirect_conflict_finished.txt').format(user1=user1_slack_id_code[1],
                                                                           filename1=conflict_file1,
                                                                           logic1=conflict_logic1,
                                                                           user2=user2_slack_id_code[1],
                                                                           filename2=conflict_file2,
                                                                           logic2=conflict_logic2)
    elif conflict_flag == Conflict_flag.indirect_conflict.value:
        # indirect conflict
        if type == 'user_call':
            if conflict_logic1 == conflict_logic2:
                message = get_message('indirect_conflict_calling_no_length.txt')
            else:
                message = get_message('indirect_conflict_calling_length.txt')
        elif type == 'user_work':
            message = get_message('indirect_conflict_working.txt')

        message = message.format(filename1=conflict_file1,
                                 filename2=conflict_file2,
                                 function1=conflict_logic1,
                                 function2=conflict_logic2,
                                 user1=user1_slack_id_code[1],
                                 user2=user2_slack_id_code[1])

    if message != "":
        if conflict_flag == Conflict_flag.indirect_conflict_finished.value:
            send_direct_message(user1_slack_id_code[1], message, "good")
        else:
            send_conflict_button_message(user1_slack_id_code[1], message, user2_name, conflict_project, conflict_file2)

    return


def send_prediction_message(project_name, user_name, probability_dict):
    user_slack_id_code = get_user_slack_id_and_code(user_name)

    w_db = work_database()
    prediction_ignore_flag = w_db.read_prediction_ignore(project_name, user_slack_id_code[1])

    if prediction_ignore_flag == 1:
        print("IGNORE MESSAGE BY PREDICTION")
        return

    user_code_list = list(probability_dict.keys())
    user_list = [0] * len(user_code_list)
    for i, user_temp in enumerate(user_code_list):
        slack_code, slack_id = w_db.convert_git_id_to_slack_code_id(user_temp)
        user_code_list[i] = "<@" + slack_code + ">"
        user_list[i] = [slack_id, slack_code]

    percentage_list = list(probability_dict.values())

    message = get_message('prediction_direct_conflict.txt')
    message = message.format(userlist=user_code_list,
                             percentagelist=percentage_list,
                             filelist="")

    send_prediction_button_message(user_slack_id_code[1], message, project_name, user_list)

def send_remove_lock_channel(channel, lock_file_list):
    message = get_message('feat_send_all_user_auto_unlock.txt').format(file_name=", ".join(lock_file_list)) + "\n"
    # for file_name in lock_file_list:
    #     message += "{} is unlocked from now on.\n".format(file_name)
    # send_channel_message(channel, message)
    send_all_user_message(message=message)


def channel_join_check(channel):
    slack = get_slack()

    channel_idx = -1
    channels_list_res = slack.channels.list()
    channels_list = channels_list_res.body["channels"]

    for cl_idx, cl in enumerate(channels_list):
        if cl.get("name") == channel:
            channel_idx = cl_idx

    if channel_idx == -1:
        #Do not implement yet
        print("Channel is not in Slack")
        return CHANNEL_NONEXISTENCE
    else:
        is_member = channels_list[channel_idx].get("is_member")
        if not is_member:
            print("Sayme is not join in {} Channel".format(channel))
            return CHANNEL_WITHOUT_SAYME
        else:
            return CHANNEL_WITH_SAYME


# Send a message to everyone in the project
def send_all_user_message(message, slack_code=""):
    if message == "":
        return
    slack = get_slack()

    u_db = user_database("parent")
    all_user = u_db.search_all_slack_code(slack_code)
    u_db.close()

    for user in all_user:
        attachments_dict = dict()
        attachments_dict['text'] = "%s" % (message)
        attachments_dict['mrkdwn_in'] = ["text", "pretext"]
        attachments = [attachments_dict]
        slack.chat.post_message(channel="" + user[0], text=None, attachments=attachments, as_user=True)

    return


# Put user slack id and message for sending chatbot message
def send_direct_message(slack_code, message, color="#D3D3D3"):
    if message == "":
        return
    slack = get_slack()
    attachments_dict = dict()
    attachments_dict['text'] = "%s" % (message)
    attachments_dict['mrkdwn_in'] = ["text", "pretext"]
    attachments_dict['color'] = color
    attachments = [attachments_dict]
    slack.chat.post_message(channel="" + slack_code, text=None, attachments=attachments, as_user=True)
    return



# Lock request button message
def send_lock_request_button_message(slack_code, lock_file, lock_time):
    slack = get_slack()

    actions = [{'name': "YES", 'text': "YES", 'type': "button", 'value': lock_time},
               {'name': "NO", 'text': "NO", 'type': "button", 'value': lock_time}]

    attachments_dict = dict()
    attachments_dict['title'] = "Lock Request"
    attachments_dict['text'] = "*{}* is just unlocked. Do you want me to lock it for {} hours?".format(lock_file, lock_time)
    attachments_dict['fallback'] = "Lock Request Button Message"
    attachments_dict['callback_id'] = lock_file
    attachments_dict['actions'] = actions
    attachments_dict['color'] = "#3AA3E3"
    attachments = [attachments_dict]
    slack.chat.post_message(channel=slack_code, text=None, attachments=attachments, as_user=True)


# Typo error file selection button message
def send_typo_error_button_message(slack_code,error_file_name, file_name, sentence, intent_type):
    slack = get_slack()
    attachments_dict = dict()

    message = ""

    actions = [{'name': sentence.replace(error_file_name, file_name), 'text': "YES", 'type': "button", 'value': "YES"},
               {'name': sentence, 'text': "NO", 'type': "button", 'value': "NO"}]

    attachments_dict['title'] = "I think you have typo error."
    attachments_dict['text'] = "You mean%s file?" % (file_name)
    attachments_dict['fallback'] = "You are unable to choose a file."
    attachments_dict['callback_id'] = intent_type
    # attachments_dict['attachment_type'] = "warning"
    attachments_dict['actions'] = actions
    attachments_dict['color'] = "#3AA3E3"
    attachments = [attachments_dict]

    slack.chat.post_message(channel="" + slack_code, text=None, attachments=attachments, as_user=True)


# File selection button message
def send_file_selection_button_message(slack_code, called_same_named_dict, sentence, intent_type):
    slack = get_slack()
    attachments_dict = dict()

    for csnd_idx, (file_name, file_abs_path_list) in enumerate(called_same_named_dict.items()):
        message = ""
        actions = []

        for fapl_idx, file_abs_path in enumerate(file_abs_path_list):
            message += "%d. %s\n" % (fapl_idx + 1, file_abs_path)
            actions_dict = dict()
            actions_dict['name'] = sentence
            actions_dict['text'] = fapl_idx + 1
            actions_dict['type'] = "button"
            actions_dict['value'] = file_abs_path
            actions.append(actions_dict)

        attachments_dict['title'] = "Which file do you mean?"
        attachments_dict['text'] = "%s" % (message)
        attachments_dict['fallback'] = "File Selection Button Message"
        attachments_dict['callback_id'] = intent_type
        # attachments_dict['attachment_type'] = "warning"
        attachments_dict['actions'] = actions
        attachments_dict['color'] = "#3AA3E3"
        attachments = [attachments_dict]

        slack.chat.post_message(channel="" + slack_code, text=None, attachments=attachments, as_user=True)


# Typo error file selection button message
def send_typo_error_button_message(slack_code,error_file_name, file_name, sentence, intent_type):
    slack = get_slack()
    attachments_dict = dict()

    message = ""

    actions = [{'name': sentence.replace(error_file_name, file_name), 'text': "YES", 'type': "button", 'value': "YES"},
               {'name': sentence, 'text': "NO", 'type': "button", 'value': "NO"}]

    attachments_dict['title'] = "I think you have typo error."
    attachments_dict['text'] = "Do you mean %s file?" % (file_name)
    attachments_dict['fallback'] = "Typo Error Button Message"
    attachments_dict['callback_id'] = intent_type
    attachments_dict['attachment_type'] = "warning"
    attachments_dict['actions'] = actions
    attachments_dict['color'] = "#3AA3E3"
    attachments = [attachments_dict]

    slack.chat.post_message(channel="" + slack_code, text=None, attachments=attachments, as_user=True)

# Git diff button message
def send_feature_button_message(slack_code,message):
    slack = get_slack()
    attachments_dict = dict()

    actions = [{'name': 'List of feature', 'text': 'List of feature', 'type': "button", 'value': 'All'},
               {'name': 'List of sample commands', 'text': 'List of sample commands', 'type': "button", 'value': 'All'}]

    attachments_dict['title'] = ""
    attachments_dict['text'] = "%s" % (message)
    attachments_dict['fallback'] = "Send list of feature button message"
    attachments_dict['callback_id'] = "ALL"
    attachments_dict['actions'] = actions
    attachments_dict['color'] = "warning"
    attachments = [attachments_dict]

    slack.chat.post_message(channel=slack_code, text=None, attachments=attachments, as_user=True)

# List of feature message after click a button
def send_list_of_feature_button_message(slack_code):
    slack = get_slack()
    list_of_feature = "# 1. ignore_file : It functions like gitignore. A user can customize his/her ignore files. \n\
# 2. lock_file : A user can lock his/her files. If other users try to modify the related file of the lock_file, chatbot gives them a warning.\n\
# 3. code_history : A user can ask who wrote certain code lines. \n\
# 4. ignore_alarm : A user can ignore direct and indirect conflicts, and prediction alarm.\n\
# 5. check_conflict : Before a user starts to work, the user can check if he/she generates conflict or not on the working file.\n\
# 6. working_status : A user can ask about other user's working status.\n\
# 7. user_message : A user can let chatbot give a message to other users.\n\
# 8. recommend : A user can ask chatbot to recommend reaction to conflict.\n\
# 9. check_ignored_file : A user can ask chatbot which files are ignored.\n\
# 10. check_who_locked_file : A user can ask chatbot about who locked the file.\n\
# 11. check_severity : A user can ask chatbot about how severe conflict is. \n\
# 12. ignore_prediction_alarm : A user can ignore prediction alarm. \n\
# 13. file_status : A user can check which user is now working on specific file. \n\
# 14. user_recognize : Chatbot knows when last time a user connected is, so bot can greet the user with time information. \n\
# 15. greeting : Chatbot can greet users.\n\
# 16. complimentary_close : Chatbot can say good bye.\n\
# 17. detect_direct_conflict : Chatbot can detect direct conflict and severity.\n\
# 18. detect_indirect_conflict : Chatbot can detect indirect conflict and severity."

    attachments_dict = dict()

    actions = [{'name': 'List of feature', 'text': 'List of feature', 'type': "button", 'value': 'All'},
               {'name': 'List of sample commands', 'text': 'List of sample commands', 'type': "button", 'value': 'All'}]

    attachments_dict['title'] = ""
    attachments_dict['text'] = list_of_feature
    attachments_dict['fallback'] = "Send list of feature button message"
    attachments_dict['callback_id'] = "ALL"
    attachments_dict['actions'] = actions
    attachments_dict['color'] = "warning"
    attachments = [attachments_dict]

    slack.chat.post_message(channel=slack_code, text=None, as_user=True, attachments= attachments)


# List of feature message after click a button
def send_list_of_command_message(slack_code):
    slack = get_slack()
    list_of_sample_commands = "# 1. ignore_file : Can you stop notifying me about file.py? / I want to get an alarm about file.py\n\
# 2. lock_file : Sayme, could you please lock file.py / Release file.py.\n\
# 3. code_history : You should tell me who wrote code line 1 to line 9 in file.py. / I want to know who writes line 15 in file.py.\n\
# 4. ignore_alarm : Don't alert me about direct conflict / Unignore direct conflict.\n\
# 5. check_conflict : I want to know if a conflict occurs when I change file.py. / Can I change file.py?\n\
# 6. working_status : What @Sun is up to? / Give me @Sun's working status.\n\
# 7. user_message : Can you send message to @Sun that “Message”? / Send “message” to @Sun.\n\
# 8. recommend : Any thought about how to solve conflict at file.py? / What should I do to solve conflict in file.py?\n\
# 9 . check_ignored_file : You should tell me which file @Sun ignored. / Tell me which files are being ignored.\n\
# 10. check_who_locked_file : Tell me who locked file.py. / Do you know who lock SquareMatrix.py?\n\
# 11. check_severity : Could you tell me the severity of file.py? / Let me know the severity of file.py\n\
# 12. ignore_prediction_alarm : Stop sending me the notification about prediction. / Inform prediction part.\n\
# 13. file_status : Who is editing file.py now? / Check the user who's working on file.py."

    attachments_dict = dict()

    actions = [{'name': 'List of feature', 'text': 'List of feature', 'type': "button", 'value': 'All'},
               {'name': 'List of sample commands', 'text': 'List of sample commands', 'type': "button", 'value': 'All'}]

    attachments_dict['title'] = ""
    attachments_dict['text'] = list_of_sample_commands
    attachments_dict['fallback'] = "Send list of sample command button message"
    attachments_dict['callback_id'] = "ALL"
    attachments_dict['actions'] = actions
    attachments_dict['color'] = "warning"
    attachments = [attachments_dict]

    slack.chat.post_message(channel=slack_code, text=None, as_user=True, attachments= attachments)

# Git diff button message
def send_conflict_button_message(slack_code, message, user2_name, project_name, file_name):
    slack = get_slack()
    attachments_dict = dict()

    actions = [{'name': user2_name, 'text': "git diff", 'type': "button", 'value': file_name}]

    attachments_dict['title'] = ""
    attachments_dict['text'] = "%s" % (message)
    attachments_dict['fallback'] = "Git Diff Code Button Message"
    attachments_dict['callback_id'] = project_name
    attachments_dict['actions'] = actions
    attachments_dict['color'] = "warning"
    attachments = [attachments_dict]

    slack.chat.post_message(channel=slack_code, text=None, attachments=attachments, as_user=True)


# Git diff message after click a button
# def send_git_diff_message(user1_name, user2_name, project_name, file_name):
#     slack = get_slack()
#     git_diff_code = "```" + get_git_diff_code(user2_name, project_name, file_name) + "```"
#     print("send_git_diff_message", git_diff_code)
#
#     slack.chat.post_message(channel=user1_name, text=git_diff_code, as_user=True)


# Prediction button message
def send_prediction_button_message(slack_code, message, project_name, user_list):
    slack = get_slack()
    attachments_dict = dict()

    actions = []
    actions.append({'name': 'all', 'text': 'ALL', 'type': "button", 'value': 'all', 'style': 'danger'})
    for user_id_and_code in user_list:
        actions_dict = dict()
        actions_dict['name'] = user_id_and_code[1]
        actions_dict['text'] = user_id_and_code[0]
        actions_dict['type'] = "button"
        actions_dict['value'] = user_id_and_code[1]
        actions.append(actions_dict)

    attachments_dict['title'] = ""
    attachments_dict['text'] = "%s" % (message)
    attachments_dict['fallback'] = "Prediction Button Message"
    attachments_dict['callback_id'] = project_name
    attachments_dict['actions'] = actions
    attachments_dict['color'] = "#3AA3E3"
    attachments = [attachments_dict]

    slack.chat.post_message(channel=slack_code, text=None, attachments=attachments, as_user=True)


# Prediction list message after click a button
def get_prediction_list_field(user1_code, user2_code, project_name):
    u_db = user_database('parent')
    user1_git_id = u_db.convert_slack_code_to_git_id(user1_code)
    user2_git_id = u_db.convert_slack_code_to_git_id(user2_code)
    u_db.close()

    w_db = work_database()

    # prediction_list_field = []

    # Show all of prediction lists
    if user2_code == "all":
        prediction_list = w_db.get_prediction_list(project_name, user1_git_id, 'all')

    # Show prediction list of user2
    else:
        prediction_list = w_db.get_prediction_list(project_name, user1_git_id, user2_git_id)

    prediction_list.sort()

    sun_test_list = []

    # {
    #     "fallback": "ReferenceError - UI is not defined: https://honeybadger.io/path/to/event/",
    #     "fields": prediction_field,
    #     "color": "good"
    # }

    # Version 7
    # prediction_list_field.append({"title": "Percentage", "short": True})
    # prediction_list_field.append({"title": "User Name", "short": True})
    # prediction_list_field.append({"title": "Related File", "short": True})
    # prediction_list_field.append({"title": "Conflict File", "short": True})
    # temp_dict = {
    #     "fallback": "ReferenceError - UI is not defined: https://honeybadger.io/path/to/event/",
    #     "fields": prediction_list_field,
    #     "color": "good"
    # }
    # sun_test_list.append(temp_dict)
    #
    # for prediction_list_temp in prediction_list:
    #     prediction_list_field = []
    #     other_name = w_db.convert_git_id_to_slack_id(prediction_list_temp[1])
    #     prediction_list_field.append({"value": str(prediction_list_temp[3]) + "%", "short": True})
    #     prediction_list_field.append({"value": other_name, "short": True})
    #     prediction_list_field.append({"value": prediction_list_temp[4], "short": True})
    #     prediction_list_field.append({"value": prediction_list_temp[2], "short": True})
    #     temp_dict = {
    #         "fallback": "ReferenceError - UI is not defined: https://honeybadger.io/path/to/event/",
    #         "fields": prediction_list_field,
    #         "color": "good"
    #     }
    #     sun_test_list.append(temp_dict)


    # Version 8
    for prediction_list_temp in prediction_list:
        prediction_list_field = []
        other_name = w_db.convert_git_id_to_slack_id(prediction_list_temp[1])
        prediction_list_field.append({"title": "Percentage", "short": True})
        prediction_list_field.append({"title": "User Name", "short": True})
        prediction_list_field.append({"value": str(prediction_list_temp[3]) + "%", "short": True})
        prediction_list_field.append({"value": other_name, "short": True})
        prediction_list_field.append({"title": "Current File", "short": True})
        prediction_list_field.append({"title": "Conflict File", "short": True})
        prediction_list_field.append({"value": prediction_list_temp[4], "short": True})
        prediction_list_field.append({"value": prediction_list_temp[2], "short": True})
        temp_dict = {
            "fallback": "ReferenceError - UI is not defined: https://honeybadger.io/path/to/event/",
            "fields": prediction_list_field,
            "color": "good"
        }
        sun_test_list.append(temp_dict)

    # Version 9
    # check = True
    # for prediction_list_temp in prediction_list:
    #     prediction_list_field = []
    #     other_name = w_db.convert_git_id_to_slack_id(prediction_list_temp[1])
    #     if check:
    #         prediction_list_field.append({"title": "Percentage", "short": True})
    #         prediction_list_field.append({"title": "User Name", "short": True})
    #     prediction_list_field.append({"value": str(prediction_list_temp[3]) + "%", "short": True})
    #     prediction_list_field.append({"value": other_name, "short": True})
    #     if check:
    #         prediction_list_field.append({"title": "Related File", "short": True})
    #         prediction_list_field.append({"title": "Conflict File", "short": True})
    #     prediction_list_field.append({"value": prediction_list_temp[4], "short": True})
    #     prediction_list_field.append({"value": prediction_list_temp[2], "short": True})
    #
    #     check = False
    #     temp_dict = {
    #         "fallback": "ReferenceError - UI is not defined: https://honeybadger.io/path/to/event/",
    #         "fields": prediction_list_field,
    #         "color": "good"
    #     }
    #     sun_test_list.append(temp_dict)

    # Version 1
    # prediction_list_field.append({"title": "Percentage", "short": True})
    # prediction_list_field.append({"title": "User Name", "short": True})
    # prediction_list_field.append({"title": "Related File", "short": True})
    # prediction_list_field.append({"title": "Conflict File", "short": True})
    # prediction_list_field.append({"value": "---------------------------------------------------------------------------------------------------", "short": False})
    #
    # for prediction_list_temp in prediction_list:
    #     other_name = w_db.convert_git_id_to_slack_id(prediction_list_temp[1])
    #     prediction_list_field.append({"value": str(prediction_list_temp[3]) + "%", "short": True})
    #     prediction_list_field.append({"value": other_name, "short": True})
    #     prediction_list_field.append({"value": prediction_list_temp[4], "short": True})
    #     prediction_list_field.append({"value": prediction_list_temp[2], "short": True})
    #     prediction_list_field.append({"value": "---------------------------------------------------------------------------------------------------", "short": False})

    # Version 2
    # for prediction_list_temp in prediction_list:
    #     other_name = w_db.convert_git_id_to_slack_id(prediction_list_temp[1])
    #     prediction_list_field.append({"title": "Percentage", "short": True})
    #     prediction_list_field.append({"title": "User Name", "short": True})
    #     prediction_list_field.append({"value": str(prediction_list_temp[3]) + "%", "short": True})
    #     prediction_list_field.append({"value": other_name, "short": True})
    #     prediction_list_field.append({"title": "Related File", "short": True})
    #     prediction_list_field.append({"title": "Conflict File", "short": True})
    #     prediction_list_field.append({"value": prediction_list_temp[4], "short": True})
    #     prediction_list_field.append({"value": prediction_list_temp[2], "short": True})
    #     prediction_list_field.append({
    #                                      "value": "---------------------------------------------------------------------------------------------------",
    #                                      "short": False})

    # Version 3
    # check = True
    # for prediction_list_temp in prediction_list:
    #     other_name = w_db.convert_git_id_to_slack_id(prediction_list_temp[1])
    #     if check:
    #         prediction_list_field.append({"title": "Percentage", "short": True})
    #         prediction_list_field.append({"title": "User Name", "short": True})
    #     prediction_list_field.append({"value": str(prediction_list_temp[3]) + "%", "short": True})
    #     prediction_list_field.append({"value": other_name, "short": True})
    #     if check:
    #         prediction_list_field.append({"title": "Related File", "short": True})
    #         prediction_list_field.append({"title": "Conflict File", "short": True})
    #     prediction_list_field.append({"value": prediction_list_temp[4], "short": True})
    #     prediction_list_field.append({"value": prediction_list_temp[2], "short": True})
    #     prediction_list_field.append({
    #                                      "value": "---------------------------------------------------------------------------------------------------",
    #                                      "short": False})
    #
    #     check = False

    w_db.close()

    # return prediction_list_field
    return sun_test_list