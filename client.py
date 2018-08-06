# Import Library
import requests
from collections import OrderedDict
import subprocess
import json
import threading
from os.path import expanduser
import os
import re

# IP definition
ip_addr = "127.0.0.1"
port = "5009"

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

    # Create URL
    url = "http://" + ip_addr + ":" + port + uri # 80

    # Headers
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    # Post To Server
    req = requests.post(url, headers=headers, data = json.dumps(json_data))

    # Log
    print(req)

    return req


# Get To Server
def getToServer(uri, json_data):

    # Create URL
    url = "http://" + ip_addr + ":" + port + uri # 80

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

    # Make Dictionary
    temp_dict = OrderedDict()

    # Add Dictionary => User git id
    temp_dict['git_id'] = email

    # Add Dictionary => git diff list
    temp_dict['git_diff'] = diff_file_list

    search_directory(root_dir)
    generate_file_dependency()
    raw_list = generate_func_class_dependency()
    temp_dict['git_graph'] = create_edge(raw_list)

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

# ----------------------------------------------------

root_dir = os.path.join(os.getcwd(), 'UCI_chatbot_Server')
file_dir = []
file_name = []
file_dependency = {}
file_content_list = dict()

group = list(list())

# Search All Directory And Append simple file name
def search_directory(url):
    for (file_path, dir, files) in os.walk(url):
        for filename in files:
            if 'conflict-detector' in str(file_name):
                continue
            ext = os.path.splitext(filename)[-1]
            if ext == '.py':
                # print("%s/%s" % (file_path, filename))
                file_dir.append(os.path.join(file_path,filename))
                file_name.append(filename[:len(filename)-3])


# File Content Data Reader
def file_reader(url):

    # file open
    f = open(url)

    # Read Raw Data from file
    raw_data = f.read()

    return raw_data


# Generate File Dependency Data / File Content Data
# 1. File dependency        # { 'file path' : [ dependency file list ], 'file path2' : [ dependency file list ] }
def generate_file_dependency():

    # Read Each File
    for temp_dir in file_dir:

        # make simple_file_name
        simple_file_name = temp_dir.split(os.sep)
        simple_file_name = simple_file_name[len(simple_file_name) - 1]
        simple_file_name = simple_file_name[:-3]

        # Read Raw data
        file_content = file_reader(temp_dir).splitlines()
        temp_file_list = []

        # log
        # print temp_dir

        # Initialize class, function set
        # Initialize file dict for dependency
        in_content = list()

        # Read Each line
        for file_line in file_content:

            # Split raw line
            index = 0
            temp_line = file_line.split(' ')

            # Detect class under function
            if (file_line[0:4] != '    '):
                if file_line != '':
                    class_dep = False

            # Read Each token
            for temp_token in temp_line:

                # Generate file dependency [keyword : import]
                if temp_token == "import":
                    import_file = temp_line[index + 1]

                    # Search import file list
                    for temp_file_dir in file_dir:
                        temp1_file_dir = temp_file_dir.split(os.sep)
                        temp1_file_dir = temp1_file_dir[len(temp1_file_dir) - 1]
                        temp1_file_dir = temp1_file_dir[:-3]

                        # if file imported => add file dependency
                        if import_file == temp1_file_dir:
                            temp_file_list.append(temp_file_dir)
                            file_dependency[temp_dir] = temp_file_list
                            break

                # Generate class dependency [ keyword : class ]
                elif temp_token == "class":

                    # Read class name
                    class_name = file_line.strip()
                    in_content.append(class_name)

                # Generate function dependency [ keyword : def ]
                elif temp_token == "def":

                    # Read function name
                    def_name = file_line.strip()
                    in_content.append(def_name)

                # index plus
                index += 1

        file_content_list[temp_dir] = in_content
        # print file_content_list


# Generate Function Class Dependency
# 1. Function dependency    # [ [ 'file name + function name', 'dependency function list' ], ['file name + function name' : 'dependency function list' ]
# 2. Class dependency       # [ [ 'file name + class name', dependency class list ], ['file name + class name', 'dependency class list' ]
def generate_func_class_dependency():

    all_dependency_list = list()

    # Read Each File
    for temp_dir in file_dir:

        # log
        # print temp_dir

        # Read Raw data
        file_content = file_reader(temp_dir).splitlines()

        content_dependency_list = []
        class_name = ""
        def_name = ""
        class_dep = False
        def_dep = False

        # Read Each line
        for file_line in file_content:

            # Split raw line
            index = 0
            temp_line = file_line.split(' ')

            # Detect class under function
            if (file_line[0:4] != '    '):
                if file_line != '':
                    class_dep = False
                    def_dep = False

            # Read Each token
            for temp_token in temp_line:

                # Generate class dependency [ keyword : class ]
                if temp_token == "class":

                    # Read class name
                    class_name = file_line.strip()

                    # String processing
                    if class_name[-1] == ':':
                        class_name = class_name[:-1].strip()

                    class_dep = True

                # Generate function dependency [ keyword : def ]
                elif temp_token == "def":

                    # Read function name
                    def_name = file_line.strip()

                    # String processing
                    def_name = def_name.split('(')[0]

                    def_dep = True

                    # class function dependency
                    if (file_line[0:4] == "    ") and (len(file_line) >= 4) and class_dep:
                        temp_list = []
                        temp_list.append(temp_dir + '|' + class_name)
                        temp_list.append(temp_dir + '|' + def_name)
                        content_dependency_list.append(temp_list)
                        all_dependency_list.append(temp_list)
                        break

                # Import function dependency
                elif file_line[0:4] == '    ':
                    for t_dir in file_dir:

                        if t_dir != temp_dir:
                            # Read clear function, class name
                            func_class_name_list = class_func_name(file_content_list[t_dir])

                            # Search about usage of function
                            for temp_func_class_name in func_class_name_list:
                                find_flag = temp_token.find(temp_func_class_name)

                                if  (find_flag > 0) and def_dep:
                                    temp_func_list = []
                                    temp_func_list.append(temp_dir + '|' + def_name)
                                    temp_func_list.append(t_dir + '|def ' + temp_func_class_name)
                                    content_dependency_list.append(temp_func_list)
                                    all_dependency_list.append(temp_func_list)
                                    break

                # index plus
                index += 1

    return all_dependency_list


def class_func_name(raw_name_list):

    convert_name_list = []

    for raw_name in raw_name_list:

        split_name = str(raw_name).split(' ')

        # if(split_name[0] == "class"):
        #     temp_name = split_name[1]
        #
        #     if(temp_name[-1] == ':'):
        #         temp_name = temp_name[:-1]
        #
        #     convert_name_list.append(temp_name)

        if(split_name[0] == "def"):
            temp_name_list = split_name[1].split('(')
            temp_name = temp_name_list[0]
            convert_name_list.append(temp_name)

    return convert_name_list


def create_edge(raw_list):

    raw_dict = dict()

    for dep_obj in raw_list:
        for compare_dep in raw_list:

            if dep_obj[1] == compare_dep[0]:
                new_temp = []
                new_temp.append(dep_obj[0])
                new_temp.append(compare_dep[1])

                raw_list.append(new_temp)
    for file_set in raw_list:
        raw_dict[file_set[0]] = file_set[1]

    # for stan_file in raw_dict.keys():
    #     group_file = raw_dict[stan_file]
    #     group_list = []
    #     while(True):
    #         group_list.append(group_file)
    #         if raw_dict[stan_file] in raw_dict.keys():
    #             group_file = raw_dict[stan_file]
    #         else:
    #             break
    #     group.append(group_list)

    return raw_dict

# MAIN
if __name__ == "__main__":

    # Start
    print("CHATBOT Client Start!")

    # User Verifying Process
    verifyingUser()
    # postToServer("/gitLsFiles",commandGitLsFiles())

    # Start Thread for sending git data
    sendToServer_git_data()