import subprocess
import json

json_data = dict()

result = subprocess.check_output('git config --local remote.origin.url', shell=True, universal_newlines=True)
print (result)
if result.startswith("git@"):
    json_data['repository_name'] = result[15:].strip()
else:
    json_data['repository_name'] = result[19:].strip()
print(json_data['repository_name'])