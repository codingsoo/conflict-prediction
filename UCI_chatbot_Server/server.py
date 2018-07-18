# Import Library
import random
import websocket
import time
import json
from flask import Flask, request
from slacker import Slacker

# Create app
app = Flask(__name__)

# Random Number
rand_set = set()

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



    return


# Verifying User
@app.route("/verifyUser", methods = ["POST"])
def verifyUser():

    return "test"


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
    app.run(debug = True, host = "0.0.0.0", port = 5009)