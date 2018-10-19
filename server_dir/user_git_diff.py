from pathlib import Path
import os
import json
import ast

class user_git_diff:

    # Constructor
    def __init__(self, content):
        self.content = content

        for proj_name_temp in self.content['git_diff'].keys():
            self.proj_name = proj_name_temp

        self.user_name = self.content['git_id']



    # getters
    def get_proj_name(self):
        return self.proj_name


    def get_user_name(self):
        return self.user_name


    def get_working_data(self):

        # working_list = [ ["file_name", "logic_name", "work_line", "work_amount"], ["file_name", "logic_name", "work_line", "work_amount"], ... ]
        working_list = []

        # get file dict
        temp_work_data_dict = self.content['git_diff'][self.proj_name]

        for file_name in temp_work_data_dict.keys():

            logic_list = temp_work_data_dict[file_name]
            # search each file name and each logic name
            # temp_work = ["file_name", "logic_name", "work_line", "work_amount"]
            for temp_logic in logic_list:
                temp_work = []
                temp_work.append(file_name.replace('\\', '/'))     # file_name
                temp_work.append(temp_logic[0]) # logic_name
                temp_work.append(temp_logic[1]) # work_line
                temp_work.append(temp_logic[2]) # work_amount

                # append temp_work
                working_list.append(temp_work)

        return working_list

    def get_edit_amount(self):

        edit_amount = dict()

        # get edit_amount
        for file_name, temp_amount in self.content['total_plus'].items():
            edit_amount[file_name] = dict()
            edit_amount[file_name]['total_plus'] = temp_amount
            edit_amount[file_name]['total_minus'] = self.content['total_minus'][file_name]

        return edit_amount

    def get_calling_data(self):
        call_dict = dict()
        calling_dict = dict()
        project_name = self.proj_name[:-4]

        for file_name, context_temp in self.content['modify_file'].items():
            call_dict[file_name] = dict()
            calling_dict[file_name] = dict()
            context = context_temp
            parse_tree = ast.parse(''.join(context))

            import_table = dict()
            import_from_table = dict()
            self.extract_call(parse_tree, import_table, import_from_table, call_dict[file_name])

            for plus_temp in self.content['plus_list'][file_name]:
                if plus_temp[1] in call_dict[file_name].keys():
                    call_context = call_dict[file_name][plus_temp[1]].split(".")
                    func_name = call_context[-1]
                    file_path_and_class_context = call_context[:-1]
                    file_path = ""
                    class_context = []
                    while file_path_and_class_context:
                        print(os.path.join(os.path.pardir, project_name, "/".join(file_path_and_class_context)) + ".py")
                        if os.path.exists(os.path.join(os.path.pardir, project_name, "/".join(file_path_and_class_context)) + ".py"):
                            file_path = os.path.join(project_name, "/".join(file_path_and_class_context)) + ".py"
                            break
                        class_context.append(file_path_and_class_context[-1])
                        file_path_and_class_context.pop()

                    # Include call in same file
                    if not file_path:
                        file_path = file_name
                    calling_dict[file_name][plus_temp[1]] = {"file_path": file_path, "class_context": class_context, "func_name": func_name}

                    # # Except call in same file
                    # if file_path:
                    #     calling_dict[file_name][plus_temp[1]] = {"file_path": file_path, "class_context": class_context, "func_name": func_name}

        for file_name, temp_calling_list in calling_dict.items():
            for line_num, temp_calling in temp_calling_list.items():
                temp_logic = ""
                if temp_calling['class_context']:
                    temp_logic += "class"
                    for temp_class in temp_calling['class_context']:
                        temp_logic += ":" + temp_class
                    temp_logic += ":" + temp_calling['func_name']

                else:
                    temp_logic += "function:" + temp_calling['func_name']
                calling_dict[file_name][line_num]['logic'] = temp_logic

        for file_name, call_list_dict in calling_dict.items():
            print("Final calling", file_name, " : ", calling_dict[file_name])

        return calling_dict


    def extract_call(self, node, import_table, import_from_table, call_list_dict, assign_dict=dict()):
        for each in node.body:

            if isinstance(each, ast.FunctionDef):
                self.extract_call(each, import_table, import_from_table, call_list_dict)

            elif isinstance(each, ast.ClassDef):
                self.extract_call(each, import_table, import_from_table, call_list_dict)

            elif isinstance(each, ast.For):
                self.extract_call(each, import_table, import_from_table, call_list_dict)

            elif isinstance(each, ast.While):
                self.extract_call(each, import_table, import_from_table, call_list_dict)

            elif isinstance(each, ast.If):
                self.extract_call(each, import_table, import_from_table, call_list_dict)

            elif isinstance(each, ast.Assign):
                print("--- Assign ---")
                if isinstance(each.value, ast.Call):
                    print("-- Call --")
                    names = []
                    for name in each.targets:
                        if isinstance(name, ast.Name):
                            print(" name.id : ", name.id)
                            names.append(name.id)
                    stack = []
                    cur = each.value.func
                    check = 0
                    while isinstance(cur, ast.Attribute):
                        if (check == 0):
                            stack.append(assign_dict.get(cur.attr, import_from_table.get(cur.attr, cur.attr)))
                            check = 1
                        else:
                            stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
                        print("stack while : ", stack)
                        cur = cur.value

                    print(cur)

                    if not isinstance(cur, ast.Name):
                        print("Done")
                        continue
                    print(cur.id)
                    stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
                    print("stack : ", stack)
                    stack = stack[::-1]
                    print("stack : ", stack)
                    stack = '.'.join(stack)
                    print("stack : ", stack)
                    for name in names:
                        assign_dict[name] = stack
                    call_list_dict[each.lineno] = stack

                elif isinstance(each.value, ast.BinOp):
                    if isinstance(each.value.left, ast.Call):
                        names = []
                        for name in each.targets:
                            if isinstance(name, ast.Name):
                                if name.id in assign_dict:
                                    del assign_dict[name.id]
                                names.append(name.id)
                        stack = []
                        cur = each.value.left.func
                        while isinstance(cur, ast.Attribute):
                            stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
                            cur = cur.value
                        if not isinstance(cur, ast.Name):
                            continue
                        stack.append(
                            assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
                        stack = stack[::-1]
                        stack = '.'.join(stack)
                        for name in names:
                            assign_dict[name] = stack
                        call_list_dict[each.lineno] = stack

                    if isinstance(each.value.right, ast.Call):
                        names = []
                        for name in each.targets:
                            if isinstance(name, ast.Name):
                                if name.id in assign_dict:
                                    del assign_dict[name.id]
                                names.append(name.id)
                        stack = []
                        cur = each.value.right.func
                        while isinstance(cur, ast.Attribute):
                            stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
                            cur = cur.value
                        if not isinstance(cur, ast.Name):
                            continue
                        stack.append(
                            assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
                        stack = stack[::-1]
                        stack = '.'.join(stack)
                        for name in names:
                            assign_dict[name] = stack
                        call_list_dict[each.lineno] = stack

                    if isinstance(each.value.left, ast.Name) or isinstance(each.value.right, ast.Name):
                        names = []
                        for name in each.targets:
                            if isinstance(name, ast.Name):
                                if name.id in assign_dict:
                                    del assign_dict[name.id]
                                names.append(name.id)
                        if isinstance(each.value.left, ast.Name) :
                            cur = each.value.left
                        elif isinstance(each.value.right, ast.Name):
                            cur = each.value.right

                        print(cur.id)
                        stack = []
                        stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
                        print("stack : ", stack)
                        stack = stack[::-1]
                        list = stack[0].split('.')[:-1]
                        class_name = ".".join(list)
                        check = 0
                        for key, ele in assign_dict.items():
                            if ele == class_name:
                                check = 1

                        if check == 0:
                            class_name = stack[0]

                        for name in names:
                            assign_dict[name] = class_name
                        call_list_dict[each.lineno] = class_name

            elif isinstance(each, ast.Expr):
                print("--- Expr ---")
                if isinstance(each.value, ast.Call):
                    print("-- Call --")
                    stack = []
                    cur = each.value.func
                    check = 0
                    while isinstance(cur, ast.Attribute):
                        if check == 0:
                            stack.append(assign_dict.get(cur.attr, import_from_table.get(cur.attr, cur.attr)))
                            check = 1
                        else:
                            stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
                        print("stack while : ", stack)
                        cur = cur.value
                    if not isinstance(cur, ast.Name):
                        continue
                    stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
                    print("stack : ", stack)
                    stack = stack[::-1]
                    print("stack : ", stack)
                    stack = '.'.join(stack)
                    print("stack : ", stack)
                    call_list_dict[each.lineno] = stack

            elif isinstance(each, ast.Import):
                for name in each.names:
                    if name.asname != None:
                        import_table[name.asname] = name.name

            elif isinstance(each, ast.ImportFrom):
                module = each.module
                for name in each.names:
                    if name.asname == None:
                        import_from_table[name.name] = module + '.' + name.name
                    else:
                        import_from_table[name.asname] = module + '.' + name.name
