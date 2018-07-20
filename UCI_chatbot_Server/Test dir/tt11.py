# import os
# from datetime import datetime
# from slackclient import SlackClient
#
# channel = 'CBNKGMWBH'
#
# token = ''
# sc = SlackClient(token)
#
# history = sc.api_call("channels.history", channel=channel)
#
# print(history)

import subprocess

raw = str(subprocess.check_output('git ls-files -m', shell=True))

print(raw)