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

        file_conflict_list = self.search_working_table(project_name, working_list)

        # Conflict
        if(file_conflict_list != []):

            print("#### Conflict !!! ####")

            already_conflict_list = self.search_already_conflict_table(project_name, file_conflict_list, working_list, user_name)

            # Already conflicted
            if(already_conflict_list != []):

                print("#### Already Conflict !!! ####")

                # Search the best value of severity and return list
                best_conflict_list = self.search_best_conflict(project_name, file_conflict_list, working_list, user_name)

                # Compare current conflict and database conflict
                # Send the conflict message
                # Update conflict database
                self.compare_current_conflict_and_db_conflict(already_conflict_list, best_conflict_list)

            # First conflict
            else:

                print("#### First Conflict !!! ####")

                # Search the best value of severity and return list
                best_conflict_list = self.search_best_conflict(project_name, file_conflict_list, working_list, user_name)
                self.update_first_best_conflict_list(best_conflict_list)

        # Non-conflict
        else:
            print("#### Non-Conflict !!! ####")
            self.non_conflict_logic(project_name, user_name)

        return


    # Delete conflict list
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
            print("ERROR : delete conflict list")

        return


    def search_working_table(self, project_name, working_list):

        all_row_list = list()

        # ["file_name", "logic_name", "work_line", "work_amount"]
        for temp_work in working_list:
            raw_list = list()
            try:
                sql = "select * " \
                      "from working_table " \
                      "where project_name = '%s' " \
                      "and file_name = '%s' " % (project_name, temp_work[0])
                print(sql)

                self.cursor.execute(sql)
                self.conn.commit()

                raw_list = self.cursor.fetchall()
                raw_list = list(raw_list)
            except:
                self.conn.rollback()
                print("ERROR : search working table")

            # There is conflict file
            if(raw_list != []):
                for temp in raw_list:
                    all_row_list.append(temp)

        return all_row_list


    def search_already_conflict_table(self, project_name, conflict_list, working_list, user_name):

        all_row_list = list()

        # [ project_name, file_name, logic_name, user_name, work_line, work_amount, log_time]
        for temp_other_work in conflict_list:

            # ["file_name", "logic_name", "work_line", "work_amount"]
            for temp_user_work in working_list:
                raw_list = list()
                try:
                    sql = "select * " \
                          "from conflict_table " \
                          "where project_name = '%s' " \
                          "and file_name = '%s' " \
                          "and user1_name = '%s' " \
                          "and user2_name = '%s' " % (project_name, temp_user_work[0], user_name, temp_other_work[3])
                    print(sql)

                    self.cursor.execute(sql)
                    self.conn.commit()

                    raw_list = self.cursor.fetchall()
                    raw_list = list(raw_list)
                except:
                    self.conn.rollback()
                    print("ERROR : search already conflict talbe")

                # There is conflict file
                if(raw_list != []):
                    for temp in raw_list:
                        all_row_list.append(temp)

        all_row_list = list(set(all_row_list))

        return all_row_list


    def search_best_conflict(self, project_name, conflict_list, working_list, user_name):
        # 미리 컨플릭트 난 리스트는 각 파일당 한개의 로직
        # 현재 컨플릭트 난 리스트는 각 파일당 여러개의 로직

        best_conflict_dict = dict()
        all_severity_list = list()

        # [ project_name, file_name, logic_name, user_name, work_line, work_amount, log_time]
        for temp_other_work in conflict_list:

            # ["file_name", "logic_name", "work_line", "work_amount"]
            for temp_user_work in working_list:

                # Same file name
                if(temp_other_work[1] == temp_user_work[0]):

                    # Calculate severity of the current conflict
                    # Same logic name => search best conflict
                    if(temp_other_work[2] == temp_user_work[1]):
                        if(temp_user_work[1][:8] == "function"):
                            print("same function conflict : 3")
                            severity = 3
                        elif(temp_user_work[1][:5] == "class"):
                            print("same def in same class conflict : 3")
                            severity = 3
                        else:
                            print("same in conflict : 1")
                            severity = 1

                    # Different logic name
                    else:
                        if(temp_user_work[1][:5] == "class"):
                            print("same class conflict : 2")
                            severity = 2
                        else:
                            print("just in conflict : 1")
                            severity = 1

                    print(temp_user_work[0])

                    # key: file name / value: severity conflict list
                    if(temp_user_work[0] in best_conflict_dict):

                        temp_conflict_list = list()
                        temp_conflict_list.append(severity)
                        temp_conflict_list.append(project_name)         # project_name
                        temp_conflict_list.append(temp_user_work[0])    # file_name
                        temp_conflict_list.append(temp_user_work[1])    # logic1_name
                        temp_conflict_list.append(temp_other_work[2])   # logic2_name
                        temp_conflict_list.append(user_name)            # user1_name
                        temp_conflict_list.append(temp_other_work[3])   # user2_name

                        temp_all_list = list()

                        for t_list in best_conflict_dict[temp_user_work[0]]:
                            temp_all_list.append(t_list)
                        temp_all_list.append(temp_conflict_list)

                        print(best_conflict_dict[temp_user_work[0]])

                        best_conflict_dict[temp_user_work[0]] = temp_all_list


                    else:
                        best_conflict_dict[temp_user_work[0]] = list()

                        temp_conflict_list = list()
                        temp_conflict_list.append(severity)
                        temp_conflict_list.append(project_name)         # project_name
                        temp_conflict_list.append(temp_user_work[0])    # file_name
                        temp_conflict_list.append(temp_user_work[1])    # logic1_name
                        temp_conflict_list.append(temp_other_work[2])   # logic2_name
                        temp_conflict_list.append(user_name)            # user1_name
                        temp_conflict_list.append(temp_other_work[3])   # user2_name

                        best_conflict_dict[temp_user_work[0]].append(temp_conflict_list)

        print(best_conflict_dict)

        for temp_key in best_conflict_dict.keys():
            print(temp_key)
            temp_best_conflict = max(best_conflict_dict[temp_key])
            all_severity_list.append(temp_best_conflict)

        print(all_severity_list)

        return all_severity_list


    def compare_current_conflict_and_db_conflict(self, already_conflict_list, best_conflict_list):

        print("#### compare current conflict ####")
        print(already_conflict_list)
        print(best_conflict_list)

        # [project_name, file_name, logic1_name, logic2_name, user1_name, user2_name, alert_count, severity, log_time]
        for temp_already in already_conflict_list:

            # [severity, project_name, file_name, logic1_name, logic2_name, user1_name, user2_name]
            for temp_best in best_conflict_list:

                conflict_flag = 0

                # Compare severity
                # same project and same logic
                if(temp_already[0] == temp_best[1] and temp_already[1] == temp_best[2]):

                    print("work name : " + temp_already[2] + " / " + temp_best[3])

                    if (temp_already[7] < temp_best[0]):
                        print("getting severity")
                        conflict_flag = 5
                        send_conflict_message(conflict_flag=conflict_flag,
                                              conflict_project=temp_best[1],
                                              conflict_file=temp_best[2],
                                              conflict_logic=temp_best[3],
                                              user1_name=temp_best[5],
                                              user2_name=temp_best[6])
                    elif (temp_already[7] == temp_best[0]):
                        print("same severity")
                        conflict_flag = 4
                    elif (temp_already[7] > temp_best[0]):
                        print("lower severity")
                        conflict_flag = 3
                        send_conflict_message(conflict_flag=conflict_flag,
                                              conflict_project=temp_best[1],
                                              conflict_file=temp_best[2],
                                              conflict_logic=temp_best[3],
                                              user1_name=temp_best[5],
                                              user2_name=temp_best[6])

                    # After 30 minutes => send direct message
                    if ((d.datetime.today() - temp_already[8] > d.timedelta(minutes=30))
                        and (temp_already[6] == 1)
                        and (conflict_flag == 4)):
                        send_conflict_message(conflict_flag=conflict_flag,
                                              conflict_project=temp_best[1],
                                              conflict_file=temp_best[2],
                                              conflict_logic=temp_best[3],
                                              user1_name=temp_best[5],
                                              user2_name=temp_best[6])
                        self.increase_alert_count(project_name=temp_best[1],
                                                  file_name=temp_best[2],
                                                  logic1_name=temp_best[3],
                                                  logic2_name=temp_best[4],
                                                  user1_name=temp_best[5],
                                                  user2_name=temp_best[6])

                    # After 60 minutes => send channel message
                    elif((d.datetime.today() - temp_already[8] > d.timedelta(minutes=60))
                        and (temp_already[6] == 2)
                        and (conflict_flag == 4)):
                        send_conflict_message_channel(conflict_project=temp_best[1],
                                                      conflict_file=temp_best[2],
                                                      conflict_logic=temp_best[3],
                                                      user1_name=temp_best[5],
                                                      user2_name=temp_best[6])


                    self.update_conflict_data(project_name=temp_best[1],
                                              file_name=temp_best[2],
                                              logic1_name=temp_best[3],
                                              logic2_name=temp_best[4],
                                              user1_name=temp_best[5],
                                              user2_name=temp_best[6],
                                              severity=temp_best[0])

        return


    def update_first_best_conflict_list(self, best_conflict_list):

        # [severity, project_name, file_name, logic1_name, logic2_name, user1_name, user2_name]
        print("#### update first best conflict list #####")
        print(best_conflict_list)
        for temp_best in best_conflict_list:
            self.insert_conflict_data(project_name=temp_best[1],
                                      file_name=temp_best[2],
                                      logic1_name=temp_best[3],
                                      logic2_name=temp_best[4],
                                      user1_name=temp_best[5],
                                      user2_name=temp_best[6],
                                      severity=temp_best[0])

            send_conflict_message(conflict_flag=4,
                                  conflict_project=temp_best[1],
                                  conflict_file=temp_best[2],
                                  conflict_logic=temp_best[3],
                                  user1_name=temp_best[5],
                                  user2_name=temp_best[6])
            return
        return


    def non_conflict_logic(self, project_name, user_name):
        raw_list_temp = list()
        try:
            sql = "select * " \
                  "from conflict_table " \
                  "where user1_name = '%s' " % (user_name)
            print(sql)

            self.cursor.execute(sql)
            self.conn.commit()

            raw_list_temp = self.cursor.fetchall()
            raw_list_temp = list(raw_list_temp)
        except:
            self.conn.rollback()
            print("ERROR : delete user conflict data")

        print(raw_list_temp)

        if (raw_list_temp != []):
            for raw_temp in raw_list_temp:
                send_conflict_message(conflict_flag=-1,
                                      conflict_project=project_name,
                                      conflict_file=raw_temp[1],
                                      conflict_logic=raw_temp[2],
                                      user1_name=user_name,
                                      user2_name=raw_temp[5])

                send_conflict_message(conflict_flag=-1,
                                      conflict_project=project_name,
                                      conflict_file=raw_temp[1],
                                      conflict_logic=raw_temp[2],
                                      user1_name=raw_temp[5],
                                      user2_name=user_name)

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
            print("temp : " + temp_work[0])
            try:
                sql = "insert into working_table (project_name, file_name, logic_name, user_name, work_line, work_amount) " \
                      "value ('%s', '%s', '%s', '%s', %d, %d)" %(project_name, temp_work[0], temp_work[1], user_name, temp_work[2], temp_work[3])
                print(sql)

                self.cursor.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()
                print("ERROR : insert user data")


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


    # Close Database connection and cursor
    def close_db(self):

        self.cursor.close()
        self.conn.close()