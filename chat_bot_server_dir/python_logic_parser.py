
DEFAULT_INDENT = 4
TAB = DEFAULT_INDENT * ' '

def func_parser( lines, start_line, indent_number, members ) :
    INDENT = TAB * indent_number
    end_of_line_number = len(lines)
    line_number = start_line + 1
    not_white_space_line_number = start_line
    while line_number < end_of_line_number:
        line = lines[line_number].rstrip()
        if not line :
            line_number += 1
            continue
        if not line.startswith(INDENT):
            break
        line = line[indent_number * DEFAULT_INDENT:]
        if not line.startswith(TAB) :
            break
        not_white_space_line_number = line_number
        line = line[DEFAULT_INDENT:]
        if line.startswith('def ') :
            function_name = line[4:].split('(')[0].strip()
            function_info = {'name': function_name, 'start': line_number, 'members': {'function': []}}
            function_info['end'] = func_parser(lines, line_number, indent_number + 1, function_info['members'])
            members['function'].append(function_info)
            line_number = min(function_info['end'] + 1, end_of_line_number)
        else :
            line_number += 1
    return not_white_space_line_number

def class_parser( lines, start_line, indent_number, members ) :
    INDENT = TAB * indent_number
    end_of_line_number = len(lines)
    line_number = start_line + 1
    not_white_space_line_number = start_line
    while line_number < end_of_line_number:
        line = lines[line_number].rstrip()
        if not line:
            line_number += 1
            continue
        if not line.startswith(INDENT) :
            break
        line = line[indent_number * DEFAULT_INDENT:]
        if not line.startswith(TAB) :
            break
        not_white_space_line_number = line_number
        line = line[DEFAULT_INDENT:]
        if line.startswith('class '):
            class_name = line[6:].split(':')[0].split('(')[0].strip()
            class_info = {'name': class_name, 'start': line_number + 1, 'members': {'class': [], 'function': []}}
            class_info['end'] = class_parser(lines, line_number, indent_number + 1, class_info['members']) + 1
            members['class'].append(class_info)
            line_number = min(class_info['end'] + 1, end_of_line_number)
        elif line.startswith('def '):
            function_name = line[4:].split('(')[0].strip()
            function_info = {'name': function_name, 'start': line_number + 1, 'members': {'function': []}}
            function_info['end'] = func_parser(lines, line_number, indent_number + 1, function_info['members']) + 1
            members['function'].append(function_info)
            line_number = min(function_info['end'] + 1, end_of_line_number)
        else :
            line_number += 1
    return not_white_space_line_number

def get_py_info( file_path ) :
    ret_dict = { 'class' : [], 'function' : [] }
    with open(file_path, 'r') as f :
        lines = f.readlines()
        line_number = 0
        end_of_line_number = len(lines)
        while line_number < end_of_line_number :
            line = lines[line_number]
            if line.startswith('class ') :
                class_name = line[6:].split(':')[0].split('(')[0].strip()
                class_info = {'name' : class_name, 'start' : line_number + 1, 'members' : { 'class' : [], 'function' : [] } }
                class_info['end'] = class_parser(lines, line_number, 0, class_info['members']) + 1
                ret_dict['class'].append(class_info)
                line_number = min(class_info['end'] + 1, end_of_line_number)
            elif line.startswith('def ') :
                function_name = line[4:].split('(')[0].strip()
                function_info = { 'name' : function_name, 'start' : line_number + 1, 'members' : { 'function' : [] }}
                function_info['end'] = func_parser(lines, line_number, 0, function_info['members']) + 1
                ret_dict['function'].append(function_info)
                line_number = min(function_info['end'] + 1, end_of_line_number)
            else :
                line_number += 1
    return ret_dict

def get_py_info_list( py_info, pre_infix = '') :
    ret_func_list, ret_class_list = [], []
    for key, value in py_info.items() :
        if pre_infix :
            infix = pre_infix + '|' + key + ':'
        else :
            infix = key + ':'
        for logic in value :
            a, b = get_py_info_list( logic['members'], infix + logic['name'])
            ret_func_list.extend(a)
            ret_class_list.extend(b)
            if key == 'class' :
                ret_class_list.append([infix + logic['name'], logic['start'], logic['end']])
            else :
                ret_func_list.append([infix + logic['name'], logic['start'], logic['end']])
    return ret_func_list, ret_class_list
