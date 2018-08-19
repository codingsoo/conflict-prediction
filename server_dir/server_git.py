from server_dir.python_logic_parser import *
from server_dir.direct_work_database import *
from server_dir.user_git_diff import *
from server_dir.indirect_work_database import *

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
BASE_PATH = os.path.pardir


def git_diff_logic(content):

    # Create user git diff data
    user_data = user_git_diff(content)

    # Create direct and indirect database connection
    w_db = direct_work_database()
    iw_db = indirect_work_database()

    # Delete current user data
    w_db.delete_user_data(user_data.get_user_name())

    # Detect direct conflict
    w_db.detect_direct_conflict(user_data.get_proj_name(),
                                user_data.get_working_data(),
                                user_data.get_user_name())

    # Detect indirect conflict
    iw_db.detect_indirect_conflict(user_data.get_proj_name(),
                                   user_data.get_working_data(),
                                   user_data.get_user_name())

    # Insert current user data
    w_db.insert_user_data(user_data.get_proj_name(),
                          user_data.get_working_data(),
                          user_data.get_user_name())

    # Close direct and indirect database connection
    w_db.close_db()
    iw_db.close_db()
    return


def convert_data(content) :

    converted_data = dict()
    converted_data['git_id'] = content['user_email']
    converted_data['git_diff'] = dict()
    print(content['repository_name'])
    content_list = content['repository_name'].split('/')
    owner_name, project_name = content_list[-2], content_list[-1]
    content['repository_name'] = owner_name + '/' + project_name
    converted_data['git_diff'][content['repository_name']] = dict()


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
        print(full_file_path)
        py_info = get_py_info(full_file_path)
        func_list, class_list = get_py_info_list(py_info)
        func_list.sort(key=lambda x : x[1])
        class_list.sort(key=lambda x : x[1])

        converted_data['git_diff'][content['repository_name']][full_file_path[len(BASE_PATH)+1:]] = []

        for chunk in value['edit_chuck'] :
            start, end = chunk
            flag = False
            for logic in func_list :
                if logic[2] < start or end < logic[1] :
                    continue
                converted_data['git_diff'][content['repository_name']][full_file_path[len(BASE_PATH)+1:]].append([ logic[0], max(logic[1], start), min(logic[2], end) - max(logic[1], start) + 1])
                flag = True
                low, high = -1, len(class_list) - 1
            for i, logic in enumerate(class_list):
                if logic[2] < start or end > logic[1] :
                    continue
                converted_data['git_diff'][content['repository_name']][full_file_path[len(BASE_PATH)+1:]].append([ logic[0], max(logic[1], start), min(logic[2], end) - max(logic[1], start) + 1])
                flag = True
            if flag == False :
                converted_data['git_diff'][content['repository_name']][full_file_path[len(BASE_PATH) + 1:]].append(['in', start, end - start + 1])

    return converted_data


