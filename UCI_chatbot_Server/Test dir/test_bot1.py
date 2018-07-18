# Import Library
from slacker import Slacker
import websocket
import thread
import time
import json

# Slack Definition
channel = '#code-conflict-chatbot'
token = ''
slack = Slacker(token)
CMDCHAR = '?'
CMD_LIST = ['work', 'home', 'cal']

# User List Data
user_list = list()


# Message Entered on Slack
def on_message(ws, message):

    # JSON Data To Message
    msg = json.loads(message)

    # log
    print(msg)

    # Import User Data
    with open('../user_data/user.json', 'r') as f:
        user_list = json.load(f)['user']
        print(user_list)

    # Message Type is message
    if msg['type'] == 'message':

        # Message Content Convert
        rand_text = str(msg['text'])

        # Detect Hash Number
        if(rand_text.isdigit() and (len(rand_text) == 5)):

            # List Index
            count = 0

            # Search User Register
            for user in user_list:

                # Slack id == RandomNumber
                if(str(user['slack_id']) == rand_text):

                    # random number convert user id
                    user_list[count]['slack_id'] = msg['user']

                    json_dict = dict()
                    json_dict['user'] = user_list

                    # Save User Data Json file
                    with open('../user_data/user.json', 'w') as make_file:
                        json.dump(json_dict, make_file)

                # Next user
                count += 1

def on_error(ws, error):
    print error


def on_close(ws):
    print "### closed ###"


def on_open(ws):
    def run(*args):
        time.sleep(1)

    thread.start_new_thread(run, ())


#### MAIN ####



res = slack.auth.test().body


msg = [{
    'fallback': res['user'] + ' is LOG-IN!',
    'pretext': '*Connected to ' + res['team'] + '(' + channel + ')*',
    'text': 'bot Usage : ' + CMDCHAR + '{' + ','.join(CMD_LIST) + '}\nbot Help : ' + CMDCHAR + 'help',
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