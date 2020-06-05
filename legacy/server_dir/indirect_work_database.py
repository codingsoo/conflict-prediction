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
    def detect_indirect_conflict(self, project_name, user_name):
        print("\n" + "#### START detect indirect conflict logic ####")
        # working_list : [ { project_name, file_name, logic_name, user_name, work_line, work_amount, log_time } , ... ]
        user_working_list = self.search_user_working_table(project_name, user_name)
        other_working_list = self.search_other_working_table(project_name, user_name)
        # calling_list : [ { project_name, user_name, file_name, calling_file, calling_logic, log_time } , ... ]
        user_calling_list = self.search_user_calling_table(project_name, user_name)
        other_calling_list = self.search_other_calling_table(project_name, user_name)

        w_db = work_database()

        self.delete_indirect_conflict_list()

        user_slack_code = w_db.convert_git_id_to_slack_code(user_name)
        user_call_indirect_conflict_list = self.search_logic_dependency(project_name, user_calling_list, other_working_list, type="user_call")
        user_work_indirect_conflict_list = self.search_logic_dependency(project_name, other_calling_list, user_working_list, type="user_work")
        # user_call_indirect_conflict_list, user_call_file_approve_list = w_db.classify_indirect_conflict_approved_list(user_slack_code, user_call_indirect_conflict_list)
        # user_work_indirect_conflict_list, user_work_file_approve_list = w_db.classify_indirect_conflict_approved_list(user_slack_code, user_work_indirect_conflict_list)

        # Conflict
        if user_call_indirect_conflict_list:

            print("\n#### User Call Indirect Conflict !!! ####")

            user_call_already_indirect_conflict_table = self.search_already_indirect_conflict_table(project_name, user_call_indirect_conflict_list, type="user_call")
            user_call_first_indirect_conflict_list, user_call_already_indirect_conflict_list = self.classify_indirect_conflict_list(user_call_indirect_conflict_list, user_call_already_indirect_conflict_table, type="user_call")
            print("user_call_already_indirect_conflict_table : ", user_call_already_indirect_conflict_table)
            print("user_call_first_indirect_conflict_list : ", user_call_first_indirect_conflict_list)
            print("user_call_already_indirect_conflict_list : ", user_call_already_indirect_conflict_list)

            # Already indirect conflicted
            if user_call_already_indirect_conflict_table:
                print("\n#### Already Indirect Conflict !!! ####")
                self.already_indirect_logic(project_name, user_call_already_indirect_conflict_table, type="user_call")

            # First indirect conflict
            if user_call_first_indirect_conflict_list:
                print("\n#### First Indirect Conflict !!! ####")
                self.first_indirect_logic(project_name, user_call_first_indirect_conflict_list, type="user_call")

        if user_work_indirect_conflict_list:

            print("\n#### User Work Indirect Conflict !!! ####")

            user_work_already_indirect_conflict_table = self.search_already_indirect_conflict_table(project_name, user_work_indirect_conflict_list, type="user_work")
            user_work_first_indirect_conflict_list, user_work_already_indirect_conflict_list = \
                self.classify_indirect_conflict_list(user_work_indirect_conflict_list, user_work_already_indirect_conflict_table, type="user_work")
            print("user_work_already_indirect_conflict_table : ", user_work_already_indirect_conflict_table)
            print("user_work_first_indirect_conflict_list : ", user_work_first_indirect_conflict_list)
            print("user_work_already_indirect_conflict_list : ", user_work_already_indirect_conflict_list)

            # Already indirect conflicted
            if user_work_already_indirect_conflict_table:
                print("\n#### Already Indirect Conflict !!! ####")
                self.already_indirect_logic(project_name, user_work_already_indirect_conflict_table, type="user_work")

            # First indirect conflict
            if user_work_first_indirect_conflict_list:
                print("\n#### First Indirect Conflict !!! ####")
                self.first_indirect_logic(project_name, user_work_first_indirect_conflict_list, type="user_work")

        non_indirect_conflict_list = self.search_non_indirect_conflict_list(project_name, user_name,
                                                                            user_call_indirect_conflict_list,
                                                                            user_work_indirect_conflict_list)

        if non_indirect_conflict_list:
            print("\n#### User Call Non-Indirect Conflict !!! ####")
            self.non_indirect_conflict_logic(project_name, non_indirect_conflict_list)

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
    def search_user_working_table(self, project_name, user_name):
        raw_list = []

        try:
            sql = "select * " \
                  "from working_table " \
                  "where project_name = '%s' " \
                  "and user_name = '%s'" % (project_name, user_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = list(self.cursor.fetchall())

        except:
            self.conn.rollback()
            print("ERROR : search indirect user working table")

        return raw_list

    def search_other_working_table(self, project_name, user_name):
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

        except:
            self.conn.rollback()
            print("ERROR : search indirect other working table")

        return raw_list

    # Search calling_table
    def search_user_calling_table(self, project_name, user_name):
        raw_list = []

        try:
            sql = "select * " \
                  "from calling_table " \
                  "where project_name = '%s' " \
                  "and user_name = '%s'" % (project_name, user_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = list(self.cursor.fetchall())

        except:
            self.conn.rollback()
            print("ERROR : search indirect user calling table ")

        return raw_list

    def search_other_calling_table(self, project_name, user_name):
        raw_list = []

        try:
            sql = "select * " \
                  "from calling_table " \
                  "where project_name = '%s' " \
                  "and user_name != '%s'" % (project_name, user_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = list(self.cursor.fetchall())

        except:
            self.conn.rollback()
            print("ERROR : search indirect other calling table ")

        return raw_list

    def extract_def_call(self, project_name):
        def_call_list = []

        try:

            sql = "select def_func, call_func " \
                  "from logic_dependency " \
                  "where project_name = '%s' " \
                  % (project_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            def_call_list = list(self.cursor.fetchall())

        except:
            self.conn.rollback()
            print("ERROR : extract u v")

        return def_call_list

    def search_logic_dependency(self, project_name, calling_list, working_list, type):
        def_call_list = self.extract_def_call(project_name)
        print("def_call_list : ", def_call_list)

        all_raw_list = []

        if type == "user_call":

            # temp_calling_list : { project_name, user_name, file_name, calling_file, calling_logic, log_time }
            for temp_user_calling_list in calling_list:
                # temp_other_working_list : { project_name, file_name, logic_name, user_name, work_line, work_amount, log_time }
                for temp_other_working_list in working_list:
                    user_logic = temp_user_calling_list[3] + "|" + temp_user_calling_list[4]
                    other_user_logic = temp_other_working_list[1] + "|" + temp_other_working_list[2]
                    # if temp_user_calling_list[0] == temp_other_working_list[0] and user_logic == other_user_logic:
                    #     temp_raw = []
                    #     temp_raw.append(temp_user_calling_list[1])  # user_name
                    #     temp_raw.append(user_logic)  # user_logic(call)
                    #     temp_raw.append(temp_other_working_list[3])  # other_user_name
                    #     temp_raw.append(other_user_logic)  # other_user_logic(def)
                    #     temp_raw.append(0)  # length
                    #
                    #     # [user_name, user_logic(call), other_name, other_logic(def), length]
                    #     all_raw_list.append(temp_raw)

                    # in logic_dependency
                    if def_call_list:
                        temp_tuple = (other_user_logic, user_logic)

                        if temp_tuple in def_call_list:
                            try:
                                sql = "select length " \
                                      "from logic_dependency " \
                                      "where project_name = '%s' " \
                                      "and (def_func = '%s' and call_func = '%s')" \
                                      % (project_name, other_user_logic, user_logic)
                                print(sql)
                                self.cursor.execute(sql)
                                self.conn.commit()

                                raw = self.cursor.fetchone()

                                if raw:
                                    temp_raw = []

                                    temp_raw.append(temp_user_calling_list[1])  # user_name
                                    temp_raw.append(temp_user_calling_list[2])  # user_file(call in this file)
                                    temp_raw.append(user_logic)  # user_logic(call)
                                    temp_raw.append(temp_other_working_list[3])  # other_user_name
                                    temp_raw.append(temp_other_working_list[1])  # other_user_file(def in this file)
                                    temp_raw.append(other_user_logic)  # other_user_logic(def)
                                    temp_raw.append(raw[0])  # length

                                    # [user_name, user_file(call in this file), user_logic(call), other_name, other_user_file(def in this file), other_logic(def), length]
                                    all_raw_list.append(temp_raw)

                            except:
                                self.conn.rollback()
                                print("ERROR : search logic dependency : user_call")
        if type == "user_work":

            # temp_user_working_list : { project_name, file_name, logic_name, user_name, work_line, work_amount, log_time }
            for temp_user_working_list in working_list:
                # temp_other_calling_list : { project_name, user_name, file_name, calling_file, calling_logic, log_time }
                for temp_other_calling_list in calling_list:
                    user_logic = temp_user_working_list[1] + "|" + temp_user_working_list[2]
                    other_user_logic = temp_other_calling_list[3] + "|" + temp_other_calling_list[4]
                    # if temp_user_working_list[0] == temp_other_calling_list[0] and user_logic == other_user_logic:
                    #     temp_raw = []
                    #
                    #     temp_raw.append(temp_user_working_list[3])  # user_name
                    #     temp_raw.append(user_logic)  # user_logic(def)
                    #     temp_raw.append(temp_other_calling_list[1])  # other_user_name
                    #     temp_raw.append(other_user_logic)  # other_userlogic(call)
                    #     temp_raw.append(0)  # length
                    #
                    #     # [user_name, other_user_logic(call), other_name, user_logic(def), length]
                    #     all_raw_list.append(temp_raw)

                    # in logic_dependency
                    if def_call_list:
                        temp_tuple = (user_logic, other_user_logic)

                        if temp_tuple in def_call_list:
                            try:
                                sql = "select length " \
                                      "from logic_dependency " \
                                      "where project_name = '%s' " \
                                      "and (def_func = '%s' and call_func = '%s')" \
                                      % (project_name, user_logic, other_user_logic)
                                print(sql)
                                self.cursor.execute(sql)
                                self.conn.commit()

                                raw = self.cursor.fetchone()

                                if raw:
                                    temp_raw = []

                                    temp_raw.append(temp_user_working_list[3])  # user_name
                                    temp_raw.append(temp_user_working_list[1])  # user_file(def in this file)
                                    temp_raw.append(user_logic)  # user_logic(def)
                                    temp_raw.append(temp_other_calling_list[1])  # other_user_name
                                    temp_raw.append(temp_other_calling_list[2])  # other_user_file(call in this file)
                                    temp_raw.append(other_user_logic)  # other_user_logic(call)
                                    temp_raw.append(raw[0])  # length

                                    # [user_name, user_file(def in this file), user_logic(call), other_name, other_user_file(call in this file), other_logic(def), length]
                                    all_raw_list.append(temp_raw)

                            except:
                                self.conn.rollback()
                                print("ERROR : search logic dependency : user_work")

        return all_raw_list

    def search_non_indirect_conflict_list(self, project_name, user_name, user_call_indirect_conflict_list, user_work_indirect_conflict_list):
        non_indirect_conflict_list = []

        try:
            sql = "select * " \
                  "from indirect_conflict_table " \
                  "where project_name = '%s' " \
                  "and user1_name = '%s'" \
                  % (project_name, user_name)

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = list(self.cursor.fetchall())
            non_indirect_conflict_list = raw_list[:]

            # [ project_name, def_file, def_func, call_file, call_func, length, user1_name, user2_name, alert_count, call_user, log_time]
            for rl in raw_list:
                # [user1_name, user1_file(call in this file), user1_logic(call), user2_name, user2_file(def in this file), user2_logic(def)]
                for icl in user_call_indirect_conflict_list:
                    if rl[2] == icl[5] and rl[4] == icl[2] and rl[6] == icl[0] and rl[7] == icl[3] and rl[9] == 1:
                        non_indirect_conflict_list.remove(rl)

                # [user1_name, user1_file(def in this file), user1_logic(def), user2_name, user2_file(call in this file), user2_logic(call)]
                for icl in user_work_indirect_conflict_list:
                    if rl[2] == icl[2] and rl[4] == icl[5] and rl[6] == icl[0] and rl[7] == icl[3] and rl[9] == 2:
                        non_indirect_conflict_list.remove(rl)


        except:
            self.conn.rollback()
            print("ERROR : search non indirect conflict list")

        return non_indirect_conflict_list

    def search_already_indirect_conflict_table(self, project_name, indirect_conflict_list, type):
        all_raw_list = []

        if type == "user_call":

            # [ user1_name, user1_file(call in this file), user1_logic(call), user2_name, user2_file(def in this file), user2_logic(def) ]
            for temp_indirect_conflict in indirect_conflict_list:
                try:
                    sql = "select * " \
                          "from indirect_conflict_table " \
                          "where project_name = '%s' " \
                          "and def_func = '%s' and call_file = '%s' and call_func = '%s' " \
                          "and user1_name = '%s' and user2_name = '%s'" \
                          % (project_name, temp_indirect_conflict[5], temp_indirect_conflict[1], temp_indirect_conflict[2], temp_indirect_conflict[0], temp_indirect_conflict[3])

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

        if type == "user_work":

            # [ user1_name, user1_file(def in this file), user1_logic(def), user2_name, user2_file(call in this file), user2_logic(call) ]
            for temp_indirect_conflict in indirect_conflict_list:
                try:
                    sql = "select * " \
                          "from indirect_conflict_table " \
                          "where project_name = '%s' " \
                          "and def_func = '%s' and call_file = '%s' and call_func = '%s' " \
                          "and user1_name = '%s' and user2_name = '%s'" \
                          % (project_name, temp_indirect_conflict[2], temp_indirect_conflict[4], temp_indirect_conflict[5], temp_indirect_conflict[0], temp_indirect_conflict[3])

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

    def classify_indirect_conflict_list(self, whole_indirect_conflict_list, already_indirect_conflict_table, type):
        # first_indirect_conflict_list = whole_indirect_conflict_list - already_indirect_conflict_list
        first_indirect_conflict_list = whole_indirect_conflict_list[:]
        already_indirect_conflict_list = []

        if type == "user_call":

            # [ user1_name, user1_file(call in this file), user1_logic(call), user2_name, user2_file(def in this file), user2_logic(def) ]
            for temp_whole_indirect_conflict_list in whole_indirect_conflict_list:
                # [ project_name, def_file, def_func, call_file, call_func, length, user1_name, user2_name, alert_count, call_user, log_time]
                for temp_already_indirect_conflict_table in already_indirect_conflict_table:
                    if (temp_whole_indirect_conflict_list[0] == temp_already_indirect_conflict_table[6] and
                            temp_whole_indirect_conflict_list[1] == temp_already_indirect_conflict_table[3] and
                            temp_whole_indirect_conflict_list[2] == temp_already_indirect_conflict_table[4] and
                            temp_whole_indirect_conflict_list[3] == temp_already_indirect_conflict_table[7] and
                            temp_whole_indirect_conflict_list[5] == temp_already_indirect_conflict_table[2] and
                            temp_already_indirect_conflict_table[9] == 1):
                        already_indirect_conflict_list.append(temp_whole_indirect_conflict_list)
                        first_indirect_conflict_list.remove(temp_whole_indirect_conflict_list)

        if type == "user_work":

            # [ user1_name, user1_file(def in this file), user1_logic(def), user2_name, user2_file(call in this file), user2_logic(call) ]
            for temp_whole_indirect_conflict_list in whole_indirect_conflict_list:
                # [ project_name, def_file, def_func, call_file, call_func, length, user1_name, user2_name, alert_count, call_user, log_time]
                for temp_already_indirect_conflict_table in already_indirect_conflict_table:
                    if (temp_whole_indirect_conflict_list[0] == temp_already_indirect_conflict_table[6] and
                            temp_whole_indirect_conflict_list[4] == temp_already_indirect_conflict_table[3] and
                            temp_whole_indirect_conflict_list[2] == temp_already_indirect_conflict_table[2] and
                            temp_whole_indirect_conflict_list[3] == temp_already_indirect_conflict_table[7] and
                            temp_whole_indirect_conflict_list[5] == temp_already_indirect_conflict_table[4] and
                            temp_already_indirect_conflict_table[9] == 2):
                        already_indirect_conflict_list.append(temp_whole_indirect_conflict_list)
                        first_indirect_conflict_list.remove(temp_whole_indirect_conflict_list)

        return first_indirect_conflict_list, already_indirect_conflict_list

    def already_indirect_logic(self, project_name, already_indirect_conflict_table, type):
        if type == "user_call":
            # [ project_name, def_file, def_func, call_file, call_func, length, user1_name, user2_name, alert_count, call_user, log_time]
            for temp_already in already_indirect_conflict_table:
                # After 30 minutes => send direct message
                if ((d.datetime.today() - temp_already[10] > d.timedelta(minutes=30)) and (temp_already[8] == 1)):

                    temp_file_logic1 = temp_already[4].split('|')
                    temp_file_logic2 = temp_already[2].split('|')

                    send_indirect_conflict_message(conflict_flag=Conflict_flag.indirect_conflict.value,
                                                   conflict_project=project_name,
                                                   conflict_file1=temp_already[3],
                                                   conflict_file2=temp_already[1],
                                                   conflict_logic1=temp_file_logic1,
                                                   conflict_logic2=temp_file_logic2,
                                                   user1_name=temp_already[6],
                                                   user2_name=temp_already[7],
                                                   type=type)

                    self.increase_alert_count(project_name=project_name,
                                              def_func=temp_already[2],
                                              call_file=temp_already[3],
                                              call_func=temp_already[4],
                                              user1_name=temp_already[6],
                                              user2_name=temp_already[7],
                                              call_user=1)

                # After 60 minutes => send channel message
                # if ((d.datetime.today() - temp_already[7] > d.timedelta(minutes=60)) and (temp_already[6] == 2)):
                #
                #     temp_file_logic1 = temp_already[2].split('|')
                #     temp_file_logic2 = temp_already[1].split('|')
                #
                #     send_conflict_message_channel(conflict_file=temp_file_logic1,
                #                                   conflict_logic=temp_file_logic2,
                #                                   user1_name=temp_already[4],
                #                                   user2_name=temp_already[5])
                #
                #     self.increase_alert_count(project_name=project_name,
                #                               def_func=temp_already[1],
                #                               call_func=temp_already[2],
                #                               user1_name=temp_already[4],
                #                               user2_name=temp_already[5])
                #
                #     self.increase_alert_count(project_name=project_name,
                #                               def_func=temp_already[1],
                #                               call_func=temp_already[2],
                #                               user1_name=temp_already[5],
                #                               user2_name=temp_already[4])

        if type == "user_work":
            # [ project_name, def_file, def_func, call_file, call_func, length, user1_name, user2_name, alert_count, call_user, log_time]
            for temp_already in already_indirect_conflict_table:
                # After 30 minutes => send direct message
                if ((d.datetime.today() - temp_already[10] > d.timedelta(minutes=30)) and (temp_already[8] == 1)):
                    temp_file_logic1 = temp_already[2].split('|')
                    temp_file_logic2 = temp_already[4].split('|')

                    send_indirect_conflict_message(conflict_flag=Conflict_flag.indirect_conflict.value,
                                                   conflict_project=project_name,
                                                   conflict_file1=temp_already[1],
                                                   conflict_file2=temp_already[3],
                                                   conflict_logic1=temp_file_logic1,
                                                   conflict_logic2=temp_file_logic2,
                                                   user1_name=temp_already[6],
                                                   user2_name=temp_already[7],
                                                   type=type)

                    self.increase_alert_count(project_name=project_name,
                                              def_func=temp_already[2],
                                              call_file=temp_already[3],
                                              call_func=temp_already[4],
                                              user1_name=temp_already[6],
                                              user2_name=temp_already[7],
                                              call_user=2)

                # After 60 minutes => send channel message
                # if ((d.datetime.today() - temp_already[7] > d.timedelta(minutes=60)) and (temp_already[6] == 2)):
                #     temp_file_logic1 = temp_already[1].split('|')
                #     temp_file_logic2 = temp_already[2].split('|')
                #
                #     send_conflict_message_channel(conflict_file=temp_file_logic1,
                #                                   conflict_logic=temp_file_logic2,
                #                                   user1_name=temp_already[4],
                #                                   user2_name=temp_already[5])
                #
                #     self.increase_alert_count(project_name=project_name,
                #                               def_func=temp_already[1],
                #                               call_func=temp_already[2],
                #                               user1_name=temp_already[4],
                #                               user2_name=temp_already[5])
                #
                #     self.increase_alert_count(project_name=project_name,
                #                               def_func=temp_already[1],
                #                               call_func=temp_already[2],
                #                               user1_name=temp_already[5],
                #                               user2_name=temp_already[4])

        return

    def first_indirect_logic(self, project_name, indirect_conflict_list, type):
        # [ user1_name, user1_file(call in this file), user1_logic(call), user2_name, user2_file(def in this file), user2_logic(def) ]
        for temp_conflict in indirect_conflict_list:
            temp_file_logic1 = temp_conflict[2].split('|')
            temp_file_logic2 = temp_conflict[5].split('|')
            self.insert_conflict_data(project_name, temp_conflict, type)
            send_indirect_conflict_message(conflict_flag=Conflict_flag.indirect_conflict.value,
                                           conflict_project=project_name,
                                           conflict_file1=temp_conflict[1],
                                           conflict_file2=temp_conflict[4],
                                           conflict_logic1=temp_file_logic1,
                                           conflict_logic2=temp_file_logic2,
                                           user1_name=temp_conflict[0],
                                           user2_name=temp_conflict[3],
                                           type=type)

        return

    # Insert conflict data
    def insert_conflict_data(self, project_name, indirect_conflict_list, type):
        sql = ""
        if type == "user_call":
            # [user1_name, user1_file(call in this file), user1_logic(call), user2_name, user2_file(def in this file), user2_logic(def), length]
            sql = "insert into indirect_conflict_table " \
                  "(project_name, def_file, def_func, call_file, call_func, length, user1_name, user2_name, call_user) " \
                  "value ('%s', '%s', '%s', '%s', '%s', %d, '%s', '%s', '%d')" \
                  % (project_name, indirect_conflict_list[4], indirect_conflict_list[5], indirect_conflict_list[1], indirect_conflict_list[2], indirect_conflict_list[6], indirect_conflict_list[0], indirect_conflict_list[3], 1)

        if type == "user_work":
            # [user1_name, user1_file(def in this file), user1_logic(def), user2_name, user2_file(call in this file), user2_logic(call), length]
            sql = "insert into indirect_conflict_table " \
                  "(project_name, def_file, def_func, call_file, call_func, length, user1_name, user2_name, call_user) " \
                  "value ('%s', '%s', '%s', '%s', '%s', %d, '%s', '%s', '%d')" \
                  % (project_name, indirect_conflict_list[1], indirect_conflict_list[2], indirect_conflict_list[4], indirect_conflict_list[5], indirect_conflict_list[6], indirect_conflict_list[0], indirect_conflict_list[3], 2)

        try:
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            print("ERROR : insert indirect conflict data")

        return


    def non_indirect_conflict_logic(self, project_name, non_indirect_conflict_list):
        print("non_indirect_conflict_logic : ", non_indirect_conflict_list)

        # Send to the user about indirect solved message
        # [ project_name, def_file, def_func, call_file, call_func, length, user1_name, user2_name, alert_count, call_user, log_time ]
        for raw_temp in non_indirect_conflict_list:
            if raw_temp[9] == 1:
                send_indirect_conflict_message(conflict_flag=Conflict_flag.indirect_conflict_finished.value,
                                               conflict_project=project_name,
                                               conflict_logic1=raw_temp[4],
                                               conflict_logic2=raw_temp[2],
                                               conflict_file1=raw_temp[3],
                                               conflict_file2=raw_temp[1],
                                               user1_name=raw_temp[6],
                                               user2_name=raw_temp[7])

                send_indirect_conflict_message(conflict_flag=Conflict_flag.indirect_conflict_finished.value,
                                               conflict_project=project_name,
                                               conflict_logic1=raw_temp[4],
                                               conflict_logic2=raw_temp[2],
                                               conflict_file1=raw_temp[1],
                                               conflict_file2=raw_temp[3],
                                               user1_name=raw_temp[7],
                                               user2_name=raw_temp[6])
            elif raw_temp[9] == 2:
                send_indirect_conflict_message(conflict_flag=Conflict_flag.indirect_conflict_finished.value,
                                               conflict_project=project_name,
                                               conflict_logic1=raw_temp[4],
                                               conflict_logic2=raw_temp[2],
                                               conflict_file1=raw_temp[1],
                                               conflict_file2=raw_temp[3],
                                               user1_name=raw_temp[6],
                                               user2_name=raw_temp[7])

                send_indirect_conflict_message(conflict_flag=Conflict_flag.indirect_conflict_finished.value,
                                               conflict_project=project_name,
                                               conflict_logic1=raw_temp[4],
                                               conflict_logic2=raw_temp[2],
                                               conflict_file1=raw_temp[3],
                                               conflict_file2=raw_temp[1],
                                               user1_name=raw_temp[7],
                                               user2_name=raw_temp[6])

        # Delete all user conflict list
        # [ project_name, def_file, def_func, call_file, call_func, length, user1_name, user2_name, alert_count, call_user, log_time ]
        for nicl in non_indirect_conflict_list:
            try:
                sql = "delete " \
                      "from indirect_conflict_table " \
                      "where project_name = '%s' " \
                      "and def_func = '%s' " \
                      "and call_file = '%s' " \
                      "and call_func = '%s' " \
                      "and user1_name = '%s' " \
                      "and user2_name = '%s' " \
                      "and call_user = '%d'" \
                      % (nicl[0], nicl[2], nicl[3], nicl[4], nicl[6], nicl[7], nicl[9])
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

            except:
                self.conn.rollback()
                print("ERROR : delete user indirect conflict data1")

            try:
                if nicl[9] == 1:
                    type = 2
                elif nicl[9] == 2:
                    type = 1
                sql = "delete " \
                      "from indirect_conflict_table " \
                      "where project_name = '%s' " \
                      "and def_func = '%s' " \
                      "and call_file = '%s' " \
                      "and call_func = '%s' " \
                      "and user1_name = '%s' " \
                      "and user2_name = '%s' " \
                      "and call_user = '%d'" \
                      % (nicl[0], nicl[2], nicl[3], nicl[4], nicl[7], nicl[6], type)
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

            except:
                self.conn.rollback()
                print("ERROR : delete user indirect conflict data2")

        return

    def increase_alert_count(self, project_name, def_func, call_file, call_func, user1_name, user2_name, call_user):
        try:
            sql = "update indirect_conflict_table " \
                  "set alert_count = alert_count + 1 " \
                  "where project_name = '%s' " \
                  "and def_func = '%s' " \
                  "and call_file = '%s '" \
                  "and call_func = '%s' " \
                  "and user1_name = '%s' " \
                  "and user2_name = '%s' " \
                  "and call_user = '%d'" % (project_name, def_func, call_file, call_func, user1_name, user2_name, call_user)
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