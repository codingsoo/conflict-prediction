from slacker import Slacker
import json

# Read token data
with open('..\\token.json', 'r') as token_file:
    token_file_json = json.load(token_file)

token = token_file_json['token']
slack = Slacker(token)


# Get user slack id
def get_user_slack_id():
    pass
    return


# def send_first_conflict(git_id, conflict_project, conflict_file, conflict_logic, ):


# Put channel name and message for sending chatbot message
def send_channel_message(channel, message):
    attachments_dict = dict()
    attachments_dict['text'] = "%s" % (message)
    attachments_dict['mrkdwn_in'] = ["text", "pretext"]
    attachments = [attachments_dict]
    slack.chat.post_message(channel="#" + channel, text=None, attachments=attachments, as_user=True)
    return


# Put user slack id and message for sending chatbot message
def send_direct_message(user_id, message):
    attachments_dict = dict()
    attachments_dict['pretext'] = "%s" % (message)
    attachments_dict['mrkdwn_in'] = ["text", "pretext"]
    attachments = [attachments_dict]
    slack.chat.post_message(channel="" + user_id, text=None, attachments=attachments, as_user=True)
    return


# if __name__ == "__main__":
#     send_channel_message("code-conflict-chatbot", "Channel output test")
#     send_direct_message("UBSUW48AX", "DM output test")