# 1. Generate Random Number
# 2. Print Random Number
# 3. Enter Random Number on Slack
# 4. User


# Import Library
import requests
from collections import OrderedDict
import subprocess

# Verifying User
def verifyingUser():

    # Get User email
    json_email = getUserEmail()

    # Get Random Number
    rand_num = int(postToServer(uri="/createRandom", json_data="create"))

    # Print Input Random Number to Slack
    print("Enter Random Number to Slack: " + rand_num)

    return

# Get User Email():
def getUserEmail():

    # Get User git Email Using subprocess
    raw = str(subprocess.check_output('git config user.email', shell=True))

    # String processing
    temp_list = raw.replace('b\'', '')
    temp_list = temp_list.replace('\\n', '')
    temp_list = temp_list.replace('\\', '')
    temp_list = temp_list.replace('\'', '')

    # Create JSON
    json_data = OrderedDict()
    json_data["email"] = temp_list

    return json_data

# Post To Server
def postToServer(uri, json_data):

    # IP Address
    ip_addr = "127.0.0.1"

    # Create URL
    url = "http://" + ip_addr + ":5009" + uri

    # Headers
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    # Post To Server
    req = requests.post(url, data = json_data, headers=headers)

    # Log
    print(req)
    print(req.status_code)

    return


# Command : git diff
def commandGitDiff():
    return

# Command : git ls-files -m
def commandGitLsFiles():
    return

# MAIN
if __name__ == "__main__":

    # Start
    print("CHATBOT Client Start!")

