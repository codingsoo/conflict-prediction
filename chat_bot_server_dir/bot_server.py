from slacker import Slacker
import websocket
import time
import json
import random
import _thread
import os
import configparser
from chat_bot_server_dir.user_intent_classifier.sentence_type_finder import require_something_sentence
from chat_bot_server_dir.project_parser import project_parser
from server_dir.slack_message_sender import send_channel_message
from server_dir.slack_message_sender import send_direct_message
import nltk
from server_dir.user_database import user_database
from pathlib import Path
from chat_bot_server_dir.user_intent_classifier.intent_classifier import extract_attention_word
from chat_bot_server_dir.sentence_process_logic import sentence_processing_main

def load_token() :
    file_path = os.path.join(Path(os.getcwd()).parent, "all_server_config.ini")

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
slack = Slacker(token)

# add_ignore = []
project_structure = project_parser('UCNLP', 'client')

def make_shell_list(file):
    f = open(file,"rt",encoding="UTF8")
    text = f.read()
    text = text.split("\n")

    return text

# add_ignore = make_shell_list(os.path.join(os.path.pardir,"situation_shell","add_ignore.txt"))

# Slack Definition
channel = '#code-conflict-chatbot'

user_git = dict()
user_slack = dict()

# User List Data
user_list = list()

# find slack user's name
def get_slack_display_name(id):
    try:
        # Get users list
        response = slack.users.list()
        users = response.body['members']
        for user in users:
            if not user['deleted'] and user['id'] == id:
                # print(user)
                # print(user['id'], user['name'], user['is_admin'], user['profile']['display_name'])
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

# Message Entered on Slack
def on_message(ws, message):

    # JSON Data To Message
    msg = json.loads(message)
    print(msg)

    # Import User Data

    # Message Type is message
    if msg['type'] == 'message':

        # Message Content Convert

        rand_text = msg['text']

        # Verifying User : Detect Hash Number
        if(rand_text.isdigit() and (len(rand_text) == 5)):
            w_db = user_database()
            w_db.set_slack_id_code(random_number=rand_text,
                                   slack_id=get_slack_display_name(msg['user']),
                                   slack_code=msg['user'])

        # Sentence Processing
        else:
            if msg['user'] != "UBP8LHJS1":
                # Search Git id
                u_db = user_database()
                user_git_id = u_db.convert_slack_code_to_git_id(msg['user'])
                user_slack_id = msg['user']
                print("print_user_id : ", user_slack_id, user_git_id)

                # Sentence Processing logic

                intent_type, return_param0, return_param1, return_param2 = extract_attention_word(rand_text, user_git_id)
                return_message = sentence_processing_main(intent_type, user_slack_id, return_param0, return_param1, return_param2)

                # Send the message to user
                if(return_message != "message" and msg['channel'] != 'CBNKGMWBH'):
                    send_direct_message(user_slack_id, return_message)
                elif(("Sayme" in msg['text']) or ("<@UBP8LHJS1>" in msg['text']) and msg['channel'] == 'CBNKGMWBH'):
                    send_channel_message("code-conflict-chatbot", return_message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        time.sleep(1)

    _thread.start_new_thread(run, ())


if __name__ == "__main__":
    #nltk.download('punkt')
    #nltk.download('wordnet')

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    res = slack.auth.test().body

    msg = [{
        'fallback': res['user'] + ' is LOG-IN!',
        'pretext': '*Connected to ' + res['team'] + '(' + channel + ')*',
        'text': 'Hello! I\'m Sayme. \nIf you need me, please call me with @Sayme first.',
        'color': '#36a64f',
        'mrkdwn_in': ['pretext']
    }]

    slack.chat.post_message(channel, '', attachments=msg, as_user=True)
    print("slack chat")
    response = slack.rtm.start()
    print("response")
    endpoint = response.body['url']
    print("endpoint")
    ws = websocket.WebSocketApp(endpoint, on_message=on_message, on_error=on_error, on_close=on_close)
    print("ws")
    ws.on_open = on_open
    print("we.on_open")
    ws.run_forever()
    print("ws.run_forever")
