from server_dir.server_git import *

if __name__ == "__main__":
    a = dict()
    b = dict()
    c = dict()
    c['file_name'] = "file_name"
    b['user_name'] = c
    a['project_name'] = b

    for t in a['project_name']['user_name'].keys():
        print(t)

    print(a)
    print(a['project_name']['user_name'].keys())