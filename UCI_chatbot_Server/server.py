########################################################################
# Import Library##
import random
import json
from flask import Flask, request
from slacker import Slacker
import os
from git_clone_info import git_clone_info
########################################################################

# Create app
app = Flask(__name__)

# User List
user_git_id_list = dict()
working_file = dict()

# git diff
working_list = dict()

# test
working_list = {u'learnitdeep2': {u'/UCI_chatbot_Server/bot_server.py': {u'import json': [u'7', u'2']}, u'/UCI_chatbot_Server/server.py': {u'def cmd1():': [u'39', u'140'], u'working_file = dict()': [u'17', u'6']}}}

# Approved list
approved_list = []

# { file_name : [user_name] }
conflict_list = dict([])

# test
conflict_list = {u'/UCI_chatbot_Server/bot_server.py': [u'learnitdeep2'], u'/UCI_chatbot_Server/user_data/user_git.json': [u'learnitdeep2'], u'/UCI_chatbot_Server/server.py': [u'learnitdeep2']}


# { user_name : { user_name : error_name } }
error_list = dict()

# test
# error_list = {u'learnitdeep': {u'learnitdeep2': u'def cmd1():'}}

git_clone_info = git_clone_info()

def make_shell_list(file):
    f = open(file,"r")
    text = f.read()
    text = unicode(text,'utf-8')
    text = text.split("\n")

    return text

# bot_rule_based_talk
go_to_same_file_shell = make_shell_list('./situation_shell/go_to_same_file.txt')
get_severe_diff_file = make_shell_list('./situation_shell/file_to_class.txt')
conflict_finished = make_shell_list('./situation_shell/conflict_finished.txt')

# test for log
@app.route("/test", methods = ["POST", "GET"])
def test():
    ##

    print git_clone_info.get_git_clone_info()

    return "test"


# Request for git diff
@app.route("/gitDiff", methods = ["POST", "GET"])
def cmd1():

    # Get command2 content
    content = request.get_json(silent=True)
    print content
    used_files = dict(list())

    with open('./user_data/user_git.json', 'r') as f:
        user_git_id_list = json.load(f)
    # Get User slack id
    if content['git_id'] :
        user_slack_id = user_git_id_list[str(content['git_id'])]
    else:
        user_slack_id = content['git_id']

    # Create working_list
    working_list[user_slack_id] = content['git_diff']

    # Put user's working list to conflict list
    for file_name in  working_list[user_slack_id]:
        user_list = []

        with open('./user_data/approved_list.json', 'r') as f:
            approved_list = json.load(f)
        if file_name in approved_list:
            continue

        # Conflict case
        if file_name in conflict_list.keys() and user_slack_id not in conflict_list[file_name]:
            # Analyze conflict severity
            if file_name in working_list[conflict_list[file_name][0]].keys():
                error = 'in'
                for user1_work_place in working_list[conflict_list[file_name][0]][file_name].keys():
                    for user2_work_place in working_list[user_slack_id][file_name].keys():
                        user1_working_line = working_list[str(conflict_list[file_name][0])][file_name][user1_work_place][0]
                        user1_working_space = working_list[str(conflict_list[file_name][0])][file_name][user1_work_place][1]
                        user2_working_line = working_list[user_slack_id][file_name][user2_work_place][0]
                        user2_working_space = working_list[user_slack_id][file_name][user2_work_place][1]
                        if user1_working_space == "" :
                            user1_working_space = 0
                        if user2_working_space == "":
                            user2_working_space = 0
                        if user1_working_line == "":
                            user1_working_line = 0
                        if user2_working_line == "":
                            user2_working_line = 0

                        # Def case
                        if user1_work_place == user2_work_place and 'def' in user1_work_place:
                            error = user1_work_place
                        # Class case
                        elif user1_work_place == user2_work_place and 'class' in user1_work_place and 'def' not in error:
                            error = user1_work_place
                        # Same file case
                        elif error == 'in':
                            working_line = abs(int(user1_working_line) - int(user2_working_line))
                            working_space = abs(int(user1_working_space) + int(user2_working_space))
                            error = error + str(working_line) + ',' + str(working_space)
                        elif 'in' in error:
                            #print working_list[user_slack_id][file_name]
                            #print working_list[conflict_list[file_name][0]][file_name]['import json']
                            pre_working_line = int(error[2:].split(',')[0])
                            pre_working_space = int(error[2:].split(',')[1])
                            working_line = abs(int(user1_working_line) - int(user2_working_line))
                            working_space = abs(int(user1_working_space) + int(user2_working_space))

                            if pre_working_space < working_space:
                                error = 'in' + str(working_line) + ',' + str(working_space)

                conflict_list[file_name].append(user_slack_id)
                conflict_list[file_name].sort()

                # When pre-conflict exist
                if conflict_list[file_name][0] in error_list.keys() and conflict_list[file_name][1] in error_list[conflict_list[file_name][0]].keys() and file_name in error_list[conflict_list[file_name][0]][conflict_list[file_name][1]].keys():
                    pre_error = error_list[conflict_list[file_name][0]][conflict_list[file_name][1]][file_name]

                    # Severe case to def
                    if 'def' in error and 'def' not in pre_error:
                        attachments_dict = dict()
                        attachments_dict['text'] = get_severe_diff_file[random.randint(0,len(get_severe_diff_file)-1)] % ('@'+conflict_list[file_name][0],'@'+conflict_list[file_name][1], file_name, error + " function")
                        attachments_dict['mrkdwn_in'] = ["text", "pretext"]
                        attachments = [attachments_dict]

                        slack.chat.post_message(channel="#code-conflict-chatbot", text=None, attachments=attachments, as_user=True)

                        error_list[conflict_list[file_name][0]][conflict_list[file_name][1]] = error

                    # Severe case to class
                    elif 'class' in error and 'def' not in pre_error and 'class' not in pre_error:
                        attachments_dict = dict()
                        attachments_dict['text'] = get_severe_diff_file[random.randint(0,len(get_severe_diff_file)-1)] % ('@'+conflict_list[file_name][0],'@'+conflict_list[file_name][1], file_name ,error + " class")
                        attachments = [attachments_dict]

                        slack.chat.post_message(channel="#code-conflict-chatbot", text=None, attachments=attachments, as_user=True)

                        error_list[conflict_list[file_name][0]][conflict_list[file_name][1]] = error

                    # Severe case to in
                    elif 'in' in pre_error and 'in' in error and int(error[2:].split(',')[1]) - 5 > int(pre_error[2:].split(',')[1]):
                        attachments_dict = dict()
                        attachments_dict['text'] = get_severe_diff_file[random.randint(0,len(get_severe_diff_file)-1)] % ('@'+conflict_list[file_name][0],'@'+conflict_list[file_name][1], " same file")
                        attachments_dict['mrkdwn_in'] = ["text", "pretext"]
                        attachments = [attachments_dict]

                        slack.chat.post_message(channel="#code-conflict-chatbot", text=None, attachments=attachments, as_user=True)

                        error_list[conflict_list[file_name][0]][conflict_list[file_name][1]] = error

                    # Conflict solved
                    elif ('def' in pre_error and 'def' not in error) or ('class' in pre_error and 'def' not in error and 'class' not in error) or ('in' in pre_error and 'in' in error and int(pre_error[2:].split(',')[1]) + 5 > int(error[2:].split(',')[1])):
                        attachments_dict = dict()
                        attachments_dict['text'] = conflict_finished[random.randint(0,len(conflict_finished)-1)] % (conflict_list[file_name][0],conflict_list[file_name][1])
                        attachments_dict['mrkdwn_in'] = ["text", "pretext"]
                        attachments = [attachments_dict]

                        slack.chat.post_message(channel="#code-conflict-chatbot", text=None, attachments=attachments, as_user=True)
                        error_list[conflict_list[file_name][0]][conflict_list[file_name][1]][file_name] = error
                    # Same conflict
                    else :
                        pass
                # When pre-conflict doesn't exist
                else:
                    user_error_dict = dict()
                    func_error_dict = dict()
                    func_error_dict[file_name] = error
                    user_error_dict[conflict_list[file_name][1]] = func_error_dict
                    error_list[conflict_list[file_name][0]] = user_error_dict

                    # def detected
                    if 'def' in error:
                        attachments_dict = dict()
                        attachments_dict['text'] = go_to_same_file_shell[random.randint(0,len(go_to_same_file_shell)-1)] % ('@'+conflict_list[file_name][0],'@'+conflict_list[file_name][1], error + " function")
                        attachments_dict['mrkdwn_in'] = ["text", "pretext"]
                        attachments = [attachments_dict]

                        slack.chat.post_message(channel="#code-conflict-chatbot", text=None, attachments=attachments, as_user=True)
                    # class detected
                    elif 'class' in error:
                        attachments_dict = dict()
                        attachments_dict['text'] = go_to_same_file_shell[random.randint(0,len(go_to_same_file_shell)-1)] % ('@'+conflict_list[file_name][0],'@'+conflict_list[file_name][1], error + " class")
                        attachments_dict['mrkdwn_in'] = ["text", "pretext"]
                        attachments = [attachments_dict]

                        slack.chat.post_message(channel="#code-conflict-chatbot", text=None, attachments=attachments, as_user=True)
                    # same file detected
                    else:
                        attachments_dict = dict()
                        attachments_dict['text'] = go_to_same_file_shell[random.randint(0,len(go_to_same_file_shell)-1)] % ('@'+conflict_list[file_name][0],'@'+conflict_list[file_name][1], file_name + " file")
                        attachments_dict['mrkdwn_in'] = ["text", "pretext"]
                        attachments = [attachments_dict]

                        slack.chat.post_message(channel="#code-conflict-chatbot", text=None, attachments=attachments, as_user=True)

            # No conflict
            else:
                # pre-conflict exist
                conflict_check_user = []
                conflict_check_user.append(conflict_list[file_name][0])
                conflict_check_user.append(user_slack_id)
                conflict_check_user.sort()
                attachments_dict = dict()
                attachments_dict['text'] = conflict_finished[random.randint(0, len(conflict_finished) - 1)] % (conflict_check_user[0], conflict_check_user[1])
                attachments_dict['mrkdwn_in'] = ["text", "pretext"]
                attachments = [attachments_dict]

                slack.chat.post_message(channel="#code-conflict-chatbot", text=None, attachments=attachments, as_user=True)
                # del (error_list[conflict_check_user[0]][conflict_check_user[1]][file_name])
                conflict_list[file_name][0] = user_slack_id

        # No conflict
        else:
            user_list.append(user_slack_id)
            conflict_list[file_name] = user_list
        #
        # # In direct
        # index = 0
        # for group in content['git_graph']:
        #     if file_name in group and index in used_files :
        #         for user in used_files[index] :
        #             if user != user_slack_id and file_name in working_list[user].keys():
        #                 # conflict detected
        #                 print("hello")
        #             else:
        #                 del(used_files[index])
        #         used_files[index].append(user_slack_id)
        #     index = index + 1

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
    with open('./user_data/user_git.json', 'r') as make_file:
        json_dict = json.load(make_file)

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


# Receive Graph Info from git_graph_drawer
@app.route("/graphInfo", methods = ["POST"])
def graphInfo():

    # Receive Graph Info
    content = request.get_json(silent=True)
    print(str(content))

    git_clone_info.set_git_clone_info(content)
    print git_clone_info.get_git_clone_info()
    return "success"

# Random Number for User sign-in
def createRandomTemp():

    # Create Random Number
    rand_num = random.randint(10000, 99999)

    # log
    print("random Number: " + str(rand_num))

    return rand_num


# MAIN
if __name__ == "__main__":

    # Import Token
    with open('../token.json', 'r') as token_file:
        token_file_json = json.load(token_file)

    token = token_file_json['token']
    slack = Slacker(token)

    # Import User Data
    with open('./user_data/user_git.json', 'r') as f:
        user_git_id_list = json.load(f)
        print(user_git_id_list)

    # Run App
    app.run(debug=True, host="0.0.0.0", port=80)
