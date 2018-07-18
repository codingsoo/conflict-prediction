# 1. Generate Random Number
# 2. Print Random Number
# 3. Enter Random Number on Slack
# 4. User


# Import Library
import requests
from collections import OrderedDict
import subprocess
import json

# Verifying User
def verifyingUser():

    # Get User email
    json_email = getUserEmail()

    # User Search
    user_flag = str(postToServer(uri="/userSearch", json_data=getUserEmail()))

    if(user_flag.isdigit()):

        # Print Input Random Number to Slack
        print("Enter Random Number to Slack : " + user_flag)

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
    json_data = dict()
    json_data["email"] = temp_list

    print(json_data)

    return str(json_data).replace('\'', '"', 4)

# Post To Server
def postToServer(uri, json_data):

    # IP Address
    ip_addr = "127.0.0.1"

    # Create URL
    url = "http://" + ip_addr + ":5009" + uri

    # Headers
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    # Post To Server
    req = requests.post(url, headers=headers, data = json_data)

    # Log
    print(req)
    print(req.status_code)

    return req


# Get To Server
def getToServer(uri, json_data):

    # IP Address
    ip_addr = "127.0.0.1"

    # Create URL
    url = "http://" + ip_addr + ":5009" + uri

    # Headers
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    # Post To Server
    req = requests.get(url, data = json.dump(json_data), headers=headers)

    # Log
    print(req)
    print(req.status_code)

    return req


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

    postToServer(uri="/test", json_data=getUserEmail())

    # Verifying User
    # verifyingUser()