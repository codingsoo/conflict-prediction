import os
from pathlib import Path
import configparser

def load_server_config() :
    file_path = os.path.join(Path(os.getcwd()).parent, "all_server_config.ini")

    host = ""
    port = ""

    if not os.path.isfile(file_path) :
        print("ERROR :: There is no all_server_config.ini")
        exit(2)
    else :
        config = configparser.ConfigParser()
        config.read(file_path)
        try :
            host = config["SERVER"]["IP"]
            port = config["SERVER"]["PORT"]
            print("SUCCESS LOADING CONFIG")
        except :
            print("ERROR :: It is all_server_config.ini")
            exit(2)
    return host, port


def load_git_graph_server_config() :
    file_path = os.path.join(Path(os.getcwd()).parent, "all_server_config.ini")

    host = ""
    port = ""

    if not os.path.isfile(file_path) :
        print("ERROR :: There is no all_server_config.ini")
        exit(2)
    else :
        config = configparser.ConfigParser()
        config.read(file_path)
        try :
            host = config["GIT_GRAPH_SERVER"]["IP"]
            port = config["GIT_GRAPH_SERVER"]["PORT"]
            print("SUCCESS LOADING CONFIG")
        except :
            print("ERROR :: It is all_server_config.ini")
            exit(2)
    return host, port


def load_database_connection_config():
    file_path = os.path.join(Path(os.getcwd()).parent, "all_server_config.ini")

    host = ""
    user = ""
    password = ""
    database = ""
    charset = ""

    if not os.path.isfile(file_path) :
        print("ERROR :: There is no all_server_config.ini")
        exit(2)
    else :
        config = configparser.ConfigParser()
        config.read(file_path)
        try :
            host = config["MYSQL_CONNECTION"]["HOST"]
            user = config["MYSQL_CONNECTION"]["USER"]
            password = config["MYSQL_CONNECTION"]["PASSWORD"]
            database = config["MYSQL_CONNECTION"]["DATABASE"]
            charset = config["MYSQL_CONNECTION"]["CHARSET"]
            print("SUCCESS LOADING CONFIG")
        except :
            print("ERROR :: It is all_server_config.ini")
            exit(2)
    return host, user, password, database, charset