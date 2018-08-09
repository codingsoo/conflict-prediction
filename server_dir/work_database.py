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

            # execute sql
            self.cursor.execute(sql)
            self.conn.commit()

        except:
            self.conn.rollback()
            print("ERROR : delete user data")

        return


    # Detect Direct Conflict
    def detect_direct_conflict(self, project_name, working_list, user_name):

        all_rows_list = list()

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

                # get rows data
                rows_list = self.cursor.fetchall()
                rows_list = list(rows_list)

                # detect direct conflict
                if(rows_list != []):
                    for temp_row in rows_list:
                        all_rows_list.append(temp_row)

        except:
            self.conn.rollback()
            print("ERROR : detect direct conflict")

        # Direct Conflict
        if(all_rows_list != []):
            for temp_other_work in all_rows_list:
                for temp_user_work in working_list:

                    # Condition
                    # other_file_name == current_user_file_name and other_logic_name == current_user_logic_name
                    if(temp_other_work[1] == temp_user_work[0]
                       and temp_other_work[2] == temp_user_work[1]):
                        print("*** Conflict ***")
                        print("project name : " + project_name)
                        print("file name : " + temp_other_work[1])
                        print("logic name : "+ temp_other_work[2] + '\n')

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