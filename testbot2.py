from slacker import Slacker
import websocket
import thread
import time
import json

channel = '#code-conflict-chatbot'
CMDCHAR='?'

token = 'xoxb-151102038320-397292596885-Gp3mK7Pi3XKaG770dKIThLXi'


slack = Slacker(token)


def on_message(ws, message):
	
	msg =  json.loads(message)

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    def run(*args):
        time.sleep(1)

    thread.start_new_thread(run, ())



res =  slack.auth.test().body

msg = [{
			'fallback':res['user']+' is LOG-IN!',
			'pretext':'*Connected to ' +res['team']+'('+channel+')*',
			'text':'bot Usage : ' + CMDCHAR + '{'+','.join(CMD_LIST)+'}\nbot Help : ' + CMDCHAR + 'help',
			'color':'#36a64f',
			'mrkdwn_in':['pretext']
		}]


slack.chat.post_message(channel,'',attachments=msg,as_user=True)


response = slack.rtm.start()
endpoint = response.body['url']


#websocket.enableTrace(True)
ws = websocket.WebSocketApp(endpoint,on_message = on_message, on_error = on_error,on_close = on_close)
ws.on_open = on_open
ws.run_forever()   
