#-*- coding:utf-8 -*-
import re, os, subprocess
from pathlib import Path

BASE_PATH = ''

email_regex = r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}'
# line_regex = r'\d+\)'
email_p = re.compile(email_regex)
# line_p = re.compile(line_regex)

def get_user_email(project_name, file_path, start_line, end_line) :
    if project_name[:-4] in file_path:
        slice_start = len(project_name[:-4]) + 1
        file_path = file_path[slice_start:]
    print(Path(os.getcwd()))
    BASE_PATH = Path(os.getcwd()).parent
    full_base_path = os.path.normpath(os.path.join(BASE_PATH, project_name[:-4]))
    if not os.path.exists(full_base_path):
        return []
    else :
        full_file_path = os.path.join(full_base_path, file_path)
        if not os.path.exists(full_file_path):
            return []
        else:
            ret_dict = dict()
            command = 'git blame --show-email -L {},{} ./{}'.format(start_line, end_line, file_path.replace(os.sep, '/'))
            lines = subprocess.check_output(command, shell=True, universal_newlines=True, cwd=full_base_path, encoding='UTF-8').splitlines()
            user_start_line = start_line
            current_line = start_line
            before_user_email = " "

            for line in lines:
                current_user_email = email_p.findall(line)[0]

                # line_info = line_p.findall(line)
                if(before_user_email == " "):
                    before_user_email = current_user_email

                if(current_user_email == before_user_email):
                    before_user_email = current_user_email
                    current_line += 1
                else :
                    if (before_user_email not in ret_dict) :
                        ret_dict[before_user_email] = [[user_start_line,current_line-1]]
                    else :
                        ret_dict[before_user_email].append([user_start_line,current_line-1])

                    before_user_email = current_user_email
                    user_start_line = current_line
                    current_line +=1

                if(current_line-1 == end_line):
                    if (current_user_email not in ret_dict) :
                        ret_dict[current_user_email] = [[user_start_line,current_line-1]]
                    else :
                        ret_dict[current_user_email].append([user_start_line,current_line-1])

    print(ret_dict)
    return ret_dict

if __name__ == '__main__' :
    get_user_email('conflict-detector', 'git_graph_draw\\git_graph_draw.py', 1, 3)