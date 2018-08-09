import pymysql
from server_dir.work_database import *

def git_diff_logic(content):

    user_name = "test"

    # create database object
    w_db = work_database()

    # delete current user data
    w_db.delete_user_data(user_name)




    pass