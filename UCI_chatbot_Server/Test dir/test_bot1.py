from slacker import Slacker
import websocket
import thread
import time
import json

rand_set = set()

channel = '#code-conflict-chatbot'
CMDCHAR = '?'

CMD_LIST = ['work', 'home', 'cal']

token = 'xoxb-151102038320-397292596885-Nv3wRxgdo5DNbwM29yjXQgMd'

slack = Slacker(token)

# User List Data
user_list = list()

def on_message(ws, message):
    msg = json.loads(message)
    print(msg)

    # Import User Data
    with open('../user_data/user.json', 'r') as f:
        user_list = json.load(f)['user']
        print(user_list)

    if msg['type'] == 'message':

        rand_text = str(msg['text'])

        if(rand_text.isdigit() and (len(rand_text) == 5)):

            count = 0

            for user in user_list:
                if(str(user['slack_id']) == rand_text):
                    user_list[count]['slack_id'] = msg['user']

                    json_dict = dict()
                    json_dict['user'] = user_list

                    # Save User Data Json file
                    with open('../user_data/user.json', 'w') as make_file:
                        json.dump(json_dict, make_file)

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