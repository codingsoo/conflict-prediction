import os
from datetime import datetime
from slackclient import SlackClient

channel = 'CBNKGMWBH'

token = ''
sc = SlackClient(token)

history = sc.api_call("channels.history", channel=channel)

print(history)