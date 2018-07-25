import os


root_dir = os.path.join(os.getcwd(), 'UCI_chatbot_Server')
file_dir = []
file_name = []
file_dependency = {}
file_content_list = dict()

group = list(list())

# Search All Directory And Append simple file name
def search_directory(url):
    for (file_path, dir, files) in os.walk(url):
        for filename in files:
            if 'conflict-detector' in str(file_name):
                continue
            ext = os.path.splitext(filename)[-1]
            if ext == '.py':
                # print("%s/%s" % (file_path, filename))
                file_dir.append(os.path.join(file_path,filename))
                file_name.append(filename[:len(filename)-3])


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
        print temp_dir

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
        print temp_dir

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
                        temp_list.append(temp_dir + '|' + class_name)
                        temp_list.append(temp_dir + '|' + def_name)
                        content_dependency_list.append(temp_list)
                        all_dependency_list.append(temp_list)
                        break

                # Import function dependency
                elif file_line[0:4] == '    ':
                    for t_dir in file_dir:

                        if t_dir != temp_dir:
                            # Read clear function, class name
                            func_class_name_list = class_func_name(file_content_list[t_dir])

                            # Search about usage of function
                            for temp_func_class_name in func_class_name_list:
                                find_flag = temp_token.find(temp_func_class_name)

                                if  (find_flag > 0) and def_dep:
                                    temp_func_list = []
                                    temp_func_list.append(temp_dir + '|' + def_name)
                                    temp_func_list.append(t_dir + '|def ' + temp_func_class_name)
                                    content_dependency_list.append(temp_func_list)
                                    all_dependency_list.append(temp_func_list)
                                    break

                # index plus
                index += 1

    return all_dependency_list


def class_func_name(raw_name_list):

    convert_name_list = []

    for raw_name in raw_name_list:

        split_name = str(raw_name).split(' ')

        # if(split_name[0] == "class"):
        #     temp_name = split_name[1]
        #
        #     if(temp_name[-1] == ':'):
        #         temp_name = temp_name[:-1]
        #
        #     convert_name_list.append(temp_name)

        if(split_name[0] == "def"):
            temp_name_list = split_name[1].split('(')
            temp_name = temp_name_list[0]
            convert_name_list.append(temp_name)

    return convert_name_list


def create_edge(raw_list):

    raw_dict = dict()

    for dep_obj in raw_list:
        for compare_dep in raw_list:

            if dep_obj[1] == compare_dep[0]:
                new_temp = []
                new_temp.append(dep_obj[0])
                new_temp.append(compare_dep[1])

                raw_list.append(new_temp)
    for file_set in raw_list:
        raw_dict[file_set[0]] = file_set[1]

    for stan_file in raw_dict.keys():
        group_file = raw_dict[stan_file]
        group_list = []
        while(True):
            group_list.append(group_file)
            if raw_dict[stan_file] in raw_dict.keys():
                group_file = raw_dict[stan_file]
            else:
                break
        group.append(group_list)

    print group

if __name__ == '__main__':

    search_directory(root_dir)

    print file_dir

    print " "
    print " "

    print file_name

    print " "
    print " "

    generate_file_dependency()

    print " "
    print " "

    raw_list = generate_func_class_dependency()

    create_edge(raw_list)

    print " "
    print " "

    print file_dependency