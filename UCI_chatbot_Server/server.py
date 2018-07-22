########################################################################
# Import Library##
import random
import json
import os
from flask import Flask, request
from slacker import Slacker
########################################################################

# Create app
app = Flask(__name__)

# User List
user_git_id_list = dict()
working_file = dict()

# git diff
working_list = dict()

# { file_name : user_name }
conflict_list = dict()

# { user_name : { user_name : error_name } }
error_list = dict()

token = ''

# test for log
@app.route("/test", methods = ["POST"])
def test():
    ##
    return "test"


# Request for git diff
@app.route("/gitDiff", methods = ["POST", "GET"])
def cmd1():

    # Get command2 content
    content = request.get_json(silent=True)

    # log
    print content

    # Get User slack id
    user_slack_id = user_git_id_list[str(content['git_id'])]

    # log
    print content['git_id']
    print user_git_id_list

    # Create working_list
    working_list[user_slack_id] = content['git_diff']

    # log
    print ("conflict list keys : " + str(conflict_list.keys()))

    # conflict list == null
    if conflict_list.keys() == []:

        # all file, user pair is added
        for file_name in content['git_diff']:
            conflict_list[file_name] = user_slack_id

    # conflict list != null
    else:

        # Append New git diff Info To conflict_list
        for file_name in content['git_diff'].keys():

            # log
            print file_name

            # conflict detect
            for conflict_file_name in conflict_list.keys():

                # log
                print conflict_file_name

                # Conflict
                if (file_name == conflict_file_name) and (conflict_list[conflict_file_name] != user_slack_id):

                    print "conflict"

                    # POP : get error_user1
                    error_user1 = conflict_list.pop(file_name)

                    error_user2_info = dict()

                    # find error header [function, class, in] about old user (user1) #
                    conflict_header_name = str(working_list[error_user1][conflict_file_name][1])

                    error_user2_info[user_slack_id] = conflict_header_name

                    error_list[error_user1] = error_user2_info

                # Non - conflict
                else:
                    print "non-conflict"
                    conflict_list[file_name] = user_slack_id

    print content
    print working_list
    print conflict_list
    print error_list

    return "test"


# Request for git ls-files -m
@app.route("/gitLsFiles", methods = ["POST", "GET"])
def cmd2():
    # for test
    working_file['test'] = {}

    # Get command2 content
    content = request.get_json(silent=True)

    # log
    print(content)

    key = str(content[0]).strip()
    for keys in working_file.keys():
        if keys == key:
            continue
        for working_files in working_file[keys]:
            for new_working_files in content:
                if new_working_files in working_files:
                    slack = Slacker(token)

                    attachments_dict = dict()
                    attachments_dict['text'] = "Conflict Detected!"
                    attachments_dict['mrkdwn_in'] = ["text", "pretext"]
                    attachments = [attachments_dict]

                    slack.chat.post_message(channel="#code-conflict-chatbot", text=None, attachments=attachments, as_user=True)

    # print working_file

    working_file[key] = content[1:]

    return "test"


# User Search And Verifying
@app.route("/userSearch", methods = ["POST"])
def userSearch():

    # Get User Git ID
    content = request.get_json(silent=True)
    git_id = str(content['email'])

    for email in user_git_id_list.keys():
        if git_id == str(email) and type(user_git_id_list[email]) != int:
            return "True"

    # Generate Random Number
    rand_num = createRandomTemp()

    # Create JSON User Data
    json_dict = dict()
    json_dict[git_id] = rand_num

    # Save User Data Json file
    with open('./user_data/user_git.json', 'w') as make_file:
        json.dump(json_dict, make_file)

    # Return Ture or Random Number
    return str(rand_num)

# Synchronize User Data
@app.route("/syncUserData", methods = ["POST"])
def syncUserData():

    # Import User Data
    with open('./user_data/user_git.json', 'r') as f:
        user_git_id_list = json.load(f)
        # print(user_list)

    return "test"

# Random Number for User sign-in
def createRandomTemp():

    # Create Random Number
    rand_num = random.randint(10000, 99999)

    # log
    print("random Number: " + str(rand_num))

    return rand_num

# MAIN
if __name__ == "__main__":

    # Import User Data
    with open('./user_data/user_git.json', 'r') as f:
        user_git_id_list = json.load(f)
        print(user_git_id_list)

    # Run App
    app.run(debug=True, host="0.0.0.0", port=5009)