import os
import json
import configparser
from pathlib import Path
from slacker import Slacker
from flask import Flask, request, make_response
from slackeventsapi import SlackEventAdapter
from slackbot.slackclient import SlackClient

def get_slack():
    bot_token = verification_token = signing_secret = ''
    file_path = os.path.join(Path(os.getcwd()).parent, "all_server_config.ini")
    if not os.path.isfile(file_path):
        print("ERROR :: There is no server_config.ini")
        exit(2)
    else:
        config = configparser.ConfigParser()
        config.read(file_path)
        try:
            bot_token = config['SLACK']['TOKEN']
            verification_token = config['SLACK']['VERIFICATION_TOKEN']
            signing_secret = config['SLACK']['SIGNING_SECRET']
        except:
            print("ERROR :: It is server_config.ini")
            exit(2)
    return bot_token, verification_token, signing_secret

# Helper for verifying that requests came from Slack
def verify_slack_token(request_token):
    if SLACK_VERIFICATION_TOKEN != request_token:
        print("Error: invalid verification token!")
        print("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
        return make_response("Request contains invalid Slack verification token", 403)


# Flask webserver for incoming traffic from Slack
app = Flask(__name__)
SLACK_BOT_TOKEN, SLACK_VERIFICATION_TOKEN, SLACK_SIGNING_SECRET = get_slack()

# Our app's Slack Event Adapter for receiving actions via the Events API
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)

# Slack client for Web API requests
slack_client = SlackClient(SLACK_BOT_TOKEN)
slack = Slacker(SLACK_BOT_TOKEN)


# Error events
@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))


# The endpoint Slack will send the user's menu selection to
@app.route("/slack/message_actions", methods=['POST'])
def message_actions():
    # Parse the request payload
    btmsg_json = json.loads(request.form['payload'])
    print("btmsg_json", btmsg_json)

    # Verify that the request came from Slack
    verify_slack_token(btmsg_json['token'])
    request_type = btmsg_json['original_message']['attachments'][0]['title']

    # Lock Request button message
    if request_type == 'Lock Request':
        selected_type = btmsg_json['actions'][0]['name']
        file_name = btmsg_json['callback_id']
        lock_time = int(btmsg_json['actions'][0]['value'])
        slack_code = btmsg_json['user']['id']
        print("slack_code", slack_code)
        if selected_type == "YES":
            slack.chat.update(
                channel=btmsg_json['channel']['id'],
                text=None,
                ts=btmsg_json['message_ts'],
                attachments=[{'title': "Lock Request",
                              'text': ":white_check_mark: Locking *{}* is completed.".format(file_name),
                              'color': "good"}]
            )
        else:
            slack.chat.update(
                channel=btmsg_json['channel']['id'],
                text=None,
                ts=btmsg_json['message_ts'],
                attachments=[{'title': "Lock Request",
                              'text': ":white_check_mark: Ok. I'll not lock *{}*".format(file_name),
                              'color': "good"}]
            )
        from chat_bot_server_dir.sentence_process_logic import lock_response_logic
        lock_response_logic(slack_code=slack_code,
                            msg_type=selected_type,
                            target_file=file_name,
                            lock_time=lock_time)

    # File selection button message
    elif request_type == 'Which file do you mean?':
        # Check to see what the user's selection was and update the message accordingly

        # callback_id : intent_type /  value : conflict_test/ClassA.py  / name : sentence  / text : 1
        selected_file = btmsg_json['actions'][0]['value']
        print('selected_file', selected_file)

        msg_json = json_parsing(btmsg_json, selected_file)
        print('msg_json', msg_json)

        slack.chat.update(
            channel=btmsg_json['channel']['id'],
            text=btmsg_json['original_message']['text'],
            ts=btmsg_json['message_ts'],
            attachments=[{'title': "Which file do you mean?",
                          'text': btmsg_json['original_message']['attachments'][0]['text']+"\n:white_check_mark: Ok!",
                          'color':"#3AA3E3"}]
        )
        from chat_bot_server_dir.bot_server import message_processing
        message_processing(msg_json)

    # Send an HTTP 200 response with empty body so Slack knows we're done here
    return make_response("", 200)


def json_parsing(btmsg_json, selected_file):
    msg_json = dict()
    msg_json['type'] = 'interactive_message'
    msg_json['user'] = btmsg_json['user']['id']
    sentence = btmsg_json['actions'][0]['name']
    print("before sentence", sentence)
    ordinary_file = ""
    word_list = sentence.split()
    for word in word_list:
        if ".py" in word:
            ordinary_file = word
    sentence = sentence.replace(ordinary_file, selected_file)
    print("sentence", sentence)
    msg_json['text'] = sentence
    msg_json['channel'] = btmsg_json['channel']['id']
    msg_json['intent_type'] = btmsg_json['callback_id']
    return msg_json

if __name__ == "__main__":
    app.run(port=8000)

