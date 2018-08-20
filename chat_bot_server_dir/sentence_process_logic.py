from chat_bot_server_dir.work_database import work_database
from chat_bot_server_dir.intent_func import get_user_email

def sentence_processing_main(intent_type, slack_code, param0, param1, param2, param3):

    message = ""

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


def approved_file_logic(slack_code, approve_set, remove_list):
    w_db = work_database()

    m1 = ""
    m2 = ""

    if(approve_set != {}):
        w_db.add_approved_list(slack_code=slack_code,
                               req_approved_set=approve_set)
        m1 = "add approve file : " + str(approve_set)
    if(remove_list != []):
        w_db.remove_approved_list(slack_code=slack_code,
                                  remove_approve_list=remove_list)
        m2 = "remove approve file : " + str(remove_list)

    message = m1 + " / " + m2

    w_db.close()
    return message


def lock_file_logic(slack_code, request_lock_set, remove_lock_list, lock_time):
    w_db = work_database()

    m1 = ""
    m2 = ""

    if(request_lock_set != {}):
        w_db.add_lock_list(slack_code, request_lock_set, lock_time)
        m1 = "add lock file : " + str(request_lock_set)
    if(remove_lock_list != []):
        w_db.remove_lock_list(slack_code, remove_lock_list)
        m2 = "remove lock file : " +str(remove_lock_list)

    message = m1 + " / " + m2

    w_db.close()
    return message


def code_history_logic(slack_code, file_path, start_line, end_line):
    w_db = work_database()

    project_name = w_db.read_project_name(slack_code)
    engaging_user_list = get_user_email(project_name, file_path, start_line, end_line)

    message = "This is code history : " + str(engaging_user_list)

    w_db.close()
    return message

def ignore_file_logic(slack_code, ignore_list):
    w_db = work_database()

    project_name = w_db.read_project_name(slack_code)
    w_db.add_update_ignore(project_name, ignore_list, slack_code)

    message = "Update direct or indirect ignore!"

    w_db.close()
    return message


def check_conflict_logic(slack_code, file_name):
    w_db = work_database()
    message = ""

    project_name = w_db.read_project_name(slack_code)
    direct_conflict_flag, indirect_conflict_flag = w_db.is_conflict(project_name, slack_code, file_name)

    if((direct_conflict_flag == True) and (indirect_conflict_flag == True)):
        message = "Direct conflict O / Indirect conflict O"
    elif((direct_conflict_flag == True) and (indirect_conflict_flag == False)):
        message = "Direct conflict O / Indirect conflict X"
    elif((direct_conflict_flag == False) and (indirect_conflict_flag == True)):
        message = "Direct conflict X / Indirect conflict O"
    elif((direct_conflict_flag == False) and (indirect_conflict_flag == False)):
        message = "Direct conflict X / Indirect conflict X"

    w_db.close()
    return message


def other_working_status_logic(slack_code, git_id):
    w_db = work_database()

    recent_conflict_data = w_db.get_recent_data(git_id)
    message = "Recent conflict data is : " + str(recent_conflict_data)

    w_db.close()
    return message


def send_message_channel_logic():
    pass


def send_message_direct_logic():
    pass


def recommend_solve_conflict_logic():
    pass


def recognize_user_logic():
    pass


def greeting_logic():
    pass


def bye_logic():
    pass