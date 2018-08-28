import json
###################################
working_list = {
    u'learnitdeep2': {
        u'/UCI_chatbot_Server/bot_server.py': {
            u'import json': [u'7', u'2']
        },
        u'/UCI_chatbot_Server/server.py': {
                u'def cmd1():': [u'39', u'140'],
                u'working_file = dict()': [u'17', u'6']
            }
    }
}

converted_data = {
    'git_id': 'chan_j@naver.com',
    'git_diff': {
        'UCNLP/client.git': {
            'UCNLP\\client\\client.py': [
                ['function:verifying_user', 151, 1],
                ['function:vvv', 141, 2]
            ]
        }
    }
}
###################################
# For Indirected
working_node_set = set()
visit = set()
q = Queue.Queue()

for key, value in working_list:         # 유저 아이디 : {파일 : { 함수명 : [ 수정 데이터] } }
    if key == user_slack_id:
        for key2, value2 in value:      # 파일 : { 함수명 : [수정 데이터] }
            for key3, value3 in value2: # 함수명 : [ 수정 데이터]
                if key3 == 'in':
                    continue
                else:
                    if value3 in visit:
                        continue
                    visit.add(value3)
                    q.put([value3, value3])
        continue
    else:
        for key2, value2 in value:
            for key3, value3 in value2:
                if key3 == 'in':
                    continue
                else:
                    working_node_set.add(key3)

with open('./user_data/approved_list.json', 'r') as f:
    approved_list = json.load(f)

graph_data = {}
git_clone_info = 1
for (u, v) in git_clone_info.get_git_clone_info():
    if not u in graph_data:
        graph_data[u] = set()
    graph_data[u].add(v)

indirected_result = []
while not q.empty():
    node, source = q.get()
    file_name = os.path.basename(node.split('|')[0])
    if file_name in approved_list:
        continue
    for next in graph_data[node]:
        if not next in visit and not os.path.basename(file_name) in approved_list:
            visit.add(next)
            q.put([next, source])
            if next in working_node_set:
                indirected_result.append([source, next])

print(indirected_result)

return "test"

############################################################################
# git clone from user git url
root_dir_temp = gitCloneFromURL("https://github.com/j21chan/py_test")
print(root_dir_temp)

# Send to the server with Git dependency of function and class
# sendGraphInfo(root_dir_temp, git_repository_name)

# send_data = dict()

# send_data['repository_name'] = git_repository_name

search_directory(root_dir_temp)

generate_file_dependency()

raw_list = generate_func_class_dependency()
graph_data = [[os.path.normpath(u), os.path.normpath(v)] for (u, v) in raw_list]

print(graph_data)

# Remove exist dir
removeDir(root_dir_temp)