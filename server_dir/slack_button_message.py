# from flask import Flask, request, make_response, Response
# import os
# import json
#
# from slackbot.slackclient import SlackClient
#
# # Your app's Slack bot user token
# SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
# SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
#
# # Slack client for Web API requests
# slack_client = SlackClient(SLACK_BOT_TOKEN)
#
# # Flask webserver for incoming traffic from Slack
# app = Flask(__name__)
#
# # Helper for verifying that requests came from Slack
# def verify_slack_token(request_token):
#     if SLACK_VERIFICATION_TOKEN != request_token:
#         print("Error: invalid verification token!")
#         print("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
#         return make_response("Request contains invalid Slack verification token", 403)
#
#
# # The endpoint Slack will load your menu options from
# @app.route("/slack/message_options", methods=["POST"])
# def message_options():
#     # Parse the request payload
#     form_json = json.loads(request.form["payload"])
#
#     # Verify that the request came from Slack
#     verify_slack_token(form_json["token"])
#
#     # Dictionary of menu options which will be sent as JSON
#     menu_options = {
#         "options": [
#             {
#                 "text": "Cappuccino",
#                 "value": "cappuccino"
#             },
#             {
#                 "text": "Latte",
#                 "value": "latte"
#             }
#         ]
#     }
#
#     # Load options dict as JSON and respond to Slack
#     return Response(json.dumps(menu_options), mimetype='application/json')
#
#
# # The endpoint Slack will send the user's menu selection to
# @app.route("/slack/message_actions", methods=["POST"])
# def message_actions():
#     # Parse the request payload
#     form_json = json.loads(request.form["payload"])
#     print("form_json", form_json)
#
#     # Verify that the request came from Slack
#     verify_slack_token(form_json["token"])
#
#     # Check to see what the user's selection was and update the message accordingly
#     selection = form_json["actions"][0]["value"]
#
#     response = slack_client.send_message(
#       channel=form_json["channel"]["id"],
#       message="One {}, right coming up!".format(selection)
#     )
#
#     # Send an HTTP 200 response with empty body so Slack knows we're done here
#     return make_response("", 200)
#
# # Send a Slack message on load. This needs to be _before_ the Flask server is started
#
# # A Dictionary of message attachment options
#
# attachments_json = [
#     {
#         "fallback": "Upgrade your Slack client to use messages like these.",
#         "color": "#3AA3E3",
#         "attachment_type": "default",
#         "callback_id": "menu_options_2319",
#         "actions": [
#             {
#                 "name": "bev_list",
#                 "text": "sooyoung",
#                 # "type":"select",
#                 # "data_source":"external"
#
#                 "type": "button",
#                 "value":"2"
#             },
# {
#                 "name": "bev_list",
#                 "text": "seonkyu",
#                 # "type":"select",
#                 # "data_source":"external"
#
#                 "type": "button",
#                 "value" : "3"
#             }
#         ]
#     }
# ]
#
# # Send a message with the above attachment, asking the user if they want coffee
# slack_client.send_message(channel=""+"UCFNMU2EM", message="Would you like some coffee? :coffee:",attachments=attachments_json)
#
#
# # def send_button_message(slack_code, file_simp_path_list):
# #     attachments_dict = dict()
# #     actions = []
# #     message = ""
# #     for fspl_idx, fspl in enumerate(file_simp_path_list):
# #         message += "%d. %s\n" % (fspl_idx + 1, fspl)
# #         actions_dict = dict()
# #         actions_dict['name'] = "file"
# #         actions_dict['text'] = fspl_idx + 1
# #         actions_dict['type'] = "button"
# #         actions_dict['value'] = fspl
# #         actions.append(actions_dict)
# #
# #     attachments_dict['text'] = "%s" % (message)
# #     attachments_dict['fallback'] = "You are unable to choose a file."
# #     attachments_dict['callback_id'] = "same_named_file"
# #     attachments_dict['attachment_type'] = "warning"
# #     attachments_dict['actions'] = actions
# #     attachments_dict['color'] = "#3AA3E3"
# #     attachments = [attachments_dict]
# #
# #     slack_client.send_message(channel="" + slack_code, message="Which file do you mean?", attachments=attachments, as_user=True)
# #
# #     # response = slack.rtm.start()
# #     # endpoint = response.body['url']
# #     # ws2 = websocket.create_connection("wss://sdcl.slack.com/messages/DCMPEV15L/slack/message_actions")
# #     # print("start loop")
# #     # while True:
# #     #     event = json.loads(ws2.recv())
# #     #     print("event", event)
# #     #     if event.get('type') != "message" or event.get('user') != slack_code:
# #     #         continue
# #     #     ws2.close()
# #     #     break
# #
# #     return
#
#
# # Start the Flask server
# if __name__ == "__main__":
#     app.run(port=4000)

#
# from slackeventsapi import SlackEventAdapter
# from slackbot.slackclient import SlackClient
# import os
#
# # Our app's Slack Event Adapter for receiving actions via the Events API
# slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
# slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")
#
# # Create a SlackClient for your bot to use for Web API requests
# slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
# slack_client = SlackClient(slack_bot_token)
#
# # Example responder to greetings
# @slack_events_adapter.on("message")
# def handle_message(event_data):
#     message = event_data["event"]
#     # If the incoming message contains "hi", then respond with a "Hello" message
#     if message.get("subtype") is None and "hi" in message.get('text'):
#         channel = message["channel"]
#         message = "Hello <@%s>! :tada:" % message["user"]
#         slack_client.api_call("chat.postMessage", channel=channel, text=message)
#
#
# # Example reaction emoji echo
# @slack_events_adapter.on("reaction_added")
# def reaction_added(event_data):
#     event = event_data["event"]
#     emoji = event["reaction"]
#     channel = event["item"]["channel"]
#     text = ":%s:" % emoji
#     slack_client.api_call("chat.postMessage", channel=channel, text=text)
#
# # Error events
# @slack_events_adapter.on("error")
# def error_handler(err):
#     print("ERROR: " + str(err))
#
# # Once we have our event listeners configured, we can start the
# # Flask server with the default `/events` endpoint on port 3000
# slack_events_adapter.start(port=4000)


from flask import Flask, request, make_response, Response
import os
import json
from slackeventsapi import SlackEventAdapter
from slackbot.slackclient import SlackClient
from server_dir.slack_message_sender import get_slack
# Flask webserver for incoming traffic from Slack
app = Flask(__name__)

# Our app's Slack Event Adapter for receiving actions via the Events API
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events", app)

# Our app's Slack bot user token
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]

# Slack client for Web API requests
slack_client = SlackClient(SLACK_BOT_TOKEN)
slack = get_slack()

# Helper for verifying that requests came from Slack
def verify_slack_token(request_token):
    if SLACK_VERIFICATION_TOKEN != request_token:
        print("Error: invalid verification token!")
        print("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
        return make_response("Request contains invalid Slack verification token", 403)

# Error events
@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))

# The endpoint Slack will send the user's menu selection to
@app.route("/slack/message_actions", methods=["POST"])
def message_actions():
    # Parse the request payload
    btmsg_json = json.loads(request.form["payload"])
    print("btmsg_json", btmsg_json)

    # Verify that the request came from Slack
    verify_slack_token(btmsg_json["token"])

    # Check to see what the user's selection was and update the message accordingly
    selected_file = btmsg_json["actions"][0]["value"]
    print("selected_file", selected_file)

    msg_json = json_parsing(btmsg_json, selected_file)
    print("msg_json", msg_json)

    slack.chat.update(
        channel = btmsg_json["channel"]["id"],
        text=btmsg_json["original_message"]["text"],
        ts=btmsg_json["message_ts"],
        attachments=[{"text":btmsg_json["original_message"]["attachments"][0]["text"]+":white_check_mark: Ok!",
                      "color":"#3AA3E3"}]
    )
    from chat_bot_server_dir.bot_server import message_processing
    message_processing(msg_json)
    # from chat_bot_server_dir.bot_server import message_processing

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

# Send a Slack message on load. This needs to be _before_ the Flask server is started
def send_button_message(slack_code, file_simp_path_list, sentence, intent_type):
    attachments_dict = dict()
    actions = []
    message = ""
    for fspl_idx, fspl in enumerate(file_simp_path_list):
        message += "%d. %s\n" % (fspl_idx + 1, fspl)
        actions_dict = dict()
        actions_dict['name'] = sentence
        actions_dict['text'] = fspl_idx + 1
        actions_dict['type'] = "button"
        actions_dict['value'] = fspl
        actions.append(actions_dict)

    attachments_dict['text'] = "%s" % (message)
    attachments_dict['fallback'] = "You are unable to choose a file."
    attachments_dict['callback_id'] = intent_type
    attachments_dict['attachment_type'] = "warning"
    attachments_dict['actions'] = actions
    attachments_dict['color'] = "#3AA3E3"
    attachments = [attachments_dict]

    slack.chat.post_message(channel="" + slack_code, text="Which file do you mean?", attachments=attachments, as_user=True)


    # slack = Slacker("SLACK_BOT_TOKEN")
    # response = slack.rtm.start()
    # endpoint = response.body['url']
    # ws2 = websocket.create_connection("ws://localhost:4000")
    # print("start loop")
    # while True:
    #     event = json.loads(ws2.recv())
    #     print("event", event)
    #     if event.get('type') != "message" or event.get('user') != slack_code:
    #         continue
    #     ws2.close()
    #     break

if __name__ == "__main__":
    # slack_events_adapter.start(port=4000)
    app.run(port=4000)


# from flask import Flask, request, make_response, Response
# import os
# import json
# from slackeventsapi import SlackEventAdapter
# from slackbot.slackclient import SlackClient
# import websocket
# from slacker import Slacker
#
# # Flask webserver for incoming traffic from Slack
# app = Flask(__name__)
#
# # Our app's Slack Event Adapter for receiving actions via the Events API
# slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
# slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events", app)
#
# # Our app's Slack bot user token
# SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
# SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
#
# # Slack client for Web API requests
# slack_client = SlackClient(SLACK_BOT_TOKEN)
#
# # # Helper for verifying that requests came from Slack
# # def verify_slack_token(request_token):
# #     if SLACK_VERIFICATION_TOKEN != request_token:
# #         print("Error: invalid verification token!")
# #         print("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
# #         return make_response("Request contains invalid Slack verification token", 403)
# #
# # # Error events
# # @slack_events_adapter.on("error")
# # def error_handler(err):
# #     print("ERROR: " + str(err))
# #
# # # The endpoint Slack will send the user's menu selection to
# @app.route("/slack/message_actions", methods=["POST"])
# def message_actions():
#     # Parse the request payload
#     form_json = json.loads(request.form["payload"])
#     print("form_json", form_json)
#
#     # Verify that the request came from Slack
#     verify_slack_token(form_json["token"])
#
#     # Check to see what the user's selection was and update the message accordingly
#     selection = form_json["actions"][0]["value"]
#
#     response = slack_client.send_message(
#       channel=form_json["channel"]["id"],
#       message="One {}, right coming up!".format(selection)
#     )
#
#     # Send an HTTP 200 response with empty body so Slack knows we're done here
#     return make_response("", 200)
#
#
# # Send a Slack message on load. This needs to be _before_ the Flask server is started
# def send_button_message(slack_code, file_simp_path_list):
#     attachments_dict = dict()
#     actions = []
#     message = ""
#     for fspl_idx, fspl in enumerate(file_simp_path_list):
#         message += "%d. %s\n" % (fspl_idx + 1, fspl)
#         actions_dict = dict()
#         actions_dict['name'] = "file"
#         actions_dict['text'] = fspl_idx + 1
#         actions_dict['type'] = "button"
#         actions_dict['value'] = fspl
#         actions.append(actions_dict)
#
#     attachments_dict['text'] = "%s" % (message)
#     attachments_dict['fallback'] = "You are unable to choose a file."
#     attachments_dict['callback_id'] = "same_named_file"
#     attachments_dict['attachment_type'] = "warning"
#     attachments_dict['actions'] = actions
#     attachments_dict['color'] = "#3AA3E3"
#     attachments = [attachments_dict]
#
#     slack_client.send_message(channel="" + slack_code, message="Which file do you mean?", attachments=attachments, as_user=True)
#
#     slack = Slacker("SLACK_BOT_TOKEN")
#     response = slack.rtm.start()
#     endpoint = response.body['url']
#     ws2 = websocket.create_connection("wss://f377a0e4.ngrok.io/slack/events:4000")
#     print("start loop")
#     while True:
#         event = json.loads(ws2.recv())
#         print("event", event)
#         if event.get('type') != "message" or event.get('user') != slack_code:
#             continue
#         ws2.close()
#         break
#
#
#     return
#
#
# if __name__ == "__main__":
# #     # slack_events_adapter.start(port=4000)
#     app.run(port=4000)