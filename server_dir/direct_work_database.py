import pymysql
import datetime as d
from server_dir.slack_message_sender import *
from server_dir.conflict_flag_enum import Conflict_flag
from chat_bot_server_dir.work_database import work_database
from server_dir.server_config_loader import load_database_connection_config

class direct_work_database:
    # Constructor
    def __init__(self):
        # Load mysql database connection config
        host, user, password, db, charset = load_database_connection_config()

        # get mysql database connection
        self.conn = pymysql.connect(host     = host,
                                    user     = user,
                                    password = password,
                                    db       = db,
                                    charset  = charset)

        # get cursor
        self.cursor = self.conn.cursor()

    # Delete User working data
    def delete_user_data(self, user_name):
        try:
            sql = "delete " \
                  "from working_table " \
                  "where user_name = '%s'" % (user_name)

            # execute sql
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

        except:
            self.conn.rollback()
            print("ERROR : delete user data")

        return

    # Detect Direct Conflict
    def detect_direct_conflict(self, project_name, working_list, user_name):
        w_db = work_database()

        remove_lock_list = w_db.prev_remove_lock_list()

        if remove_lock_list:
            send_remove_lock_channel("code-conflict-chatbot", remove_lock_list)
        w_db.auto_remove_lock_list()
        self.delete_direct_conflict_list()

        lock_file_list = w_db.inform_lock_file(project_name, working_list, user_name)
        lock_noticed_user_list = w_db.check_lock_noticed_user(project_name, lock_file_list, user_name)

        if lock_file_list and not lock_noticed_user_list:
            send_lock_message(lock_file_list, user_name)
            w_db.add_lock_notice_list(project_name, lock_file_list, user_name)


        elif lock_file_list and lock_noticed_user_list:
            already_noticed_lock_file_list = []
            for lfl in lock_file_list:
                for lnul in lock_noticed_user_list:
                   if lfl[1] == lnul[1]:
                       already_noticed_lock_file_list.append(lfl)

            for anlfl in already_noticed_lock_file_list:
                lock_file_list.remove(anlfl)

            if lock_file_list:
                send_lock_message(lock_file_list, user_name)
                w_db.add_lock_notice_list(project_name, lock_file_list, user_name)


        print("working list : ", working_list)

        file_conflict_list = self.search_working_table(project_name, working_list)
        file_conflict_list, file_approve_list = w_db.classify_direct_conflict_approved_list(project_name, file_conflict_list)
        w_db.close()

        print ("file_conflict_list : ",file_conflict_list)

        # Conflict
        if file_conflict_list:

            print("\n#### Direct Conflict !!! ####")

            already_conflict_list = self.search_already_direct_conflict_table(project_name, file_conflict_list, working_list, user_name)
            print("already_conflict_list : ", already_conflict_list)

            # Already conflicted
            if already_conflict_list:

                print("\n#### Already Direct Conflict !!! ####")

                # Search the best value of severity and return list
                best_conflict_list = self.search_best_conflict(project_name, file_conflict_list, working_list, user_name)

                # Compare current conflict and database conflict
                # Send the conflict message
                # Update conflict database
                self.compare_current_conflict_and_db_conflict(already_conflict_list, best_conflict_list)

            # First conflict
            else:

                print("\n#### First Direct Conflict !!! ####")

                # Search the best value of severity and return list
                best_conflict_list = self.search_best_conflict(project_name, file_conflict_list, working_list, user_name)
                self.update_first_best_conflict_list(best_conflict_list)

        # Non-conflict
        else:

            print("\n#### Non-Direct Conflict !!! ####")

            self.non_conflict_logic(project_name, user_name, file_approve_list)

        return

    # Delete conflict list
    def delete_direct_conflict_list(self):
        try:
            sql = "delete " \
                  "from direct_conflict_table " \
                  "where alert_count >= 2 " \
                  "and TIMEDIFF(now(),log_time) > 24*60*60"
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

        except:
            self.conn.rollback()
            print("ERROR : delete direct conflict list")

        return

    # Search same project and same file from working table
    def search_working_table(self, project_name, working_list):

        raw_list = []

        # ["file_name", "logic_name", "work_line", "work_amount"]
        for temp_work in working_list:
            if temp_work[3] == -1:
                temp_work[1] = "in"
            try:
                sql = "select * " \
                      "from working_table"

                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()
                test_tuple = self.cursor.fetchall()
                test_list = list(test_tuple)
                print("test : ", test_list)

                sql = "select * " \
                      "from working_table " \
                      "where project_name = '%s' " \
                      "and file_name = '%s' " % (project_name, temp_work[0])
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

                raw_list = list(self.cursor.fetchall())
                print ("Select from working_table : ", raw_list)

            except:
                self.conn.rollback()
                print("ERROR : search working table")

        return raw_list

    def search_already_direct_conflict_table(self, project_name, conflict_list, working_list, user_name):
        raw_list = list()

        # [ project_name, file_name, logic_name, user_name, work_line, work_amount, log_time]
        for temp_other_work in conflict_list:
            # ["file_name", "logic_name", "work_line", "work_amount"]
            for temp_user_work in working_list:
                try:
                    sql = "select * " \
                          "from direct_conflict_table " \
                          "where project_name = '%s' " \
                          "and file_name = '%s' " \
                          "and user1_name = '%s' " \
                          "and user2_name = '%s' " % (project_name, temp_user_work[0], user_name, temp_other_work[3])
                    print(sql)
                    self.cursor.execute(sql)
                    self.conn.commit()

                    raw_list = list(set(self.cursor.fetchall()))
                except:
                    self.conn.rollback()
                    print("ERROR : search already direct conflict table")

        return raw_list


    def search_best_conflict(self, project_name, conflict_list, working_list, user_name):
        best_conflict_dict = dict()
        all_severity_list = []

        # [ project_name, file_name, logic_name, user_name, work_line, work_amount, log_time]
        for temp_other_work in conflict_list:
            # ["file_name", "logic_name", "work_line", "work_amount"]
            for temp_user_work in working_list:
                # Same file name
                if temp_other_work[1] == temp_user_work[0]:
                    # Calculate severity of the current conflict
                    # Same logic name => search best conflict
                    if temp_other_work[2] == temp_user_work[1]:
                        if temp_user_work[1][:8] == "function":
                            print("same function direct conflict : 3")
                            severity = 3
                        elif temp_user_work[1][:5] == "class":
                            print("same def in same class direct conflict : 3")
                            severity = 3
                        else:
                            print("same in direct conflict : 1")
                            severity = 1
                    # Different logic name
                    else:
                        if ((temp_user_work[1][:5] == "class") and (temp_other_work[2][:5] == "class")
                        and (temp_user_work[1].split(':')[1] == temp_other_work[2].split(':')[1])):
                            print("same class direct conflict : 2")
                            severity = 2
                        else:
                            print("just in direct conflict : 1")
                            severity = 1

                    # key: file name / value: severity conflict list
                    if temp_user_work[0] in best_conflict_dict:
                        temp_conflict_list = []
                        temp_conflict_list.append(severity)
                        temp_conflict_list.append(project_name)         # project_name
                        temp_conflict_list.append(temp_user_work[0])    # file_name
                        temp_conflict_list.append(temp_user_work[1])    # logic1_name
                        temp_conflict_list.append(temp_other_work[2])   # logic2_name
                        temp_conflict_list.append(user_name)            # user1_name
                        temp_conflict_list.append(temp_other_work[3])   # user2_name

                        temp_all_list = []

                        for t_list in best_conflict_dict[temp_user_work[0]]:
                            temp_all_list.append(t_list)
                        temp_all_list.append(temp_conflict_list)

                        best_conflict_dict[temp_user_work[0]] = temp_all_list

                    else:
                        best_conflict_dict[temp_user_work[0]] = []

                        temp_conflict_list = []
                        temp_conflict_list.append(severity)
                        temp_conflict_list.append(project_name)         # project_name
                        temp_conflict_list.append(temp_user_work[0])    # file_name
                        temp_conflict_list.append(temp_user_work[1])    # logic1_name
                        temp_conflict_list.append(temp_other_work[2])   # logic2_name
                        temp_conflict_list.append(user_name)            # user1_name
                        temp_conflict_list.append(temp_other_work[3])   # user2_name

                        best_conflict_dict[temp_user_work[0]].append(temp_conflict_list)

        for temp_key in best_conflict_dict.keys():
            temp_best_conflict = max(best_conflict_dict[temp_key])
            all_severity_list.append(temp_best_conflict)

        return all_severity_list

    def compare_current_conflict_and_db_conflict(self, already_conflict_list, best_conflict_list):
        # [project_name, file_name, logic1_name, logic2_name, user1_name, user2_name, alert_count, severity, log_time]
        for temp_already in already_conflict_list:
            # [severity, project_name, file_name, logic1_name, logic2_name, user1_name, user2_name]
            for temp_best in best_conflict_list:
                conflict_flag = 0

                # Compare severity
                # same project and same logic
                if temp_already[0] == temp_best[1] and temp_already[1] == temp_best[2]:
                    if temp_already[7] < temp_best[0]:
                        print("direct : getting severity")
                        conflict_flag = Conflict_flag.getting_severity.value
                        send_conflict_message(conflict_flag=conflict_flag,
                                              conflict_project=temp_best[1],
                                              conflict_file=temp_best[2],
                                              conflict_logic=temp_best[3],
                                              user1_name=temp_best[5],
                                              user2_name=temp_best[6])

                    elif temp_already[7] == temp_best[0]:
                        print("direct same severity")
                        conflict_flag = Conflict_flag.same_severity.value

                    elif temp_already[7] > temp_best[0]:
                        print("direct lower severity")
                        conflict_flag = Conflict_flag.lower_severity.value
                        send_conflict_message(conflict_flag=conflict_flag,
                                              conflict_project=temp_best[1],
                                              conflict_file=temp_best[2],
                                              conflict_logic=temp_best[3],
                                              user1_name=temp_best[5],
                                              user2_name=temp_best[6])

                    # After 30 minutes => send direct message
                    if ((d.datetime.today() - temp_already[8] > d.timedelta(minutes=30))
                        and (temp_already[6] == 1) and (conflict_flag == Conflict_flag.same_severity.value)):
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
                        and (conflict_flag == Conflict_flag.same_severity.value)):
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

            if(temp_best[3] == temp_best[4]
                and temp_best[3][:5] == "class"
                and temp_best[4][:5] == "class"):
                # same class and same function
                conflict_flag = Conflict_flag.same_function.value

            elif(temp_best[3] == temp_best[4]
                and temp_best[3][:8] == "function"
                and temp_best[4][:8] == "function"):
                # same function
                conflict_flag = Conflict_flag.same_function.value

            elif(temp_best[3] != temp_best[4]
                and temp_best[3][:5] == "class"
                and temp_best[4][:5] == "class"
                and temp_best[3].split(':')[1] == temp_best[4].split(':')[1]):
                # just same class
                conflict_flag = Conflict_flag.same_class.value

            else:
                # just in
                conflict_flag = Conflict_flag.file_in.value

            send_conflict_message(conflict_flag=conflict_flag,
                                  conflict_project=temp_best[1],
                                  conflict_file=temp_best[2],
                                  conflict_logic=temp_best[3],
                                  user1_name=temp_best[5],
                                  user2_name=temp_best[6])
            return

        return

    def non_conflict_logic(self, project_name, user_name, file_approve_list):
        raw_list = []

        try:
            sql = "select * " \
                  "from direct_conflict_table " \
                  "where project_name = '%s' " \
                  "and user1_name = '%s'" % (project_name, user_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = list(self.cursor.fetchall())
        except:
            self.conn.rollback()
            print("ERROR : select user direct conflict data")

        # Do not notice a Conflict-Solve alarm that is resolved by Approve.
        remove_list = []

        print(raw_list)
        print(file_approve_list)
        for fal in file_approve_list:
            for rl in raw_list:
                if fal[0] == rl[0] and fal[1] == rl[1] and (fal[3] == rl[4] or fal[3] == rl[5]):
                    remove_list.append(rl)

        for rl in remove_list:
            raw_list.remove(rl)

        print("non_conflict_logic : ", raw_list)
        for raw_temp in raw_list:
            send_conflict_message(conflict_flag=Conflict_flag.conflict_finished.value,
                                  conflict_project=project_name,
                                  conflict_file=raw_temp[1],
                                  conflict_logic=raw_temp[2],
                                  user1_name=user_name,
                                  user2_name=raw_temp[5])

            send_conflict_message(conflict_flag=Conflict_flag.conflict_finished.value,
                                  conflict_project=project_name,
                                  conflict_file=raw_temp[1],
                                  conflict_logic=raw_temp[2],
                                  user1_name=raw_temp[5],
                                  user2_name=user_name)

        try:
            sql = "delete " \
                  "from direct_conflict_table " \
                  "where project_name = '%s' " \
                  "and (user1_name = '%s' or user2_name = '%s')" % (project_name, user_name, user_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            print("ERROR : delete user direct conflict data")

        return

    # Insert User data to working_table
    def insert_user_data(self, project_name, working_list, user_name):
        for temp_work in working_list:
            print("temp_work : ",temp_work)
            try:
                if temp_work[3] == -1:
                    temp_work[1] = "in"
                sql = "insert into working_table " \
                      "(project_name, file_name, logic_name, user_name, work_line, work_amount) " \
                      "value ('%s', '%s', '%s', '%s', %d, %d)" % (project_name, temp_work[0], temp_work[1], user_name, temp_work[2], temp_work[3])
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()
                print("ERROR : insert user data")

        return

    # Insert conflict data
    def insert_conflict_data(self, project_name, file_name, logic1_name, logic2_name, user1_name, user2_name, severity):
        try:
            if "in" in logic1_name or "in" in logic2_name:
                severity = 1
            sql = "insert into direct_conflict_table " \
                   "(project_name, file_name, logic1_name, logic2_name, user1_name, user2_name, severity) " \
                   "value ('%s', '%s', '%s', '%s', '%s', '%s', %d)" % (project_name, file_name, logic1_name, logic2_name, user1_name, user2_name, severity)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            print("ERROR : insert direct conflict data")

        return

    # update conflict data
    def update_conflict_data(self, project_name, file_name, logic1_name, logic2_name, user1_name, user2_name, severity):
        try:
            sql = "update direct_conflict_table " \
                  "set logic1_name = '%s', logic2_name = '%s', severity = %d " \
                  "where project_name = '%s' " \
                  "and file_name = '%s' " \
                  "and user1_name = '%s' " \
                  "and user2_name = '%s'" % (logic1_name, logic2_name, severity, project_name, file_name, user1_name, user2_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            print("ERROR : update direct direct_conflict_table")

        return

    def increase_alert_count(self, project_name, file_name, logic1_name, logic2_name, user1_name, user2_name):
        try:
            sql = "update direct_conflict_table " \
                  "set alert_count = alert_count + 1 " \
                  "where project_name = '%s' " \
                  "and file_name = '%s' " \
                  "and logic1_name = '%s' " \
                  "and logic2_name = '%s' " \
                  "and user1_name = '%s' " \
                  "and user2_name = '%s'" % (project_name, file_name, logic1_name, logic2_name, user1_name, user2_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            print("ERROR : increase direct alert count")

        return

    # Close Database connection and cursor
    def close_db(self):
        self.cursor.close()
        self.conn.close()