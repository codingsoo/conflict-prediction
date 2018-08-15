import pymysql
import datetime as d
from server_dir.slack_message_sender import *

class indirect_work_database:

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
    def detect_indirect_conflict(self, project_name, working_list, user_name):

        self.delete_conflict_list()

        other_working_list = self.search_working_table(project_name)
        indirect_conflict_list = self.search_logic_dependency(project_name, working_list, other_working_list, user_name)

        print("other_working_list : " + str(other_working_list))
        print("indirect_conflict_list : " + str(indirect_conflict_list))

        # Conflict
        if(indirect_conflict_list != []):

            print("#### Indirect Conflict !!! ####")
            already_indirect_conflict_list = self.search_already_indirect_conflict_table(project_name, indirect_conflict_list)

            # Already indirect conflicted
            if(already_indirect_conflict_list != []):

                print("#### Already Indirect Conflict !!! ####")
                # db insert
                # 사용자 알람 => 30분 이상일때만 알람
                # 알람 카운트 증가

            # First conflict
            else:

                print("#### First Conflict !!! ####")
                # db insert
                # 사용자한태 알람

        # Non-conflict
        else:
            print("#### Non-Conflict !!! ####")
            # indirect conlfict table 자기 정보 다 삭제

        return


    # Delete conflict list
    def delete_conflict_list(self):

        try:
            sql = "delete " \
                  "from indirect_conflict_table " \
                  "where alert_count >= 2 " \
                  "and TIMEDIFF(now(),log_time) > 24"
            print(sql)

            self.cursor.execute(sql)
            self.conn.commit()

        except:
            self.conn.rollback()
            print("ERROR : delete indirect conflict list")

        return

    # Search working_table
    def search_working_table(self, project_name):

        raw_list = list()

        try:
            sql = "select * " \
                  "from working_table " \
                  "where project_name = '%s' " % (project_name)
            print(sql)

            self.cursor.execute(sql)
            self.conn.commit()

            raw_list = self.cursor.fetchall()
            raw_list = list(raw_list)
        except:
            self.conn.rollback()
            print("ERROR : search indirect working table")

        print(raw_list)

        return raw_list


    def search_logic_dependency(self, project_name, user_working_list, other_working_list, user_name):

        all_raw_list = list()

        # ["file_name", "logic_name", "work_line", "work_amount"]
        for temp_user_work in user_working_list:
            # [ project_name, file_name, logic_name, user_name, work_line, work_amount, log_time]
            for temp_other_work in other_working_list:

                temp_user_logic = temp_user_work[0] + "|" + temp_user_work[1]
                temp_other_logic = temp_other_work[1] + "|" + temp_other_work[2]

                try:
                    sql = "select * " \
                          "from logic_dependency " \
                          "where project_name = '%s' " \
                          "and ((u = '%s' or v = '%s') and (u = '%s' or v = '%s')) " %(project_name,
                                                                                       temp_user_logic, temp_user_logic,
                                                                                       temp_other_logic, temp_other_logic)
                    print(sql)

                    self.cursor.execute(sql)
                    self.conn.commit()

                    raw_list = self.cursor.fetchall()
                    raw_list = list(raw_list)

                    if(raw_list != []):
                        temp_raw = list()

                        temp_raw.append(user_name)          # user name
                        temp_raw.append(temp_user_logic)    # user logic
                        temp_raw.append(temp_other_work[3]) # other name
                        temp_raw.append(temp_other_logic)   # other logic

                        all_raw_list.append(temp_raw)

                except:
                    self.conn.rollback()
                    print("ERROR : search logic dependency")

        print(all_raw_list)

        return all_raw_list


    def search_already_indirect_conflict_table(self, project_name, indirect_conflict_list):

        all_raw_list = list()

        # [user1_name, user1_logic, user2_name, user2_logic]
        for temp_indirect_conflict in indirect_conflict_list:
            try:
                sql = "select * " \
                      "from indirect_conflict_table " \
                      "where project_name = '%s' " \
                      "and u = '%s' and v = '%s' " \
                      "and user1_name = '%s' and user2_name = '%s' " % (project_name,
                                                                        temp_indirect_conflict[1], temp_indirect_conflict[3],
                                                                        temp_indirect_conflict[0], temp_indirect_conflict[2])

                print(sql)

                self.cursor.execute(sql)
                self.conn.commit()

                raw_list = self.cursor.fetchall()
                raw_list = list(raw_list)

                if (raw_list != []):
                    for temp_raw in raw_list:
                        all_raw_list.append(temp_raw)

            except:
                self.conn.rollback()
                print("ERROR : search already indirect conflict table")

        return all_raw_list