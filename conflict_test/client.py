import configparser
import subprocess
import queue
import os
import requests
import json
import threading
import sys

IP = ""
PORT = ""

GRAPH_IP = ""
GRAPH_PORT = ""


def load_config():

    global IP
    global PORT

    global GRAPH_IP
    global GRAPH_PORT

    if not os.path.isfile("client_settings.ini"):
        print("ERROR :: There is no client_settings.ini")
        exit(2)

    else:
        config = configparser.ConfigParser()
        config.read("client_settings.ini")

        try:
            IP=config["CONNECTION"]["IP"]
            PORT=config["CONNECTION"]["Port"]
            GRAPH_IP=config["GRAPH_CONNECTION"]["IP"]
            GRAPH_PORT=config["GRAPH_CONNECTION"]["PORT"]

        except:
            print("ERROR :: It is client_settings.ini")
            exit(2)


def post_to_server(uri, json_data):

    url = "http://{IP}:{PORT}{URI}".format(IP = IP, PORT = PORT, URI = uri);
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    req = requests.post(url, headers=headers, data=json.dumps(json_data))
    print("Status Code:", req.status_code, "(post_to_server)")

    return req


def set_repository_name(json_data):

    result = subprocess.check_output('git config --local remote.origin.url', shell=True, universal_newlines=True)

    if result.startswith("git@"):
        json_data['repository_name'] = result[15:].strip()

    else:
        json_data['repository_name'] = result[19:].strip()

    print(json_data['repository_name'])


def set_user_email(json_data):

    user_email = subprocess.check_output('git config user.email', shell=True, universal_newlines=True).strip()

    if not user_email:
        print("""
        ERROR :: Can not find email info.
        Please set your email before run the client.py
        git config --global user.email \"email@example.com\"
        """)
        exit(1)

    else:
        json_data['user_email'] = user_email


def set_user_git_diff(json_data) :

    path_queue = queue.Queue()
    path_queue.put('.')
    json_data['working_list'] = dict()
    json_data['plus_list'] = dict()
    json_data['minus_list'] = dict()
    json_data['git_diff_info'] = dict()
    plus_dict = dict()
    minus_dict = dict()
    git_diff_info_dict = dict()

    flag = False

    while not path_queue.empty():

        cur_path = path_queue.get()
        ### SUN
        # print("user_git_diff : ", subprocess.check_output('git diff HEAD', shell=True, universal_newlines=True, cwd=cur_path))
        user_git_diff = subprocess.check_output('git diff HEAD', shell=True, universal_newlines=True, cwd=cur_path).splitlines()
        ### SUN
        # print("##git_diff : ", user_git_diff)
        cur = 'in'
        idx = 0
        chunk_idx = 0
        end_of_line = len(user_git_diff)

        while idx < end_of_line:
            line = user_git_diff[idx]

            if line.startswith('diff --git'):
                if flag:
                    if first_minus != 0 and first_plus != 0:
                        start_point, end_point = min(origin_start + (first_minus - start_idx), origin_start + (first_plus - start_idx - 1)), max(origin_start + (first_minus - start_idx) + minus_count - 1,origin_start + (first_plus - start_idx - 1))
                        json_data['working_list'][full_path]['edit_chuck'].append([start_point, end_point])

                    elif first_plus != 0:
                        start_point, end_point = origin_start + (first_plus - start_idx - 1), origin_start + (first_plus - start_idx - 1)
                        json_data['working_list'][full_path]['edit_chuck'].append([start_point, end_point])

                    elif first_minus != 0:
                        start_point, end_point = origin_start + (first_minus - start_idx), origin_start + (first_minus - start_idx) + minus_count - 1
                        json_data['working_list'][full_path]['edit_chuck'].append([start_point, end_point])

                    else:
                        json_data['working_list'][full_path]['edit_chuck'].append([-1,-1])

                    json_data['working_list'][full_path]['total_plus'] += plus_count
                    json_data['working_list'][full_path]['total_minus'] += minus_count
                    json_data['working_list'][full_path]['total_edit'] += plus_count + minus_count

                flag = False

                # temp = "a/filename b/filename"
                temp = line[11:]
                # path = "filename"
                path = os.path.normpath(temp[2:len(temp)//2])
                full_path = os.path.join(cur_path, path)

                if os.path.isdir(full_path):

                    path_queue.put(full_path)
                    idx += 1
                    line = user_git_diff[idx]

                    while not line.startswith('diff --git'):
                       idx += 1
                       if idx == end_of_line:
                           break
                       line = user_git_diff[idx]
                    idx -= 1

                elif os.path.isfile(full_path):
                    json_data['working_list'][full_path] = {'edit_chuck': [], 'total_edit': 0, 'total_plus': 0,'total_minus': 0}
                    plus_dict[full_path] = []
                    minus_dict[full_path] = []
                    git_diff_info_dict[full_path] = []
                    logic = []
                    if user_git_diff[idx + 4].startswith("@@"):
                        idx += 4
                    else :
                        idx += 5

                    continue

            elif line.startswith("@@"):

                if flag:

                    if first_minus != 0 and first_plus != 0:
                        start_point, end_point = min(origin_start + (first_minus - start_idx), origin_start + (first_plus - start_idx - 1)), max(origin_start + (first_minus - start_idx) + minus_count - 1,origin_start + (first_plus - start_idx - 1))
                        json_data['working_list'][full_path]['edit_chuck'].append([start_point, end_point])

                    elif first_plus != 0:

                        start_point, end_point = origin_start + (first_plus - start_idx - 1), origin_start + (first_plus - start_idx - 1)
                        json_data['working_list'][full_path]['edit_chuck'].append([start_point, end_point])

                    elif first_minus != 0:

                        start_point, end_point = origin_start + (first_minus - start_idx), origin_start + (first_minus - start_idx) + minus_count - 1
                        json_data['working_list'][full_path]['edit_chuck'].append([start_point, end_point])

                    else:

                        json_data['working_list'][full_path]['edit_chuck'].append([-1,-1])

                    json_data['working_list'][full_path]['total_plus'] += plus_count
                    json_data['working_list'][full_path]['total_minus'] += minus_count
                    json_data['working_list'][full_path]['total_edit'] += plus_count + minus_count

                _, number, code = [each.strip() for each in line.split("@@")]
                comma_count = number.count(',')
                # print("number", number)

                origin_start, origin_end, edited_start, edited_end = -1, -1, -1, -1
                if comma_count == 2:

                    origin_start, middle, edited_end = number.split(',')
                    origin_end, edited_start = middle.split(' ')
                    origin_start, origin_end, edited_start, edited_end = \
                        abs(int(origin_start)), int(origin_end), int(edited_start), int(edited_end)
                    chunk_idx = edited_start - 1

                elif comma_count == 1:

                    origin_start, middle = number.split(',')
                    edited_start, edited_end = middle.split(' ')
                    origin_start, edited_start, edited_end = \
                        abs(int(origin_start)), int(edited_start), int(edited_end)
                    chunk_idx = edited_start - 1

                # print(origin_start, origin_end, edited_start, edited_end)
                # code = "@@ Start Line {} @@ ".format(edited_start, edited_end) + code
                code = "@@ " + code
                # print("code", code)
                git_diff_info_dict[full_path].append(code)

                first_minus, first_plus = 0, 0
                start_idx = idx + 1
                minus_count, plus_count = 0, 0

                flag = True

            else:
                line.strip()
                git_diff_info_dict[full_path].append(line)
                if line[0] == '-':
                    minus_dict[full_path].append([line[1:], chunk_idx])
                    if first_minus == 0:
                        first_minus = idx

                        if (idx + 1 < end_of_line and user_git_diff[idx + 1] == '\\ No newline at end of file'):
                            temp_line = user_git_diff[idx + 2][1:].strip()
                            if line[1:].strip() == temp_line:
                                first_minus = 0
                    minus_count += 1
                    chunk_idx -= 1

                elif line[0] == '+':
                    plus_dict[full_path].append([line[1:], chunk_idx])
                    if first_plus == 0 :
                        first_plus = idx
                    plus_count += 1

            idx += 1
            chunk_idx += 1

    if flag:

        if first_minus != 0 and first_plus != 0:
            start_point, end_point = min(origin_start + (first_minus - start_idx),
                                         origin_start + (first_plus - start_idx - 1)), max(
                origin_start + (first_minus - start_idx) + minus_count - 1, origin_start + (first_plus - start_idx - 1))
            json_data['working_list'][full_path]['edit_chuck'].append([start_point, end_point])

        elif first_plus != 0:

            start_point, end_point = origin_start + (first_plus - start_idx - 1), origin_start + (
                        first_plus - start_idx - 1)
            json_data['working_list'][full_path]['edit_chuck'].append([start_point, end_point])

        elif first_minus != 0:

            start_point, end_point = origin_start + (first_minus - start_idx), origin_start + (
                        first_minus - start_idx) + minus_count - 1
            json_data['working_list'][full_path]['edit_chuck'].append([start_point, end_point])

        else:
            json_data['working_list'][full_path]['edit_chuck'].append([-1, -1])

        json_data['working_list'][full_path]['total_plus'] += plus_count
        json_data['working_list'][full_path]['total_minus'] += minus_count
        json_data['working_list'][full_path]['total_edit'] += plus_count + minus_count

    for key_temp, value_temp in plus_dict.items():
        json_data['plus_list'][key_temp] = value_temp

    for key_temp, value_temp in minus_dict.items():
        json_data['minus_list'][key_temp] = value_temp

    for key_temp, value_temp in git_diff_info_dict.items():
        json_data['git_diff_info'][key_temp] = value_temp


def set_modify_file_content(json_data):
    json_data['modify_file'] = dict()
    for file_name_temp in json_data['plus_list'].keys():
        context = load_file(file_name_temp)
        json_data['modify_file'][file_name_temp] = context


def set_git_log_name_only(json_data):
    json_data['git_log_name_only'] = subprocess.check_output('git log --name-only', shell=True, universal_newlines=True).splitlines()


def load_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        context = f.readlines()
    return context


def verifying_user():

    json_data = dict()
    set_user_email(json_data)
    res = post_to_server("/user_search", json_data)
    user_flag = res.text
    print("user_flag : ", user_flag)

    if(user_flag.isdigit()):
        print("Enter Random Number to Slack : " + user_flag)
        input("Input Any Key (If you entered random number to Slack): ")
        print("Success")


def send_to_server_git_data():

    json_data = dict()
    set_user_email(json_data)
    set_repository_name(json_data)
    set_user_git_diff(json_data)
    set_modify_file_content(json_data)
    set_git_log_name_only(json_data)

    ### SUN
    # for key_temp, value_temp in json_data.items():
    #     print(key_temp, " : ", value_temp)

    print("### send_to_server_git_data /git_diff ###")
    post_to_server("/git_diff", json_data)
    threading.Timer(1, send_to_server_git_data).start()


def send_to_graph_server_repository_name():

    json_data = dict()
    set_repository_name(json_data)
    set_user_email(json_data)

    ### SUN ###
    # print(json_data)

    url = "http://" + GRAPH_IP + ":" + GRAPH_PORT + "/repository_name"
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    print("### send_to_graph_server_repository_name /repository_name ###")
    req = requests.post(url, headers=headers, data=json.dumps(json_data))
    print("Status Code:", req.status_code, "(post_to_graph_server)")

    threading.Timer(60, send_to_graph_server_repository_name).start()


if __name__ == '__main__' :

    print("CHATBOT Client Start!")
    load_config()
    verifying_user()
    send_to_server_git_data()
    send_to_graph_server_repository_name()