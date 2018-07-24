import os

root_dir = "C:\Users\jc\Desktop\py_test"
file_dir = []
file_name = []
file_dependency = {}

def search_directory(url):
    for (file_path, dir, files) in os.walk(url):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.py':
                print("%s/%s" % (file_path, filename))
                file_dir.append(os.path.join(file_path,filename))
                file_name.append(filename[:len(filename)-3])


def file_reader(url):

    # file open
    f = open(url)

    # Read Raw Data from file
    raw_data = f.read()

    return raw_data


def generate_file_dependency():

    # Read Each File
    for temp_dir in file_dir:

        # Read Raw data
        file_content = file_reader(temp_dir).splitlines()

        temp_file_list = []

        for file_line in file_content:

            temp_line = file_line.split(' ')


            for temp_token in temp_line:
                if temp_token == "import":
                    import_file = temp_line[1]


                    for temp_file_name in file_name:
                        if import_file == temp_file_name:
                            temp_file_list.append(import_file)

                            simple_file_name = str(temp_dir).split('\\')
                            simple_file_name = simple_file_name[len(simple_file_name)-1]
                            simple_file_name = simple_file_name[:len(simple_file_name)-3]

                            file_dependency[simple_file_name] = temp_file_list
                            file_dependency['path'] = root_dir
                            break


if __name__ == '__main__':
    search_directory(root_dir)
    print file_dir
    print file_name
    generate_file_dependency()

    print file_dependency