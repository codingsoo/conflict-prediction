import os

root_dir = "C:\Users\jc\Desktop\py_test"
file_dir = []
file_name = []
file_dependency = {}

# Search All Directory And Append simple file name
def search_directory(url):
    for (file_path, dir, files) in os.walk(url):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.py':
                print("%s/%s" % (file_path, filename))
                file_dir.append(os.path.join(file_path,filename))
                file_name.append(filename[:len(filename)-3])

# File Content Data Reader
def file_reader(url):

    # file open
    f = open(url)

    # Read Raw Data from file
    raw_data = f.read()

    return raw_data

# Generate Dependency Data
# 1. File dependency        # { 'file path' : [ dependency file list ], 'file path2' : [ dependency file list ] }
# 2. Function dependency    # { 'file name + function name' : [ dependency function list ], 'file name + function name' : [ dependency function list ] }
# 3. Class dependency       # { 'file name + class name' : [ dependency class list ], 'file name + class name' : [ dependency class list ] }
def generate_dependency():

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
        file_content_list = dict()
        content_dependency_list = []
        class_name = ""
        def_name = ""

        # Read Each line
        for file_line in file_content:

            index = 0
            temp_line = file_line.split(' ')

            if file_line[0:4] != "    ":
                print()

            # Read Each token
            for temp_token in temp_line:

                # Generate file dependency [keyword : import]
                if temp_token == "import":
                    import_file = temp_line[index + 1]

                    for temp_file_dir in file_dir:
                        temp1_file_dir = str(temp_file_dir).split('\\')
                        temp1_file_dir = temp1_file_dir[len(temp1_file_dir) - 1]
                        temp1_file_dir = temp1_file_dir[:-3]

                        if import_file == temp1_file_dir:
                            temp_file_list.append(temp_file_dir)
                            file_dependency[temp_dir] = temp_file_list
                            break

                # Generate class dependency [ keyword : class ]
                elif temp_token == "class":
                    class_name = file_line.strip()
                    in_content.append(class_name)

                    print class_name

                # Generate function dependency [ keyword : def ]
                elif temp_token == "def":
                    def_name = file_line.strip()
                    in_content.append(def_name)

                    print def_name

                    # class function dependency
                    if (file_line[0:4] == "    ") and (len(file_line) >= 4):
                        temp_list = []
                        temp_list.append(temp_dir + ' | ' + class_name)
                        temp_list.append(temp_dir + ' | ' + def_name)
                        content_dependency_list.append(temp_list)

                    if (file_line[0:4] == "    ") and (len(file_line) >= 4):
                        temp_list1 = []
                        temp_list1.append(temp_dir + ' | ' + def_name)
                        temp_list1.append(temp_dir + ' | ' + def_name)
                        content_dependency_list.append(temp_list1)

                # index plus
                index += 1

        file_content_list[temp_dir] = in_content
        print file_content_list
        print 111
        print content_dependency_list


if __name__ == '__main__':
    search_directory(root_dir)

    print file_dir
    print file_name

    generate_dependency()

    print file_dependency