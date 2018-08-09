"""
Import Library
"""
import json
import random


"""
User Search Logic
function    : receive user git email and verify user
parameter   : content_json, user_git_id_list
return      : True / Random Number
"""
def user_search_logic(content, user_git_id_list):

    git_id = str(content['email'])

    for email in user_git_id_list.keys():
        if git_id == str(email) and type(user_git_id_list[email]) != int:
            return "True"

    # Generate Random Number
    rand_num = create_random_number()

    # Create JSON User Data
    json_dict = dict()
    with open('./user_data/user_git.json', 'r') as make_file:
        json_dict = json.load(make_file)

    json_dict[git_id] = rand_num

    # Save User Data Json file
    with open('./user_data/user_git.json', 'w') as make_file:
        json.dump(json_dict, make_file)

    # Return Ture or Random Number
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
    with open('./user_data/user_git.json', 'r') as f:
        user_git_id_list = json.load(f)

    return user_git_id_list