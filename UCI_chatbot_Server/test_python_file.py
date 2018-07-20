import subprocess

raw = str(subprocess.check_output('git ls-files -m', shell=True))

temp_list = raw.splitlines()

file_list = list()

for temp in temp_list:

    print(temp.strip())

    temp_file_name = temp.strip()

test11 = 2

print(2)