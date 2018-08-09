import pymysql

def git_diff_logic(content):

    pass


def get_db_cursor():

    # get mysql database connection
    conn = pymysql.connect(host = '127.0.0.1',
                           user = 'root',
                           password = '99189918',
                           db = 'uci_chat_bot',
                           charset = 'utf8')

    # return mysql connection cursor
    return conn.cursor()


def delete_user_data(user_name):

    # create sql
    sql = "select * " \
          "from working_table " \
          "where user_name = \'%s\'" %user_name

    # get cursor
    curs = get_db_cursor()

    # execute sql
    curs.execute(sql)

    # get rows
    rows = curs.fetchall()
    rows = list(rows)

    if rows == []:
        print("none")
    else:
        print("data !!")

    return