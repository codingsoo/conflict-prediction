"""
    @file   project_analyzer.py
    @brief
        After getting information from the py_file_parser, it analyzed the structure of the code.
        Which classes, functions the code have. Whether the function is in class or not.
"""

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

def class_append_edge_list(full_path,func_id,owner,paths,project_dict,logic_dict,edges_list, type = ""):
        if full_path + '.py' in project_dict:
            if 'class:' + paths[-1] in logic_dict[full_path + '.py']['Class'] and type == 'With':
                edges_list.append([owner + '/' + full_path + '.py|' + 'function:__enter__', owner + '/' + func_id])
                edges_list.append([owner + '/' + full_path + '.py|' + 'function:__exit__', owner + '/' + func_id])
                pass
            elif 'class:' + paths[-1] in logic_dict[full_path + '.py']['Class']:
                pass
            elif 'function:' + paths[-1] in logic_dict[full_path + '.py']['Function']:
                edges_list.append([owner + '/' + full_path + '.py|' + 'function:' + paths[-1], owner + '/' + func_id])
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

                if class_path == " ":
                    edges_list.append([owner + '/' + full_path + '.py|' + 'class:' + paths[-2] + ':' + paths[-1], owner + '/' + func_id])
                else:
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


def func_append_edge_list(full_path,owner,paths,project_dict,logic_dict,edges_list,id, type =""):
    if full_path + '.py' in project_dict:
        if 'class:' + paths[-1] in logic_dict[full_path + '.py']['Class'] and type == 'With':
            edges_list.append([owner + '/' + full_path + '.py|' + 'function:__enter__', owner + '/' + id])
            edges_list.append([owner + '/' + full_path + '.py|' + 'function:__exit__', owner + '/' + id])
            pass
        elif 'class:' + paths[-1] in logic_dict[full_path + '.py']['Class']:
            pass
        elif 'function:' + paths[-1] in logic_dict[full_path + '.py']['Function']:
            edges_list.append([owner + '/' + full_path + '.py|' + 'function:' + paths[-1], owner + '/' + id])

    else :
        full_path = full_path.split("/")[:-1]
        if (len(full_path) != 1):
            new_path = " "
            for each_path in full_path:
                if (new_path == " "):
                    new_path = each_path
                else :
                    new_path = new_path + "/" + each_path

            func_append_edge_list(new_path,owner,paths,project_dict,logic_dict,edges_list,id)

def make_class_edge(owner, project_name, file_path, value, project_dict, logic_dict, edges_list,outer_class = ""):
    if(outer_class == ""):
        id = file_path + '|' + 'class:' + value['name']
    else:
        id = file_path + '|' + 'class:' +outer_class + ":"+ value['name']
    nexts = []
    for each in value.get('members', []):
        if each['type'] == 'Function':
            nexts.append([id + ':' + each['name'], each.get('members', [])])
            edges_list.append([owner + '/' + id + ':' + each['name'], owner + '/' + id + ':' + each['name']])

        elif each['type'] == 'Class' :
            if (outer_class == ""):
                outer_class = value['name']
            else:
                outer_class = outer_class + ":" + value['name']
            make_class_edge(owner,project_name,file_path,each,project_dict,logic_dict,edges_list,outer_class)

    for func_id, func_members in nexts:
        for each in func_members:
            if each['type'] == 'Call'or each['type'] == 'With':
                type = each['type']
                if not '.' in each['id']:
                    continue
                paths = each['id'].split('.')
                if len(paths) == 2:
                    full_path = project_name + '/' + paths[0]
                    if full_path + '.py' in project_dict:
                        if 'class:' + paths[-1] in logic_dict[full_path + '.py']['Class']:
                            pass
                        elif 'function:' + paths[-1] in logic_dict[full_path + '.py']['Function']:
                            edges_list.append([owner + '/' + full_path + '.py|' + 'function:' + paths[-1], owner + '/' + func_id])
                        elif 'class:'+paths[-1] in logic_dict[full_path + '.py']['Function']:
                            edges_list.append([owner + '/' + full_path + '.py|' + 'class:' + paths[-1], owner + '/' + func_id])

                    else:
                        if 'class:' + paths[-1] in logic_dict[file_path]['Class']:
                            pass
                        elif 'function:' + paths[0]+':'+paths[1] in logic_dict[file_path]['Function'] :
                            edges_list.append([owner + '/' + file_path + 'function:' + paths[0]+':'+paths[1], owner + '/' + func_id])
                        elif 'class:' + paths[0]+':'+paths[1] in logic_dict[file_path]['Function']:
                            edges_list.append([owner + '/' + file_path + '|class:'+ paths[0]+':'+paths[1], owner + '/' + func_id])
                else:
                    real_paths = paths[:len(paths) - 2]
                    full_path = project_name
                    for each in real_paths:
                        full_path = full_path + '/' + each

                    if full_path + '.py' in project_dict:
                        if 'class:' + paths[-2] + ':' + paths[-1] in logic_dict[full_path + '.py']['Function']:
                            edges_list.append([owner + '/' + full_path + '.py|'  + 'class:' + paths[-2] + ':' + paths[-1],owner + '/' + func_id])
                        pass
                    else:
                        full_path = full_path + '/' + paths[-2]
                        class_append_edge_list(full_path, func_id, owner, paths, project_dict, logic_dict, edges_list, type)

def make_func_edge(owner, project_name, file_path, value, project_dict, logic_dict, edges_list):
    id = file_path + '|' + 'function:' + value['name']

    edges_list.append([owner + '/' + id, owner + '/' + id])

    for each in value.get('members', []):
        if each['type'] == 'Call' or each['type'] == 'With':
            type = each['type']
            if '.' in each['id']:
                paths = each['id'].split('.')
            else :
                paths = [each['id']]

            if len(paths) == 2:
                full_path = project_name + '/' + paths[0]
                if full_path + '.py' in project_dict:
                    if 'class:' + paths[-1] in logic_dict[full_path + '.py']['Class']:
                        pass
                    elif 'function:' + paths[-1] in logic_dict[full_path + '.py']['Function']:
                        edges_list.append([owner + '/' + full_path + '.py|' + 'function:' + paths[-1], owner + '/' + id])
                else:
                    if 'class:' + paths[-1] in logic_dict[file_path]['Class']:
                        pass
                    elif 'function:' + paths[0] + ':' + paths[1] in logic_dict[file_path]['Function']:
                        edges_list.append(
                            [owner + '/' + file_path + '|function:' + paths[0] + ':' + paths[1], owner + '/' + id])
                    elif 'class:' + paths[0] + ':' + paths[1] in logic_dict[file_path]['Function']:
                        edges_list.append([owner + '/' + file_path + '|class:' + paths[0] + ':' + paths[1], owner + '/' + id])

            elif len(paths) == 1:
                if 'class:' + paths[0] in logic_dict[file_path]['Class']:
                    pass
                elif 'function:' + paths[0] in logic_dict[file_path]['Function']:
                    edges_list.append(
                        [owner + '/' + file_path + '|function:' + paths[0], owner + '/' + id])
                elif 'class:' + paths[0] in logic_dict[file_path]['Function']:
                    edges_list.append(
                        [owner + '/' + file_path + '|class:' + paths[0], owner + '/' + id])
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
                    func_append_edge_list(full_path, owner, paths, project_dict, logic_dict, edges_list,id,type)



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

    file_information = dict()

    for file_full_path in file_list:
        file_path = owner + '/' + os.path.join(file_full_path[len(root) - len(project_name):]).replace(os.sep, '/')
        file_information[file_path] = dict()

        with open(file_full_path, 'r', encoding='utf-8') as f:
            total_lines = len(f.readlines())

        file_information[file_path]['total_lines'] = total_lines

    return edges_list, logic_dict, file_information
