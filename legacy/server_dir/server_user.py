"""
Import Library
"""
import json
import random
import os
from pathlib import Path
from server_dir.user_database import user_database


"""
User Search Logic
function    : receive user git email and verify user
parameter   : content_json, user_git_id_list
return      : True / Random Number
"""
def user_search_logic(content):

    git_id = str(content['user_email'])
    u_db = user_database("parent")

    if(u_db.search_user(git_id)):
        # Already Sign-in
        u_db.close()
        return "True"

    else:
        # Process of Sign-in

        # Generate Random Number
        rand_num = create_random_number()

        # Insert git id and random number
        u_db.insert_git_id_random_number(git_id, rand_num)
        u_db.close()
        return str(rand_num)


"""
Create Random Number
function    : Create Random Number
parameter   : None
return      : Random Number
"""
def create_random_number():

    # Create Random Number
    rand_num = random.randint(10000, 99999)

    # log
    print("random Number: " + str(rand_num))

    return rand_num


"""
Read User Data
function    : Sync User Data
parameter   : None
return      : user_git_id_list
"""
def read_user_data_logic():

    # Import User Data
    with open(os.path.join(Path(os.getcwd()).parent, "user_data", "user_git.json"), 'r') as f:
        user_git_id_list = json.load(f)

    return user_git_id_list