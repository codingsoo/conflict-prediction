# import subprocess
#
# temp = subprocess.check_output('dir', shell=True)
#
# print(temp)
import thread
import time
import json
from slacker import Slacker


channel = '#code-conflict-chatbot'
CMDCHAR = '?'

token = 'xoxp-151102038320-390002713766-398183694295-dd41aaa72fdb6ff69321cba698acf989'

slack = Slacker(token)

def on_message(ws, message):
    msg = json.loads(message)


def on_error(ws, error):
    print
    error


def on_close(ws):
    print
    "### closed ###"


def on_open(ws):
    def run(*args):
        time.sleep(1)

history = slack.channels.history(channel)
print(history)

# res = slack.auth.test().body
# print (res['user'])
#
# msg = [{
#     'fallback': res['user'] + ' is LOG-IN!',
#     'pretext': '*Connected to ' + res['team'] + '(' + channel + ')*',
#     'text': 'bot Usage : ' + CMDCHAR + 'bot Help : ' + CMDCHAR + 'help',
#     'color': '#36a64f',
#     'mrkdwn_in': ['pretext']
# }]

# slack.chat.post_message(channel, '', attachments=msg, as_user=True)

# response = slack.rtm.start()
# endpoint = response.body['url']
#
# # websocket.enableTrace(True)
# ws = websocket.WebSocketApp(endpoint, on_message=on_message, on_error=on_error, on_close=on_close)
# ws.on_open = on_open
# ws.run_forever()