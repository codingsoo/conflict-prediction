"""
    @file   server_git.py
    @brief
        Detecting direct and indirect conflict, updating user data and converting data from the client.
"""

from server_dir.python_logic_parser import *
from server_dir.direct_work_database import *
from server_dir.user_git_diff import *
from server_dir.indirect_work_database import *

import os
import subprocess
import time
import shutil
import threading

"""
git diff logic
function    : detect direct conflict between the developers
parameter   : content_json
return      : none
"""
# BASE_PATH for clone repository.
BASE_PATH = os.path.pardir

def git_logic(content):
    print("\n" + "#### START git logic ####")

    threadLock = threading.Lock()
    threadLock.acquire()

    # Create user git diff data
    user_data = user_git_info(content)

    git_log_logic(user_data)
    git_diff_logic(user_data)

    threadLock.release()

    return

def git_diff_logic(user_data):
    print("\n" + "#### START git diff logic ####")

    # Create direct and indirect database connection
    dw_db = direct_work_database()
    iw_db = indirect_work_database()
    w_db = work_database()

    # Remove lock list
    remove_lock_list = w_db.prev_remove_lock_list()
    if remove_lock_list:
        send_remove_lock_channel("code-conflict-chatbot", remove_lock_list)
    w_db.auto_remove_lock_list()

    project_name = user_data.get_proj_name()
    working_data = user_data.get_working_data()
    edit_amount = user_data.get_edit_amount()
    calling_data = user_data.get_calling_data()
    user_name = user_data.get_user_name()

    # Check whether we need prediction
    predict_flag = dw_db.check_necessity_prediction(project_name,
                                                   working_data,
                                                   user_name)

    # Remove previous user data
    w_db.remove_user_data(project_name,
                          working_data,
                          edit_amount,
                          calling_data,
                          user_name,)

    # Update current user data
    w_db.update_user_data(project_name,
                          working_data,
                          edit_amount,
                          calling_data,
                          user_name)

    # Predict conflict
    if predict_flag:
        print("\n#### START predict_conflict ####")
        dw_db.predict_conflict(project_name,
                              user_name)


    # Detect direct conflict
    dw_db.detect_direct_conflict(project_name,
                                 working_data,
                                 user_name)

    # Detect indirect conflict
    iw_db.detect_indirect_conflict(project_name,
                                   user_name)

    # Close direct and indirect database connection
    dw_db.close_db()
    iw_db.close_db()
    w_db.close()

    return

def git_log_logic(user_data):
    print("\n" + "#### START git log logic ####")

    w_db = work_database()

    project_name = user_data.get_proj_name()
    last_commit_date = user_data.get_last_commit_data()

    if w_db.is_empty_git_log_name_only(project_name) or w_db.is_old_git_log_name_only(project_name, last_commit_date):
        log_file_list = user_data.get_log_file_list()
        w_db.update_git_log_name_only(project_name, log_file_list)
        w_db.update_last_commit_date(project_name, last_commit_date)

    w_db.close()

    return

def convert_data(content) :

    print("\n" + "#### START convert_data logic ####")
    converted_data = dict()
    converted_data['git_id'] = content['user_email']
    converted_data['git_diff'] = dict()
    print(content['repository_name'])
    content_list = content['repository_name'].split('/')
    owner_name, project_name = content_list[-2], content_list[-1]
    content['repository_name'] = owner_name + '/' + project_name
    converted_data['git_diff'][content['repository_name']] = dict()

    converted_data['plus_list'] = dict()
    converted_data['minus_list'] = dict()
    converted_data['git_diff_info'] = dict()
    converted_data['modify_file'] = dict()
    converted_data['total_plus'] = dict()
    converted_data['total_minus'] = dict()
    converted_data['git_log_name_only'] = content['git_log_name_only']
    converted_data['func_list'] = dict()
    converted_data['class_list'] = dict()

    URL = "https://github.com/{}/{}".format(owner_name, project_name)
    full_base_path = os.path.join(BASE_PATH, owner_name)
    print(full_base_path)

    if not os.path.isdir(full_base_path) :
        os.makedirs(full_base_path)
    if os.path.isdir(os.path.join(full_base_path, os.path.splitext(project_name)[0])) :
        edit_time = os.path.getatime(os.path.join(full_base_path, os.path.splitext(project_name)[0]))
        gap = time.time() - edit_time
        if gap >= 14400 :
            shutil.rmtree(os.path.join(full_base_path, os.path.splitext(project_name)[0]))
            subprocess.check_output('git clone {}'.format(URL), shell=True, cwd=full_base_path)
    else :
        subprocess.check_output('git clone {}'.format(URL), shell=True, cwd=full_base_path)

    full_base_path = os.path.join(full_base_path, os.path.splitext(project_name)[0])
    for file_path, value in content['working_list'].items() :
        file_path = os.path.normpath(file_path)
        if not os.path.splitext(file_path)[-1] == '.py' :
            continue
        full_file_path = os.path.join(full_base_path, file_path)
        if not os.path.exists(full_file_path) :
            continue

        converted_data['total_plus'][full_file_path[len(BASE_PATH)+1:]] = value['total_plus']
        converted_data['total_minus'][full_file_path[len(BASE_PATH) + 1:]] = value['total_minus']

        print("--- working_list ---")
        print("full_file_path : ", full_file_path)
        py_info = get_py_info(full_file_path)
        print("py_info : ", py_info)
        func_list, class_list = get_py_info_list(py_info)
        func_list.sort(key=lambda x : x[1])
        class_list.sort(key=lambda x : x[1])
        print("func_list : ", func_list)
        print("class_list : ", class_list)

        converted_data['func_list'][full_file_path[len(BASE_PATH) + 1:]] = func_list
        converted_data['class_list'][full_file_path[len(BASE_PATH) + 1:]] = class_list

        converted_data['git_diff'][content['repository_name']][full_file_path[len(BASE_PATH)+1:]] = []

        for chunk in value['edit_chuck'] :
            start, end = chunk
            flag = False
            temp_data = []
            for logic in func_list :
                if logic[2] < start or end < logic[1] :
                    continue
                temp_data = [logic[0], max(logic[1], start), min(logic[2], end) - max(logic[1], start) + 1]
                flag = True

            if flag is True:
                converted_data['git_diff'][content['repository_name']][full_file_path[len(BASE_PATH) + 1:]].append(temp_data)

            if flag is False:
                for i, logic in enumerate(class_list):
                    if logic[2] < start or end < logic[1] :
                        continue
                    temp_data = [logic[0], max(logic[1], start), min(logic[2], end) - max(logic[1], start) + 1]
                    flag = True

                if flag is True:
                    converted_data['git_diff'][content['repository_name']][full_file_path[len(BASE_PATH) + 1:]].append(temp_data)

            if flag is False:
                converted_data['git_diff'][content['repository_name']][full_file_path[len(BASE_PATH) + 1:]].append(['in', start, end - start + 1])

    for file_path, value in content['plus_list'].items() :
        file_path = os.path.normpath(file_path)
        if not os.path.splitext(file_path)[-1] == '.py' :
            continue
        full_file_path = os.path.join(full_base_path, file_path)
        if not os.path.exists(full_file_path) :
            continue

        converted_data['plus_list'][full_file_path[len(BASE_PATH) + 1:]] = value

    for file_path, value in content['minus_list'].items() :
        file_path = os.path.normpath(file_path)
        if not os.path.splitext(file_path)[-1] == '.py' :
            continue
        full_file_path = os.path.join(full_base_path, file_path)
        if not os.path.exists(full_file_path) :
            continue

        converted_data['minus_list'][full_file_path[len(BASE_PATH) + 1:]] = value

    for file_path, value in content['modify_file'].items() :
        file_path = os.path.normpath(file_path)
        if not os.path.splitext(file_path)[-1] == '.py' :
            continue
        full_file_path = os.path.join(full_base_path, file_path)
        if not os.path.exists(full_file_path) :
            continue

        converted_data['modify_file'][full_file_path[len(BASE_PATH) + 1:]] = value

    for file_path, value in content['git_diff_info'].items():
        file_path = os.path.normpath(file_path)
        if not os.path.splitext(file_path)[-1] == '.py':
            continue
        full_file_path = os.path.join(full_base_path, file_path)
        if not os.path.exists(full_file_path):
            continue
        converted_data['git_diff_info'][full_file_path[len(BASE_PATH) + 1:]] = value

    return converted_data


