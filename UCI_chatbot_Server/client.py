# Import Library
import requests
from collections import OrderedDict
import subprocess
import json
import threading

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

    # Input User Git Email
    email = str(subprocess.check_output('git config user.email', shell=True)).strip()

    # Input Git Diff Command
    raw = str(subprocess.check_output('git diff', shell=True))

    # Split by Lines
    temp_list = raw.splitlines()

    # log
    print(temp_list)

    # Changed git files To String
    raw_ls_files = str(subprocess.check_output('git ls-files -m', shell=True))

    # Input changed file name list
    file_name_list = raw_ls_files.splitlines()

    # File Content List
    file_content_list = list()

    # Read Files Content
    for temp_name in file_name_list:

        # log
        print(temp_name.strip())

        # File name modify process
        temp_file_name = temp_name.strip()

        # File Open
        file = open(temp_file_name, 'r')

        # log
        print(file_content_list.append(file.read()))

    # Make Dictionary
    temp_dict = OrderedDict()

    # Add Dictionary => User git id
    temp_dict['git_id'] = email

    # Add Dictionary => git diff list
    temp_dict['git_diff'] = temp_list

    # Add Dictionary => changed file content
    temp_dict['git_diff_content'] = file_content_list

    return temp_dict


# Command : git ls-files -m
def commandGitLsFiles():

    # Input User Git Email
    email = str(subprocess.check_output('git config user.email', shell=True))

    # Input Git Diff Command
    raw = str(subprocess.check_output('git ls-files -m', shell=True))

    # Create JSON_data List
    json_data = []

    # Append JSON data
    json_data.append(email)
    order_num = 0

    while ('\n' in raw):
        order_num = order_num + 1
        check_point = raw.find('\n')
        json_data.append(raw[:check_point])
        raw = raw[check_point + 1:]

    # log
    print(json_data)

    return json_data


# Class for Threading
class AsyncTask:

    # init
    def __init__(self):
        pass

    # send To Server : git diff / git ls-files -m
    def sendToServer_GitDiff_GitLsFiles(self):

        # Post To Server : git diff
        postToServer("/gitDiff", commandGitDiff())

        # Post To Server : git ls-files -m
        postToServer("/gitLsFiles", commandGitLsFiles())

        # Thread Start
        threading.Timer(10, self.sendToServer_GitDiff_GitLsFiles).start()


# Send To Server : Git Info
def sendToServer_git_data():
    # Create Async Object
    asyncTask = AsyncTask()

    # Start Sending Git Data
    asyncTask.sendToServer_GitDiff_GitLsFiles()

    return


# MAIN
if __name__ == "__main__":

    # Start
    print("CHATBOT Client Start!")

    # User Verifying Process
    verifyingUser()
    # postToServer("/gitLsFiles",commandGitLsFiles())

    # Start Thread for sending git data
    sendToServer_git_data()