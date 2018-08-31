#-*- coding:utf-8 -*-
import re, os, subprocess
from pathlib import Path

BASE_PATH = ''

regex = r'^Author: ([가-힣a-zA-Z\s]+) <[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}>$'
email_regex = r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}'

p = re.compile(regex)
email_p = re.compile(email_regex)

def get_user_email(project_name, file_path, start_line, end_line) :
    if project_name[:-4] in file_path:
        slice_start = len(project_name[:-4]) + 1
        file_path = file_path[slice_start:]
    print(Path(os.getcwd()))
    BASE_PATH = Path(os.getcwd()).parent
    full_base_path = os.path.normpath(os.path.join(BASE_PATH, project_name[:-4]))
    if not os.path.exists(full_base_path) :
        return []
    else :
        full_file_path = os.path.join(full_base_path, file_path)
        if not os.path.exists(full_file_path) :
            return []
        else :
            ret_list = []
            command = 'git log -L {},{}:{}'.format(start_line, end_line, file_path.replace(os.sep, '/'))
            lines = subprocess.check_output(command, shell=True, universal_newlines=True, cwd=full_base_path, encoding='UTF-8').splitlines()
            for line in lines :
                if p.match(line) != None :
                    ret_list.extend(email_p.findall(line))

    ret_list = list(set(ret_list))
    print(ret_list)
    return ret_list

if __name__ == '__main__' :
    get_user_email('conflict-detector', 'git_graph_draw\\git_graph_draw.py', 1, 3)