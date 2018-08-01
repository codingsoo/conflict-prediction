from slacker import Slacker
import websocket
import thread
import time
import json
import random

add_ignore = []

def make_shell_list(file):
    f = open(file,"r")
    text = f.read()
    text = text.split("\n")

    return text

add_ignore = make_shell_list('./situation_shell/add_ignore.txt')
print add_ignore

# Slack Definition
channel = '#code-conflict-chatbot'
token = ''
slack = Slacker(token)

user_git = dict()
user_slack = dict()

# User List Data
user_list = list()

# find slack user's name
def list_slack(id):
    try:
        slack = Slacker(token)

        # Get users list
        response = slack.users.list()
        users = response.body['members']
        for user in users:
            if not user['deleted'] and user['id'] == id:
                print user
                # print(user['id'], user['name'], user['is_admin'], user['is_owner'])
                return user['display_name_normalized']
    except KeyError as ex:
        print('Invalid key : %s' % str(ex))

# Message Entered on Slack
def on_message(ws, message):

    # JSON Data To Message
    msg = json.loads(message)

    # log
    print(msg)

    # Import User Data

    # Message Type is message
    if msg['type'] == 'message':

        # Message Content Convert
        ran_text = str(msg['text'])

        chatting_word = dict()

        chatting_word['NP'] = 'No Problem'
        chatting_word['np'] = 'No Problem'

        rand_text = ''

        for word in ran_text.split(' '):
            if len(word) <=4 and word in chatting_word:
                rand_text = rand_text + chatting_word[word] + ' '
            else:
                rand_text = rand_text + word + ' '

        print do_punctuate(rand_text)

        # Detect Hash Number
        if(rand_text.isdigit() and (len(rand_text) == 5)):
            with open('./user_data/user_git.json', 'r') as f1, open('./user_data/user_slack.json','r') as f2:
                user_git = json.load(f1)
                user_slack = json.load(f2)
                # Search User Register

                for git_user in user_git.keys():
                    # Slack id == RandomNumber ####
                    if str(user_git[git_user]) == rand_text:
                        # random number convert user id
                        # user_list[count]['slack_id'] = msg['user']
                        user_name = list_slack(msg['user'])
                        user_slack[msg['user']] = user_name
                        user_git[git_user] = user_name
                #
                #         # Save User Data Json file
            with open('./user_data/user_git.json', 'w') as make_file1, open('./user_data/user_slack.json', 'w') as make_file2:
                json.dump(user_git, make_file1)
                json.dump(user_slack, make_file2)

        elif '.py' in rand_text:
            for py_file in rand_text.split(' '):
                if '.py' in py_file:
                    approved_list = []
                    with open('./user_data/approved_list.json', 'r') as f:
                        approved_list = json.load(f)

                    approved_list.append(py_file)
                    attachments_dict = dict()
                    attachments_dict['text'] = add_ignore[random.randint(0, len(add_ignore)-1)] % (py_file)
                    attachments_dict['mrkdwn_in'] = ["text", "pretext"]
                    attachments = [attachments_dict]

                    slack.chat.post_message(channel="#code-conflict-chatbot", text=None, attachments=attachments, as_user=True)

                    with open('./user_data/approved_list.json', 'w') as f:
                        json.dump(approved_list,f)
                    break

def on_error(ws, error):
    print error


def on_close(ws):
    print "### closed ###"


def on_open(ws):
    def run(*args):
        time.sleep(1)

    thread.start_new_thread(run, ())
get_severe_shell = make_shell_list('./situation_shell/get_severe.txt')
approved_shell = make_shell_list('./situation_shell/approved.txt')
notify_conflict_shell = make_shell_list('./situation_shell/go_to_same_file.txt')

#### MAIN ####

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

# websocket.enableTrace(True)
ws = websocket.WebSocketApp(endpoint, on_message=on_message, on_error=on_error, on_close=on_close)
ws.on_open = on_open
ws.run_forever()
