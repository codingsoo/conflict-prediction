########################################################################
# Import Library
import random
import websocket
import time
import json
from flask import Flask, request
from slacker import Slacker
import thread
########################################################################

# Create app
app = Flask(__name__)

# User List
user_list = list()

@app.route("/test", methods = ["POST"])
def test():

    if request.method == "POST":
        content = request.get_json()
        print(content)

    return "test"

# Request for Command1
@app.route("/gitDiff", methods = ["POST", "GET"])
def cmd1():

    # Get command1 content
    content = request.get_json()
    print(content)
    return "test"


# Request for Command2
@app.route("/gitLsFiles", methods = ["POST", "GET"])
def cmd2():

    # Get command2 content
    content = request.get_json()

    print(content)

    return


# User Search
@app.route("/userSearch", methods = ["POST"])
def userSearch():

    # Initialize sign_in_flag
    sign_in_flag = "False"

    # Get User Git ID
    content = request.get_json()
    git_id = str(content['email'])

    # User Search
    for temp in user_list:

        print (str(temp['git_id']))

        if(str(temp['git_id']) == git_id):
            sign_in_flag = "True"
            break
        else:
            rand_num = createRandomTemp()
            temp_dict = dict()
            temp_dict['slack_id'] = str(rand_num)
            temp_dict['git_id'] = git_id
            user_list.append(temp_dict)
            print(user_list)
            sign_in_flag = rand_num

    return sign_in_flag


# Verifying User
@app.route("/verifyUser", methods = ["POST"])
def verifyUser():

    return "test"


def createRandomTemp():

    # Create Random Number
    rand_num = random.randint(10000, 99999)

    # log
    print("random Number: " + str(rand_num))

    return rand_num

# Create Random Number
@app.route("/createRandom", methods = ["GET"])
def createRandom():

    # Get Git ID
    content = request.get_json()
    git_id = content['email']

    # Create Random Number
    rand_num = random.randint(10000, 99999)

    # log
    print("random Number: " + str(rand_num))

    # Add Random Number
    rand_set.add({ 'rand_num':rand_num, 'git_id':git_id})

    return str(rand_num)


# Observe Random Number
@app.route("/observeRandom", methods = ["GET"])
def observeRandomNumber():

    return

# Observing Direct
def observeDirect():

    return

# MAIN
if __name__ == "__main__":

    # Import User Data
    with open('./user_data/user.json', 'r') as f:
        user_list = json.load(f)['user']
        print(user_list)

    # Run App
    app.run(debug=True, host="0.0.0.0", port=5009)