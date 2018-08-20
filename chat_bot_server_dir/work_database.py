import pymysql
import time
import datetime
from server_dir.server_config_loader import *

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
    Approved list
    '''

    # Add approved list
    def add_approved_list(self, slack_code, req_approved_set):
        project_name = self.read_project_name(slack_code)
        if(str(project_name).isdigit()):
            print("ERROR : NO PROJECT NAME")
            return
        db_approved_set = set(self.read_approved_list(project_name))

        diff_approved_set = req_approved_set-db_approved_set

        # [[project_name, approved_file], [project_name, approved_file], [project_name, approved_file]]
        sql1 = "insert into approved_list (project_name, approved_file) values "
        for temp_diff_approved in diff_approved_set:
            sql1 += "('%s', '%s'), " % (project_name, temp_diff_approved)

        sql1 = sql1[:-2]

        try:
            self.cursor.execute(sql1)
            self.conn.commit()
            print(sql1)
        except:
            self.conn.rollback()
            print("ERROR : add approved list")

        return


    # Remove approved list
    def remove_approved_list(self, slack_code, remove_approve_list):
        project_name = self.read_project_name(slack_code)
        if(str(project_name).isdigit()):
            print("ERROR : NO PROJECT NAME")
            return
        for temp_remove_file in remove_approve_list:
            try:
                sql = "delete " \
                      "from approved_list " \
                      "where project_name = '%s' " \
                      "and approved_file = '%s' " %(project_name, temp_remove_file)
                self.cursor.execute(sql)
                self.conn.commit()
                print(sql)
            except:
                self.conn.rollback()
                print("ERROR : remove approved list")

        return

    def recommendation(self, user1, user2):

        user1_working_amount = "SELECT work_amount " \
                               "FROM working_table " \
                               "WHERE user_name= '%s' " % user1
        user2_working_amount = "SELECT work_amount " \
                               "FROM working_table " \
                               "WHERE user_name= '%s' " % user2

        try:
            self.cursor.execute(user1_working_amount)
            self.conn.commit()
            user1_working_amount = self.cursor.fetchall()[0][0]
            self.cursor.execute(user2_working_amount)
            self.conn.commit()
            user2_working_amount = self.cursor.fetchall()[0][0]

        except:
            self.conn.rollback()
            print("ERROR : recommendation")

        response_list = []

        if user1_working_amount > user2_working_amount :
            response_list.append(user1)
            response_list.append(user1_working_amount)
            return response_list
        elif user1_working_amount < user2_working_amount :
            response_list.append(user2)
            response_list.append(user2_working_amount)
            return response_list
        else :
            return response_list

    def user_recognize(self, user):
        last_connection = "SELECT last_connection " \
                          "FROM user_last_connection " \
                          "WHERE slack_code = '%s'" % (user)
        try:
            self.cursor.execute(last_connection)
            self.conn.commit()
            last_connection = self.cursor.fetchall()[0][0]

        except:
            self.conn.rollback()
            print("ERROR : last_connection")

        print (last_connection)

        if (datetime.datetime.now() - last_connection) > datetime.timedelta(days=3) :
            return 1
        elif (datetime.datetime.now() - last_connection) > datetime.timedelta(days=7) :
            return 2
        elif (datetime.datetime.now() - last_connection) > datetime.timedelta(days=30) :
            return 3

    def get_user_working_status(self, git_email_id):
        sql = "SELECT file_name, logic_name, work_line, work_amount " \
              "FROM working_table " \
              "WHERE user_name = '%s'" % git_email_id
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            working_status = self.cursor.fetchall()[0]
            print(working_status)
            return working_status
        except:
            self.conn.rollback()
            print("ERROR : get user working status")

    # 컨플릭트 파일 받아서 현재 어프루브 리스트 파일 빼서 남은 것만 반환해주기
    def classify_direct_conflict_approved_list(self, project_name, current_conflict_list):
        db_approved_list = self.read_approved_list(project_name)

        print(db_approved_list)

        for temp_db_aproved in db_approved_list:
            print("temp db approved : " + str(temp_db_aproved[0]))
            for temp_current_conflict in current_conflict_list:

                if(temp_db_aproved[0] == temp_current_conflict[1]):
                    try:
                        current_conflict_list.remove(temp_current_conflict)
                    except:
                        print("ERROR : classify conflict approved list")

        return current_conflict_list


    # 컨플릭트 파일 받아서 현재 어프루브 리스트 파일 빼서 남은 것만 반환해주기
    def classify_indirect_conflict_approved_list(self, project_name, current_conflict_list):
        db_approved_list = self.read_approved_list(project_name)

        print("current_conflict : " + str(current_conflict_list))
        print(db_approved_list)

        for temp_db_aproved in db_approved_list:
            print("temp db approved : " + str(temp_db_aproved[0]))
            for temp_current_conflict in current_conflict_list:

                # [user_name, user_logic, other_name, other_logic]
                user1_file = str(temp_current_conflict[1]).split('|')[0]
                user2_file = str(temp_current_conflict[3]).split('|')[0]

                if((temp_db_aproved[0] == user1_file)
                   or (temp_db_aproved[0] == user2_file)):
                    try:
                        current_conflict_list.remove(temp_current_conflict)
                    except:
                        print("ERROR : classify conflict approved list")

        return current_conflict_list


    def read_approved_list(self, project_name):
        raw_list = list()
        try:
            sql = "select approved_file " \
                  "from approved_list " \
                  "where project_name = '%s' " % project_name

            self.cursor.execute(sql)
            self.conn.commit()
            print(sql)

            raw_list = self.cursor.fetchall()
            raw_list = set(raw_list)

            # raw_list = self.cursor.fetchall()
            # raw_list = list(raw_list)
            #
            # for temp in raw_list:
            #     raw_set.add(temp)
        except:
            self.conn.rollback()
            print("ERROR : read approved list")

        return raw_list


    ####################################################################3
    '''
    lock list
    '''
    # Add lock list
    def add_lock_list(self, slack_code, req_lock_set, delete_time):
        project_name = self.read_project_name(slack_code)
        if(str(project_name).isdigit()):
            print("ERROR : NO PROJECT NAME")
            return
        db_lock_set = set(self.read_lock_list(slack_code, project_name))

        diff_lock_set = req_lock_set-db_lock_set

        # [[project_name, approved_file], [project_name, approved_file], [project_name, approved_file]]
        sql1 = "insert into lock_list (project_name, lock_file, slack_code) values "
        for temp_diff_lock in diff_lock_set:
            sql1 += "('%s', '%s', '%s', %d), " % (project_name, temp_diff_lock, slack_code, delete_time)

        sql1 = sql1[:-2]

        try:
            self.cursor.execute(sql1)
            self.conn.commit()
            print(sql1)
        except:
            self.conn.rollback()
            print("ERROR : add lock list")

        return

    # Remove approved list
    def remove_lock_list(self, slack_code, remove_lock_list):
        project_name = self.read_project_name(slack_code)
        if(str(project_name).isdigit()):
            print("ERROR : NO PROJECT NAME")
            return
        for temp_remove_file in remove_lock_list:
            try:
                sql = "delete " \
                      "from lock_list " \
                      "where project_name = '%s' " \
                      "and lock_file = '%s' " \
                      "and slack_code = '%s' " %(project_name, temp_remove_file, slack_code)
                self.cursor.execute(sql)
                self.conn.commit()
                print(sql)
            except:
                self.conn.rollback()
                print("ERROR : remove lock list")

        return


    def auto_remove_lock_list(self):
        try:
            sql = "delete " \
                  "from lock_list " \
                  "where TIMEDIFF(now(),log_time) > delete_time * 60 * 60"
            self.cursor.execute(sql)
            self.conn.commit()
            print(sql)

        except:
            self.conn.rollback()
            print("ERROR : auto remove lock list")

        return

    def read_lock_list(self, slack_code, project_name):
        raw_list = list()
        try:
            sql = "select lock_file " \
                  "from lock_list " \
                  "where project_name = '%s' " \
                  "and slack_code = '%s' " % (project_name, slack_code)

            self.cursor.execute(sql)
            self.conn.commit()
            print(sql)

            raw_list = self.cursor.fetchall()
            raw_list = list(raw_list)

        except:
            self.conn.rollback()
            print("ERROR : read lock list")

        return raw_list


    def inform_lock_file(self, project_name, working_list, git_id):
        all_raw_list = list()

        # working_list = [ ["file_name", "logic_name", "work_line", "work_amount"], ["file_name", "logic_name", "work_line", "work_amount"], ... ]
        slack_code = self.convert_git_id_to_slack_code(git_id)[0]
        if(str(slack_code).isdigit()):
            print("ERROR : NO SLACK CODE")
            return

        for temp_work in working_list:
            try:
                sql = "select * " \
                      "from lock_list " \
                      "where project_name = '%s' " \
                      "and lock_file = '%s' " \
                      "and slack_code != '%s' " %(project_name, temp_work[0], slack_code)
                self.cursor.execute(sql)
                self.conn.commit()
                print(sql)

                raw_list = list(self.cursor.fetchall())
                if(raw_list != []):
                    for temp in raw_list:
                        all_raw_list.append(temp)
            except:
                self.conn.rollback()
                print("ERROR : inform lock file")

        if(all_raw_list != []):
            for temp_raw in all_raw_list:
                print("lock file : " + str(temp_raw))

        return


    ####################################################################
    '''
    ignore
    '''
    def add_update_ignore(self, project_name, ignore_list, slack_code):
        read_ignore = self.read_ignore(project_name, slack_code)

        if(read_ignore == []):
            # First ignore register
            sql = "insert into ignore_table " \
                  "(project_name, slack_code, direct_ignore, indirect_ignore) value " \
                  "('%s', '%s', %d, %d) " % (project_name, slack_code, ignore_list[0], ignore_list[1])
        else:
            # Already exists ignore
            sql = "update ignore_table " \
                  "set direct_ignore = %d, indirect_ignore = %d " \
                  "where project_name = '%s' " \
                  "and slack_code = '%s' " %(ignore_list[0], ignore_list[1],
                                             project_name, slack_code)

        # ignore_list : [direct_ignore, indirect_ignore]
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            print(sql)

        except:
            self.conn.rollback()
            print("ERROR : add ignore")


    def remove_ignore(self, project_name, slack_code):
        try:
            sql = "delete " \
                  "from ignore_table " \
                  "where project_name = '%s' " \
                  "and slack_code = '%s' " %(project_name, slack_code)

            self.cursor.execute(sql)
            self.conn.commit()
            print(sql)

        except:
            self.conn.rollback()
            print("ERROR : remove ignore")


    def search_ignore(self, project_name, git_id):
        slack_code = self.convert_git_id_to_slack_code(git_id)[0]
        raw = tuple()

        try:
            sql = "select * " \
                  "from ignore_table " \
                  "where project_name = '%s' " \
                  "and slack_code = '%s' " %(project_name, slack_code)

            self.cursor.execute(sql)
            self.conn.commit()
            print(sql)

            # [project_name, slack_code, direct_ignore, indirect_ignore]
            raw = tuple(self.cursor.fetchone())
        except:
            self.conn.rollback()
            print("ERROR : search ignore")

        # direct_ignore, indirect_ignore
        # 0 => non-ignore / 1 => ignore
        return raw[2], raw[3]

    def get_recent_data(self, github_email):
        sql1  =  "SELECT file_name, logic1_name, logic2_name, user1_name, user2_name, log_time " \
                "FROM direct_conflict_table " \
                "WHERE user1_name = '%s' or user2_name = '%s'" % (github_email, github_email)

        sql2 = "SELECT u, v, user1_name, user2_name, log_time " \
                "FROM indirect_conflict_table " \
                "WHERE user1_name = '%s' or user2_name = '%s'" % (github_email, github_email)

        try:
            self.cursor.execute(sql1)
            self.conn.commit()
            direct_recent_data = self.cursor.fetchall()
            direct_recent_data_mod = list()
            indirect_recent_data_mod = list()

            for conf in direct_recent_data:
                conf = list(conf)
                conf[1] = conf[0] + '|' + conf[1]
                conf[2] = conf[0] + '|' + conf[2]
                direct_recent_data_mod.append(conf[1:])
            self.cursor.execute(sql2)
            self.conn.commit()
            indirect_recent_data = list(self.cursor.fetchall())
            for conf in indirect_recent_data:
                conf = list(conf)
                indirect_recent_data_mod.append(conf)
            conflict_recent_data = direct_recent_data_mod+indirect_recent_data_mod

            sorted(conflict_recent_data, key=lambda s: s[4])
            conflict_recent_data[-1].remove(github_email)

            return conflict_recent_data[-1]

        except:
            self.conn.rollback()
            print("ERROR : Get recent data")



    def read_ignore(self, project_name, slack_code):
        raw_list = list()
        try:
            sql = "select * " \
                  "from ignore_table " \
                  "where project_name = '%s' " \
                  "and slack_code = '%s' " % (project_name, slack_code)

            self.cursor.execute(sql)
            self.conn.commit()
            print(sql)

            raw_list = self.cursor.fetchall()
            raw_list = list(raw_list)
        except:
            self.conn.rollback()
            print("ERROR : read project name")

        return raw_list

    ####################################################################
    '''
    Utility
    '''
    def convert_git_id_to_slack_code(self, git_id):
        raw_list = list()

        try:
            sql = "select slack_code " \
                  "from user_table " \
                  "where git_id = '%s' " % git_id

            self.cursor.execute(sql)
            self.conn.commit()
            print(sql)

            raw_list = self.cursor.fetchall()
            raw_list = list(raw_list)
        except:
            self.conn.rollback()
            print("ERROR : read project name")

        if(raw_list != []):
            return raw_list[0]
        else:
            return -1

    def read_project_name(self, slack_code):
        # Read git_id
        raw_list = list()
        try:
            sql = "select git_id " \
                  "from user_table " \
                  "where slack_code = '%s' " % slack_code

            self.cursor.execute(sql)
            self.conn.commit()
            print(sql)

            raw_list = self.cursor.fetchall()
            raw_list = list(raw_list)
        except:
            self.conn.rollback()
            print("ERROR : read project name")

        # slack_code don't verified
        if(raw_list == []):
            print("ERROR : slack_code don't verified")
            return -2
        else:
            git_id = raw_list[0]
            print(git_id)

        # Read the project name
        raw_list1 = list()
        try:
            sql = "select project_name " \
                  "from working_table " \
                  "where user_name = '%s' " % git_id

            self.cursor.execute(sql)
            self.conn.commit()
            print(sql)

            raw_list1 = self.cursor.fetchall()
            raw_list1 = list(raw_list1)
        except:
            self.conn.rollback()
            print("ERROR : read project name")

        # This user don't have project
        if(raw_list1 == []):
            print("ERROR : This user don't have project")
            return -1
        else:
            return raw_list[0]


    def close(self):
        self.cursor.close()
        self.conn.close()

a = work_database()
a.get_recent_data('a')