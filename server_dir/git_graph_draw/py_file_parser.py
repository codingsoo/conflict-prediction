import ast

import_table = {}
import_from_table = {}

def get_end_of_logic( node ) :
    last_body = node.body[-1]
    while isinstance(last_body, (ast.For, ast.While, ast.If, ast.FunctionDef, ast.With, ast.ClassDef)):
        last_body = last_body.body[-1]
    return last_body.lineno

def get_logic_info( node, logic_info, assign_dict = {}):
    print("##### assign_dict #####\n", assign_dict)
    print("##### import_table\n", import_table)
    for each in node.body :
        print("##### each ##### : ", each)

        if isinstance(each, ast.FunctionDef):
            print("--- FunctionDef --- : ", each.name)
            function_info = { 'type' : 'Function', 'name' : each.name, 'start' : each.lineno, 'end' : get_end_of_logic(each) }
            ret_list = []
            get_logic_info( each, ret_list )
            if len(ret_list) != 0 :
                function_info['members'] = ret_list
            logic_info.append (function_info)
        elif isinstance(each, ast.ClassDef):
            print("--- ClassDef --- : ", each.name)
            function_info = { 'type' : 'Class', 'name' : each.name, 'start' : each.lineno, 'end' : get_end_of_logic(each) }
            ret_list = []
            get_logic_info( each, ret_list )
            if len(ret_list) != 0 :
                function_info['members'] = ret_list
            logic_info.append(function_info)
            pass
        elif isinstance(each, ast.For):
            print("--- For ---")
            get_logic_info(each, logic_info, assign_dict)
        elif isinstance(each, ast.While) :
            print("--- While ---")
            get_logic_info(each, logic_info, assign_dict)
        elif isinstance(each, ast.If) :
            print("--- If ---")
            get_logic_info(each, logic_info, assign_dict)

        elif isinstance(each, ast.Assign):
            print("--- Assign --- : ", each.value)
            if isinstance(each.value, ast.Call) :
                names = []
                print("each.value == Call | each.targets : ", each.targets)
                for name in each.targets :
                    if isinstance(name, ast.Name) :
                        print("each.target == Name | name.id : ", name.id)
                        if name.id in assign_dict :
                            del assign_dict[name.id]
                        names.append(name.id)
                stack = []
                cur = each.value.func
                print("each.value.func : ", cur)
                check = 0
                while isinstance(cur, ast.Attribute)  :
                    print("each.value.func == Attribute : ", cur.attr)
                    if(check == 0) :
                        stack.append(assign_dict.get(cur.attr, import_from_table.get(cur.attr, cur.attr)))
                        check = 1
                    else:
                        stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
                    cur = cur.value
                print("cur.value : ", cur)
                if not isinstance(cur, ast.Name) :
                    continue
                print("cur == Name", cur.id)
                stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
                stack = stack[::-1]
                stack = '.'.join(stack)
                for name in names :
                    assign_dict[name] = stack
                print("Sun : ", assign_dict)
                logic_info.append({'type': 'Call', 'id': stack})

            elif isinstance(each.value, ast.BinOp):
                print("BinOp | left : ", each.value.left)
                if isinstance(each.value.left, ast.Call):
                    names = []
                    print("each.value.left == Call | each.targets : ", each.targets)
                    for name in each.targets:
                        if isinstance(name, ast.Name):
                            print("each.target == Name | name.id : ", name.id)
                            if name.id in assign_dict:
                                del assign_dict[name.id]
                            names.append(name.id)
                    stack = []
                    cur = each.value.left.func
                    print("each.value.func : ", cur)
                    while isinstance(cur, ast.Attribute):
                        print("each.value.func == Attribute : ", cur.value)
                        print("each.value.func == Attribute : ", cur.value.id)
                        print("each.value.func == Attribute : ", cur.attr)
                        stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
                        cur = cur.value
                    print("cur.value : ", cur)
                    if not isinstance(cur, ast.Name):
                        continue
                    print("cur == Name", cur.id)
                    stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
                    stack = stack[::-1]
                    stack = '.'.join(stack)
                    for name in names:
                        assign_dict[name] = stack
                    print("Sun : ", assign_dict)
                    logic_info.append({'type': 'Call', 'id': stack})

                print("BinOp | right : ", each.value.right)
                if isinstance(each.value.right, ast.Call):
                    names = []
                    print("each.value.right == Call | each.targets : ", each.targets)
                    for name in each.targets:
                        if isinstance(name, ast.Name):
                            print("each.target == Name | name.id : ", name.id)
                            if name.id in assign_dict:
                                del assign_dict[name.id]
                            names.append(name.id)
                    stack = []
                    cur = each.value.right.func
                    print("each.value.func : ", cur)
                    while isinstance(cur, ast.Attribute):
                        print("each.value.func == Attribute : ", cur.value)
                        print("each.value.func == Attribute : ", cur.value.id)
                        print("each.value.func == Attribute : ", cur.attr)
                        stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
                        cur = cur.value
                    print("cur.value : ", cur)
                    if not isinstance(cur, ast.Name):
                        continue
                    print("cur == Name", cur.id)
                    stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
                    stack = stack[::-1]
                    stack = '.'.join(stack)
                    for name in names:
                        assign_dict[name] = stack
                    print("Sun : ", assign_dict)
                    logic_info.append({'type': 'Call', 'id': stack})

        elif isinstance(each, ast.Expr) :
            print("--- Expr --- : ", each.value)
            if isinstance(each.value, ast.Call) :
                print("each.value == Call : ", each.value.func)
                stack = []
                cur = each.value.func
                check = 0
                while isinstance(cur, ast.Attribute)  :
                    print("each.value.func == Attribute : ", each.value.func.value)
                    print("each.value.func == Attribute : ", each.value.func.attr)
                    if (check == 0):
                        stack.append(assign_dict.get(cur.attr, import_from_table.get(cur.attr, cur.attr)))
                        check = 1
                    else:
                        stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr,import_from_table.get(cur.attr,cur.attr))))
                    cur = cur.value
                if not isinstance(cur, ast.Name) :
                    continue
                stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
                stack = stack[::-1]
                stack = '.'.join(stack)
                logic_info.append({'type' : 'Call', 'id' : stack})

        elif isinstance(each, ast.Import):
            print("--- Import ---")
            print("each.names : ", each.names)
            for name in each.names :
                print("name.name : ", name.name)
                print("name.asname : ", name.asname)
                if name.asname != None:
                    print("name.asname != None | name.name : ", name.name)
                    import_table[name.asname] = name.name

        elif isinstance(each, ast.ImportFrom) :
            module = each.module
            for name in each.names :
                if name.asname == None :
                    import_from_table[name.name] = module + '.' + name.name
                else :
                    import_from_table[name.asname] = module + '.' + name.name

def load_file( file_path ) :
    with open(file_path, 'r', encoding='utf-8') as f :
        context = f.readlines()
    return context

def parsing_code( file_path ) :
    logic_info = list()
    context = load_file( file_path )
    number_of_file_line = len(context)
    parse_tree = ast.parse(''.join(context))
    get_logic_info(parse_tree, logic_info)
    return logic_info
