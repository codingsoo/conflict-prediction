"""
App name : server.py
Function : Detect git conflict between developers
"""

# import library
from flask import Flask, request
from server_dir.server_git import *
from server_dir.server_user import *

# Create Server
app = Flask(__name__)


"""
Static Definition
"""
user_git_diff_dict = dict()
user_git_id_list = list()


# root page
@app.route("/", methods = ["GET", "POST"])
def root():
    return "root page"


# User Search
@app.route("/user_search", methods = ["POST"])
def user_search():

    # Get User Git ID
    content = request.get_json(silent=True)

    # Return True or Random Number
    return str(user_search_logic(content, user_git_id_list))


# Synchronize User Data
@app.route("/sync_user_data", methods = ["POST"])
def sync_user_data():

    user_git_id_list = read_user_data_logic()

    return "sync success"


# Read the information of User Git Diff data
@app.route("/git_diff", methods = ["POST"])
def git_diff():

    content = request.get_json(silent=True)



# Main
if __name__ == "__main__":

    # Read User Data
    user_git_id_list = read_user_data_logic()

    # Run Server
    app.run(debug=True, host="0.0.0.0", port="5009")