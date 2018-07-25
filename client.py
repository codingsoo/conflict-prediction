# Import Library
import requests
from collections import OrderedDict
import subprocess
import json
import threading
from os.path import expanduser
import os
import re

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

        # Delays
        raw_input("Input Any Key (If you entered random number to Slack): ")

        # Synchronize User Data
        postToServer("/syncUserData", "sync")

        print("Success")

    return


# Get User Email():
def getUserEmail():

    # Get User git Email Using subprocess
    raw = str(subprocess.check_output('git config user.email', shell=True))

    # Get User git Name if user doesn't set their info
    if len(raw)==0:
        current_path = os.getcwd()
        home_path = expanduser("~")

        os.chdir(home_path)

        raw = str(subprocess.check_output('cat .gitconfig', shell=True))
        raw = raw.split("#")
        raw = re.sub("\n","",raw[3])
        raw = re.sub("\t","", raw)
        raw = re.sub("[a-z]* = ","", raw)

        os.chdir(current_path)

    # Create JSON
    json_data = OrderedDict()
    json_data["email"] = raw.strip()
    # json_data["email"] = "jcjc@naver.com"

    return json_data


# Post To Server
def postToServer(uri, json_data):

    # IP Address
    ip_addr = "127.0.0.1" #"35.237.100.101"

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
    ip_addr = "127.0.0.1" #"35.237.100.101"

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
# Output : git_id : , file_name : [edit_part, working_line,working_range, new_line_count, deleted_line_count]
def commandGitDiff():

    # Input User Git Email
    email = str(subprocess.check_output('git config user.email', shell=True)).strip()

    # Input Git Diff Command
    raw = str(subprocess.check_output('git diff HEAD', shell=True))

    # Split by Lines
    temp_list = raw.splitlines()

    # Modify git diff : Delete white space
    for i in range(0, len(temp_list)):
        temp_list[i].strip()

    # For MAKE git diff HEAD
    dt = 0
    df = 0

    # diff_total : Total git information
    diff_file_list = dict()

    # diff_file list
    diff_function_list = dict()

    # diff_obj_dict
    diff_function_dict = dict()
    # diff_obj : each git information content
    diff_function_obj = list()

    # diff_function_obj Definition
    file_name = ""
    function_name = ""
    working_line = ""
    plus_minus_count = 0
    temp_func_name = ""
    temp_count = 0

    for t in temp_list:
        # Find file_name
        if t[0:10] == "diff --git":

            # Second File name
            if (dt != 0):

                # Create diff function obj
                # diff_function_obj.append(function_name)
                diff_function_obj.append(working_line)
                diff_function_obj.append(str(plus_minus_count))

                diff_function_dict[function_name] = diff_function_obj

                # Create diff function list
                # diff_function_list.append(diff_function_dict)

                # Add diff_file_list
                diff_file_list[str(file_name)] = diff_function_dict

                diff_function_obj = list()
                diff_function_dict = dict()

                dt = 0
                df = 0
                plus_minus_count = 0

            # Find file name
            file_name = t.split(' ')[2][1:]

            dt += 1

        # Find function_name / working number
        elif t[0:2] == "@@":

            # Second function name
            if(df != 0):
                if(function_name == temp_func_name):
                    plus_minus_count += temp_count

                # Create diff_function_obj
                diff_function_obj.append(working_line)
                diff_function_obj.append(str(plus_minus_count))
                diff_function_dict[function_name] = diff_function_obj

                # Create diff_function_list
                # diff_function_list.append(diff_function_obj)

                # Initialize obj
                diff_function_obj = list()

                # Initialize plus, minus count
                temp_count = plus_minus_count
                plus_minus_count = 0
                df = 0

            # Find function name
            temp_func_name = function_name
            function_name = t.split("@@")[2].strip()

            if(function_name == temp_func_name):
                pass
            elif(function_name == "") or (function_name != temp_func_name):
                function_name = "in"
            # else:
            #     # Find working Line
            #     working_line = t.split(' ')[1].strip()
            #     working_line = working_line.split(',')[0][1:]

            df += 1

        # Find plus_token
        elif (t[0] == "+") and (t[1:3] != "++"):

            # Find plus length
            plus_minus_count += 1

        # Find minus_token
        elif (t[0] == "-") and (t[1:3] != "--"):

            # Find minus length
            plus_minus_count += 1

        # Final plus, minus count finish => ADD all
        if str(t) == str(temp_list[len(temp_list)-1]):

            # Create diff_function_obj
            diff_function_obj.append(working_line)
            diff_function_obj.append(str(plus_minus_count))
            diff_function_dict[function_name] = diff_function_obj

            # Create diff function list
            # diff_function_list.append(diff_function_obj)

            # Create diff file list
            diff_file_list[str(file_name)] = diff_function_dict

            # dic_keys = diff_file_list.keys()
            #
            # key_flag = False
            #
            # # Dictionary key replication check
            # for temp_key in dic_keys:
            #
            #     # Dictionary key is replication
            #     if temp_key == file_name:
            #         key_flag = True
            #         break
            #     # Dictionary key is not replication
            #     else:
            #         key_flag = False
            #
            # # Dictionary key replication check
            # if (key_flag):
            #
            #     # Already exist dictionary
            #     for temp_function_obj in diff_function_list:
            #         diff_file_list[str(file_name)].append(temp_function_obj)
            #
            # else:
            #     # Create diff file list
            #     diff_file_list[str(file_name)] = diff_function_list

    # Make Dictionary
    temp_dict = OrderedDict()

    # Add Dictionary => User git id
    temp_dict['git_id'] = email

    # Add Dictionary => git diff list
    temp_dict['git_diff'] = diff_file_list

    print(temp_dict)

    # # Add Dictionary => changed file content
    # temp_dict['git_diff_content'] = file_content_list

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

    # print log
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
        # postToServer("/gitLsFiles", commandGitLsFiles())

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
