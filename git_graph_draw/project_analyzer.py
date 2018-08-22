import os, sys
from git_graph_draw import py_file_parser

def get_file_list( root ) :
    py_list = []
    for path, dirs, files in os.walk(root) :
        for file in files :
            if os.path.splitext(file)[-1] == '.py' :
                py_list.append(os.path.join(path, file))
    return py_list

def run( root ) :
    project_dict = dict()
    project_name = os.path.basename(root)
    file_list = get_file_list(root)
    print("Project Nmae : {}".format(project_name))
    print("Code Amount : {}".format(len(file_list)))

    for file_path in file_list :
        project_dict[os.path.join(file_path[len(root) - len(project_name):]).replace(os.sep, '/')] = py_file_parser.parsing_code(file_path)

    logic_dict = dict()
    for file_path, values in project_dict.items() :
        base_path = os.path.split(file_path)[0]
        logic_dict[file_path] = { "Class" : set(), "Function" : set() }
        for value in values :
            if value['type'] == 'Class' :
                id = 'class:' + value['name']
                logic_dict[file_path]['Class'].add(id)
                nexts = []
                for each in value.get('members', []) :
                    if each['type'] == 'Function' :
                        logic_dict[file_path]['Function'].add(id + ':' + each['name'])

            elif value['type'] =='Function' :
                logic_dict[file_path]['Function'].add('function:' + value['name'])



    edges_list = []
    for file_path, values in project_dict.items() :
        base_path = os.path.split(file_path)[0]
        for value in values :
            if value['type'] == 'Class' :
                id = file_path + '.py|' + 'class:' + value['name']
                nexts = []
                for each in value.get('members', []) :
                    if each['type'] == 'Function' :
                        nexts.append([ id + ':' + each['name'] , each.get('members', [])])
                for func_id, func_members in nexts :
                    for each in func_members :
                        if each['type'] == 'Call' :
                            if not '.' in each['id']:
                                continue
                            paths = each['id'].split('.')
                            if len(paths) == 2:
                                full_path = base_path + '/' + paths[0]
                                if full_path + '.py' in project_dict:
                                    if 'class:' + paths[-1] in logic_dict[full_path + '.py']['Class']:
                                        pass
                                    elif 'function:' + paths[-1] in logic_dict[full_path + '.py']['Function']:
                                        edges_list.append(['UCNLP/' + full_path + '.py|' + 'function:' + paths[-1], 'UCNLP/' + func_id])
                            else:
                                real_paths = paths[:len(paths) - 2]
                                full_path = base_path
                                for each in real_paths:
                                    full_path = full_path + '/' + each
                                if full_path + '.py' in project_dict:
                                    if 'class:' + paths[-2] + ':' + paths[-1] in logic_dict[full_path + '.py']['Function']:
                                        edges_list.append(['UCNLP/' + full_path + '.py|' + 'class:' + paths[-2] + ':' + paths[-1], 'UCNLP/' + func_id])
                                    pass
                                else:
                                    full_path = full_path + '/' + paths[-2]
                                    if full_path + '.py' in project_dict:
                                        if 'class:' + paths[-1] in logic_dict[full_path + '.py']['Class']:
                                            pass
                                        elif 'function:' + paths[-1] in logic_dict[full_path + '.py']['Function']:
                                            edges_list.append(['UCNLP/' + full_path + '.py|' + 'function:' + paths[-1]], 'UCNLP/' + func_id)
                                            pass


            elif value['type'] =='Function' :
                id = file_path + '.py|' + 'function:' + value['name']
                for each in value.get('members', []) :
                    if each['type'] == 'Call' :
                        if not '.' in each['id'] :
                            continue
                        paths = each['id'].split('.')
                        if len(paths) == 2 :
                            full_path = base_path + '/' + paths[0]
                            if full_path + '.py' in project_dict :
                                if 'class:' + paths[-1] in logic_dict[full_path + '.py']['Class']:
                                    pass
                                elif 'function:' + paths[-1] in logic_dict[full_path + '.py']['Function']:
                                    edges_list.append(['UCNLP/' + full_path + '|' + 'function:' + paths[-1], 'UCNLP/' + id])
                        else :
                            real_paths = paths[:len(paths) - 2]
                            full_path = base_path
                            for each in real_paths :
                                full_path = full_path + '/' + each
                            if full_path + '.py' in project_dict :
                                if 'class:' + paths[-2] + ':' + paths[-1] in logic_dict[full_path + '.py']['Function']:
                                    edges_list.append(['UCNLP/' + full_path + '.py|' + 'class:' + paths[-2] + ':' + paths[-1], 'UCNLP/' + id])
                                pass
                            else :
                                full_path = full_path + '/' + paths[-2]
                                if full_path + '.py' in project_dict :
                                    if 'class:' + paths[-1] in logic_dict[full_path + '.py']['Class'] :
                                        pass
                                    elif 'function:' + paths[-1] in logic_dict[full_path + '.py']['Function'] :
                                        edges_list.append(['UCNLP/' + full_path + '|' + 'function:' + paths[-1]], 'UCNLP/' + id)

    return edges_list