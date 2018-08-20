from chat_bot_server_dir.work_database import *
from chat_bot_server_dir.intent_func import *

def sentence_processing_main(intent_type, slack_code, param0, param1, param2, param3):

    if(intent_type == 1):
        approved_file_logic(slack_code, param0, param1)

    elif(intent_type == 2):
        lock_file_logic(slack_code, param0, param1, param2)

    elif(intent_type == 3):
        code_history_logic()


def approved_file_logic(slack_code, approve_set, remove_list):
    w_db = work_database()

    if(approve_set != {}):
        w_db.add_approved_list(slack_code=slack_code,
                               req_approved_set=approve_set)
    if(remove_list != []):
        w_db.remove_approved_list(slack_code=slack_code,
                                  remove_approve_list=remove_list)

    w_db.close()
    return


def lock_file_logic(slack_code, request_lock_set, remove_lock_list, lock_time):
    w_db = work_database()

    if(request_lock_set != {}):
        w_db.add_lock_list(slack_code, request_lock_set, lock_time)
    if(remove_lock_list != []):
        w_db.remove_lock_list(slack_code, remove_lock_list)

    w_db.close()
    return


def code_history_logic(slack_code, file_path, start_line, end_line):
    w_db = work_database()

    project_name = w_db.read_project_name(slack_code)
    engaging_user_list = get_user_email(project_name, file_path, start_line, end_line)

    w_db.close()
    return

def ignore_file_logic():
    pass


def check_conflict_logic():
    pass


def other_working_status_logic():
    pass


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