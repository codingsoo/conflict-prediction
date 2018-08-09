import pymysql
from server_dir.work_database import *
from server_dir.user_git_diff import *

def git_diff_logic(content):

    user_name = "test"

    # create user git diff data
    user_data = user_git_diff(content)

    # create database object
    w_db = work_database()

    # delete current user data
    w_db.delete_user_data(user_data.get_user_name())

    # detect direct conflict
    w_db.detect_direct_conflict(user_data.get_proj_name(),
                                user_data.get_working_data(),
                                user_data.get_user_name())

    # close database
    w_db.close_db()