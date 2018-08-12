from slacker import Slacker
import json
import os
from pathlib import Path
import random
import configparser

def get_slack():
    token = ''
    if not os.path.isfile("server_config.ini"):
        print("ERROR :: There is no server_config.ini")
        exit(2)
    else:
        config = configparser.ConfigParser()
        config.read("server_config.ini")
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
    go_to_same_file_shell_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "same_file.txt"))
    return go_to_same_file_shell_list

def make_server_shell_list():
    get_server_shell_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "get_server.txt"))
    return get_server_shell_list

def make_conflict_finished_list():
    conflict_finished = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "conflict_finished.txt"))
    return conflict_finished

def make_get_closer_list():
    get_closer_list = make_shell_list(os.path.join(Path(os.getcwd()).parent, "situation_shell", "get_closer.txt"))
    return get_closer_list

# Get user slack id
def get_user_slack_id(git_id):
    slack_id = ""

    # Import User Data
    with open(os.path.join(Path(os.getcwd()).parent, "user_data", "user_slack.json"), 'r') as f1:
        user_slack_id_dict = json.load(f1)

    # Import User Data
    with open(os.path.join(Path(os.getcwd()).parent, "user_data", "user_git.json"), 'r') as f2:
        user_git_id_dict = json.load(f2)

    try:
        slack_id = user_git_id_dict[git_id]
        slack_id_code = user_slack_id_dict[slack_id]
    except:
        print("ERROR : no slack id data")
        slack_id_code = "AAAA"

    f1.close()
    f2.close()

    return slack_id, slack_id_code


def send_conflict_message(conflict_flag, conflict_project, conflict_file, conflict_logic, user1_name, user2_name):

    user1_slack_id_code = get_user_slack_id(user1_name)
    user2_slack_id_code = get_user_slack_id(user2_name)
    message = ""

    # Already conflict
    if(conflict_flag == 5):
        # get server
        server_shell = make_server_shell_list()
        message = server_shell[random.randint(0, len(server_shell) - 1)]

    elif(conflict_flag == 4):
        # same server
        same_shell = make_same_file_shell_list()
        message = same_shell[random.randint(0, len(same_shell) - 1)] % (user1_slack_id_code[0], user2_slack_id_code[0], conflict_file, conflict_logic)

    elif(conflict_flag == 3):
        # lower serverity
        conflict_finished_shell = make_conflict_finished_list()
        message = conflict_finished_shell[random.randint(0, len(conflict_finished_shell) - 1)] % (user1_slack_id_code[0], user2_slack_id_code[0])


    # First conflict
    elif(conflict_flag == 2):
        # same function
        same_shell = make_same_file_shell_list()
        message = same_shell[random.randint(0, len(same_shell) - 1)] % (user1_slack_id_code[0], user2_slack_id_code[0], conflict_file, conflict_logic)

    elif(conflict_flag == 1):
        # same class
        same_shell = make_same_file_shell_list()
        message = same_shell[random.randint(0, len(same_shell) - 1)] % (user1_slack_id_code[0], user2_slack_id_code[0], conflict_file, conflict_logic)

    elif(conflict_flag == 0):
        # just in
        get_closer = make_same_file_shell_list()
        message = get_closer[random.randint(0, len(get_closer) - 1)] % (user1_slack_id_code[0], user2_slack_id_code[0])

    send_direct_message(user1_slack_id_code[1], message)
    print(message)

    return


# Put channel name and message for sending chatbot message
def send_channel_message(channel, message):
    slack = get_slack()
    attachments_dict = dict()
    attachments_dict['text'] = "%s" % (message)
    attachments_dict['mrkdwn_in'] = ["text", "pretext"]
    attachments = [attachments_dict]
    slack.chat.post_message(channel="#" + channel, text=None, attachments=attachments, as_user=True)
    return


# Put user slack id and message for sending chatbot message
def send_direct_message(user_id, message):
    slack = get_slack()
    attachments_dict = dict()
    attachments_dict['text'] = "%s" % (message)
    attachments_dict['mrkdwn_in'] = ["text", "pretext"]
    attachments = [attachments_dict]
    slack.chat.post_message(channel="" + user_id, text=None, attachments=attachments, as_user=True)
    return