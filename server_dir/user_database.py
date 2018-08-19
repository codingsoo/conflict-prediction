import pymysql

class user_database:

    # Constructor
    def __init__(self):
        # get mysql database connection
        self.conn = pymysql.connect(host     = '127.0.0.1',
                                    user     = 'root',
                                    password = '99189918',
                                    db       = 'uci_chat_bot',
                                    charset  = 'utf8')

        # get cursor
        self.cursor = self.conn.cursor()


    def search_user(self, user_name):
        raw_list = list()

        try:
            # create sql
            sql = "select *" \
                  "from user_table " \
                  "where git_id = '%s' " \
                  "and slack_code = 'NULL' " % user_name

            # execute sql
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = self.cursor.fetchall()
            raw_list = list(raw_list)

        except:
            self.conn.rollback()
            print("ERROR : search user data")

        if(raw_list != []):
            return True
        else:
            return False


    def insert_git_id_random_number(self, git_id, random_number):
        try:
            # create sql
            sql = "insert into user_table " \
                  "(git_id, slack_id) " \
                  "value ('%s', '%s') " % (git_id, str(random_number))

            # execute sql
            self.cursor.execute(sql)
            self.conn.commit()
            print(sql)
        except:
            self.conn.rollback()
            print("ERROR : insert git id random number")


    def set_slack_id_code(self, random_number, slack_id, slack_code):
        try:
            # create sql
            sql = "update user_table " \
                  "set slack_id = '%s', slack_code = '%s' " \
                  "where slack_id = '%s' " % (slack_id, slack_code, random_number)

            # execute sql
            self.cursor.execute(sql)
            self.conn.commit()
            print(sql)
        except:
            self.conn.rollback()
            print("ERROR : set slack id code")


    def search_user_slack_id_code(self, git_id):
        raw_list = list()

        try:
            # create sql
            sql = "select slack_id, slack_code " \
                  "from user_table " \
                  "where git_id = '%s' " % git_id

            # execute sql
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = self.cursor.fetchall()
            raw_list = list(raw_list)

        except:
            self.conn.rollback()
            print("ERROR : search user slack id code data")

        if(raw_list != []):
            return raw_list
        else:
            return "No data", "No data"

    def close(self):
        self.cursor.close()
        self.conn.close()
        return