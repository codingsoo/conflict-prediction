import configparser
import subprocess
import queue
import os
import requests
import json
import threading

IP = "127.0.0.1"
PORT = "0"

def load_config() :
    global IP
    global PORT
    if not os.path.isfile("client_settings.ini") :
        print("ERROR :: There is no client_settings.ini")
        exit(2)
    else :
        config = configparser.ConfigParser()
        config.read("client_settings.ini")
        try :
            IP=config["CONNECTION"]["IP"]
            PORT=config["CONNECTION"]["Port"]
        except :
            print("ERROR :: It is client_settings.ini")
            exit(2)

def post_to_server(uri, json_data) :
    url = "http://{IP}:{PORT}{URI}".format(IP = IP, PORT = PORT, URI = uri);
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    req = requests.post(url, headers=headers, data=json.dumps(json_data))
    print("Status Code:", req.status_code)
    return req

def set_repository_name(json_data) :
    result = subprocess.check_output('git config --local remote.origin.url', shell=True, universal_newlines=True)
    if result.startswith("git@") :
        json_data['repository_name'] = result[15:].strip()
    else :
        json_data['repository_name'] = result[19:].strip()
    print(json_data['repository_name'])

def set_user_email(json_data) :
    user_email = subprocess.check_output('git config user.email', shell=True, universal_newlines=True).strip()
    if not user_email :
        print("""
        ERROR :: Can not find email info.
        Please set your email before run the client.py
        git config --global user.email \"email@example.com\"
        """)
        exit(1)
    else :
        json_data['user_email'] = user_email

def set_user_git_diff(json_data) :
    path_queue = queue.Queue()
    path_queue.put('.')
    json_data['working_list'] = dict()
    flag = False

    while not path_queue.empty() :
        cur_path = path_queue.get()
        user_git_diff = subprocess.check_output('git diff HEAD', shell=True, universal_newlines=True, cwd=cur_path).splitlines()
        cur = 'in'
        idx = 0
        end_of_line = len(user_git_diff)
        while idx < end_of_line :
            line = user_git_diff[idx]
            if line.startswith('diff --git') :
                if flag :
                    if first_minus != 0 :
                        first_minus -= start_idx
                        start_point, end_point = origin_start + first_minus, origin_start + first_minus + minus_count - 1
                        json_data['working_list'][full_path]['edit_chuck'].append([start_point, end_point])
                    json_data['working_list'][full_path]['total_edit']+=plus_count+minus_count
                flag = False
                temp = line[11:]
                path = os.path.normpath(temp[2:len(temp)//2])
                full_path = os.path.join(cur_path, path)
                if os.path.isdir(full_path) :
                    path_queue.put(full_path)
                    idx += 1
                    line = user_git_diff[idx]
                    while not line.startswith('diff --git') :
                       idx += 1
                       if idx == end_of_line : break
                       line = user_git_diff[idx]
                    idx -= 1
                elif os.path.isfile(full_path) :
                    json_data['working_list'][full_path] = { 'edit_chuck' : [], 'total_edit' : 0}
                    logic = []
                    if user_git_diff[idx + 4].startswith("@@") :
                        idx += 4
                    else :
                        idx += 5
                    continue
            elif line.startswith("@@") :
                if flag :
                    if first_minus != 0:
                        first_minus -= start_idx
                        start_point, end_point = origin_start + first_minus, origin_start + first_minus + minus_count - 1
                        json_data['working_list'][full_path]['edit_chuck'].append([start_point, end_point])
                    json_data['working_list'][full_path]['total_edit'] += plus_count + minus_count


                _, number, code = [ each.strip() for each in line.split("@@")]
                comma_count = number.count(',')
                if comma_count == 2 :
                    origin_start, middle, edited_end = number.split(',')
                    origin_end, edited_start = middle.split(' ')

                    origin_start, origin_end, edited_start, edited_end = \
                        abs(int(origin_start)), int(origin_end), int(edited_start), int(edited_end)
                elif comma_count == 1 :
                    origin_start, middle = number.split(',')
                    edited_start, edited_end = middle.split(' ')
                    origin_start, edited_start, edited_end = \
                        abs(int(origin_start)), int(edited_start), int(edited_end)
                first_minus, first_plus = 0, 0
                start_idx = idx + 1
                minus_count, plus_count = 0, 0
                flag = True
            else :
                line.strip()
                if line[0] == '-' :
                    if first_minus == 0 and (idx + 1 < end_of_line and user_git_diff[idx + 1] != '\\ No newline at end of file') :
                        first_minus = idx
                    minus_count += 1
                elif line[0] == '+' :
                    if first_plus == 0 :
                        first_plus = idx
                    plus_count += 1
            idx += 1
    if flag:
        if first_minus != 0 :
            first_minus -= start_idx
            start_point, end_point = origin_start + first_minus, origin_start + first_minus + minus_count - 1
            json_data['working_list'][full_path]['edit_chuck'].append([start_point, end_point])
        json_data['working_list'][full_path]['total_edit'] += plus_count + minus_count

def verifying_user() :
    json_data = dict()
    set_user_email(json_data)
    res = post_to_server("/user_search", json_data)
    user_flag = res.text
    print(user_flag)
    if(user_flag.isdigit()):
        print("Enter Random Number to Slack : " + user_flag)
        input("Input Any Key (If you entered random number to Slack): ")
        print("Success")

def send_to_server_git_data() :
    json_data = dict()
    set_user_email(json_data)
    set_repository_name(json_data)
    set_user_git_diff(json_data)
    print(json_data)
    post_to_server("/git_diff", json_data)
    threading.Timer(10, send_to_server_git_data).start()


def send_to_graph_server_repository_name():
    ip_addr = "127.0.0.1"
    port = "5010"

    json_data = dict()
    set_repository_name(json_data)
    print(json_data)

    url = "http://" + ip_addr + ":" + port + "/repository_name"
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    req = requests.post(url, headers=headers, data=json.dumps(json_data))
    print("Status Code:", req.status_code)

    threading.Timer(60, send_to_graph_server_repository_name).start()


if __name__ == '__main__' :
    print("CHATBOT Client Start!")
    load_config()
    verifying_user()
    # send_to_server_git_data()
    # send_to_graph_server_repository_name()