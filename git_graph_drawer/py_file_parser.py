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
            function_info = { 'type' : 'Function', 'name' : each.name, 'start' : each.lineno, 'end' : get_end_of_logic(each) }
            ret_list = []
            get_logic_info( each, ret_list )
            if len(ret_list) != 0 :
                function_info['members'] = ret_list
            logic_info.append (function_info)
        elif isinstance(each, ast.ClassDef):
            function_info = { 'type' : 'Class', 'name' : each.name, 'start' : each.lineno, 'end' : get_end_of_logic(each) }
            ret_list = []
            get_logic_info( each, ret_list )
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

        elif isinstance(each, ast.Assign):
            if isinstance(each.value, ast.Call) :
                names = []
                for name in each.targets :
                    if isinstance(name, ast.Name) :
                        if name.id in assign_dict :
                            del assign_dict[name.id]
                        names.append(name.id)
                stack = []
                cur = each.value.func
                while not isinstance(cur, ast.Name) :
                    stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
                    cur = cur.value
                stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
                stack = stack[::-1]
                stack = '.'.join(stack)
                for name in names :
                    assign_dict[name] = stack
                logic_info.append({'type': 'Call', 'id': stack})

        elif isinstance(each, ast.Expr) :
            if isinstance(each.value, ast.Call) :
                stack = []
                cur = each.value.func
                while not isinstance(cur, ast.Name) :
                    stack.append(assign_dict.get(cur.attr, import_table.get(cur.attr, import_from_table.get(cur.attr, cur.attr))))
                    cur = cur.value
                stack.append(assign_dict.get(cur.id, import_table.get(cur.id, import_from_table.get(cur.id, cur.id))))
                stack = stack[::-1]
                stack = '.'.join(stack)
                logic_info.append({'type' : 'Call', 'id' : stack})

        elif isinstance(each, ast.Import) :
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
