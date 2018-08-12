import pymysql
import datetime as d
from server_dir.slack_message_sender import *

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

        self.delete_conflict_list()

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
                print(sql)

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

        all_rows_list = list(set(all_rows_list))
        print(all_rows_list)

        # Conflict
        if(all_rows_list != []):

            # temp_other_work : ["project_name", "file_name", "logic_name", "user_name", "working_line", "working_amount","timestamp"]
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

                    print(already_conflict_list)

                    # Already conflict
                    if(already_conflict_list != []):
                        for temp_already1 in already_conflict_list:

                            t_ser = temp_already1[7]  # severity

                            # calculate severity
                            if (temp_user_work[0] == temp_other_work[1]
                                and temp_user_work[1] == temp_other_work[2]):
                                if (temp_user_work[1][:8] == "function"):
                                    severity = 3
                                elif (temp_user_work[1][:5] == "class"):
                                    severity = 3
                                else:
                                    severity = 1

                                # After 30 minutes
                                if ((d.datetime.today() - temp_already1[8] > d.timedelta(minutes=30))
                                     and (temp_already1[6] == 1)):
                                    if (t_ser < severity):
                                        print("getting severity")
                                        conflict_flag = 5
                                    elif (t_ser == severity):
                                        print("same severity")
                                        conflict_flag = 4
                                    else:
                                        print("lower severity")
                                        conflict_flag = 3
                                    send_conflict_message(conflict_flag=conflict_flag,
                                                          conflict_project=project_name,
                                                          conflict_file=temp_user_work[1],
                                                          conflict_logic=temp_user_work[0],
                                                          user1_name=user_name,
                                                          user2_name=temp_other_work[3])



                                    self.increase_alert_count(project_name=project_name,
                                                              file_name=temp_user_work[0],
                                                              logic1_name=temp_user_work[1],
                                                              logic2_name=temp_other_work[2],
                                                              user1_name=user_name,
                                                              user2_name=temp_other_work[3])

                                self.update_conflict_data(project_name=project_name,
                                                          file_name=temp_user_work[0],
                                                          logic1_name=temp_user_work[1],
                                                          logic2_name=temp_other_work[2],
                                                          user1_name=user_name,
                                                          user2_name=temp_other_work[3],
                                                          severity=severity)


                            elif(temp_user_work[0] == temp_other_work[1]
                                 and temp_user_work[1] != temp_other_work[2]):


                                if (temp_user_work[1][:5] == "class"):
                                    severity = 2
                                    print("alredy conflict : class : 2")
                                else:
                                    print("already conflict : softer : 1")
                                    severity = 1

                                # After 30 minutes
                                if ((d.datetime.today() - temp_already1[8] > d.timedelta(minutes=30))
                                     and (temp_already1[6] == 1)):
                                    if (t_ser < severity):
                                        print("getting severity")
                                        conflict_flag = 5
                                    elif (t_ser == severity):
                                        print("same severity")
                                        conflict_flag = 4
                                    else:
                                        print("lower severity")
                                        conflict_flag = 3

                                    send_conflict_message(conflict_flag=conflict_flag,
                                                          conflict_project=project_name,
                                                          conflict_file=temp_user_work[1],
                                                          conflict_logic=temp_user_work[0],
                                                          user1_name=user_name,
                                                          user2_name=temp_other_work[3])


                                    self.increase_alert_count(project_name=project_name,
                                                              file_name=temp_user_work[0],
                                                              logic1_name=temp_user_work[1],
                                                              logic2_name=temp_other_work[2],
                                                              user1_name=user_name,
                                                              user2_name=temp_other_work[3])

                                self.update_conflict_data(project_name=project_name,
                                                          file_name=temp_user_work[0],
                                                          logic1_name=temp_user_work[1],
                                                          logic2_name=temp_other_work[2],
                                                          user1_name=user_name,
                                                          user2_name=temp_other_work[3],
                                                          severity=severity)

                    # First Conflict
                    else:
                        # file name is same
                        # logic name is same
                        if(temp_user_work[0] == temp_other_work[1]
                            and temp_user_work[1] == temp_other_work[2]):
                            print("work name : " + temp_user_work[1] + temp_other_work[2])

                            # calculate severity
                            if (temp_user_work[1][:8] == "function"):
                                severity = 3
                                conflict_flag = 2
                                print("### first conflict : function : 3")
                            elif (temp_user_work[1][:5] == "class"):
                                severity = 3
                                conflict_flag = 1
                                print("### first conflict : same function in class : 3")
                            else:
                                severity = 1
                                conflict_flag = 0
                                print("### first conflict: : just in : 1")

                            send_conflict_message(conflict_flag=conflict_flag,
                                                  conflict_project=project_name,
                                                  conflict_file=temp_user_work[1],
                                                  conflict_logic=temp_user_work[0],
                                                  user1_name=user_name,
                                                  user2_name=temp_other_work[3])

                            self.insert_conflict_data(project_name=project_name,
                                                      file_name=temp_user_work[0],
                                                      logic1_name=temp_user_work[1],
                                                      logic2_name=temp_other_work[2],
                                                      user1_name=user_name,
                                                      user2_name=temp_other_work[3],
                                                      severity = severity)

                        # Just in
                        # file name is same
                        elif(temp_user_work[0] == temp_other_work[1]):

                            # Same class conflict
                            if(temp_user_work[1][:5] == "class"):
                                severity = 2
                                conflict_flag = 1
                                print("### first conflict : just in class : 2 ###")

                            # in conflict
                            else:
                                severity = 1
                                conflict_flag = 0
                                print("### just in ####")

                            send_conflict_message(conflict_flag=conflict_flag,
                                                  conflict_project=project_name,
                                                  conflict_file=temp_user_work[1],
                                                  conflict_logic=temp_user_work[0],
                                                  user1_name=user_name,
                                                  user2_name=temp_other_work[3])

                            self.insert_conflict_data(project_name=project_name,
                                                      file_name=temp_user_work[0],
                                                      logic1_name=temp_user_work[1],
                                                      logic2_name=temp_other_work[2],
                                                      user1_name=user_name,
                                                      user2_name=temp_other_work[3],
                                                      severity=severity)

        # Non-conflict
        else:
            try:
                sql = "delete " \
                      "from conflict_table " \
                      "where user1_name = '%s' " \
                      "or user2_name = '%s' " % (user_name, user_name)
                print(sql)

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
                print(sql)

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
            print(sql1)
        except:
            self.conn.rollback()
            print("ERROR : insert conflict data")
        return


    # update conflict data
    def update_conflict_data(self, project_name, file_name, logic1_name, logic2_name, user1_name, user2_name, severity):
        try:
            sql = "update conflict_table " \
                  "set logic1_name = '%s', logic2_name = '%s', severity = %d " \
                  "where project_name = '%s' " \
                  "and file_name = '%s' " \
                  "and user1_name = '%s' " \
                  "and user2_name = '%s' " % (logic1_name, logic2_name, severity,
                                              project_name, file_name, user1_name, user2_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

        except:
            self.conn.rollback()
            print(self.cursor.Error)
            print("ERROR : update conflict_table")
        return
    

    def increase_alert_count(self, project_name, file_name, logic1_name, logic2_name, user1_name, user2_name):
        try:
            sql = "update conflict_table " \
                  "set alert_count = alert_count + 1 " \
                  "where project_name = '%s' " \
                  "and file_name = '%s' " \
                  "and logic1_name = '%s' " \
                  "and logic2_name = '%s' " \
                  "and user1_name = '%s' " \
                  "and user2_name = '%s' " % (project_name, file_name, logic1_name, logic2_name, user1_name, user2_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            print("ERROR : increase alert count")


    def delete_conflict_list(self):

        try:
            sql = "delete " \
                  "from conflict_table " \
                  "where alert_count >= 2 " \
                  "and TIMEDIFF(now(),log_time) > 24"
            print(sql)

            self.cursor.execute(sql)
            self.conn.commit()

        except:
            self.conn.rollback()
            print("ERROR : get conflict_table")

        return


    # Close Database connection and cursor
    def close_db(self):

        self.cursor.close()
        self.conn.close()