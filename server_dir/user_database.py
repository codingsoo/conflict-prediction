import pymysql
from server_dir.server_config_loader import load_database_connection_config
class user_database:

    # Constructor
    def __init__(self):
        # Load mysql database connection config
        host, user, password, db, charset = load_database_connection_config()

        # get mysql database connection
        self.conn = pymysql.connect(host=host,
                                    user=user,
                                    password=password,
                                    db=db,
                                    charset=charset)

        # get cursor
        self.cursor = self.conn.cursor()


    def search_user(self, user_name):
        raw_list = list()

        try:
            # create sql
            sql = "select * " \
                  "from user_table " \
                  "where git_id = '%s' " % user_name

            # execute sql
            print(sql)
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
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
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
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
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
            print(sql)
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


    def convert_slack_code_to_git_id(self, slack_code):

        raw = ""

        try:
            sql = "select git_id " \
                  "from user_table " \
                  "where slack_code = '%s' " % slack_code

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw = self.cursor.fetchall()[0][0]

        except:
            self.conn.rollback()
            print("ERROR : convert slack code to git id")

        return raw


    def match_user_git_id_code(self, slack_id):
        raw_list = list()
        try:
            sql = "select git_id " \
                  "from user_table " \
                  "where slack_id = '%s' " % slack_id

            # execute sql
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = self.cursor.fetchall()
            raw_list = list(raw_list)

        except:
            self.conn.rollback()
            print("ERROR : match user git id code data")

        if (raw_list != []):
            return raw_list
        else:
            return "No data", "No data"


    def close(self):
        self.cursor.close()
        self.conn.close()
        return
