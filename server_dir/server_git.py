# def git_diff_logic(content):
#
#     used_files = dict(list())
#
#     with open('./user_data/user_git.json', 'r') as f:
#         user_git_id_list = json.load(f)
#     # Get User slack id
#     if content['git_id']:
#         user_slack_id = user_git_id_list[str(content['git_id'])]
#     else:
#         user_slack_id = content['git_id']
#
#     # Create working_list
#     working_list[user_slack_id] = content['git_diff']
#
#     # Put user's working list to conflict list
#     for file_name in working_list[user_slack_id]:
#         user_list = []
#
#         with open('./user_data/approved_list.json', 'r') as f:
#             approved_list = json.load(f)
#         if file_name in approved_list:
#             continue
#
#         # Conflict case
#         if file_name in conflict_list.keys() and user_slack_id not in conflict_list[file_name]:
#             # Analyze conflict severity
#             if file_name in working_list[conflict_list[file_name][0]].keys():
#                 error = 'in'
#                 for user1_work_place in working_list[conflict_list[file_name][0]][file_name].keys():
#                     for user2_work_place in working_list[user_slack_id][file_name].keys():
#                         user1_working_line = \
#                         working_list[str(conflict_list[file_name][0])][file_name][user1_work_place][0]
#                         user1_working_space = \
#                         working_list[str(conflict_list[file_name][0])][file_name][user1_work_place][1]
#                         user2_working_line = working_list[user_slack_id][file_name][user2_work_place][0]
#                         user2_working_space = working_list[user_slack_id][file_name][user2_work_place][1]
#                         if user1_working_space == "":
#                             user1_working_space = 0
#                         if user2_working_space == "":
#                             user2_working_space = 0
#                         if user1_working_line == "":
#                             user1_working_line = 0
#                         if user2_working_line == "":
#                             user2_working_line = 0
#
#                         # Def case
#                         if user1_work_place == user2_work_place and 'def' in user1_work_place:
#                             error = user1_work_place
#                         # Class case
#                         elif user1_work_place == user2_work_place and 'class' in user1_work_place and 'def' not in error:
#                             error = user1_work_place
#                         # Same file case
#                         elif error == 'in':
#                             working_line = abs(int(user1_working_line) - int(user2_working_line))
#                             working_space = abs(int(user1_working_space) + int(user2_working_space))
#                             error = error + str(working_line) + ',' + str(working_space)
#                         elif 'in' in error:
#                             # print working_list[user_slack_id][file_name]
#                             # print working_list[conflict_list[file_name][0]][file_name]['import json']
#                             pre_working_line = int(error[2:].split(',')[0])
#                             pre_working_space = int(error[2:].split(',')[1])
#                             working_line = abs(int(user1_working_line) - int(user2_working_line))
#                             working_space = abs(int(user1_working_space) + int(user2_working_space))
#
#                             if pre_working_space < working_space:
#                                 error = 'in' + str(working_line) + ',' + str(working_space)
#
#                 conflict_list[file_name].append(user_slack_id)
#                 conflict_list[file_name].sort()
#
#                 # When pre-conflict exist
#                 if conflict_list[file_name][0] in error_list.keys() and conflict_list[file_name][1] in error_list[
#                     conflict_list[file_name][0]].keys() and file_name in error_list[conflict_list[file_name][0]][
#                     conflict_list[file_name][1]].keys():
#                     pre_error = error_list[conflict_list[file_name][0]][conflict_list[file_name][1]][file_name]
#
#                     # Severe case to def
#                     if 'def' in error and 'def' not in pre_error:
#                         attachments_dict = dict()
#                         attachments_dict['text'] = get_severe_diff_file[
#                                                        random.randint(0, len(get_severe_diff_file) - 1)] % (
#                                                    '@' + conflict_list[file_name][0],
#                                                    '@' + conflict_list[file_name][1], file_name,
#                                                    error + " function")
#                         attachments_dict['mrkdwn_in'] = ["text", "pretext"]
#                         attachments = [attachments_dict]
#
#                         slack.chat.post_message(channel="#code-conflict-chatbot", text=None,
#                                                 attachments=attachments, as_user=True)
#
#                         error_list[conflict_list[file_name][0]][conflict_list[file_name][1]] = error
#
#                     # Severe case to class
#                     elif 'class' in error and 'def' not in pre_error and 'class' not in pre_error:
#                         attachments_dict = dict()
#                         attachments_dict['text'] = get_severe_diff_file[
#                                                        random.randint(0, len(get_severe_diff_file) - 1)] % (
#                                                    '@' + conflict_list[file_name][0],
#                                                    '@' + conflict_list[file_name][1], file_name, error + " class")
#                         attachments = [attachments_dict]
#
#                         slack.chat.post_message(channel="#code-conflict-chatbot", text=None,
#                                                 attachments=attachments, as_user=True)
#
#                         error_list[conflict_list[file_name][0]][conflict_list[file_name][1]] = error
#
#                     # Severe case to in
#                     elif 'in' in pre_error and 'in' in error and int(error[2:].split(',')[1]) - 5 > int(
#                             pre_error[2:].split(',')[1]):
#                         attachments_dict = dict()
#                         attachments_dict['text'] = get_severe_diff_file[
#                                                        random.randint(0, len(get_severe_diff_file) - 1)] % (
#                                                    '@' + conflict_list[file_name][0],
#                                                    '@' + conflict_list[file_name][1], " same file")
#                         attachments_dict['mrkdwn_in'] = ["text", "pretext"]
#                         attachments = [attachments_dict]
#
#                         slack.chat.post_message(channel="#code-conflict-chatbot", text=None,
#                                                 attachments=attachments, as_user=True)
#
#                         error_list[conflict_list[file_name][0]][conflict_list[file_name][1]] = error
#
#                     # Conflict solved
#                     elif ('def' in pre_error and 'def' not in error) or (
#                                 'class' in pre_error and 'def' not in error and 'class' not in error) or (
#                                 'in' in pre_error and 'in' in error and int(pre_error[2:].split(',')[1]) + 5 > int(
#                             error[2:].split(',')[1])):
#                         attachments_dict = dict()
#                         attachments_dict['text'] = conflict_finished[
#                                                        random.randint(0, len(conflict_finished) - 1)] % (
#                                                    conflict_list[file_name][0], conflict_list[file_name][1])
#                         attachments_dict['mrkdwn_in'] = ["text", "pretext"]
#                         attachments = [attachments_dict]
#
#                         slack.chat.post_message(channel="#code-conflict-chatbot", text=None,
#                                                 attachments=attachments, as_user=True)
#                         error_list[conflict_list[file_name][0]][conflict_list[file_name][1]][file_name] = error
#                     # Same conflict
#                     else:
#                         pass
#                 # When pre-conflict doesn't exist
#                 else:
#                     user_error_dict = dict()
#                     func_error_dict = dict()
#                     func_error_dict[file_name] = error
#                     user_error_dict[conflict_list[file_name][1]] = func_error_dict
#                     error_list[conflict_list[file_name][0]] = user_error_dict
#
#                     # def detected
#                     if 'def' in error:
#                         attachments_dict = dict()
#                         attachments_dict['text'] = go_to_same_file_shell[
#                                                        random.randint(0, len(go_to_same_file_shell) - 1)] % (
#                                                    '@' + conflict_list[file_name][0],
#                                                    '@' + conflict_list[file_name][1], error + " function")
#                         attachments_dict['mrkdwn_in'] = ["text", "pretext"]
#                         attachments = [attachments_dict]
#
#                         slack.chat.post_message(channel="#code-conflict-chatbot", text=None,
#                                                 attachments=attachments, as_user=True)
#                     # class detected
#                     elif 'class' in error:
#                         attachments_dict = dict()
#                         attachments_dict['text'] = go_to_same_file_shell[
#                                                        random.randint(0, len(go_to_same_file_shell) - 1)] % (
#                                                    '@' + conflict_list[file_name][0],
#                                                    '@' + conflict_list[file_name][1], error + " class")
#                         attachments_dict['mrkdwn_in'] = ["text", "pretext"]
#                         attachments = [attachments_dict]
#
#                         slack.chat.post_message(channel="#code-conflict-chatbot", text=None,
#                                                 attachments=attachments, as_user=True)
#                     # same file detected
#                     else:
#                         attachments_dict = dict()
#                         attachments_dict['text'] = go_to_same_file_shell[
#                                                        random.randint(0, len(go_to_same_file_shell) - 1)] % (
#                                                    '@' + conflict_list[file_name][0],
#                                                    '@' + conflict_list[file_name][1], file_name + " file")
#                         attachments_dict['mrkdwn_in'] = ["text", "pretext"]
#                         attachments = [attachments_dict]
#
#                         slack.chat.post_message(channel="#code-conflict-chatbot", text=None,
#                                                 attachments=attachments, as_user=True)
#
#             # No conflict
#             else:
#                 # pre-conflict exist
#                 conflict_check_user = []
#                 conflict_check_user.append(conflict_list[file_name][0])
#                 conflict_check_user.append(user_slack_id)
#                 conflict_check_user.sort()
#                 attachments_dict = dict()
#                 attachments_dict['text'] = conflict_finished[random.randint(0, len(conflict_finished) - 1)] % (
#                 conflict_check_user[0], conflict_check_user[1])
#                 attachments_dict['mrkdwn_in'] = ["text", "pretext"]
#                 attachments = [attachments_dict]
#
#                 slack.chat.post_message(channel="#code-conflict-chatbot", text=None, attachments=attachments,
#                                         as_user=True)
#                 # del (error_list[conflict_check_user[0]][conflict_check_user[1]][file_name])
#                 conflict_list[file_name][0] = user_slack_id
#
#         # No conflict
#         else:
#             user_list.append(user_slack_id)
#             conflict_list[file_name] = user_list
#             #
#             # # In direct
#             # index = 0
#             # for group in content['git_graph']:
#             #     if file_name in group and index in used_files :
#             #         for user in used_files[index] :
#             #             if user != user_slack_id and file_name in working_list[user].keys():
#             #                 # conflict detected
#             #                 print("hello")
#             #             else:
#             #                 del(used_files[index])
#             #         used_files[index].append(user_slack_id)
#             #     index = index + 1
#
#     return "test"



def git_diff_logic(content):
