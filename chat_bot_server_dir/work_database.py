import pymysql
from datetime import datetime, timedelta
from server_dir.server_config_loader import *
import json

class work_database:
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

    ####################################################
    '''
    Working_Table && Calling_Table
    '''

    # Update User data to working_table
    def update_user_data(self, project_name, working_list, edit_amount, calling_list, user_name):
        # in working_table
        # working_list = [ ["file_name", "logic_name", "work_line", "work_amount"] ]
        for temp_work in working_list:
            print("temp_work : ", temp_work)
            try:
                if temp_work[3] == -1:
                    temp_work[1] = "in"

                sql = "select * " \
                      "from working_table " \
                      "where project_name = '%s' " \
                      "and file_name = '%s' " \
                      "and logic_name = '%s' " \
                      "and user_name = '%s' " \
                      "and work_line = '%d' " \
                      "and work_amount = '%d'" \
                      % (project_name, temp_work[0], temp_work[1], user_name, temp_work[2], temp_work[3])
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

                if not self.cursor.fetchone():
                    sql = "replace into working_table " \
                          "(project_name, file_name, logic_name, user_name, work_line, work_amount) " \
                          "value ('%s', '%s', '%s', '%s', %d, %d)" % (
                          project_name, temp_work[0], temp_work[1], user_name, temp_work[2], temp_work[3])

                    print(sql)
                    self.cursor.execute(sql)
                    self.conn.commit()
            except:
                self.conn.rollback()
                print("ERROR : update_user_data : working")

        # in calling_table
        # { file_name : { line : { 'file_path': value, 'class_context': [value], 'func_name': value, 'logic': value } } }
        for file_name, temp_calling_list in calling_list.items():
            print("temp_calling_list : ", temp_calling_list)
            for line_num, temp_calling_list_list in temp_calling_list.items():
                for temp_calling in temp_calling_list_list:
                    try:
                        sql = "replace into calling_table " \
                              "(project_name, user_name, file_name, calling_file, calling_logic) " \
                              "value ('%s', '%s', '%s', '%s', '%s')" \
                              % (project_name, user_name, file_name, temp_calling['file_path'], temp_calling['logic'])
                        print(sql)
                        self.cursor.execute(sql)
                        self.conn.commit()
                    except:
                        self.conn.rollback()
                        print("ERROR : update_user_data : calling")

        # in edit_amount
        # { file_name : { 'total_plus': value, 'total_minus': value, 'git_diff_code' : text }
        for file_name, temp_edit_amount in edit_amount.items():
            print("temp_edit_amount : ", temp_edit_amount)
            try:
                sql = "replace into edit_amount " \
                      "(project_name, file_name, user_name, total_plus, total_minus, git_diff_code) " \
                      "value ('%s', '%s', '%s', '%d', '%d', '%s')" \
                      % (project_name, file_name, user_name, temp_edit_amount['total_plus'],
                         temp_edit_amount['total_minus'], temp_edit_amount['git_diff_code'])
                # sql = "replace into edit_amount " \
                #       "(project_name, file_name, user_name, total_plus, total_minus, git_diff_code) " \
                #       "value ('%s', '%s', '%s', '%d', '%d', '%s')" \
                #       % (project_name, file_name, user_name, temp_edit_amount['total_plus'],
                #          temp_edit_amount['total_minus'], json.dumps(temp_edit_amount['git_diff_code']))

                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()
                print("ERROR : update_user_data : calling")
        return

    # Remove User data to working_table
    def remove_user_data(self, project_name, working_list, edit_amount, calling_list, user_name):
        # in working_table
        user_working_db = set()

        try:
            sql = "select * " \
                  "from working_table " \
                  "where project_name = '%s' " \
                  "and user_name = '%s'" % (project_name, user_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_tuple = self.cursor.fetchall()
            for raw in raw_tuple:
                user_working_db.add(raw)

        except:
            self.conn.rollback()
            print("ERROR : remove_user_data1")

        current_working_db = set()

        for temp_work in working_list:
            try:
                sql = "select * " \
                      "from working_table " \
                      "where project_name = '%s' " \
                      "and file_name = '%s' " \
                      "and logic_name = '%s' " \
                      "and user_name = '%s' " \
                      "and work_line = %d " \
                      "and work_amount = %d" % (
                      project_name, temp_work[0], temp_work[1], user_name, temp_work[2], temp_work[3])
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

                raw_tuple = self.cursor.fetchall()
                for raw in raw_tuple:
                    current_working_db.add(raw)

            except:
                self.conn.rollback()
                print("ERROR : remove_user_data2")

        remove_working_db = user_working_db - current_working_db

        for temp_remove in remove_working_db:
            try:
                sql = "delete " \
                      "from working_table " \
                      "where project_name = '%s' " \
                      "and file_name = '%s' " \
                      "and logic_name = '%s' " \
                      "and user_name = '%s' " \
                      "and work_line = %d " \
                      "and work_amount = %d" % (
                      temp_remove[0], temp_remove[1], temp_remove[2], temp_remove[3], temp_remove[4], temp_remove[5])

                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

            except:
                self.conn.rollback()
                print("ERROR : remove_user_data3")

        # in calling_table
        user_calling_db = set()
        try:
            sql = "select * " \
                  "from calling_table " \
                  "where project_name = '%s' " \
                  "and user_name = '%s'" % (project_name, user_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_tuple = self.cursor.fetchall()
            for raw in raw_tuple:
                user_calling_db.add(raw)

        except:
            self.conn.rollback()
            print("ERROR : remove_user_data4")

        current_calling_db = set()

        # { file_name : { line : { 'file_path': value, 'class_context': [value], 'func_name': value, 'logic': value } } }
        for file_name, temp_calling_list in calling_list.items():
            for line_num, temp_calling_list_list in temp_calling_list.items():
                for temp_calling in temp_calling_list_list:
                    try:
                        sql = "select * " \
                              "from calling_table " \
                              "where project_name = '%s' " \
                              "and user_name = '%s' " \
                              "and file_name = '%s' " \
                              "and calling_file = '%s' " \
                              "and calling_logic = '%s' " \
                              % (project_name, user_name, file_name, temp_calling['file_path'], temp_calling['logic'])
                        print(sql)
                        self.cursor.execute(sql)
                        self.conn.commit()

                        raw_tuple = self.cursor.fetchall()
                        for raw in raw_tuple:
                            current_calling_db.add(raw)

                    except:
                        self.conn.rollback()
                        print("ERROR : remove_user_data5")

        remove_calling_db = user_calling_db - current_calling_db

        for temp_remove in remove_calling_db:
            try:
                sql = "delete " \
                      "from calling_table " \
                      "where project_name = '%s' " \
                      "and user_name = '%s' " \
                      "and file_name = '%s' " \
                      "and calling_file = '%s' " \
                      "and calling_logic = '%s' " \
                      % (temp_remove[0], temp_remove[1], temp_remove[2], temp_remove[3], temp_remove[4])

                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

            except:
                self.conn.rollback()
                print("ERROR : remove_user_data6")

        # in edit_amount
        user_edit_amount_db = set()
        try:
            sql = "select * " \
                  "from edit_amount " \
                  "where project_name = '%s' " \
                  "and user_name = '%s'" % (project_name, user_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_tuple = self.cursor.fetchall()
            for raw in raw_tuple:
                user_edit_amount_db.add(raw)

        except:
            self.conn.rollback()
            print("ERROR : remove_user_data7")

        current_edit_amount_db = set()

        # { file_name : { 'total_plus': value, 'total_minus': value } }
        for file_name, temp_edit_amount in edit_amount.items():
            try:
                sql = "select * " \
                      "from edit_amount " \
                      "where project_name = '%s' " \
                      "and file_name = '%s' " \
                      "and user_name = '%s' " \
                      "and total_plus = '%s' " \
                      "and total_minus = '%s' " \
                      % (project_name, file_name, user_name, temp_edit_amount['total_plus'], temp_edit_amount['total_minus'])
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

                raw_tuple = self.cursor.fetchall()
                for raw in raw_tuple:
                    current_edit_amount_db.add(raw)

            except:
                self.conn.rollback()
                print("ERROR : remove_user_data8")

        remove_edit_amount_db = user_edit_amount_db - current_edit_amount_db

        for temp_remove in remove_edit_amount_db:
            try:
                sql = "delete " \
                      "from edit_amount " \
                      "where project_name = '%s' " \
                      "and file_name = '%s' " \
                      "and user_name = '%s' " \
                      "and total_plus = '%s' " \
                      "and total_minus = '%s' " \
                      % (temp_remove[0], temp_remove[1], temp_remove[2], temp_remove[3], temp_remove[4])

                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

            except:
                self.conn.rollback()
                print("ERROR : remove_user_data9")

        return

    ####################################################
    '''
    Approved list
    '''

    # Read approved list
    def read_approved_list(self, slack_code):
        raw_set = set()
        try:
            sql = "SELECT approved_file " \
                  "from approved_list " \
                  "where slack_code = '%s' " % (slack_code)

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_tuple = self.cursor.fetchall()
            for rt in raw_tuple:
                raw_set.add(rt[0])

        except:
            self.conn.rollback()
            print("ERROR : read approved list")

        return raw_set

    # Add approved list
    def add_approved_list(self, slack_code, req_approved_set):
        db_approved_set = self.read_approved_list(slack_code)

        diff_approved_set = req_approved_set - db_approved_set
        # [[slack_code, approved_file], [slack_code, approved_file], [slack_code, approved_file]]
        if diff_approved_set:
            try:
                sql = "insert into approved_list (slack_code, approved_file) values "

                for temp_diff_approved in diff_approved_set:
                    sql += "('%s', '%s'), " % (slack_code, temp_diff_approved)
                sql = sql[:-2]
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()
                print("ERROR : add approved list")

        return list(diff_approved_set), db_approved_set

    # Remove approved list
    def remove_approved_list(self, slack_code, remove_approved_list):
        success_remove_approved_list = []
        fail_remove_approved_list = []

        for temp_removed_file in remove_approved_list:
            try:
                sql = "select * " \
                      "from approved_list " \
                      "where slack_code = '%s' " \
                      "and approved_file = '%s'" % (slack_code, temp_removed_file)

                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

                raw = self.cursor.fetchone()

                # if file that user want to remove is in approved_list
                if raw:
                    try:
                        sql = "delete " \
                              "from approved_list " \
                              "where slack_code = '%s' " \
                              "and approved_file = '%s'" % (slack_code, temp_removed_file)
                        print(sql)
                        self.cursor.execute(sql)
                        self.conn.commit()

                        success_remove_approved_list.append(temp_removed_file)
                    except:
                        self.conn.rollback()
                        print("ERROR : remove approved list one")

                # if file that user want to remove is not in approved_list
                else:
                    fail_remove_approved_list.append(temp_removed_file)

            except:
                self.conn.rollback()
                print("ERROR : remove approved list two")

        return success_remove_approved_list, fail_remove_approved_list


##########################################################

    def get_working_amount_dict(self, user_git_id, file_name):
        raw_tuple = tuple()
        working_amt_dict = dict()
        try:
            sql = "SELECT user_name, total_plus, total_minus " \
                                "FROM edit_amount " \
                                "WHERE file_name = '%s' " % (file_name)

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
            raw_tuple = self.cursor.fetchall()
            print("get_working_amount_dict : ", raw_tuple)

            for rt in raw_tuple:
                if rt[0] == user_git_id:
                    working_amt_dict[rt[0]] = rt[1] + rt[2]
                else:
                    working_amt_dict[self.convert_git_id_to_slack_id(rt[0])] = rt[1] + rt[2]

        except:
            self.conn.rollback()
            print("ERROR : get working amount dict ")

        return working_amt_dict

    def get_working_amount_percentage(self, project_name, user_git_id, file_name):
        user_edit_amount = tuple()
        other_edit_amount = tuple()
        file_total_lines = tuple()

        try:
            sql = "select total_plus, total_minus " \
                  "from edit_amount " \
                  "where project_name = '%s' " \
                  "and file_name = '%s' " \
                  "and user_name = '%s'" \
                  % (project_name, file_name, user_git_id)

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            user_edit_amount = self.cursor.fetchone()

        except:
            self.conn.rollback()
            print("ERROR : update first best conflict list")

        try:
            sql = "select total_plus, total_minus, user_name " \
                  "from edit_amount " \
                  "where project_name = '%s' " \
                  "and file_name = '%s' " \
                  "and user_name != '%s'" \
                  % (project_name, file_name, user_git_id)

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            other_edit_amount = self.cursor.fetchone()
            print(other_edit_amount)
            if not other_edit_amount:
                return 0, 0, "NO_ONE"

        except:
            self.conn.rollback()
            print("ERROR : update first best conflict list")

        try:
            sql = "select total_lines " \
                  "from file_information " \
                  "where project_name = '%s' " \
                  "and file_name = '%s' " \
                  % (project_name, file_name)

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            file_total_lines = self.cursor.fetchone()

        except:
            self.conn.rollback()
            print("ERROR : update first best conflict list")

        user_percentage = 0

        if user_edit_amount[0] == 0:
            user_percentage = (100 * user_edit_amount[1]) / file_total_lines[0]
        elif user_edit_amount[1] == 0:
            user_percentage = (100 * user_edit_amount[0]) / (file_total_lines[0] + user_edit_amount[0])
        elif user_edit_amount[0] > user_edit_amount[1]:
            user_percentage = (100 * user_edit_amount[0]) / (file_total_lines[0] + user_edit_amount[0] - user_edit_amount[1])
        elif user_edit_amount[0] <= user_edit_amount[1]:
            user_percentage = (100 * user_edit_amount[1]) / (file_total_lines[0])

        other_percentage = 0

        if other_edit_amount[0] == 0:
            other_percentage = (100 * other_edit_amount[1]) / file_total_lines[0]
        elif other_edit_amount[1] == 0:
            other_percentage = (100 * other_edit_amount[0]) / (file_total_lines[0] + other_edit_amount[0])
        elif other_edit_amount[0] > other_edit_amount[1]:
            other_percentage = (100 * other_edit_amount[0]) / (file_total_lines[0] + other_edit_amount[0] - other_edit_amount[1])
        elif other_edit_amount[0] <= other_edit_amount[1]:
            other_percentage = (100 * other_edit_amount[1]) / (file_total_lines[0])

        other_user_git_id = other_edit_amount[2]

        return user_percentage, other_percentage, other_user_git_id

    # def recommendation(self, user1_git_id, file_name):
        # user1_working_amount = "SELECT work_amount " \
        #                        "FROM working_table " \
        #                        "WHERE user_name= '%s'" % user1
        # user2_working_amount = "SELECT work_amount " \
        #                        "FROM working_table " \
        #                        "WHERE user_name= '%s'" % user2
        #
        # try:
        #     self.cursor.execute(user1_working_amount)
        #     self.conn.commit()
        #     user1_working_amount = self.cursor.fetchall()[0][0]
        #     self.cursor.execute(user2_working_amount)
        #     self.conn.commit()
        #     user2_working_amount = self.cursor.fetchall()[0][0]
        #
        # except:
        #     self.conn.rollback()
        #     print("ERROR : recommendation")
        #
        # response_list = []
        #
        # if user1_working_amount >= user2_working_amount:
        #     response_list.append(user1)
        #     response_list.append(user1_working_amount)
        #     response_list.append(user2)
        #     response_list.append(user2_working_amount)
        #     return response_list
        # elif user1_working_amount < user2_working_amount:
        #     response_list.append(user2)
        #     response_list.append(user2_working_amount)
        #     response_list.append(user1)
        #     response_list.append(user1_working_amount)
        #     return response_list[0], response_list[1], response_list[2], response_list[3]
        # else:
        #     return response_list[0], response_list[1], response_list[2], response_list[3]

#################################################################

    def insert_last_connection(self, slack_code):
        try:
            sql = "SELECT last_connection " \
                  "FROM user_last_connection " \
                  "WHERE slack_code = '%s'" % (slack_code)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            if not self.cursor.fetchall():
                try:
                    sql = "insert into user_last_connection " \
                          "(slack_code) " \
                          "value ('%s')" % (slack_code)
                    print(sql)
                    self.cursor.execute(sql)
                    self.conn.commit()

                except:
                    self.conn.rollback()
                    print("ERROR : insert last_connection one")
            # else:
            #     try:
            #         sql = "update user_last_connection " \
            #               "set last_connection = %s " \
            #               "where slack_code = '%s'" % ("NOW()", slack_code)
            #         print(sql)
            #         self.cursor.execute(sql)
            #         self.conn.commit()
            #
            #     except:
            #         self.conn.rollback()
            #         print("ERROR : last_connection two")

        except:
            try:
                sql = "insert into user_last_connection " \
                      "(slack_code) " \
                      "value ('%s')" % (slack_code)
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

            except:
                self.conn.rollback()
                print("ERROR : insert last_connection three")

    def user_recognize(self, user):
        try:
            sql = "SELECT last_connection " \
                  "FROM user_last_connection " \
                  "WHERE slack_code = '%s'" % (user)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw = self.cursor.fetchone()
            if raw:
                last_connection = raw[0]
                print(last_connection)

            try:
                sql = "update user_last_connection " \
                      "set last_connection = %s " \
                      "where slack_code = '%s'" % ("NOW()", user)
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

            except:
                self.conn.rollback()
                print("ERROR : user recognize")

            now_time = datetime.now()
            diff_time = now_time - last_connection
            diff_time_days = diff_time.days

            if diff_time_days > 3:
                return 1
            elif diff_time_days > 7:
                return 2
            elif diff_time_days > 30:
                return 3
            else:
                return 4

        except:
            self.conn.rollback()
            print("Last connection less than 3 days.")
            return -1

    def get_user_working_status(self, git_email_id):
        try:
            sql = "SELECT file_name, logic_name, work_line, work_amount " \
                  "FROM working_table " \
                  "WHERE user_name = '%s'" \
                  "ORDER BY log_time DESC LIMIT 1 " % git_email_id
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            # sorted(student_tuples, key=lambda student: student[2])
            raw_tuple = self.cursor.fetchall()
            raw = tuple()

            if raw_tuple:
                raw = raw_tuple[0]

            return raw

        except:
            self.conn.rollback()
            print("ERROR : get user working status")

    # 컨플릭트 파일 받아서 현재 어프루브 리스트 파일 빼서 남은 것만 반환해주기
    def classify_direct_conflict_approved_list(self, slack_code, whole_direct_conflict_list):
        db_approved_set = self.read_approved_list(slack_code)

        print("db_approved_list(set) : ", db_approved_set)
        print("whole_direct_conflict_list : ", whole_direct_conflict_list)

        remove_list = []

        # ( file_name )
        for temp_db_approved_list in db_approved_set:
            print("temp db approved : ", str(temp_db_approved_list))
            # [ project_name, file_name, logic_name, user_name, work_line, work_amount, log_time ]
            for temp_whole_direct_conflict_list in whole_direct_conflict_list:
                if temp_db_approved_list == temp_whole_direct_conflict_list[1]:
                    try:
                        remove_list.append(temp_whole_direct_conflict_list)
                        print("removed by approved list : ", temp_whole_direct_conflict_list)

                    except:
                        print("ERROR : classify direct conflict approved list")

        for temp_remove in remove_list:
            whole_direct_conflict_list.remove(temp_remove)

        print("after classify approved list : ", whole_direct_conflict_list)
        return whole_direct_conflict_list, remove_list

    # 컨플릭트 파일 받아서 현재 어프루브 리스트 파일 빼서 남은 것만 반환해주기
    def classify_indirect_conflict_approved_list(self, slack_code, whole_indirect_conflict_list):
        db_approved_set = self.read_approved_list(slack_code)

        print("db_approved_set : ", db_approved_set)
        print("whole_indirect_conflict_list : ", whole_indirect_conflict_list)

        remove_list = []

        # [ approved_file ]
        for temp_db_aproved_list in db_approved_set:
            # user_call : [ user_name, user_file(call in this file), user_logic(call), other_user_name, other_user_file(def in this file), other_user_logic(def), length ]
            # user_work : [ user_name, user_file(def in this file), user_logic(def), other_user_name, other_user_file(call in this file), other_user_logic(call), length ]
            for temp_whole_indirect_conflict_list in whole_indirect_conflict_list:
                user1_file = str(temp_whole_indirect_conflict_list[1])

                if temp_db_aproved_list == user1_file:
                    remove_list.append(temp_whole_indirect_conflict_list)
                    print("removed by approved list : ", temp_whole_indirect_conflict_list)

        for temp_remove in remove_list:
            whole_indirect_conflict_list.remove(temp_remove)

        print("after classify approved list : ", whole_indirect_conflict_list)
        return whole_indirect_conflict_list, remove_list



    ####################################################################3
    '''
    lock list
    '''
    # Add lock list
    def add_lock_list(self, project_name, slack_code, req_lock_set, delete_time):

        db_lock_set = set(self.read_lock_list(project_name))

        diff_lock_set = req_lock_set - db_lock_set
        already_lock_set = req_lock_set & db_lock_set

        # [[project_name, approved_file], [project_name, approved_file], [project_name, approved_file]]
        if diff_lock_set:
            sql = "insert into lock_list " \
                  "(project_name, lock_file, slack_code, delete_time) " \
                  "values "
            for temp_diff_lock in diff_lock_set:
                sql += "('%s', '%s', '%s', %d), " % (project_name, temp_diff_lock, slack_code, delete_time)

            sql = sql[:-2]

            try:
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

            except:
                self.conn.rollback()
                print("ERROR : add lock list")

        if already_lock_set:
            sql = "insert into lock_try_history " \
                  "(project_name, file_name, slack_code, delete_time) " \
                  "values "

            for temp_diff_lock in already_lock_set:
                sql += "('%s', '%s', '%s', %d), " % (project_name, temp_diff_lock, slack_code, delete_time)

            sql = sql[:-2]

            try:
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

            except:
                self.conn.rollback()
                print("ERROR : add lock try history list")

        return diff_lock_set, already_lock_set

    # Remove approved list
    def prev_remove_lock_list(self):
        raw_list = []
        try:
            sql = "select lock_file " \
                  "from lock_list " \
                  "where TIMEDIFF(now(),log_time) > delete_time * 60 * 60"
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_tuple = self.cursor.fetchall()
            for rt in raw_tuple:
                raw_list.append(rt[0])

        except:
            self.conn.rollback()
            print("ERROR : prev remove lock list")

        return raw_list

    def remove_lock_list(self, project_name, slack_code, remove_lock_set):

        for temp_remove_file in remove_lock_set:
            try:
                sql = "delete " \
                      "from lock_list " \
                      "where project_name = '%s' " \
                      "and lock_file = '%s' " \
                      "and slack_code = '%s'" % (project_name, temp_remove_file, slack_code)
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

            except:
                self.conn.rollback()
                print("ERROR : remove lock list")

        return


    def auto_remove_lock_list(self):
        try:
            sql = "select * " \
                  "from lock_list " \
                  "where TIMEDIFF(now(),log_time) > delete_time * 60 * 60"
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = list(self.cursor.fetchall())

            for rl in raw_list:
                sql = "delete " \
                      "from lock_notice_list " \
                      "where project_name = '%s' " \
                      "and lock_file = '%s'" % (rl[0], rl[1])
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

            sql = "delete " \
                  "from lock_list " \
                  "where TIMEDIFF(now(),log_time) > delete_time * 60 * 60"
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

        except:
            self.conn.rollback()
            print("ERROR : auto remove lock list")

        return

    def read_lock_list(self, project_name):
        raw_list = []

        try:
            sql = "select lock_file " \
                  "from lock_list " \
                  "where project_name = '%s'" % (project_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_tuple = self.cursor.fetchall()
            for rt in raw_tuple:
                raw_list.append(rt[0])

        except:
            self.conn.rollback()
            print("ERROR : read lock list")

        return raw_list

    def read_lock_list_of_slack_code(self, project_name, slack_code):
        raw_list = []

        try:
            sql = "select lock_file " \
                  "from lock_list " \
                  "where slack_code = '%s' " \
                  "and project_name = '%s' " % (slack_code, project_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_tuple = self.cursor.fetchall()
            for rt in raw_tuple:
                raw_list.append(rt[0])
        except:
            self.conn.rollback()
            print("ERROR :read lock list of slack code")

        return raw_list

        return

    def read_oldest_lock_history_list(self, slack_code, unlock_file):
        raw_list = []

        try:
            for file in unlock_file:
                sql = "select * " \
                      "from lock_try_history " \
                      "where file_name = '%s'"  \
                      "ORDER BY lock_try_time ASC LIMIT 1 " % (file)
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

                raw_tuple = self.cursor.fetchall()
                for rt in raw_tuple:
                    raw_list.append(list(rt))
        except:
            self.conn.rollback()
            print("ERROR : read oldest lock history list")

        return raw_list

    def read_lock_history_list(self, project_name, slack_code):
        raw_list = []

        try:
            sql = "select file_name " \
                  "from lock_try_history "\
                  "where project_name = '%s' " \
                  "and slack_code = '%s'" % (project_name, slack_code)

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_tuple = self.cursor.fetchall()
            for rt in raw_tuple:
                raw_list.append(rt[0])
            print("read_lock_history_list : ", raw_list)
        except:
            self.conn.rollback()
            print("ERROR : read lock history list")

        return raw_list

    def delete_lock_history(self, project_name, slack_code, delete_file):
        try:

            sql = "delete "\
                  "from lock_try_history "\
                  "where project_name = '%s' " \
                  "and file_name = '%s' "\
                  "and slack_code = '%s'" %(project_name, delete_file, slack_code)

            # execute sql
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

        except:
            self.conn.rollback()
            print("ERROR : delete user data")

        return


    def inform_lock_file_direct(self, project_name, working_list, git_id):
        raw_set = set()

        # working_list = [ ["file_name", "logic_name", "work_line", "work_amount"], ["file_name", "logic_name", "work_line", "work_amount"], ... ]
        slack_code = self.convert_git_id_to_slack_code(git_id)

        if str(slack_code).isdigit():
            print("ERROR : NO SLACK CODE")
            return

        for temp_work in working_list:
            try:
                sql = "select * " \
                      "from lock_list " \
                      "where project_name = '%s' " \
                      "and lock_file = '%s' " \
                      "and slack_code != '%s'" % (project_name, temp_work[0], slack_code)
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

                raw_tuple = self.cursor.fetchall()

                for ele in raw_tuple:
                    raw_set.add(ele)
            except:
                self.conn.rollback()
                print("ERROR : inform lock file")

        return list(raw_set)

    def inform_lock_file_indirect(self, project_name, working_list, git_id):
        raw_list = []
        file_list_set = set()

        slack_code = self.convert_git_id_to_slack_code(git_id)

        if str(slack_code).isdigit():
            print("ERROR : NO SLACK CODE")
            return

        # working_list : [ { project_name, file_name, logic_name, user_name, work_line, work_amount, log_time } , ... ]
        for working_list_temp in working_list:
            file_list_set.add(working_list_temp[1])

        for file_name in file_list_set:
            try:
                sql = "select * " \
                      "from lock_list " \
                      "where project_name = '%s' " \
                      "and lock_file = '%s' " \
                      "and slack_code != '%s'" % (project_name, file_name, slack_code)
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

                raw_list = list(self.cursor.fetchall())
            except:
                self.conn.rollback()
                print("ERROR : inform lock file")

        return raw_list

    def add_lock_notice_list(self, project_name, lock_list, git_id):
        try:
            sql = "insert into lock_notice_list " \
                  "(project_name, lock_file, noticed_user) values "
            for ll in lock_list:
                sql += "('%s', '%s', '%s'), " % (project_name, str(ll[1]), git_id)

            sql = sql[:-2]

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            print("ERROR : add lock notice list")

    def check_lock_noticed_user(self, project_name, lock_list, git_id):
        raw_list = []

        for ll in lock_list:
            try:
                sql = "select * " \
                      "from lock_notice_list " \
                      "where project_name = '%s' " \
                      "and lock_file = '%s' " \
                      "and noticed_user = '%s'" % (project_name, str(ll[1]), git_id)
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

                raw_tuple = self.cursor.fetchall()

                for ele in raw_tuple:
                    raw_list.append(ele)

            except:
                self.conn.rollback()
                print("ERROR : check_lock_noticed_user")

        return raw_list


    def check_user_and_remain_time_of_lock_file(self, project_name, file_name):
        remain_time_str = ""
        slack_code = ""
        try:
            sql = "select * " \
                  "from lock_list " \
                  "where project_name = '%s' " \
                  "and lock_file = '%s'" % (project_name, file_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw = self.cursor.fetchone()

            slack_code = raw[2]
            delete_time = raw[3]
            log_time = raw[4]

            end_time = log_time + timedelta(hours=delete_time)
            remain_time = end_time - datetime.now()
            remain_time_str = str(int(remain_time.seconds / 3600)).zfill(2) + " : " + str(int((remain_time.seconds % 3600) / 60)).zfill(2) + " : " + str(int(remain_time.seconds % 60)).zfill(2)

        except:
            self.conn.rollback()
            print("ERROR : check_remain_time_of_lock_file")

        return slack_code, remain_time_str

    def check_target_user_remain_time_of_lock_file(self, project_name, file_name, slack_code):
        remain_time_str = ""
        slack_code = ""
        raw_list = []
        try:
            for file in file_name :
                sql = "select * " \
                      "from lock_list " \
                      "where project_name = '%s' " \
                      "and slack_code = '%s' "\
                      "and lock_file = '%s'" % (project_name, slack_code, file)
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

                raw = self.cursor.fetchone()

                delete_time = raw[3]
                log_time = raw[4]

                end_time = log_time + timedelta(hours=delete_time)
                remain_time = end_time - datetime.now()
                remain_time_str = str(int(remain_time.seconds / 3600)).zfill(2) + " : " + str(int((remain_time.seconds % 3600) / 60)).zfill(2) + " : " + str(int(remain_time.seconds % 60)).zfill(2)
                raw_list.append(remain_time_str);
        except:
            self.conn.rollback()
            print("ERROR : check_remain_time_of_lock_file")

        return raw_list


    ####################################################################
    '''
    ignore
    '''
    def insert_ignore(self, project_name, slack_code):
        try:
            sql = "insert into ignore_table" \
                  "(project_name, slack_code) value " \
                  "('%s', '%s')" % (project_name, slack_code)

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            print("ERROR : insert_ignore")

    def update_ignore(self, project_name, ignore_list, slack_code, set_value):
        if ignore_list == 1:
            sql = "update ignore_table " \
                  "set direct_ignore = %d " \
                  "where project_name = '%s' " \
                  "and slack_code = '%s'" % (set_value, project_name, slack_code)
        elif ignore_list == 2:
            sql = "update ignore_table " \
                  "set indirect_ignore = %d " \
                  "where project_name = '%s' " \
                  "and slack_code = '%s'" % (set_value, project_name, slack_code)
        elif ignore_list == 3:
            sql = "update ignore_table " \
                  "set prediction_ignore = %d " \
                  "where project_name = '%s' " \
                  "and slack_code = '%s'" % (set_value, project_name, slack_code)
        try:
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

        except:
            self.conn.rollback()
            print("ERROR : update_ignore")

    def read_ignore_list(self, project_name, slack_code):
        raw = []

        try:
            sql = "select * " \
                  "from ignore_table " \
                  "where project_name = '%s' " \
                  "and slack_code = '%s'" % (project_name, slack_code)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw = list(self.cursor.fetchone())
            print(raw)
        except:
            self.conn.rollback()
            print("ERROR : read ignore")

        if not raw:
            return raw
        else:
            # direct_ignore, indirect_ignore, prediction_ignore
            # 0 => non-ignore / 1 => ignore
            return raw[2], raw[3], raw[4]

    def read_direct_ignore(self, project_name, slack_code):
        raw = []

        try:
            sql = "select direct_ignore " \
                  "from ignore_table " \
                  "where project_name = '%s' " \
                  "and slack_code = '%s'" % (project_name, slack_code)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw = list(self.cursor.fetchone())
        except:
            self.conn.rollback()
            print("ERROR : read_direct_ignore")

        if not raw:
            return 0
        else:
            # 0 => non-ignore / 1 => ignore
            return raw[0]

    def read_indirect_ignore(self, project_name, slack_code):
        raw = []

        try:
            sql = "select indirect_ignore " \
                  "from ignore_table " \
                  "where project_name = '%s' " \
                  "and slack_code = '%s'" % (project_name, slack_code)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw = list(self.cursor.fetchone())
        except:
            self.conn.rollback()
            print("ERROR : read_indirect_ignore")

        if not raw:
            return 0
        else:
            # 0 => non-ignore / 1 => ignore
            return raw[0]

    def read_prediction_ignore(self, project_name, slack_code):
        raw = []

        try:
            sql = "select prediction_ignore " \
                  "from ignore_table " \
                  "where project_name = '%s' " \
                  "and slack_code = '%s'" % (project_name, slack_code)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw = list(self.cursor.fetchone())
        except:
            self.conn.rollback()
            print("ERROR : read_prediction_ignore")

        if not raw:
            return 0
        else:
            # 0 => non-ignore / 1 => ignore
            return raw[0]

#############################

    def get_recent_data(self, github_email):
        try:
            sql1 = "SELECT file_name, logic1_name, logic2_name, user1_name, user2_name, log_time " \
                   "FROM direct_conflict_table " \
                   "WHERE user1_name = '%s' or user2_name = '%s'" % (github_email, github_email)
            sql2 = "SELECT def_func, call_func, user1_name, user2_name, log_time " \
                   "FROM indirect_conflict_table " \
                   "WHERE user1_name = '%s' or user2_name = '%s'" % (github_email, github_email)
            print(sql1)
            self.cursor.execute(sql1)
            self.conn.commit()

            direct_recent_data = list(self.cursor.fetchall())
            print("direct_recent_data : ", direct_recent_data)
            direct_recent_data_mod = []
            indirect_recent_data_mod = []

            if direct_recent_data:
                for conf in direct_recent_data:
                    conf = list(conf)
                    conf[1] = conf[0] + '|' + conf[1]
                    conf[2] = conf[0] + '|' + conf[2]
                    direct_recent_data_mod.append(conf[1:])

            print(sql2)
            self.cursor.execute(sql2)
            self.conn.commit()

            indirect_recent_data = list(self.cursor.fetchall())
            if indirect_recent_data:
                for conf in indirect_recent_data:
                    conf = list(conf)
                    indirect_recent_data_mod.append(conf)

            conflict_recent_data = direct_recent_data_mod + indirect_recent_data_mod

            sorted(conflict_recent_data, key=lambda s: s[4])
            if conflict_recent_data:
                conflict_recent_data[-1].remove(github_email)
                return conflict_recent_data[-1]
            else:
                return "no recent data"

        except:
            self.conn.rollback()
            print("ERROR : Get recent data")



    ####################################################################
    '''
    is conflict
    '''

    def is_conflict(self, project_name, slack_code, file_name):
        direct_conflict_flag = False
        indirect_conflict_flag = False

        if self.is_direct_conflict(project_name, file_name):
            print("IS DIRECT CONFLICT TRUE")
            direct_conflict_flag = True
        if self.is_indirect_conflict(project_name, file_name):
            print("IS INDIRECT CONFLICT TRUE")
            indirect_conflict_flag = True

        return direct_conflict_flag, indirect_conflict_flag

    def is_direct_conflict(self, project_name, file_name):
        raw_list = []
        try:
            sql = "select * " \
                  "from working_table " \
                  "where project_name = '%s' " \
                  "and file_name = '%s'" % (project_name, file_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = list(self.cursor.fetchall())
            print("is_direct_conflict : ", raw_list)

        except:
            self.conn.rollback()
            print("ERROR : is_direct_conflict")

        if raw_list:
            return True
        else:
            return False

    def is_indirect_conflict(self, project_name, file_name):
        raw_list = []
        try:
            temp_file_name = str(file_name) + "%"

            sql = "select * " \
                  "from uci_chat_bot.logic_dependency " \
                  "where project_name = '%s' " \
                  "and (def_func like '%s' or call_func like '%s')" % (project_name, temp_file_name, temp_file_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = list(self.cursor.fetchall())
            print("is_indirect_conflict : ", raw_list)

        except:
            self.conn.rollback()
            print("ERROR : is_indirect_conflict")

        file_list = []

        # [project_name, u, v, length]
        for temp_raw in raw_list:
            temp_u = str(temp_raw[1]).split('|')[0]
            temp_v = str(temp_raw[2]).split('|')[0]
            file_list.append(temp_u)
            file_list.append(temp_v)

        file_list = list(set(file_list))

        for temp_file in file_list:
            try:
                sql = "select * " \
                      "from uci_chat_bot.working_table " \
                      "where project_name = '%s' " \
                      "and file_name = '%s' " % (project_name, temp_file)
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

                raw_list = list(self.cursor.fetchall())
                print("is_indirect_conflict2 : ", raw_list)

                if raw_list:
                    return True
            except:
                self.conn.rollback()
                print("ERROR : is indirect logic 2")

        return False

    def get_direct_conflict_user_list(self, project_name, user_git_id, file_name):
        raw_list = []
        try:
            sql = "select distinct user_name " \
                  "from working_table " \
                  "where project_name = '%s' " \
                  "and user_name != '%s'" \
                  "and file_name = '%s' " % (project_name, user_git_id, file_name)

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = list(self.cursor.fetchall()[0])
            print("direct_conflict : ", raw_list)

        except:
            self.conn.rollback()
            print("ERROR : get_direct_conflict_user_list")

        return raw_list


    def get_indirect_conflict_user_list(self, project_name, user_git_id, file_name):
        raw_list = []
        raw_dict = dict()
        file_set = set()
        try:
            temp_file_name = str(file_name) + "%"

            sql = "select * " \
                  "from uci_chat_bot.logic_dependency " \
                  "where project_name = '%s' " \
                  "and (def_func like '%s' or call_func like '%s')" % (project_name, temp_file_name, temp_file_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = list(self.cursor.fetchall())
            print("indirect_logic_dependency : ", raw_list)

        except:
            self.conn.rollback()
            print("ERROR : get_indirect_conflict_user_list 1")

        # [project_name, u, v, length]
        for temp_raw in raw_list:
            temp_file_u = str(temp_raw[1]).split('|')[0]
            temp_file_v = str(temp_raw[2]).split('|')[0]
            temp_logic_u = str(temp_raw[1]).split('|')[1]
            temp_logic_v = str(temp_raw[2]).split('|')[1]
            # (file_name, logic_name)
            if temp_file_u != file_name:
                file_set.add((temp_file_u, temp_logic_u))
            if temp_file_v != file_name:
                file_set.add((temp_file_v, temp_logic_v))

        print("indirect_associated_file_set : ", file_set)

        raw_list = []
        # file_name 내에서 call 가능한 다른 파일의 함수를 수정하고 있는지 working list에서 조사
        for temp_raw in file_set:
            try:
                temp_file = temp_raw[0]
                temp_logic = temp_raw[1]
                sql = "select distinct user_name " \
                      "from uci_chat_bot.working_table " \
                      "where project_name = '%s' " \
                      "and file_name = '%s' " \
                      "and logic_name = '%s' " \
                      "and user_name != '%s'" % (project_name, temp_file, temp_logic, user_git_id)

                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()

                raw_list = list(self.cursor.fetchall())
                print("indirect_def_list : ", raw_list)

                for user_name in raw_list:
                    msg = "[" + temp_file + ", " + temp_logic + "]"
                    try:
                        raw_dict[user_name[0]].append(msg)
                    except:
                        raw_dict[user_name[0]] = [msg]

            except:
                self.conn.rollback()
                print("ERROR : get_indirect_conflict_user_list 2")

        # counting_triangle.py 에서 run을 수정했을 때 -> SquareMatrix.py에서 run을 부를 수 있는가
        # SquareMatrix.py 에서 get_lower을 수정했을 때 -> counting_triangle.py 에서 get_lower을 부를 수 있는가
        # counting_triangle.py에서 get_lower을 불렀을 때
        # SquareMatrix.py에서 run을 불렀을 때 -> counting_triangle.py에서 run을 수정할 수 있는가

        raw_list = []
        try:
            sql = "select user_name, file_name, calling_logic " \
                  "from calling_table " \
                  "where project_name = '%s' " \
                  "and calling_file = '%s' " % (project_name, file_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
            raw_list = list(self.cursor.fetchall())
            print("indirect_call_list : ", raw_list)
            for temp_raw in raw_list:
                msg = "[" + temp_raw[1] + ", " + (file_name + "|" + temp_raw[2]) + "]"
                try:
                    raw_dict[temp_raw[0]].append(msg)
                except:
                    raw_dict[temp_raw[0]] = [msg]
        except:
            self.conn.rollback()
            print("ERROR : get_indirect_conflict_user_list 3")

        print("indirect_call_and_def_dict : ", raw_dict)
        return list(raw_dict.keys()), list(raw_dict.values())


    def all_conflict_list(self, github_email):
        conflict_set = set()
        try:
            sql = "select distinct file_name " \
                  "from direct_conflict_table " \
                  "WHERE user1_name = '%s' or user2_name = '%s'" % (github_email, github_email)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            direct_tuple = self.cursor.fetchall()
            print("all_direct_conflict_list : ", direct_tuple)
            for dt in direct_tuple:
                conflict_set.add(dt[0])

            sql = "select distinct def_func, call_func " \
                  "from indirect_conflict_table " \
                  "WHERE user1_name = '%s' or user2_name = '%s'" % (github_email, github_email)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            indirect_tuple = self.cursor.fetchall()
            print("all_indirect_conflict_list : ", indirect_tuple)
            for it in indirect_tuple:
                conflict_set.add(it[0].split('|')[0])
                conflict_set.add(it[1].split('|')[0])

            print("all_conflict_list : ", conflict_set)

        except:
            self.conn.rollback()
            print("ERROR : read conflict table")

        return conflict_set

    ####################################################################
    '''
    Find Ignored Files 
    '''

    def get_ignored_file_list(self, slack_code):
        raw_list = []
        try:
            sql = "select approved_file " \
                  "from approved_list " \
                  "where slack_code = '%s'" % (slack_code)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_tuple = self.cursor.fetchall()
            for rt in raw_tuple:
                raw_list.append(rt[0])

        except:
            self.conn.rollback()
            print("ERROR : get ignored file list")

        return raw_list



    ####################################################################
    '''
    Find Locker
    '''
    def get_locker_slack_code(self, project_name, file_path):
        locker_name = ""
        try:
            sql = "select slack_code " \
                  "from lock_list " \
                  "where project_name = '%s' " \
                  "and lock_file = '%s'" % (project_name, file_path)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            locker_name = self.cursor.fetchall()[0][0]
            print("locker_name : ", locker_name)
        except:
            self.conn.rollback()
            print("ERROR : get locker slack code")

        return locker_name

    ####################################################################
    # '''
    # Find Git diff code
    # '''

    def get_git_diff_code(self, user_name, project_name, file_path):
        raw_tuple = tuple()
        try:
            sql = "select git_diff_code " \
                  "from edit_amount " \
                  "where user_name = '%s' " \
                  "and project_name = '%s' " \
                  "and file_name = '%s'" % (user_name, project_name, file_path)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
            raw_tuple = self.cursor.fetchone()[0]

        except:
            self.conn.rollback()
            print("ERROR : get git diff code")

        return raw_tuple

    ####################################################################
    '''
    Find the information of Severity
    '''

    def get_severity_set(self, project_name, file_path):
        raw_set = set()
        try:
            sql = "select logic1_name, logic2_name, user1_name, user2_name, severity " \
                  "from direct_conflict_table " \
                  "where project_name = '%s' " \
                  "and file_name = '%s'" % (project_name, file_path)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
            raw_tuple = self.cursor.fetchall()
            for rt in raw_tuple:
                if not ((rt[1], rt[3]), (rt[0], rt[2]), rt[4]) in raw_set:
                    raw_set.add(((rt[0], rt[2]), (rt[1], rt[3]), rt[4]))

        except:
            self.conn.rollback()
            print("ERROR : get severity set")

        return raw_set

    def get_severity_percentage(self, project_name, file_name):
        user_edit_amount = tuple()
        other_edit_amount = tuple()
        file_total_lines = tuple()
        raw_list = list()
        try:
            sql = "select total_plus, total_minus, user_name " \
                  "from edit_amount " \
                  "where project_name = '%s' " \
                  "and file_name = '%s' " \
                  % (project_name, file_name)

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            users_edit_amount = list(self.cursor.fetchall())

        except:
            self.conn.rollback()
            print("ERROR : get_severity_percentage")

        try:
            sql = "select total_lines " \
                  "from file_information " \
                  "where project_name = '%s' " \
                  "and file_name = '%s' " \
                  % (project_name, file_name)

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            file_total_lines = self.cursor.fetchone()

        except:
            self.conn.rollback()
            print("ERROR : update first best conflict list")

        for user_edit_amount in users_edit_amount:
            user_percentage = 0

            if user_edit_amount[0] == 0:
                user_percentage = (100 * user_edit_amount[1]) / file_total_lines[0]
            elif user_edit_amount[1] == 0:
                user_percentage = (100 * user_edit_amount[0]) / (file_total_lines[0] + user_edit_amount[0])
            elif user_edit_amount[0] > user_edit_amount[1]:
                user_percentage = (100 * user_edit_amount[0]) / (file_total_lines[0] + user_edit_amount[0] - user_edit_amount[1])
            elif user_edit_amount[0] <= user_edit_amount[1]:
                user_percentage = (100 * user_edit_amount[1]) / (file_total_lines[0])

            raw_list.append((user_edit_amount[2], user_percentage))

        return raw_list


    def get_working_users_on_file(self, project_name, file_name):
        user_list = []
        try:
            sql = "select user_name " \
                  "from working_table " \
                  "where project_name = '%s' " \
                  "and file_name = '%s'" \
                  % (project_name, file_name)

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_tuple = self.cursor.fetchall()
            for rt in raw_tuple:
                user_list.append(rt[0])

            print("get_working_users_on_file : ", user_list)

        except:
            self.conn.rollback()
            print("ERROR : get working users on file")

        return user_list


    ####################################################################
    '''
    Utility
    '''
    def read_project_name(self, slack_code):
        # Read git_id
        raw_list = []
        try:
            sql = "select git_id " \
                  "from user_table " \
                  "where slack_code = '%s'" % (slack_code)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = list(self.cursor.fetchall())

        except:
            self.conn.rollback()
            print("ERROR : read project name")

        # slack_code don't verified
        if not raw_list:
            print("ERROR : slack_code don't verified")
            return -2
        else:
            git_id = raw_list[0]

        # Read the project name
        raw_list1 = []
        try:
            sql = "select project_name " \
                  "from working_table " \
                  "where user_name = '%s'" % (git_id)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_list1 = list(self.cursor.fetchall())
        except:
            self.conn.rollback()
            print("ERROR : read project name")

        # This user don't have project
        if not raw_list1:
            print("ERROR : This user don't have project")
            return -1
        else:
            return raw_list1[0][0]

    def get_repository_name(self, slack_code):
        repository_name = ""
        try:
            sql = "select repository_name " \
                  "from user_table " \
                  "where slack_code = '%s'" % (slack_code)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
            repository_name = self.cursor.fetchall()[0][0]

        except:
            self.conn.rollback()
            print("ERROR : get repository name")

        if str(repository_name).isdigit():
            print("ERROR : NO PROJECT NAME")
            return

        return repository_name

    def get_repository_name_by_git_id(self, git_id):
        repository_name = ""
        try:
            sql = "select repository_name " \
                  "from user_table " \
                  "where git_id = '%s'" % (git_id)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
            repository_name = self.cursor.fetchall()[0][0]

        except:
            self.conn.rollback()
            print("ERROR : get repository name by git id")

        if str(repository_name).isdigit():
            print("ERROR : NO PROJECT NAME")
            return

        return repository_name

    def get_repository_and_user_name(self, slack_code):
        repository_name = ""
        user_name = ""
        try:
            sql = "select repository_name, slack_id " \
                  "from user_table " \
                  "where slack_code = '%s'" % (slack_code)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_tuple = self.cursor.fetchall()[0]

            repository_name = raw_tuple[0]
            user_name = raw_tuple[1]

        except:
            self.conn.rollback()
            print("ERROR : get repository and user name")

        if str(repository_name).isdigit():
            print("ERROR : NO PROJECT NAME")
            return

        if str(user_name).isdigit():
            print("ERROR : NO USER NAME")
            return

        return repository_name, user_name


    # Ex) git_id = "qortndud97@naver.com", slack_code = "<@UCFNMU2EM>", slack_id = "Sooyoung Baek"
    def convert_slack_id_to_git_id(self, slack_name):
        try:
            sql = "SELECT git_id " \
                  "FROM user_table " \
                  "WHERE slack_id = '%s'" % (slack_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            git_email = self.cursor.fetchall()[0][0]

        except:
            self.conn.rollback()
            print("ERROR : convert slack id to git id")

        return git_email

    def convert_slack_id_to_slack_code(self, slack_name):
        try:
            sql = "SELECT slack_code " \
                  "FROM user_table " \
                  "WHERE slack_id = '%s'" % (slack_name)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            slack_code = self.cursor.fetchall()[0][0]

        except:
            self.conn.rollback()
            print("ERROR : convert slack id to slack code")

        return slack_code

    def convert_git_id_to_slack_code(self, git_id):
        slack_code = ""

        try:
            sql = "select slack_code " \
                  "from user_table " \
                  "where git_id = '%s'" % (git_id)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_tuple = self.cursor.fetchall()
            print(raw_tuple)
            slack_code = raw_tuple[0][0]
            print(slack_code)

        except:
            self.conn.rollback()
            print("ERROR : convert_git_id_to_slack_code")

        return slack_code

    def convert_git_id_to_slack_id(self, git_id):
        # Read git_id
        git_id = git_id.replace('@', '@')
        slack_id = ""

        try:
            sql = "select slack_id " \
                  "from user_table " \
                  "where git_id = '%s'" % (git_id)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            query_result = self.cursor.fetchall()
            slack_id = query_result[0][0]

        except:
            self.conn.rollback()
            print("ERROR : convert_git_id_to_slack_id")

        return slack_id

    def convert_git_id_list_to_slack_code_list(self, git_id_list):
        slack_code_list = []

        for git_id in git_id_list:
            try:
                sql = "select slack_code " \
                      "from user_table " \
                      "where git_id = '%s'" % (git_id)
                print(sql)
                self.cursor.execute(sql)
                self.conn.commit()
                raw_tuple = self.cursor.fetchall()

                slack_code = "<@" + raw_tuple[0][0] + ">"
                slack_code_list.append(slack_code)

            except:
                self.conn.rollback()
                print("ERROR : convert_git_id_to_slack_id")

        return slack_code_list

    def convert_git_id_to_slack_code_id(self, git_id):
        try:
            sql = "select slack_code, slack_id " \
                  "from user_table " \
                  "where git_id = '%s'" % (git_id)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_tuple = self.cursor.fetchone()

        except:
            self.conn.rollback()
            print("ERROR : convert_slack_code_to_git_id")

        return raw_tuple[0], raw_tuple[1]

    def convert_slack_code_to_git_id(self, slack_code):
        # Read git_id
        git_id = ""
        try:
            sql = "select git_id " \
                  "from user_table " \
                  "where slack_code = '%s'" % (slack_code)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            query_result = self.cursor.fetchall()
            git_id = query_result[0][0]

        except:
            self.conn.rollback()
            print("ERROR : convert_slack_code_to_git_id")

        return git_id

    def convert_slack_code_to_slack_id(self, slack_code):
        slack_id = ""

        try:
            sql = "select slack_id " \
                  "from user_table " \
                  "where slack_code = '%s'" % (slack_code)
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw_tuple = self.cursor.fetchall()
            if raw_tuple:
                slack_id = raw_tuple[0][0]

        except:
            self.conn.rollback()
            print("ERROR : convert slack code to git id")

        return slack_id

    def is_old_git_log_name_only(self, project_name, last_commit_date):
        try:
            sql = "select last_commit_date " \
                  "from last_commit_date " \
                  "where project_name = '%s'" % (project_name)

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw = self.cursor.fetchone()

            if raw[0] == last_commit_date:
                return False
            else:
                return True

        except:
            self.conn.rollback()
            print("ERROR : is_old_git_log_name_only")

    def is_empty_git_log_name_only(self, project_name):
        try:
            sql = "select last_commit_date " \
                  "from last_commit_date " \
                  "where project_name = '%s'" % (project_name)

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

            raw = self.cursor.fetchone()

            if raw:
                return False
            else:
                return True

        except:
            self.conn.rollback()
            print("ERROR : is_empty_git_log_name_only")

    def update_git_log_name_only(self, project_name, log_file_list):
        try:
            sql = "replace into git_log_name_only " \
                  "(project_name, commit_order, file_list) values "

            for index, file_list in enumerate(log_file_list):
                sql += "('%s', '%d', '%s'), " % (project_name, index, json.dumps(file_list))

            sql = sql[:-2]

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

        except:
            self.conn.rollback()
            print("ERROR : update_git_log_name_only")

    def update_last_commit_date(self, project_name, last_commit_date):
        try:
            sql = "replace into last_commit_date " \
                  "(project_name, last_commit_date) value" \
                  "('%s', '%s')" % (project_name, last_commit_date)

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()

        except:
            self.conn.rollback()
            print("ERROR : update_last_commit_date")

    def get_prediction_list(self, project_name, user1_git_id, user2_git_id):
        prediction_list = []

        try:
            sql = "select order_num, other_name, file_name, percentage, related_file_list from prediction_list " \
                  "where project_name = '%s' " \
                  "and user_name = '%s' " \
                  "and target = '%s'" % (project_name, user1_git_id, user2_git_id)

            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
            prediction_list = list(self.cursor.fetchall())

        except:
            self.conn.rollback()
            print("ERROR : get_prediction_list")

        return prediction_list

    def close(self):
        self.cursor.close()
        self.conn.close()