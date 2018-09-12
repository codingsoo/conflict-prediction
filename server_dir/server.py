"""
App name : server.py
Function : Detect git conflict between developers
"""

# import library
from flask import Flask, request
from server_dir.server_user import *
from server_dir.server_git import *
from server_dir.server_config_loader import *

# Create Server
app = Flask(__name__)
git_diff_ip = []

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
    return str(user_search_logic(content))


# Read the information of Upser Git Diff data
@app.route("/git_diff", methods = ["POST"])
def git_diff():

    print(git_diff_ip)

    # This condition logic is for prevent deleting working table simultaneously
    if not git_diff_ip:
        git_diff_ip.append(str(request.remote_addr))
        print("##### START request git_diff logic ##### (", str(request.remote_addr), ")")
        content = request.get_json(silent=True)
        print("content : " + str(content))
        converted_data = convert_data(content)
        print("prev converted_data : " + str(converted_data))
        git_diff_logic(converted_data)
        print("next converted_data : " + str(converted_data))
        print("##### END request git_diff logic ##### (", str(request.remote_addr), ")")
        git_diff_ip.remove(str(request.remote_addr))

    return "git_diff"


# Main
if __name__ == "__main__":

    # Load config
    host, port = load_server_config()

    # Run Server
    app.run(debug=True, host=host, port=port)
