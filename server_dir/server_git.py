import pymysql

def git_diff_logic(content):

    pass


def get_db_conn():

    # get mysql database connection
    conn = pymysql.connect(host = '127.0.0.1',
                           user = 'root',
                           password = '99189918',
                           db = 'uci_chat_bot',
                           charset = 'utf8')

    # return mysql connection cursor
    return conn.cursor()