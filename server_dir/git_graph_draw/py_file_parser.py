import ast

import_table = {}
import_from_table = {}

def get_end_of_logic( node ) :
    last_body = node.body[-1]
    while isinstance(last_body, (ast.For, ast.While, ast.If, ast.FunctionDef, ast.With, ast.ClassDef)):
        last_body = last_body.body[-1]
    return last_body.lineno

def get_logic_info( node, logic_info, assign_dict = {}):
    for each in node.body :

        if isinstance(each, ast.FunctionDef):
            function_info = {'type': 'Function', 'name': each.name, 'start': each.lineno, 'end': get_end_of_logic(each)}
            ret_list = []
            get_logic_info( each, ret_list )
            if len(ret_list) != 0:
                function_info['members'] = ret_list
            logic_info.append (function_info)

        elif isinstance(each, ast.ClassDef):
            function_info = {'type': 'Class', 'name': each.name, 'start': each.lineno, 'end': get_end_of_logic(each)}
            ret_list = []
            get_logic_info(each, ret_list)
            if len(ret_list) != 0 :
                function_info['members'] = ret_list
            logic_info.append(function_info)
            pass

        elif isinstance(each, ast.For):
            get_logic_info(each, logic_info, assign_dict)

        elif isinstance(each, ast.While) :
            get_logic_info(each, logic_info, assign_dict)

        elif isinstance(each, ast.If) :
            get_logic_info(each, logic_info, assign_dict)

        elif isinstance(each, ast.With):
            cur = each.items[0].context_expr
            if isinstance(cur, ast.Call):
                for arg in cur.args:
                    if isinstance(arg, ast.Call):
                        get_attribute_logic(arg.func, assign_dict, logic_info, type='Call')

                cur = cur.func
                if isinstance(cur, ast.Name):
                    logic_info.append({'type': 'With', 'id': cur.id})
                elif isinstance(cur, ast.Attribute):
                    get_attribute_logic(cur, assign_dict, logic_info, type='With')

            get_logic_info(each, logic_info, assign_dict)

        elif isinstance(each, ast.Assign):
            if isinstance(each.value, ast.Call) :
                names = []
                for name in each.targets :
                    if isinstance(name, ast.Name) :
                        print("each.target == Name | name.id : ", name.id)
                        if name.id in assign_dict :
                            del assign_dict[name.id]
                        names.append(name.id)

                for keyword in each.value.keywords:
                    if isinstance(keyword.value, ast.Attribute):
                        get_attribute_logic(keyword.value, assign_dict, logic_info, type='Call')

                    if isinstance(keyword.value, ast.Call):
                        get_attribute_logic(keyword.value.func, assign_dict, logic_info, type='Call')

                for arg in each.value.args:
                    if isinstance(arg, ast.Attribute):
                        get_attribute_logic(arg, assign_dict, logic_info, type='Call')

                    if isinstance(arg, ast.Call):
                        get_attribute_logic(arg.func, assign_dict, logic_info, type='Call')

                stack = []
                cur = each.value.func
                check = 0
                while isinstance(cur, ast.Attribute)  :
                    if check == 0:
                        stack.append(assign_dict.get(cur.attr, import_from_table.get(cur.attr, cur.attr)))
                        check = 1
                    else:
                        stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
                    cur = cur.value
                if not isinstance(cur, ast.Name) :
                    continue
                stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
                stack = stack[::-1]
                stack = '.'.join(stack)
                for name in names :
                    assign_dict[name] = stack
                logic_info.append({'type': 'Call', 'id': stack})
                get_attribute_logic(each.value.func, assign_dict, logic_info, type='Call')

            elif isinstance(each.value, ast.BinOp):
                if isinstance(each.value.left, ast.Call):
                    names = []
                    for name in each.targets:
                        if isinstance(name, ast.Name):
                            if name.id in assign_dict:
                                del assign_dict[name.id]
                            names.append(name.id)

                    for arg in each.value.left.args:
                        if isinstance(arg, ast.Call):
                            get_attribute_logic(arg.func, assign_dict, logic_info, type='Call')

                    stack = []
                    cur = each.value.left.func
                    while isinstance(cur, ast.Attribute):
                        stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
                        cur = cur.value
                    if not isinstance(cur, ast.Name):
                        continue
                    stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
                    stack = stack[::-1]
                    stack = '.'.join(stack)
                    for name in names:
                        assign_dict[name] = stack
                    logic_info.append({'type': 'Call', 'id': stack})

                if isinstance(each.value.right, ast.Call):
                    names = []
                    for name in each.targets:
                        if isinstance(name, ast.Name):
                            if name.id in assign_dict:
                                del assign_dict[name.id]
                            names.append(name.id)

                    for arg in each.value.right.args:
                        if isinstance(arg, ast.Call):
                            get_attribute_logic(arg.func, assign_dict, logic_info, type='Call')

                    stack = []
                    cur = each.value.right.func
                    while isinstance(cur, ast.Attribute):
                        stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
                        cur = cur.value
                    if not isinstance(cur, ast.Name):
                        continue
                    stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
                    stack = stack[::-1]
                    stack = '.'.join(stack)
                    for name in names:
                        assign_dict[name] = stack
                    logic_info.append({'type': 'Call', 'id': stack})

        elif isinstance(each, ast.Expr) :
            if isinstance(each.value, ast.Call) :
                for arg in each.value.args:
                    if isinstance(arg, ast.Call):
                        get_attribute_logic(arg.func, assign_dict, logic_info, type='Call')

                get_attribute_logic(each.value.func, assign_dict, logic_info, type='Call')

        elif isinstance(each, ast.Import):
            for name in each.names :
                if name.asname != None:
                    import_table[name.asname] = name.name

        elif isinstance(each, ast.ImportFrom) :
            module = each.module
            for name in each.names :
                if name.asname == None :
                    import_from_table[name.name] = module + '.' + name.name
                else :
                    import_from_table[name.asname] = module + '.' + name.name

def get_attribute_logic(cur_arg, assign_dict, logic_info, type):
    stack = []
    cur = cur_arg
    check = 0
    inner = 0
    while isinstance(cur, ast.Attribute):
        if check == 0:
            stack.append(assign_dict.get(cur.attr, import_from_table.get(cur.attr, cur.attr)))
            check = 1
        else:
            stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
        cur = cur.value
    if isinstance(cur, ast.Call):
        inner = 1
        cur = cur.func

    if not isinstance(cur, ast.Name):
        return
    stack.append(
        assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
    stack = stack[::-1]
    stack = '.'.join(stack)
    logic_info.append({'type': type, 'id': stack})

def load_file( file_path ) :
    with open(file_path, 'r', encoding='utf-8') as f :
        context = f.readlines()
    return context

def parsing_code( file_path ) :
    logic_info = list()
    context = load_file( file_path )
    parse_tree = ast.parse(''.join(context))
    get_logic_info(parse_tree, logic_info)
    return logic_info
