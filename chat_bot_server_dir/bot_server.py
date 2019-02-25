import websocket
import time
import json
import _thread
import os
import nltk
import configparser
from pathlib import Path
from slacker import Slacker
import subprocess
from chat_bot_server_dir.project_parser import project_parser
# from server_dir.slack_message_sender import send_channel_message
from server_dir.slack_message_sender import send_all_user_message
from server_dir.slack_message_sender import send_direct_message
from server_dir.user_database import user_database
from chat_bot_server_dir import work_database
from chat_bot_server_dir.user_intent_classifier.intent_classifier import extract_attention_word
from chat_bot_server_dir.sentence_process_logic import sentence_processing_main

print("hi")
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

# add_ignore = []
# project_structure = project_parser('UCNLP', 'conflict_test')

def make_shell_list(file):
    f = open(file,"rt",encoding="UTF8")
    text = f.read()
    text = text.split("\n")

    return text

# add_ignore = make_shell_list(os.path.join(os.path.pardir,"situation_shell","goadd_ignore.txt"))

# Slack Definition
channel = '#code-conflict-chatbot'
user_git = dict()
user_slack = dict()
user_list = list()

# find slack user's name
def get_slack_display_name(id):
    try:
        # Get users list
        response = slack.users.list()
        users = response.body['members']
        for user in users:
            if not user['deleted'] and user['id'] == id:
                if user.get('profile').get('display_name') != '':
                    return user.get('profile').get('display_name')
                else:
                    return user.get('profile').get('real_name')
    except KeyError as ex:
        print('Invalid key : %s' % str(ex))

def get_slack_name_list():
    try:
        user_list = list()
        # Get users list
        response = slack.users.list()
        users = response.body['members']
        for user in users:
            if user.get('profile').get('display_name') != '':
                user_list.append(user.get('profile').get('display_name'))
            else:
                user_list.append(user.get('profile').get('real_name'))
    except KeyError as ex:
        print('Invalid key : %s' % str(ex))
    return user_list

slack_name_list = get_slack_name_list()

def message_processing(msg):
    # Message Type is message
    if msg['type'] == 'message' or msg['type'] == "interactive_message":

        # Message Content Convert
        rand_text = msg['text']

        # Verifying User : Detect Hash Number
        if(rand_text.isdigit() and (len(rand_text) == 5)):
            w_db = user_database("parent")
            w_db.set_slack_id_code(random_number=rand_text,
                                   slack_id=get_slack_display_name(msg['user']),
                                   slack_code=msg['user'])
            w_db.close()
        elif msg['channel'] == 'CBNKGMWBH':
            if (("Sayme" in msg['text']) or ("<@UCKJC17HT1>" in msg['text'])): # Sayme slack code : "UBP8LHJS1" / Sayme2 slack code : "UCKJC17HT"
                u_db = user_database("parent")
                user_git_id = u_db.convert_slack_code_to_git_id(msg['user'])
                user_slack_code = msg['user']
                print("channel : ", user_slack_code, user_git_id)

                w_db = work_database.work_database()
                repository_name = w_db.get_repository_name(user_slack_code)
                owner_name = repository_name.split('/')[0]
                project_name = repository_name.split('/')[1]
                project_name = project_name[:-4]
                w_db.close()

                # Sentence Processing logic
                if msg['type'] == 'message':
                    intent_type, return_param0, return_param1, return_param2 = extract_attention_word(owner_name, project_name, rand_text, user_git_id, -1, msg['type'])
                elif msg['type'] == 'interactive_message':
                    intent_type, return_param0, return_param1, return_param2 = extract_attention_word(owner_name, project_name, rand_text, user_git_id, msg['intent_type'], msg['type'])


                return_message = sentence_processing_main(intent_type, user_slack_code, return_param0, return_param1, return_param2)

                print("return message : " + str(return_message))
                # send_channel_message("code-conflict-chatbot", return_message)
                send_all_user_message(message=return_message)

            else:
                pass


        # Sentence Processing
        else:
            if msg['user'] != "UCKJC17HT":  # Sayme slack code : "UBP8LHJS1" / Sayme2 slack code : "UCKJC17HT"
                # Search Git id
                u_db = user_database("parent")
                w_db = work_database.work_database()

                w_db.insert_last_connection(msg['user'])

                user_git_id = u_db.convert_slack_code_to_git_id(msg['user'])
                user_slack_code = msg['user']
                print("user : ", user_slack_code, user_git_id)

                # Sentence Processing logic
                repository_name = w_db.get_repository_name(user_slack_code)
                owner_name = repository_name.split('/')[0]
                project_name = repository_name.split('/')[1]
                project_name = project_name[:-4]
                print(owner_name, project_name)

                if msg['type'] == 'message':
                    intent_type, return_param0, return_param1, return_param2 = extract_attention_word(owner_name, project_name, rand_text, user_git_id, -1, msg['type'])
                elif msg['type'] == 'interactive_message':
                    intent_type, return_param0, return_param1, return_param2 = extract_attention_word(owner_name, project_name, rand_text, user_git_id, msg['intent_type'], msg['type'])


                return_message = sentence_processing_main(intent_type, user_slack_code, return_param0, return_param1, return_param2)

                # BASE_PATH = os.path.pardir
                # delete_path = os.path.join(BASE_PATH, owner_name)
                #
                # # windows
                # # cmd_line = 'rmdir /S /Q ' + root_dir_temp
                #
                # # linux
                # cmd_line = 'rm -rf ' + delete_path
                #
                # print("delete_path : ", delete_path)
                #
                # subprocess.check_output(cmd_line, shell=True)


                print("return message : " + str(return_message))
                # Send the message to user

                send_direct_message(user_slack_code, return_message)
                w_db.close()
                u_db.close()

            else:
                pass

# Message Entered on Slack
def on_message(ws, message):

    # JSON Data To Message
    msg_json = json.loads(message)
    print(msg_json)

    owner_name = " "
    project_name = " "

    # Import User Data
    message_processing(msg_json)

def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        time.sleep(1)

    _thread.start_new_thread(run, ())


if __name__ == "__main__":
    print("main")
    # nltk.download('punkt')
    # nltk.download('wordnet')
    #
    # tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    res = slack.auth.test().body

    msg = [{
        'fallback': res['user'] + ' is LOG-IN!',
        'pretext': '*Connected to ' + res['team'] + '(' + channel + ')*',
        'text': 'Hello! I\'m Sayme. \nIf you need me, please call me with @Sayme first.',
        'color': '#36a64f',
        'mrkdwn_in': ['pretext']
    }]

    slack.chat.post_message(channel, '', attachments=msg, as_user=True)
    response = slack.rtm.start()
    endpoint = response.body['url']
    ws = websocket.WebSocketApp(endpoint, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()