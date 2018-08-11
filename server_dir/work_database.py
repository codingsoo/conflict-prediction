import pymysql
import datetime as d
"""
class : work_database
function list
- __init__
- delete_user_data
"""

class work_database:

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

        ##### 1.
        # all conflict list
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

                # detect direct conflict : same file
                if (rows_list != []):
                    for temp_row in rows_list:
                        all_rows_list.append(temp_row)

        except:
            self.conn.rollback()
            print("ERROR : detect direct conflict")

        print(all_rows_list)


        # Conflict
        if(all_rows_list != []):

            # temp_other_work : ["project_name", "file_name", "logic_name", "user_name", "timestamp"]
            for temp_other_work in all_rows_list:
                # temp_user_work : ["file_name", "logic_name", "work_line", "work_amount"]
                for temp_user_work in working_list:

                    # Search already conflict data
                    already_conflict_list = list()

                    try:
                        # n_list = [user_name, temp_other_work[3]].sort()

                        sql = "select * " \
                              "from conflict_table " \
                              "where project_name = '%s' " \
                              "and file_name = '%s' " \
                              "and user1_name = '%s' " \
                              "and user2_name = '%s' " % (project_name, temp_user_work[0], user_name, temp_other_work[3])
                        print(sql)
                        self.cursor.execute(sql)
                        self.conn.commit()

                        already_conflict_list = self.cursor.fetchall()
                        already_conflict_list = list(already_conflict_list)

                    except:
                        self.conn.rollback()
                        print("ERROR : get conflict_table")


                    # Already conflict
                    if(already_conflict_list != []):
                        for temp_already1 in already_conflict_list:

                            t_ser = temp_already1[7]  # severity

                            # calculate severity
                            if (temp_user_work[1] == temp_other_work[2]):
                                if (temp_user_work[1][:3] == "def"):
                                    severity = 3
                                elif (temp_user_work[1][:5] == "class"):
                                    severity = 2
                                else:
                                    severity = 1

                                # After 30 minutes
                                if (d.datetime.today() - temp_already1[8] > d.timedelta(minutes=30)):
                                    if (t_ser < severity):
                                        print("getting severity")
                                    elif (t_ser == severity):
                                        print("same severity")
                                    else:
                                        print("lower severity")

                            else:
                                # After 30 minutes
                                if (d.datetime.today() - temp_already1[8] > d.timedelta(minutes=30)):
                                    print("softer")
                                severity = 1

                            try:
                                sql = "update conflict_table " \
                                      "set logic1_name = '%s', logic2_name = '%s', severity = %d " \
                                      "where project_name = '%s' " \
                                      "and file_name = '%s' " \
                                      "and user1_name = '%s' " \
                                      "and user2_name = '%s' " % (temp_user_work[1], temp_other_work[2], severity,
                                                                  project_name, temp_user_work[0], user_name, temp_other_work[3])
                                print(sql)
                                self.cursor.execute(sql)
                                self.conn.commit()

                            except:
                                self.conn.rollback()
                                print("ERROR : get conflict_table")

                    # First Conflict
                    else:
                        # logic name is same
                        if(temp_user_work[1] == temp_other_work[2]):

                            # calculate severity
                            if (temp_user_work[1][:3] == "def"):
                                severity = 3
                            elif (temp_user_work[1][:5] == "class"):
                                severity = 2
                            else:
                                severity = 1

                            print("first conflict!!")

                            self.insert_conflict_data(project_name=project_name,
                                                      file_name=temp_user_work[0],
                                                      logic1_name=temp_user_work[1],
                                                      logic2_name=temp_other_work[2],
                                                      user1_name=user_name,
                                                      user2_name=temp_other_work[3],
                                                      severity = severity)

        # Non-conflict
        else:
            try:
                sql = "delete " \
                      "from conflict_table " \
                      "where user1_name = '%s' " \
                      "or user2_name = '%s' " % (user_name, user_name)

                self.cursor.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()
                print("ERROR : delete user conflict data")

        return

    # Insert User data to working_table
    def insert_user_data(self, project_name, working_list, user_name):

        for temp_work in working_list:
            try:
                sql = "insert into working_table (project_name, file_name, logic_name, user_name, work_line, work_amount) " \
                      "value ('%s', '%s', '%s', '%s', %d, %d)" %(project_name, temp_work[0], temp_work[1], user_name, temp_work[2], temp_work[3])

                self.cursor.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()
                print("ERROR : insert user data")


    def alert_conflict(self):



        pass


    # Insert conflict data
    def insert_conflict_data(self, project_name, file_name, logic1_name, logic2_name, user1_name, user2_name, severity):
        # User 1 data
        try:
            sql1 = "insert into conflict_table (project_name, file_name, logic1_name, logic2_name, user1_name, user2_name, severity) " \
                   "value ('%s', '%s', '%s', '%s', '%s', '%s', %d)" % (project_name, file_name, logic1_name, logic2_name, user1_name, user2_name, severity)
            self.cursor.execute(sql1)
            self.conn.commit()
        except:
            self.conn.rollback()
            print("ERROR : insert conflict data")
        return


    # update conflict data
    def update_conflict_data(self, project_name, file_name, logic_name, user1_name, user2_name, severity):
        try:
            sql1 = "update conflict_table " \
                   "set logic_name = '%s', severity = %d " \
                   "where project_name = '%s' " \
                   "and file_name = '%s' " \
                   "and user1_name = '%s' " \
                   "and user2_name = '%s' " \
                   "" % (logic_name, severity, project_name, file_name, user1_name, user2_name)
            print(sql1)
            self.cursor.execute(sql1)
            self.conn.commit()
        except:
            self.conn.rollback()
            print("ERROR : update conflict data")
        return
    

    # Close Database connection and cursor
    def close_db(self):

        self.cursor.close()
        self.conn.close()