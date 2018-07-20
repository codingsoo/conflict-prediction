import subprocess

raw = str(subprocess.check_output('git ls-files -m', shell=True))

temp_list = raw.splitlines()

file_list = list()

for temp in temp_list:

    print(temp.strip())

    temp_file_name = temp.strip()

    file = open(temp_file_name, 'r')

    print(file_list.append(file.read()))

print(file_list)