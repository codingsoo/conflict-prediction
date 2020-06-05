import re
import subprocess
from server_dir.git_graph_draw.project_analyzer import run
from flask import Flask, request
from server_dir.git_graph_draw.python_floyd import create_indirect_edge_list
import pymysql
from server_dir.server_config_loader import *
from server_dir.user_database import user_database
# Create Server
app = Flask(__name__)


# File definition
# os.path.join(os.getcwd(), 'UCI_chatbot_Server')
file_dir = []
file_name = []

# Dependency definition
file_dependency = {}
file_content_list = dict()

class mysql_conn:

    def __init__(self):
        # Load mysql database connection config
        host, user, password, db, charset = load_database_connection_config("grandparent")

        # get mysql database connection
        self.conn = pymysql.connect(host=host,
                                    user=user,
                                    password=password,
                                    db=db,
                                    charset=charset)
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()


# Search All Directory And Append simple file name
def search_directory(url):
    repo = os.path.basename(url)
    for (file_path, dir, files) in os.walk(url):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.py':
                sub_file_path = repo + file_path[len(url):]
                # print("%s/%s" % (sub_file_path, filename))
                file_dir.append(os.path.join(sub_file_path, filename))
                file_name.append(filename[:len(filename)-3])

    print("file_dir: " + str(file_dir))
    print("file_name : " + str(file_name))

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
        simple_file_name = str(temp_dir).split('\\')
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
                    def_dep = False

            # Read Each token
            for temp_token in temp_line:

                # Generate file dependency [keyword : import]
                if temp_token == "import":
                    import_file = temp_line[index + 1]

                    # Search import file list
                    for temp_file_dir in file_dir:
                        temp1_file_dir = str(temp_file_dir).split('\\')
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
                        temp_list.append(temp_dir + '|' + 'class:' + class_name[6:] + ':' + def_name[4:])
                        temp_list.append(temp_dir + '|' + 'class:' + class_name[6:])
                        content_dependency_list.append(temp_list)
                        all_dependency_list.append(temp_list)
                        break

                # Import function dependency
                elif re.findall(str("  "), file_line) != None:

                    # function - function call dependency
                    if def_dep:

                        # Search all directory
                        for t_dir in file_dir:

                            # Search other directory
                            if t_dir != temp_dir:

                                # Read clear function, class name
                                func_name_list = convert_func_name(file_content_list[t_dir])

                                # Search about usage of function
                                for temp_func_name in func_name_list:
                                    find_flag = temp_token.find(temp_func_name)

                                    # Find function dependency
                                    if find_flag > 0:
                                        temp_func_list = []
                                        print("temp_func_name : " +str(temp_func_name))
                                        temp_func_list.append(t_dir + '|function:' + temp_func_name)

                                        # class dependency discriptor
                                        if class_dep:
                                            temp_func_list.append(temp_dir + '|' + 'class:' + class_name[6:])
                                        else:
                                            temp_func_list.append(temp_dir + '|' + 'function:' + def_name[4:])

                                        content_dependency_list.append(temp_func_list)
                                        all_dependency_list.append(temp_func_list)
                                        break

                    # function - class call dependency
                    elif class_dep:

                        # Search all directory
                        for t_dir in file_dir:

                            # Search other directory
                            if t_dir != temp_dir:

                                # Read clear function, class name
                                class_name_list = convert_class_name(file_content_list[t_dir])

                                # Search about usage of function
                                for temp_class_name in class_name_list:
                                    find_flag = temp_token.find(temp_class_name)

                                    # Find Class dependency
                                    if find_flag > 0:
                                        temp_func_list = []

                                        print("temp_class_name : " +str(temp_class_name))
                                        print("class_name : " + str(class_name))

                                        temp_func_list.append(t_dir + '|class:' + temp_class_name)
                                        temp_func_list.append(temp_dir + '|class:' + class_name)
                                        content_dependency_list.append(temp_func_list)
                                        all_dependency_list.append(temp_func_list)
                                        break

            # index plus
                index += 1

        #print content_dependency_list

    return all_dependency_list


def convert_func_name(raw_name_list):

    convert_name_list = []

    for raw_name in raw_name_list:

        split_name = str(raw_name).split(' ')

        if(split_name[0] == "def"):
            temp_name_list = split_name[1].split('(')
            temp_name = temp_name_list[0]
            convert_name_list.append(temp_name)

    return convert_name_list


def convert_class_name(raw_name_list):

    convert_name_list = []

    for raw_name in raw_name_list:

        split_name = str(raw_name).split(' ')

        if(split_name[0] == "class"):
            temp_name = split_name[1]

            if(temp_name[-1] == ':'):
                temp_name = temp_name[:-1]

            convert_name_list.append(temp_name)

    print(convert_name_list)
    return convert_name_list


def create_edge(raw_list):

    # print "raw_list"
    # print raw_list

    for dep_obj in raw_list:
        for compare_dep in raw_list:

            if dep_obj[1] == compare_dep[0]:
                new_temp = []
                new_temp.append(dep_obj[0])
                new_temp.append(compare_dep[1])

                raw_list.append(new_temp)

    #print raw_list

# # Post To Server
# def postToServer(uri, json_data):
#
#     # Create URL
#     url = "http://" + ip_addr + ":" + port + uri # 80
#
#     # Headers
#     headers = {'Content-Type': 'application/json; charset=utf-8'}
#
#     # Post To Server
#     req = requests.post(url, headers=headers, data = json.dumps(json_data))
#
#     # Log
#     print(req)
#
#     return req


# Git clone using user URL
def gitCloneFromURL(git_url):

    cmd_line = 'git clone ' + git_url
    git_dir_name = git_url.split('/')[4]
    root_dir_temp = os.path.join(os.getcwd(), git_dir_name)

    print(root_dir_temp)

    # git clone from user git url
    subprocess.check_output(cmd_line, shell=True)

    return root_dir_temp


# Remove exists dir
def removeDir(root_dir_temp):

    print(root_dir_temp)

    # shutil.rmtree(root_dir_temp)

    # windows
    #cmd_line = 'rmdir /S /Q ' + root_dir_temp

    #linux
    cmd_line = 'rm -rf ' + root_dir_temp

    subprocess.check_output(cmd_line, shell=True)

def store_file_information(repository_name, file_information):

    mysql_conn_obj = mysql_conn()

    for file_path, temp_file_inforamation in file_information.items():
        try:
            sql = "replace into file_information " \
                  "(project_name, file_name, total_lines) " \
                  "value ('%s', '%s', '%d')" % (repository_name, file_path, temp_file_inforamation['total_lines'])

            print(sql)
            mysql_conn_obj.cursor.execute(sql)
            mysql_conn_obj.conn.commit()

        except:
            mysql_conn_obj.conn.rollback()
            print("ERROR : store_file_information")

    # remove not currenct value
    raw_list = []

    try:
        sql = "select file_name " \
              "from file_information " \
              "where project_name = '%s'" \
              % (repository_name)

        print(sql)
        mysql_conn_obj.cursor.execute(sql)
        mysql_conn_obj.conn.commit()

        raw_list = list(mysql_conn_obj.cursor.fetchall())

    except:
        mysql_conn_obj.conn.rollback()
        print("ERROR : store_file_information2")

    remove_list = raw_list[:]

    for file_path in file_information.keys():
        for raw in raw_list:
            if raw[0] == file_path:
                remove_list.remove(raw)

    for temp_remove_list in remove_list:
        try:
            sql = "delete " \
                  "from file_information " \
                  "where project_name = '%s' " \
                  "and file_name = '%s' " \
                  % (repository_name, temp_remove_list[0])

            print(sql)
            mysql_conn_obj.cursor.execute(sql)
            mysql_conn_obj.conn.commit()
        except:
            mysql_conn_obj.conn.rollback()
            print("ERROR : store_file_information3")


    mysql_conn_obj.close()

    return

def store_graph_to_db(repository_name, graph_list):

    mysql_conn_obj = mysql_conn()

    try:
        sql = "replace into logic_dependency " \
              "(project_name, def_func, call_func, length) " \
              "values"

        for temp_graph in graph_list:
            sql += " ('%s', '%s', '%s', %d), " %(repository_name, temp_graph[0].replace('\\', '/'), temp_graph[1].replace('\\', '/'), temp_graph[2])

        sql = sql[:-2]

        print(sql)
        mysql_conn_obj.cursor.execute(sql)
        mysql_conn_obj.conn.commit()

    except:
        mysql_conn_obj.conn.rollback()
        print("ERROR : insert graph info")

    try:
        sql = "select * " \
              "from logic_dependency " \
              "where project_name = '%s' " % (repository_name)

        print(sql)
        mysql_conn_obj.cursor.execute(sql)
        mysql_conn_obj.conn.commit()

        raw_list = list(mysql_conn_obj.cursor.fetchall())

    except:
        mysql_conn_obj.conn.rollback()
        print("ERROR : insert graph info")

    remove_list = raw_list[:]

    for temp_graph in graph_list:
        for raw in raw_list:
            if temp_graph[0].replace('\\', '/') == raw[1] and temp_graph[1].replace('\\', '/') == raw[2]:
                remove_list.remove(raw)

    for temp_remove in remove_list:
        try:
            sql = "delete " \
                  "from logic_dependency " \
                  "where project_name = '%s' " \
                  "and def_func = '%s' " \
                  "and call_func = '%s' " \
                  % (repository_name, temp_remove[1], temp_remove[2])

            print(sql)
            mysql_conn_obj.cursor.execute(sql)
            mysql_conn_obj.conn.commit()

        except:
            mysql_conn_obj.conn.rollback()
            print("ERROR : insert graph info")


    mysql_conn_obj.close()

    return


def insert_function_list(project_name, logic_dict):
    mysql_conn_obj = mysql_conn()

    try:
        sql = "insert into function_list " \
              "(project_name, file_name, logic)" \
              "values "
        for file_name, temp_logic_list in logic_dict.items():
            for temp_logic in temp_logic_list['Function']:
                sql += "('%s', '%s', '%s'), " % (project_name, file_name, temp_logic)
        sql = sql[:-2]
        print(sql)
        mysql_conn_obj.cursor.execute(sql)
        mysql_conn_obj.conn.commit()
    except:
        mysql_conn_obj.conn.rollback()
        print("ERROR : insert functino list")

    mysql_conn_obj.close()


def indirect_logic(git_repository_name):

    # git clone from user git url
    print("git_repository_name : " + str(git_repository_name))
    git_repository_name_temp = str(git_repository_name).split('/')[0]
    print("git_repository_name_temp : " + str(git_repository_name_temp))
    root_dir_temp = gitCloneFromURL("https://github.com/" + str(git_repository_name))
    root_dir_temp = root_dir_temp[:len(root_dir_temp)-4]
    print("root_dir_temp: " + str(root_dir_temp))

    # search_directory(root_dir_temp)

    # generate_file_dependency()

    graph_data, logic_dict, file_information = run(root_dir_temp, git_repository_name_temp)

    print("graph data : " + str(graph_data))

    edge_list = create_indirect_edge_list(graph_data)

    print("edge_list: " + str(edge_list))

    store_file_information(git_repository_name, file_information)
    store_graph_to_db(git_repository_name, edge_list)
    insert_function_list(git_repository_name, logic_dict)

    # Remove exist dir
    removeDir(root_dir_temp)

    return

def is_empty_git_clone(repository_name):
    mysql_conn_obj = mysql_conn()
    raw_list = list()

    try:
        sql = "select * " \
              "from logic_dependency " \
              "where project_name = '%s'" \
              % (repository_name)

        print(sql)
        mysql_conn_obj.cursor.execute(sql)
        mysql_conn_obj.conn.commit()

        raw_list = list(mysql_conn_obj.cursor.fetchall())

    except:
        mysql_conn_obj.conn.rollback()
        print("ERROR : check git clone time")

    if raw_list:
        return False
    else:
        return True

def is_old_git_clone(repository_name):
    mysql_conn_obj = mysql_conn()
    raw_list = list()

    try:
        sql = "select * " \
              "from logic_dependency " \
              "where project_name = '%s' " \
              "and TIMEDIFF(now(),log_time) > 4*60*60" % (repository_name)

        print(sql)
        mysql_conn_obj.cursor.execute(sql)
        mysql_conn_obj.conn.commit()

        raw_list = list(mysql_conn_obj.cursor.fetchall())

    except:
        mysql_conn_obj.conn.rollback()
        print("ERROR : check git clone time")

    if raw_list:
        return True
    else:
        return False

@app.route('/repository_name', methods = ["GET", "POST"])
def repository_name():

    # Get User Git ID
    content = request.get_json(silent=True)

    git_repository_name = content['repository_name']
    git_id = content['user_email']

    u_db = user_database("grandparent")
    u_db.set_repository_name(git_id, git_repository_name)
    u_db.close()

    if is_empty_git_clone(git_repository_name) or is_old_git_clone(git_repository_name):
        indirect_logic(git_repository_name)

    return "Success repository name"


if __name__ == '__main__':

    # Load config
    host, port = load_git_graph_server_config("grandparent")

    # Run Server
    app.run(debug=True, host=host, port=port)

    # indirect_logic("j21chan/py_test.git")