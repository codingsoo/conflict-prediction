import pymysql

class work_database:

    # Constructor
    def __init__(self):
        # get mysql database connection
        self.conn = pymysql.connect(host='127.0.0.1',
                               user='root',
                               password='99189918',
                               db='uci_chat_bot',
                               charset='utf8')
        self.cursor = self.conn.cursor()


    # Delete User working data
    def delete_user_data(self, user_name):

        try:
            # create sql
            sql = "delete from working_table where user_name = '%s'" % user_name
            print(sql)

            # execute sql
            self.cursor.execute(sql)
            self.conn.commit()

        except:
            self.conn.rollback()

        return


    # Close Database connection and cursor
    def close_db(self):

        self.cursor.close()
        self.conn.close()