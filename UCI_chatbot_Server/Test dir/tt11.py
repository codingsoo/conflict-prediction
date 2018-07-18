import os
from datetime import datetime
from slackclient import SlackClient

channel = 'CBNKGMWBH'

token = 'xoxp-151102038320-390002713766-398183694295-dd41aaa72fdb6ff69321cba698acf989'
sc = SlackClient(token)

history = sc.api_call("channels.history", channel=channel)

print(history)