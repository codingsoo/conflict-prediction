from chat_bot_server_dir.work_database import work_database
from chat_bot_server_dir.intent_func import get_user_email
from server_dir.slack_message_sender import send_channel_message
from server_dir.slack_message_sender import send_direct_message

import os, random

def sentence_processing_main(intent_type, slack_code, param0, param1, param2):

    message = "default"

    if(intent_type == 1):
        message = approved_file_logic(slack_code, param0, param1)

    elif(intent_type == 2):
        message = lock_file_logic(slack_code, param0, param1, param2)

    elif(intent_type == 3):
        message = code_history_logic(slack_code, param0, param1, param2)

    elif(intent_type == 4):
        message = ignore_file_logic(slack_code, param0)

    elif(intent_type == 5):
        message = check_conflict_logic(slack_code, param0)

    elif(intent_type == 6):
        message = other_working_status_logic(slack_code, param0)

    elif(intent_type == 7):
        message = send_message_channel_logic(param0, param1)

    elif(intent_type == 8):
        message = send_message_direct_logic(param0, param1)

    elif(intent_type == 9):
        message = recommend_solve_conflict_logic(param0, param1)

    elif(intent_type == 10):
        message = greeting_logic(slack_code)

    elif(intent_type == 11):
        message = bye_logic()

    elif(intent_type == 12):
        message = "I don't know what are you talking about"

    return message

def approved_file_logic(slack_code, approve_set, remove_list):
    print(slack_code)
    print("approve !! : " + str(approve_set))
    print("remove !! : " + str(remove_list))
    w_db = work_database()

    if(approve_set != {}):
        w_db.add_approved_list(slack_code=slack_code,
                               req_approved_set=approve_set)
        message = random.choice(shell_dict['feat_ignore_file'])
        print(message)
        print(type(message))
        approve_list = list(approve_set)
        print(approve_list)
        message = message.format(approve_list[0])

    if(remove_list != []):
        w_db.remove_approved_list(slack_code=slack_code,
                                  remove_approve_list=remove_list)

        message = random.choice(shell_dict['feat_unignore_file'])
        message = message.format(remove_list[-1])

    w_db.close()
    print(type(message))
    return message


def lock_file_logic(slack_code, request_lock_set, remove_lock_list, lock_time):
    w_db = work_database()

    m1 = ""
    m2 = ""

    if(request_lock_set == {}):
        message = random.choice(shell_dict['feat_lock_file'])
        w_db.add_lock_list(slack_code, request_lock_set, lock_time)
        #m1 = "add lock file : " + str(request_lock_set)
        ele = ','.join(list(request_lock_set))
        message = message.format(ele)
    if(remove_lock_list != []):
        message = random.choice(shell_dict['feat_unlock_file'])
        w_db.remove_lock_list(slack_code, remove_lock_list)
        #m2 = "remove lock file : " +str(remove_lock_list)
        ele = ','.join(remove_lock_list)
        message = message.format(request_lock_set)

    # message = m1 + " / " + m2


    w_db.close()
    return message


def code_history_logic(slack_code, file_path, start_line, end_line):
    w_db = work_database()

    project_name = w_db.read_project_name(slack_code)
    engaging_user_list = get_user_email(project_name, file_path, start_line, end_line)

    #message = "This is code history : " + str(engaging_user_list)

    message = random.choice(shell_dict['feat_history_logic'])
    ele = ','.join(engaging_user_list)
    message =message.format(ele)
    w_db.close()
    return message

def ignore_file_logic(slack_code, ignore_list):
    w_db = work_database()
    print("ignore : " + str(ignore_list))
    project_name = w_db.read_project_name(slack_code)
    w_db.add_update_ignore(project_name, ignore_list, slack_code)

    message = random.choice(shell_dict['feat_history_logic'])
    ele = ','.join(ignore_list)
    message = message.format(ele)

    w_db.close()
    return message


def check_conflict_logic(slack_code, file_name):
    w_db = work_database()
    message = ""

    project_name = w_db.read_project_name(slack_code)
    direct_conflict_flag, indirect_conflict_flag = w_db.is_conflict(project_name, slack_code, file_name)

    if((direct_conflict_flag == True) and (indirect_conflict_flag == True)):
        message = random.choice(shell_dict['feat_conflict_di'])
    elif((direct_conflict_flag == True) and (indirect_conflict_flag == False)):
        message = random.choice(shell_dict['feat_conflict_d'])
    elif((direct_conflict_flag == False) and (indirect_conflict_flag == True)):
        message = random.choice(shell_dict['feat_conflict_i'])
    else:
        message = "I think it'll not cause any conflict."

    w_db.close()
    return message


def other_working_status_logic(slack_code, git_id):
    w_db = work_database()

    recent_conflict_data = w_db.get_recent_data(git_id)

    message = random.choice(shell_dict['feat_working_status'])
    message = message.format(recent_conflict_data)

    w_db.close()
    return message


def send_message_channel_logic(channel, msg):
    send_channel_message(channel, msg)
    message = random.choice(shell_dict['feat_send_message_user'])
    message = message.format(channel)
    return message


def send_message_direct_logic(slack_code, msg):
    send_direct_message(slack_code, msg)
    message = random.choice(shell_dict['feat_send_message_user'])
    message = message.format(slack_code)
    return message


# Finn can not
def recommend_solve_conflict_logic(user1_git_id, user2_git_id):
    w_db = work_database()

    recommend_git_id, recommend_working_amount = w_db.recommendation(user1_git_id, user2_git_id)
    message = "Recommend user git id : " + str(recommend_git_id) + " / " + "Recommend working amount : " + str(recommend_working_amount)

    w_db.close()
    return message


def greeting_logic(slack_code):
    w_db = work_database()
    message = ""

    last_connection = w_db.user_recognize(slack_code)

    if(last_connection == 1):
        message = random.choice(shell_dict['feat_greetings'])

    # Finn can not
    elif(last_connection == 2):
        message = random.choice(shell_dict['feat_greetings2'])
    elif(last_connection == 3):
        message = random.choice(shell_dict['feat_greetings3'])
    else:
        message = random.choice(shell_dict['feat_greetings'])

    w_db.close()

    return message


def bye_logic():
    message = random.choice(shell_dict['feat_goodbye'])
    return message



shell_dict = dict()

for path, dirs, files in os.walk('../situation_shell') :
    for file in files :
        file_name, ext = os.path.splitext(file)
        if ext == '.txt' :
            shell_dict[file_name] = list()
            with open(os.path.join(path, file) , 'r', encoding="UTF-8") as f :
                for line in f.readlines() :
                    shell_dict[file_name].append(line.strip())
