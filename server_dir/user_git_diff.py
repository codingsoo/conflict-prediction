"""
    @file   user_git_diff.py
    @brief
        User git diff logic. Get user's working data, calling data, and user's last commit data.
"""
from pathlib import Path
import os
import json
import ast

class user_git_info:

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
            edit_amount[file_name]['git_diff_code'] = self.get_git_diff_info(file_name)

        return edit_amount

    def get_git_diff_info(self, file_name):
        git_diff_info = self.content['git_diff_info'][file_name]

        git_diff_code = "|||".join(git_diff_info).replace("'", "\\'")
        print("get_git_diff_info", git_diff_code)

        return git_diff_code


    def get_git_diff_code(self, file_name):
        minus_list = self.content['minus_list'][file_name]
        plus_list = self.content['plus_list'][file_name]
        modify_file = self.content['modify_file'][file_name]

        git_diff_code = ""
        git_diff_file = []

        for idx, line in enumerate(modify_file):
            git_diff_file.append(line)
            # print(idx, line)

        # 105번째가 수정되었으면, 104번째에서 -, 105번째에서 +
        for code, line in plus_list:
            git_diff_file[line - 1] = "+" + str(code) + "\n"
            # print("plus", line, git_diff_file[line - 1])

        for code, line in minus_list:
            git_diff_file[line] = "-" + str(code) + "\n" + git_diff_file[line]
            # print("minus", line, git_diff_file[line])

        # for idx, code in enumerate(git_diff_file):
        #     print(idx + 1, code)

        git_diff_code = "|||".join(git_diff_file).replace("'", "\\'")

        return git_diff_code

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
                    for call_dict_context in call_dict[file_name][plus_temp[1]]:
                        if call_dict_context is not None:
                            call_context = call_dict_context.split(".")
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
                            if plus_temp[1] not in calling_dict[file_name].keys():
                                calling_dict[file_name][plus_temp[1]] = []
                            calling_dict[file_name][plus_temp[1]].append({"file_path": file_path, "class_context": class_context[::-1], "func_name": func_name})

                            # # Except call in same file
                            # if file_path:
                            #     calling_dict[file_name][plus_temp[1]] = {"file_path": file_path, "class_context": class_context, "func_name": func_name}

        for file_name, temp_calling_list in calling_dict.items():
            for line_num, temp_calling_list_list in temp_calling_list.items():
                for temp_calling in temp_calling_list_list:
                    temp_logic = ""
                    if temp_calling['class_context']:
                        temp_logic += "class"
                        for temp_class in temp_calling['class_context']:
                            temp_logic += ":" + temp_class
                        temp_logic += ":" + temp_calling['func_name']

                    else:
                        temp_logic += "function:" + temp_calling['func_name']
                    temp_calling['logic'] = temp_logic

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

            elif isinstance(each, ast.With):
                self.extract_call(each, import_table, import_from_table, call_list_dict)

            elif isinstance(each, ast.Assign):
                if isinstance(each.value, ast.Call):
                    names = []
                    for name in each.targets:
                        if isinstance(name, ast.Name):
                            names.append(name.id)

                    for keyword in each.value.keywords:
                        if isinstance(keyword.value, ast.Call):
                            stack = self.get_extract_call_logic(keyword.value.func, import_table, import_from_table, assign_dict, names)
                            if each.lineno not in call_list_dict.keys():
                                call_list_dict[each.lineno] = []
                            call_list_dict[each.lineno].append(stack)

                    for arg in each.value.args:
                        if isinstance(arg, ast.Call):
                            stack = self.get_extract_call_logic(arg.func, import_table, import_from_table, assign_dict, names)
                            if each.lineno not in call_list_dict.keys():
                                call_list_dict[each.lineno] = []
                            call_list_dict[each.lineno].append(stack)

                    stack = self.get_extract_call_logic(each.value.func, import_table, import_from_table, assign_dict, names)
                    if each.lineno not in call_list_dict.keys():
                        call_list_dict[each.lineno] = []
                    call_list_dict[each.lineno].append(stack)

                elif isinstance(each.value, ast.BinOp):
                    if isinstance(each.value.left, ast.Call):
                        names = []
                        for name in each.targets:
                            if isinstance(name, ast.Name):
                                if name.id in assign_dict:
                                    del assign_dict[name.id]
                                names.append(name.id)
                        stack = self.get_extract_call_logic(each.value.left.func, import_table, import_from_table, assign_dict, names)
                        if each.lineno not in call_list_dict.keys():
                            call_list_dict[each.lineno] = []
                        call_list_dict[each.lineno].append(stack)

                    if isinstance(each.value.right, ast.Call):
                        names = []
                        for name in each.targets:
                            if isinstance(name, ast.Name):
                                if name.id in assign_dict:
                                    del assign_dict[name.id]
                                names.append(name.id)
                        stack = self.get_extract_call_logic(each.value.right.func, import_table, import_from_table, assign_dict, names)
                        if each.lineno not in call_list_dict.keys():
                            call_list_dict[each.lineno] = []
                        call_list_dict[each.lineno].append(stack)

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

                        stack = []
                        stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
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
                if isinstance(each.value, ast.Call):
                    for keyword in each.value.keywords:
                        if isinstance(keyword.value, ast.Call):
                            stack = []
                            cur = keyword.value.func
                            check = 0
                            while isinstance(cur, ast.Attribute):
                                if check == 0:
                                    stack.append(assign_dict.get(cur.attr, import_from_table.get(cur.attr, cur.attr)))
                                    check = 1
                                else:
                                    stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
                                cur = cur.value
                            if not isinstance(cur, ast.Name):
                                continue
                            stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id,cur.id))))
                            stack = stack[::-1]
                            stack = '.'.join(stack)
                            if each.lineno not in call_list_dict.keys():
                                call_list_dict[each.lineno] = []
                            call_list_dict[each.lineno].append(stack)

                    for arg in each.value.args:
                        if isinstance(arg, ast.Call):
                            stack = []
                            cur = arg.func
                            check = 0
                            while isinstance(cur, ast.Attribute):
                                if check == 0:
                                    stack.append(assign_dict.get(cur.attr, import_from_table.get(cur.attr, cur.attr)))
                                    check = 1
                                else:
                                    stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
                                cur = cur.value
                            if not isinstance(cur, ast.Name):
                                continue
                            stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
                            stack = stack[::-1]
                            stack = '.'.join(stack)
                            if each.lineno not in call_list_dict.keys():
                                call_list_dict[each.lineno] = []
                            call_list_dict[each.lineno].append(stack)

                    stack = []
                    cur = each.value.func
                    check = 0
                    while isinstance(cur, ast.Attribute):
                        if check == 0:
                            stack.append(assign_dict.get(cur.attr, import_from_table.get(cur.attr, cur.attr)))
                            check = 1
                        else:
                            stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
                        cur = cur.value
                    if not isinstance(cur, ast.Name):
                        continue
                    stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
                    stack = stack[::-1]
                    stack = '.'.join(stack)
                    if each.lineno not in call_list_dict.keys():
                        call_list_dict[each.lineno] = []
                    call_list_dict[each.lineno].append(stack)

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

    def get_extract_call_logic(self, cur, import_table, import_from_table, assign_dict, names):
        stack = []
        check = 0
        while isinstance(cur, ast.Attribute):
            if check == 0:
                stack.append(assign_dict.get(cur.attr, import_from_table.get(cur.attr, cur.attr)))
                check = 1
            else:
                stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
            cur = cur.value

        if not isinstance(cur, ast.Name):
            return
        stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
        stack = stack[::-1]
        stack = '.'.join(stack)
        for name in names:
            assign_dict[name] = stack

        return stack

    def get_last_commit_data(self):
        last_commit_date = ""
        git_log_name_only = self.content['git_log_name_only']
        for line in git_log_name_only:
            if line[:5] == 'Date:':
                last_commit_date = line
                break

        return last_commit_date

    def get_log_file_list(self):
        log_file_list = []
        git_log_name_only = self.content['git_log_name_only']

        pos_check = 0
        row = []
        for line in git_log_name_only:
            if line == '':
                pos_check += 1
                pos_check %= 3
                if pos_check == 0:
                    log_file_list.insert(0, row)
                    row = []
                continue

            if pos_check == 2:
                if line[:7] == 'commit ':
                    pos_check = 0
                    continue
                row.append(line)

        if row:
            log_file_list.insert(0, row)

        return log_file_list
