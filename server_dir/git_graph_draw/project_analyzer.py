import os

from server_dir.git_graph_draw import py_file_parser

def get_file_list( root ) :
    py_list = []
    for path, dirs, files in os.walk(root) :
        for file in files :
            if os.path.splitext(file)[-1] == '.py' :
                py_list.append(os.path.join(path, file))

    print("Get file list : ", py_list)
    return py_list

def insert_into_logic_dict(file_path, values, logic_dict):
    for value in values:
        if value['type'] == 'Class':
            id = 'class:' + value['name']
            logic_dict[file_path]['Class'].add(id)
            for each in value.get('members', []):
                if each['type'] == 'Class':
                    send_each = list()
                    send_each.append(each)
                    insert_into_logic_dict(file_path, send_each, logic_dict)
                elif each['type'] == 'Function':
                    logic_dict[file_path]['Function'].add(id + ':' + each['name'])

        elif value['type'] == 'Function':
            logic_dict[file_path]['Function'].add('function:' + value['name'])

def class_append_edge_list(full_path,func_id,owner,paths,project_dict,logic_dict,edges_list):
        if full_path + '.py' in project_dict:
            if 'class:' + paths[-1] in logic_dict[full_path + '.py']['Class']:
                pass
            elif 'function:' + paths[-1] in logic_dict[full_path + '.py']['Function']:
                edges_list.append([owner + '/' + full_path + '.py|' + 'function:' + paths[-1]],owner + '/' + func_id)
                pass
            elif 'class:' + paths[-2] + ':' + paths[-1] in logic_dict[full_path + '.py']['Function']:
                full_path_list = full_path.split("/")[1:]
                class_path_list = paths[:-1]
                for ele in full_path_list:
                    class_path_list.remove(ele)

                class_path = " "
                for element in class_path_list:
                    if (class_path == " "):
                        class_path = element
                    else:
                        class_path = class_path + ":" + element

                edges_list.append([owner + '/' + full_path + '.py|' + 'class:' + class_path + ':' + paths[-1], owner + '/' + func_id])
        else :
            full_path = full_path.split("/")[:-1]
            if (len(full_path) != 1):
                new_path = " "
                for each_path in full_path:
                    if (new_path == " "):
                        new_path = each_path
                    else:
                        new_path = new_path + "/" + each_path

                class_append_edge_list(new_path,func_id,owner, paths, project_dict, logic_dict, edges_list)


def func_append_edge_list(full_path,owner,paths,project_dict,logic_dict,edges_list):
    if full_path + '.py' in project_dict:
        if 'class:' + paths[-1] in logic_dict[full_path + '.py']['Class']:
            pass
        elif 'function:' + paths[-1] in logic_dict[full_path + '.py']['Function']:
            edges_list.append([owner + '/' + full_path + '|' + 'function:' + paths[-1]], owner + '/' + id)

    else :
        full_path = full_path.split("/")[:-1]
        if (len(full_path) != 1):
            new_path = " "
            for each_path in full_path:
                if (new_path == " "):
                    new_path = each_path
                else :
                    new_path = new_path + "/" + each_path

            func_append_edge_list(new_path,owner,paths,project_dict,logic_dict,edges_list)

def make_class_edge(owner, project_name, file_path, value, project_dict, logic_dict, edges_list):
    id = file_path + '|' + 'class:' + value['name']
    nexts = []
    for each in value.get('members', []):
        if each['type'] == 'Function':
            nexts.append([id + ':' + each['name'], each.get('members', [])])
        elif each['type'] == 'Class' :
            make_class_edge(owner,project_name,file_path,each,project_dict,logic_dict,edges_list)

    for func_id, func_members in nexts:
        for each in func_members:
            if each['type'] == 'Call':
                if not '.' in each['id']:
                    continue
                paths = each['id'].split('.')
                if len(paths) == 2:
                    full_path = project_name + '/' + paths[0]
                    if full_path + '.py' in project_dict:
                        if 'class:' + paths[-1] in logic_dict[full_path + '.py']['Class']:
                            pass
                        elif 'function:' + paths[-1] in logic_dict[full_path + '.py']['Function']:
                            edges_list.append(
                                [owner + '/' + full_path + '.py|' + 'function:' + paths[-1], owner + '/' + func_id])
                else:
                    real_paths = paths[:len(paths) - 2]
                    full_path = project_name
                    for each in real_paths:
                        full_path = full_path + '/' + each

                    if full_path + '.py' in project_dict:
                        if 'class:' + paths[-2] + ':' + paths[-1] in logic_dict[full_path + '.py']['Function']:

                            edges_list.append([owner + '/' + full_path + '.py|' + 'class:' + paths[-2] + ':' + paths[-1],owner + '/' + func_id])
                        pass
                    else:
                        full_path = full_path + '/' + paths[-2]
                        class_append_edge_list(full_path, func_id, owner, paths, project_dict, logic_dict, edges_list)

def make_func_edge(owner, project_name, file_path, value, project_dict, logic_dict, edges_list):
    id = file_path + '|' + 'function:' + value['name']
    for each in value.get('members', []):
        if each['type'] == 'Call':
            if not '.' in each['id']:
                continue
            paths = each['id'].split('.')
            if len(paths) == 2:
                full_path = project_name + '/' + paths[0]
                if full_path + '.py' in project_dict:
                    if 'class:' + paths[-1] in logic_dict[full_path + '.py']['Class']:
                        pass
                    elif 'function:' + paths[-1] in logic_dict[full_path + '.py']['Function']:
                        edges_list.append([owner + '/' + full_path + '|' + 'function:' + paths[-1], owner + '/' + id])
            else:
                real_paths = paths[:len(paths) - 2]
                full_path = project_name
                for each in real_paths:
                    full_path = full_path + '/' + each
                if full_path + '.py' in project_dict:
                    if 'class:' + paths[-2] + ':' + paths[-1] in logic_dict[full_path + '.py']['Function']:
                        edges_list.append([owner + '/' + full_path + '.py|' + 'class:' + paths[-2] + ':' + paths[-1],
                                           owner + '/' + id])
                    pass
                else:
                    full_path = full_path + '/' + paths[-2]
                    func_append_edge_list(full_path, owner, paths, project_dict, logic_dict, edges_list)

def run( root , owner) :
    project_dict = dict()
    project_name = os.path.basename(root)
    file_list = get_file_list(root)
    print("Project Name : {}".format(project_name))
    print("file_list : {}".format(file_list))
    print("Code Amount : {}".format(len(file_list)))

    for file_path in file_list :
        project_dict[os.path.join(file_path[len(root) - len(project_name):]).replace(os.sep, '/')] = py_file_parser.parsing_code(file_path)

    logic_dict = dict()
    for file_path, values in project_dict.items() :
        logic_dict[file_path] = {"Class": set(), "Function": set()}
        insert_into_logic_dict(file_path,values,logic_dict)

    edges_list = []

    for file_path, values in project_dict.items() :
        for value in values :
            if value['type'] == 'Class' :
                make_class_edge(owner,project_name,file_path,value,project_dict,logic_dict,edges_list)
            elif value['type'] =='Function' :
                make_func_edge(owner, project_name, file_path, value, project_dict, logic_dict, edges_list)

    return edges_list, logic_dict
