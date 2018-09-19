import pymysql
import datetime as d
from server_dir.slack_message_sender import *
from server_dir.conflict_flag_enum import Conflict_flag
from chat_bot_server_dir.work_database import work_database
from server_dir.server_config_loader import *

class indirect_work_database:

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
    def detect_indirect_conflict(self, project_name, working_list, user_name):
        print("\n" + "#### START detect indirect conflict logic ####")
        w_db = work_database()

        self.delete_indirect_conflict_list()

        remove_lock_list = w_db.prev_remove_lock_list()
        if remove_lock_list:
            send_remove_lock_channel("code-conflict-chatbot", remove_lock_list)
        w_db.auto_remove_lock_list()

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

        other_working_list = self.search_working_table(project_name, user_name)
        indirect_conflict_list = self.search_logic_dependency(project_name, working_list, other_working_list, user_name)
        indirect_conflict_list, file_approve_list = w_db.classify_indirect_conflict_approved_list(project_name, indirect_conflict_list)

        print("indirect_conflict_list : ", indirect_conflict_list)

        # Conflict
        if indirect_conflict_list:

            print("\n#### Indirect Conflict !!! ####")

            already_indirect_conflict_table = self.search_already_indirect_conflict_table(project_name, indirect_conflict_list)
            first_indirect_conflict_list, already_indirect_conflict_list = self.classify_indirect_conflict_list(indirect_conflict_list, already_indirect_conflict_table)
            print("already_indirect_conflict_table : ", already_indirect_conflict_table)
            print("first_indirect_conflict_list : ", first_indirect_conflict_list)
            print("already_indirect_conflict_list : ", already_indirect_conflict_list)

            # Already indirect conflicted
            if already_indirect_conflict_table:
                print("\n#### Already Indirect Conflict !!! ####")
                self.already_indirect_logic(project_name, user_name, already_indirect_conflict_table)

            # First indirect conflict
            if first_indirect_conflict_list:
                print("\n#### First Indirect Conflict !!! ####")
                self.first_indirect_logic(project_name, user_name, first_indirect_conflict_list)

        # Non-conflict
        else:
            print("\n#### Non-Indirect Conflict !!! ####")
            self.non_indirect_conflict_logic(project_name, user_name, file_approve_list)

        w_db.close()
        return


    # Delete conflict list
    def delete_indirect_conflict_list(self):
        try:
            sql = "delete " \
                  "from indirect_conflict_table " \
                  "where alert_count >= 3 " \
                  "and TIMEDIFF(now(),log_time) > 24*60*60"
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

        except:
            self.conn.rollback()
            print("ERROR : delete indirect conflict list")

        return

    # Search working_table
    def search_working_table(self, project_name, user_name):
        raw_list = []

        try:
            sql = "select * " \
                  "from working_table " \
                  "where project_name = '%s' " \
                  "and user_name != '%s'" % (project_name, user_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = list(self.cursor.fetchall())
            print("select from working_table : ", raw_list)
        except:
            self.conn.rollback()
            print("ERROR : search indirect working table")

        return raw_list

    def search_logic_dependency(self, project_name, user_working_list, other_working_list, user_name):
        all_raw_list = []

        # ["file_name", "logic_name", "work_line", "work_amount"]
        for temp_user_work in user_working_list:
            # [ project_name, file_name, logic_name, user_name, work_line, work_amount, log_time]
            for temp_other_work in other_working_list:
                if temp_user_work[0] != temp_other_work[1]:
                    temp_user_logic = temp_user_work[0] + "|" + temp_user_work[1]
                    temp_other_logic = temp_other_work[1] + "|" + temp_other_work[2]

                    try:
                        sql = "select * " \
                              "from logic_dependency " \
                              "where project_name = '%s' " \
                              "and ((u = '%s' and v = '%s') or (u = '%s' and v = '%s'))" \
                              % (project_name, temp_user_logic, temp_other_logic, temp_other_logic, temp_user_logic)
                        print(sql)
                        self.cursor.execute(sql)
                        self.conn.commit()

                        raw = self.cursor.fetchone()

                        if raw:
                            temp_raw = []

                            temp_raw.append(user_name)          # user name
                            temp_raw.append(temp_user_logic)    # user logic
                            temp_raw.append(temp_other_work[3]) # other name
                            temp_raw.append(temp_other_logic)   # other logic
                            temp_raw.append(raw[3])        # length

                            # [user_name, user_logic, other_name, other_logic]
                            all_raw_list.append(temp_raw)

                    except:
                        self.conn.rollback()
                        print("ERROR : search logic dependency")

        return all_raw_list

    def search_already_indirect_conflict_table(self, project_name, indirect_conflict_list):
        all_raw_list = []

        # [ user1_name, user1_logic, user2_name, user2_logic ]
        for temp_indirect_conflict in indirect_conflict_list:
            try:
                sql = "select * " \
                      "from indirect_conflict_table " \
                      "where project_name = '%s' " \
                      "and u = '%s' and v = '%s' " \
                      "and user1_name = '%s' and user2_name = '%s'" \
                      % (project_name, temp_indirect_conflict[1], temp_indirect_conflict[3], temp_indirect_conflict[0], temp_indirect_conflict[2])

                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

                raw_list = list(self.cursor.fetchall())
                if raw_list:
                    for raw in raw_list:
                        all_raw_list.append(raw)

            except:
                self.conn.rollback()
                print("ERROR : search already indirect conflict table")

        return all_raw_list

    def classify_indirect_conflict_list(self, whole_indirect_conflict_list, already_indirect_conflict_table):
        # first_indirect_conflict_list = whole_indirect_conflict_list - already_indirect_conflict_list
        first_indirect_conflict_list = whole_indirect_conflict_list
        already_indirect_conflict_list = []
        # [ user1_name, user1_logic, user2_name, user2_logic ]
        for temp_whole_indirect_conflict_list in whole_indirect_conflict_list:
            # [ project_name, logic1_name, logic2_name, length, user1_name, user2_name, alert_count, log_time]
            for temp_already_indirect_conflict_table in already_indirect_conflict_table:
                if (temp_whole_indirect_conflict_list[0] == temp_already_indirect_conflict_table[4] and
                        temp_whole_indirect_conflict_list[1] == temp_already_indirect_conflict_table[1] and
                        temp_whole_indirect_conflict_list[2] == temp_already_indirect_conflict_table[5] and
                        temp_whole_indirect_conflict_list[3] == temp_already_indirect_conflict_table[2]):
                    already_indirect_conflict_list.append(temp_whole_indirect_conflict_list)

        for temp_already_indirect_conflict_list in already_indirect_conflict_list:
            first_indirect_conflict_list.remove(temp_already_indirect_conflict_list)

        return first_indirect_conflict_list, already_indirect_conflict_list

    def already_indirect_logic(self, project_name, user_name, already_indirect_conflict_table):
        # [ project_name, logic1_name, logic2_name, length, user1_name, user2_name, alert_count, log_time]
        for temp_already in already_indirect_conflict_table:
            # After 30 minutes => send direct message
            if ((d.datetime.today() - temp_already[7] > d.timedelta(minutes=30)) and (temp_already[6] == 1)):

                temp_file_logic1 = temp_already[1].split('|')
                temp_file_logic2 = temp_already[2].split('|')

                send_conflict_message(conflict_flag=Conflict_flag.indirect_conflict.value,
                                      conflict_project=project_name,
                                      conflict_file=temp_file_logic1,
                                      conflict_logic=temp_file_logic2,
                                      user1_name=user_name,
                                      user2_name=temp_already[5])

                self.increase_alert_count(project_name=project_name,
                                          u=temp_already[1],
                                          v=temp_already[2],
                                          user1_name=temp_already[4],
                                          user2_name=temp_already[5])

            # After 60 minutes => send channel message
            if ((d.datetime.today() - temp_already[7] > d.timedelta(minutes=60)) and (temp_already[6] == 2)):

                temp_file_logic1 = temp_already[1].split('|')
                temp_file_logic2 = temp_already[2].split('|')

                send_conflict_message_channel(conflict_file=temp_file_logic1,
                                              conflict_logic=temp_file_logic2,
                                              user1_name=user_name,
                                              user2_name=temp_already[5])

                self.increase_alert_count(project_name=project_name,
                                          u=temp_already[1],
                                          v=temp_already[2],
                                          user1_name=temp_already[4],
                                          user2_name=temp_already[5])

                self.increase_alert_count(project_name=project_name,
                                          u=temp_already[2],
                                          v=temp_already[1],
                                          user1_name=temp_already[5],
                                          user2_name=temp_already[4])

        return

    def first_indirect_logic(self, project_name, user_name, indirect_conflict_list):
        for temp_conflict in indirect_conflict_list:
            temp_file_logic1 = temp_conflict[1].split('|')
            temp_file_logic2 = temp_conflict[3].split('|')
            self.insert_conflict_data(project_name, temp_conflict)
            send_conflict_message(conflict_flag=Conflict_flag.indirect_conflict.value,
                                  conflict_project=project_name,
                                  conflict_file=temp_file_logic1,
                                  conflict_logic=temp_file_logic2,
                                  user1_name=user_name,
                                  user2_name=temp_conflict[2])

        return

    # Insert conflict data
    def insert_conflict_data(self, project_name, indirect_conflict_list):
        # [user1_name, user1_logic, user2_name, user2_logic, length]
        sql = "insert into indirect_conflict_table " \
              "(project_name, u, v, length, user1_name, user2_name) " \
              "value ('%s', '%s', '%s', %d, '%s', '%s')" \
              % (project_name, indirect_conflict_list[1], indirect_conflict_list[3], indirect_conflict_list[4], indirect_conflict_list[0], indirect_conflict_list[2])

        try:
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            print("ERROR : insert indirect conflict data")

        return


    def non_indirect_conflict_logic(self, project_name, user_name, approve_file_list):
        raw_list = []
        try:
            sql = "select * " \
                  "from indirect_conflict_table " \
                  "where project_name = '%s' " \
                  "and (user1_name = '%s' or user2_name = '%s') " % (project_name, user_name, user_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = list(self.cursor.fetchall())

        except:
            self.conn.rollback()
            print("ERROR : select user indirect conflict data")

        # Do not notice a Conflict-Solve alarm that is resolved by Approve.
        remove_list = []

        print("indirect_conflict_table : ", raw_list)
        print("approve_file_list : ", approve_file_list)

        # [ user_name, user_logic, other_name, other_logic ]
        for afl in approve_file_list:
            # [ project_name, u, v, length, user1_name, user2_name, alert_count, log_time ]
            for rl in raw_list:
                if ((afl[0] == rl[4] or afl[0] == rl[5]) and
                        (afl[1] == rl[1] or afl[1] == rl[2]) and
                        (afl[2] == rl[4] or afl[2] == rl[5]) and
                        (afl[3] == rl[1] or afl[3] == rl[2])):
                    remove_list.append(rl)

        for temp_remove_list in remove_list:
            raw_list.remove(temp_remove_list)

        print("non_indifrect_conflict_logic : ", raw_list)

        # Send to the user about indirect solved message
        for raw_temp in raw_list:
            send_conflict_message(conflict_flag=Conflict_flag.indirect_conflict_finished.value,
                                  conflict_project=project_name,
                                  conflict_file=raw_temp[1],
                                  conflict_logic=raw_temp[2],
                                  user1_name=user_name,
                                  user2_name=raw_temp[5])

            send_conflict_message(conflict_flag=Conflict_flag.indirect_conflict_finished.value,
                                  conflict_project=project_name,
                                  conflict_file=raw_temp[1],
                                  conflict_logic=raw_temp[2],
                                  user1_name=raw_temp[5],
                                  user2_name=user_name)

        # Delete all user conflict list
        try:
            sql = "delete " \
                  "from indirect_conflict_table " \
                  "where project_name = '%s' " \
                  "and (user1_name = '%s' or user2_name = '%s')" % (project_name, user_name, user_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

        except:
            self.conn.rollback()
            print("ERROR : delete user indirect conflict data")

        return

    def increase_alert_count(self, project_name, u, v, user1_name, user2_name):
        try:
            sql = "update indirect_conflict_table " \
                  "set alert_count = alert_count + 1 " \
                  "where project_name = '%s' " \
                  "and u = '%s' " \
                  "and v = '%s' " \
                  "and user1_name = '%s' " \
                  "and user2_name = '%s'" % (project_name, u, v, user1_name, user2_name)
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