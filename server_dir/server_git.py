from server_dir.work_database import *
from server_dir.user_git_diff import *


"""
git diff logic
function    : detect direct conflict between the developers
parameter   : content_json
return      : none
"""
def git_diff_logic(content):

    # create user git diff data
    user_data = user_git_diff(content)

    # create database object
    w_db = work_database()

    # delete current user data
    w_db.delete_user_data(user_data.get_user_name())

    # detect direct conflict
    w_db.detect_direct_conflict(project_name = user_data.get_proj_name(),
                                working_list = user_data.get_working_data(),
                                user_name    = user_data.get_user_name())

    # insert user data
    w_db.insert_user_data(project_name = user_data.get_proj_name(),
                          working_list = user_data.get_working_data(),
                          user_name    = user_data.get_user_name())

    # close database
    w_db.close_db()

    return