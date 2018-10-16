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

def make_go_to_same_file_shell_list():
    go_to_same_file_shell_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "go_to_same_file.txt"))
    return go_to_same_file_shell_list

def make_same_file_shell_list():
    same_file_shell_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "same_file.txt"))
    return same_file_shell_list

def make_same_file_channel_shell_list():
    same_file_channel_shell_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "same_file_channel.txt"))
    return same_file_channel_shell_list

def make_server_shell_list():
    server_shell_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "get_severe.txt"))
    return server_shell_list

def make_direct_conflict_finished_list():
    conflict_finished_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "direct_conflict_finished.txt"))
    return conflict_finished_list

def make_indirect_conflict_finished_list():
    conflict_finished_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "indirect_conflict_finished.txt"))
    return conflict_finished_list

def make_get_closer_list():
    get_closer_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "get_closer.txt"))
    return get_closer_list

def make_lower_severity_list():
    lower_severity_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "conflict_alleviated.txt"))
    return lower_severity_list

def make_indirect_conflict_shell_list():
    indirect_conflict_shell_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "indirect_conflict.txt"))
    return indirect_conflict_shell_list

# Get user slack id
def get_user_slack_id(git_id):
    u_db = user_database("parent")
    return u_db.search_user_slack_id_code(git_id)

def send_lock_message(lock_file_list, user_name):
    w_db = work_database()
    user_slack_id_code = get_user_slack_id(user_name)
    message = ""
    for lfl in lock_file_list:
        lock_user = w_db.convert_slack_code_to_slack_id(lfl[2])

        end_time = lfl[4] + timedelta(hours=lfl[3])
        remain_time = end_time - datetime.now()
        remain_time_str = str(int(remain_time.seconds / 3600)).zfill(2) + " : " + str(int((remain_time.seconds % 3600) / 60)).zfill(2) + " : " + str(int(remain_time.seconds % 60)).zfill(2)

        lock_message_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "feat_lock_alarm.txt"))
        message = random.choice(lock_message_list)
        message = message.format(lock_user, str(lfl[1]), remain_time_str)
    send_direct_message(user_slack_id_code[1], message)
    w_db.close()

def send_conflict_message(conflict_flag, conflict_project, conflict_file, conflict_logic, user1_name, user2_name, user1_percentage = -1, user2_percentage = -1):

    if conflict_logic == "in":
        conflict_logic = ""

    # Get user slack nickname
    user1_slack_id_code = get_user_slack_id(user1_name)
    user2_slack_id_code = get_user_slack_id(user2_name)

    # Initialize ignore flag
    direct_ignore_flag = 0
    indirect_ignore_flag = 0

    try:
        w_db = work_database()
        direct_ignore_flag, indirect_ignore_flag = w_db.read_ignore(conflict_project, user1_slack_id_code[1])
        w_db.close()
    except:
        print("no ignore list")

    if(direct_ignore_flag == 1 or indirect_ignore_flag == 1):
        print("IGNORE MESSAGE")
        return

    message = ""

    # Already conflict
    if(conflict_flag == Conflict_flag.getting_severity.value):
        # get severity
        server_shell = make_server_shell_list()
        message = server_shell[random.randint(0, len(server_shell) - 1)]

    elif(conflict_flag == Conflict_flag.same_severity.value):
        # same severity
        same_shell = make_same_file_shell_list()
        message = same_shell[random.randint(0, len(same_shell) - 1)].format(str(user2_slack_id_code[0]), str(conflict_file), str(conflict_logic))

    elif(conflict_flag == Conflict_flag.lower_severity.value):
        # lower severity
        lower_severity = make_lower_severity_list()
        message = lower_severity[random.randint(0, len(lower_severity) - 1)].format(user2_slack_id_code[0])

    # First conflict
    elif(conflict_flag == Conflict_flag.same_function.value):
        # same function
        same_shell = make_same_file_shell_list()
        message = same_shell[random.randint(0, len(same_shell) - 1)].format(user2_slack_id_code[0], conflict_file, conflict_logic)
        message += "\n### Percentage ###\nUser1 : {a:.2f}%   |   user2 : {b:.2f}%".format(a=user1_percentage, b=user2_percentage)

    elif(conflict_flag == Conflict_flag.same_class.value):
        # same class
        same_shell = make_same_file_shell_list()
        logic_list = conflict_logic.split(':')[:-1]
        con_logic_for_class = ""
        for logic in logic_list:
            con_logic_for_class = con_logic_for_class + logic + ' '
        print(con_logic_for_class)
        message = same_shell[random.randint(0, len(same_shell) - 1)].format(user2_slack_id_code[0], conflict_file, con_logic_for_class)
        message += "\n### Percentage ###\nUser1 : {a:.2f}%   |   user2 : {b:.2f}%".format(a=user1_percentage, b=user2_percentage)

    elif(conflict_flag == Conflict_flag.file_in.value):
        # just in
        get_closer = make_same_file_shell_list()
        message = get_closer[random.randint(0, len(get_closer) - 1)].format(user2_slack_id_code[0], conflict_file, "")
        message += "\n### Percentage ###\nUser1 : {a:.2f}%   |   user2 : {b:.2f}%".format(a=user1_percentage, b=user2_percentage)

    elif(conflict_flag == Conflict_flag.direct_conflict_finished.value):
        # conflict solved
        conflict_finished = make_direct_conflict_finished_list()
        if user2_slack_id_code[0] == user1_slack_id_code[0]:
            pass
        else:
            message = conflict_finished[random.randint(0, len(conflict_finished) - 1)].format(user2_slack_id_code[0])

    elif (conflict_flag == Conflict_flag.indirect_conflict_finished.value):
        # conflict solved
        conflict_finished = make_indirect_conflict_finished_list()
        if user2_slack_id_code[0] == user1_slack_id_code[0]:
            pass
        else:
            message = conflict_finished[random.randint(0, len(conflict_finished) - 1)].format(user2_slack_id_code[0])

    elif(conflict_flag == Conflict_flag.indirect_conflict.value):
        # indirect conflict
        indirect_shell = make_indirect_conflict_shell_list()
        message = indirect_shell[random.randint(0, len(indirect_shell) - 1)].format(conflict_file, user2_slack_id_code[0], conflict_logic)

    if message != "":
        send_direct_message(user1_slack_id_code[1], message)

    return

def send_conflict_message_channel(conflict_file, conflict_logic, user1_name, user2_name):
    user1_slack_id_code = get_user_slack_id(user1_name)
    user2_slack_id_code = get_user_slack_id(user2_name)
    message = ""

    # same server
    same_channel_shell = make_same_file_channel_shell_list()
    if conflict_logic == "in":
        message = same_channel_shell[random.randint(0, len(same_channel_shell) - 1)]
        message = message.format(user1_slack_id_code[0], user2_slack_id_code[0], conflict_file, '')
    else:
        send_channel_message("code-conflict-chatbot", message)
        message = same_channel_shell[random.randint(0, len(same_channel_shell) - 1)]
        message = message.format(user1_slack_id_code[0], user2_slack_id_code[0], conflict_file, conflict_logic)
    send_channel_message("code-conflict-chatbot", message)
    return

def send_remove_lock_channel(channel, lock_file_list):
    message = ""
    for file_name in lock_file_list:
        message += "{} is unlocked from now on.\n".format(file_name)
    send_channel_message(channel, message)

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


# Put channel name and message for sending chatbot message
def send_channel_message(channel, message):
    if message == "":
        return
    slack = get_slack()
    ret_cjc = channel_join_check(channel)

    if ret_cjc == CHANNEL_WITH_SAYME:
        attachments_dict = dict()
        attachments_dict['text'] = "%s" % (message)
        attachments_dict['mrkdwn_in'] = ["text", "pretext"]
        attachments = [attachments_dict]
        slack.chat.post_message(channel="#" + channel, text=None, attachments=attachments, as_user=True)

    return ret_cjc

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
def send_direct_message(slack_code, message):
    if message == "":
        return
    slack = get_slack()
    attachments_dict = dict()
    attachments_dict['text'] = "%s" % (message)
    attachments_dict['mrkdwn_in'] = ["text", "pretext"]
    attachments = [attachments_dict]
    slack.chat.post_message(channel="" + slack_code, text=None, attachments=attachments, as_user=True)
    return

def send_file_button_message(slack_code, called_same_named_dict, sentence, intent_type):
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
        attachments_dict['fallback'] = "You are unable to choose a file."
        attachments_dict['callback_id'] = intent_type
        # attachments_dict['attachment_type'] = "warning"
        attachments_dict['actions'] = actions
        attachments_dict['color'] = "#3AA3E3"
        attachments = [attachments_dict]

        slack.chat.post_message(channel="" + slack_code, text=None, attachments=attachments, as_user=True)

    # slack = Slacker("SLACK_BOT_TOKEN")
    # response = slack.rtm.start()
    # endpoint = response.body['url']
    # ws2 = websocket.create_connection("ws://localhost:4000")
    # print("start loop")
    # while True:
    #     event = json.loads(ws2.recv())
    #     print("event", event)
    #     if event.get('type') != "message" or event.get('user') != slack_code:
    #         continue
    #     ws2.close()
    #     break

def send_lock_button_message(slack_code, lock_file, lock_time):
    slack = get_slack()

    actions = [{'name': "YES", 'text': "YES", 'type': "button", 'value': lock_time},
               {'name': "NO", 'text': "NO", 'type': "button", 'value': lock_time}]

    attachments_dict = dict()
    attachments_dict['title'] = "Approval Request"
    attachments_dict['text'] = "*{}* is just unlocked. Do you want me to lock it for {} hours?".format(lock_file, lock_time)
    attachments_dict['fallback'] = "You are unable to choose yes or no."
    attachments_dict['callback_id'] = lock_file
    attachments_dict['actions'] = actions
    attachments_dict['color'] = "good"
    attachments = [attachments_dict]
    slack.chat.post_message(channel=slack_code, text=None, attachments=attachments, as_user=True)