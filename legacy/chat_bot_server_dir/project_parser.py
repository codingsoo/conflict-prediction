import os
import time
import shutil
import subprocess

from chat_bot_server_dir.python_logic_parser import *

BASE_PATH = os.path.pardir

def project_parser( owner_name, project_name ) :
    URL = "https://github.com/{}/{}".format(owner_name, project_name)
    full_base_path = os.path.join(BASE_PATH, owner_name)

    if not os.path.isdir(full_base_path) :
        os.makedirs(full_base_path)
    if os.path.isdir(os.path.join(full_base_path, os.path.splitext(project_name)[0])) :
        edit_time = os.path.getatime(os.path.join(full_base_path, os.path.splitext(project_name)[0]))
        gap = time.time() - edit_time
        if gap >= 14400:
            shutil.rmtree(os.path.join(full_base_path, os.path.splitext(project_name)[0]))
            subprocess.check_output('git clone {}'.format(URL), shell=True, cwd=full_base_path)
    else :
        subprocess.check_output('git clone {}'.format(URL), shell=True, cwd=full_base_path)
    full_base_path = os.path.join(full_base_path, os.path.splitext(project_name)[0])

    ret_dict = {
        "file" : [],
        "function" : [],
        "class" : []
    }

    for path, dirs, files in os.walk(full_base_path) :
        for file in files :
            if os.path.splitext(file)[-1] == '.py':
                full_file_path = os.path.join(path, file)
                file_path = full_file_path[len(full_base_path)+1:]
                ret_dict['file'].append(file_path)
                py_info = get_py_info(full_file_path)
                func_list, class_list = get_py_info_list(py_info)
                func_list = [ file_path+'|'+each[0] for each in func_list ]
                class_list = [ file_path+'|'+each[0] for each in class_list ]
                ret_dict["function"].extend(func_list)
                ret_dict["class"].extend(class_list)

    return ret_dict