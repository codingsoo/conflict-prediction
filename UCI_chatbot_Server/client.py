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
    res = postToServer(uri="/userSearch", json_data=json_email)

    # Response Data Parsing
    user_flag = res.text

    # log
    print(user_flag)

    # User Verifying Process
    if(user_flag.isdigit()):

        # Print Input Random Number to Slack
        print("Enter Random Number to Slack : " + user_flag)

        # Delay
        raw_input("Input Any Key (If you entered random number to Slack): ")

        # Synchronize User Data
        postToServer("/syncUserData", "sync")

        print("Success")

    return


# Get User Email():
def getUserEmail():

    # Get User git Email Using subprocess
    raw = str(subprocess.check_output('git config user.email', shell=True))

    # Create JSON
    json_data = OrderedDict()
    json_data["email"] = raw.strip()

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
    req = requests.post(url, headers=headers, data = json.dumps(json_data))

    # Log
    print(req)

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
    req = requests.get(url, data = json.dumps(json_data), headers=headers)

    # Log
    print(req)
    print(req.status_code)

    return req


# Command : git diff
def commandGitDiff():
    return


# Command : git ls-files -m
def commandGitLsFiles():
    email = str(subprocess.check_output('git config user.email', shell=True))
    raw = str(subprocess.check_output('git ls-files -m', shell=True))
    json_data = []
    json_data.append(email)
    order_num = 0

    while ('\n' in raw):
        order_num = order_num + 1
        check_point = raw.find('\n')
        json_data.append(raw[:check_point])
        raw = raw[check_point + 1:]

    return json_data


# MAIN
if __name__ == "__main__":

    # Start
    print("CHATBOT Client Start!")

    # User Verifying Process
    verifyingUser()
    # postToServer("/gitLsFiles",commandGitLsFiles())

