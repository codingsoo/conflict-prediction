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

        # get cursor
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
            print("ERROR : delete user data")

        return


    # Detect Direct Conflict
    def detect_direct_conflict(self, project_name, working_list, user_name):

        rows = list()

        # search [project_name, file_name] in the working_table
        try:
            # search each file name
            for temp_work in working_list:
                sql = "select * " \
                      "from working_table " \
                      "where project_name = '%s' " \
                      "and file_name = '%s'" % (project_name, temp_work[0])

                self.cursor.execute(sql)
                self.conn.commit()

                rows = self.cursor.fetchall()
                rows = list(rows)

                # detect direct conflict
                if(rows != []):
                    break

        except:
            self.conn.rollback()
            print("ERROR : detect direct conflict")

        # Direct Conflict
        if(rows != []):
            for temp_other_work in rows:
                for temp_user_work in working_list:

                    # other_logic_name == current_user_logic_name
                    if(temp_other_work[2] == temp_user_work[1]):
                        print(temp_other_work[2] + " conflict")

            result = "conflict"
        else:
            result = "non-conflict"

        return result


    def insert_user_data(self, project_name, working_list, user_name):

        for temp_work in working_list:
            sql = "insert into working_table (project_name, file_name, logic_name, user_name) " \
                  "value ('%s', '%s', '%s', '%s')" %(project_name, temp_work[0], temp_work[1], user_name)

            self.cursor.execute(sql)
            self.conn.commit()

    # Close Database connection and cursor
    def close_db(self):

        self.cursor.close()
        self.conn.close()