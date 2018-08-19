from slacker import Slacker
import websocket
import time
import json
import random
import _thread
import os
import configparser
from chat_bot_server_dir.punctuator2.play_with_model import punctuator
from chat_bot_server_dir.punctuator2.play_with_model import model_loading
from chat_bot_server_dir.user_intent_classifier.intent_classifier import require_something_sentence
from chat_bot_server_dir.user_intent_classifier.intent_classifier_12case import give_intent_return_message
from chat_bot_server_dir.project_parser import project_parser
from server_dir.slack_message_sender import send_channel_message
from server_dir.slack_message_sender import send_direct_message
import nltk
from server_dir.user_database import user_database

def load_token() :
    if not os.path.isfile("bot_server_config.ini") :
        print("ERROR :: There is no bot_server_config.ini")
        exit(2)
    else :
        config = configparser.ConfigParser()
        config.read("bot_server_config.ini")
        try :
            token=config["SLACK"]["TOKEN"]
        except :
            print("ERROR :: It is bot_server_config.ini")
            exit(2)
    return token

token = load_token()
slack = Slacker(token)

add_ignore = []
project_structure = project_parser('UCNLP', 'client')

def make_shell_list(file):
    f = open(file,"rt",encoding="UTF8")
    text = f.read()
    text = text.split("\n")

    return text

add_ignore = make_shell_list(os.path.join(os.path.pardir,"situation_shell","add_ignore.txt"))

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
        try:
            rand_text = str(punctuator(msg['text'], model_list[0], model_list[1], model_list[2], model_list[3]))
        except:
            rand_text = msg['text']
        # Detect Hash Number
        if(rand_text.isdigit() and (len(rand_text) == 5)):
            w_db = user_database()
            w_db.set_slack_id_code(random_number=rand_text,
                                   slack_id=get_slack_display_name(msg['user']),
                                   slack_code=msg['user'])

        elif '.py' in rand_text:
            for py_file in rand_text.split(' '):
                if '.py' in py_file:
                    approved_list = []
                    with open('../user_data/approved_list.json', 'r') as f:
                        approved_list = json.load(f)

                    approved_list.append(py_file)
                    attachments_dict = dict()
                    attachments_dict['text'] = add_ignore[random.randint(0, len(add_ignore)-1)] % (py_file)
                    attachments_dict['mrkdwn_in'] = ["text", "pretext"]
                    attachments = [attachments_dict]

                    slack.chat.post_message(channel="#code-conflict-chatbot", text=None, attachments=attachments, as_user=True)

                    with open('../user_data/approved_list.json', 'w') as f:
                        json.dump(approved_list,f)
                    break

        else:
            content = tokenizer.tokenize(rand_text)
            for sentence in content:
                if require_something_sentence(sentence):
                    response = give_intent_return_message(sentence)
                    if response != None:
                        send_direct_message(msg["user"], response)
                    else:
                        response = chatbot.get_response(sentence)
                        send_direct_message(msg["user"], response)
                else:
                    try:
                        response = chatbot.get_response(sentence)
                        send_direct_message(msg["user"], response)
                    except:
                        pass

def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        time.sleep(1)

    _thread.start_new_thread(run, ())

get_severe_shell = make_shell_list(os.path.join(os.path.pardir,"situation_shell","get_severe.txt"))
approved_shell = make_shell_list(os.path.join(os.path.pardir,"situation_shell","approved.txt"))
notify_conflict_shell = make_shell_list(os.path.join(os.path.pardir,"situation_shell","go_to_same_file.txt"))

#### MAIN ####
nltk.download('punkt')
nltk.download('wordnet')
model_list = model_loading()
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

response = slack.rtm.start()
endpoint = response.body['url']

# print(project_structure)
# print(slack_name_list)

# websocket.enableTrace(True)
ws = websocket.WebSocketApp(endpoint, on_message=on_message, on_error=on_error, on_close=on_close)
ws.on_open = on_open
ws.run_forever()
