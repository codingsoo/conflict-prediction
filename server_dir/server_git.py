from server_dir.python_logic_parser import *
from server_dir.work_database import *
from server_dir.user_git_diff import *

import os
import subprocess
import time
import shutil

"""
git diff logic
function    : detect direct conflict between the developers
parameter   : content_json
return      : none
"""

# BASE_PATH for clone repository.
BASE_PATH =""

def git_diff_logic(content):

    # create user git diff data
    user_data = user_git_diff(content)

    # create database object
    w_db = work_database()

    # delete current user data
    w_db.delete_user_data(user_data.get_user_name())

    # detect direct conflict
    w_db.detect_direct_conflict(project_name = user_data.get_proj_name(),
                                working_list = user_data.get_working_data(),
                                user_name    = user_data.get_user_name())

    # insert user data
    w_db.insert_user_data(project_name = user_data.get_proj_name(),
                          working_list = user_data.get_working_data(),
                          user_name    = user_data.get_user_name())

    # close database
    w_db.close_db()

    return


def convert_data(content) :
    converted_data = dict()
    converted_data['git_id'] = content['user_email']
    converted_data['git_diff'] = dict()
    converted_data['git_diff'][content['repository_name']] = dict()
    owner_name, project_name = content['repository_name'].split('/')

    URL = "https://github.com/{}/{}".format(owner_name, project_name)
    full_base_path = os.path.join(BASE_PATH, owner_name)

    if os.path.isdir(os.path.join(full_base_path, project_name)) :
        edit_time = os.path.getatime(os.path.join(full_base_path, project_name))
        gap = time.time() - edit_time
        if gap >= 14400 :
            shutil.rmtree(os.path.join(full_base_path, project_name))
            subprocess.check_output('git clone {}'.format(URL), shell=True, cwd=os.path.join(BASE_PATH, owner_name))
    else :
        subprocess.check_output('git clone {}'.format(URL), shell=True, cwd=os.path.join(BASE_PATH, owner_name))

    full_base_path = os.path.join(full_base_path, project_name)

    for each_work in content['working_list'] :
        for file_path, value in each_work :
            file_path = os.path.normpath(file_path)[2:]
            full_file_path = os.path.join(full_base_path, file_path)
            py_info = get_py_info(full_file_path)
            func_list, class_list = get_py_info_list(py_info)
            func_list.sort(key=lambda x : x[1])
            class_list.sort(key=lambda x : x[1])

            converted_data['git_diff'][content['repository_name']][full_file_path] = []

            for chunk in value['edit_chuck'] :
                start, end = chunk
                for logic in func_list :
                    if logic[2] < start or end > logic[1] :
                        continue
                    converted_data['git_diff'][content['repository_name']][full_file_path].append([ logic[0], max(logic[1], start), min(logic[2], end) - max(logic[1], start)])
                    low, high = -1, len(class_list) - 1
                for i, logic in enumerate(class_list):
                    if logic[2] < start or end > logic[1] :
                        continue
                    converted_data['git_diff'][content['repository_name']][full_file_path].append([ logic[0], max(logic[1], start), min(logic[2], end) - max(logic[1], start)])

    return converted_data


