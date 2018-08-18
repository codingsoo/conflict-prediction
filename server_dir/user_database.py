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
                  "where git_id = '%s' " % user_name

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
            sql = "insert into working_table " \
                  "(git_id, slack_id) " \
                  "value ('%s', '%s') " % (git_id, str(random_number))

            # execute sql
            self.cursor.execute(sql)
            self.conn.commit()

        except:
            self.conn.rollback()
            print("ERROR : insert git id random number")