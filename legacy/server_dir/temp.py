from server_dir.server_git import *
from server_dir.indirect_work_database import *
from chat_bot_server_dir.sentence_process_logic import *

def temp(self, project_name, working_list, user_name):
    # 알람 카운트 2인것들 다 삭제

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

    # Process Direct Conflict
    if (all_rows_list != []):
        # CONFLICT

        # Get database user conflict data
        database_user_conflict_list = list()
        try:
            sql = "select * " \
                  "from conflict_table " \
                  "where user_name = '%s'" % (user_name)

            self.cursor.execute(sql)
            self.conn.commit()

            # get rows data
            database_user_conflict_list = self.cursor.fetchall()
            database_user_conflict_list = list(database_user_conflict_list)

        except:
            self.conn.rollback()
            print("ERROR : alert conflict")

        # temp_other_work : ["project_name", "file_name", "logic_name", "user_name", "timestamp"]
        for temp_other_work in all_rows_list:

            # temp_user_work : ["file_name", "logic_name", "work_line", "work_amount"]
            for temp_user_work in working_list:
                print(temp_other_work)
                print(temp_user_work)

                # Condition
                # [other_file_name == current_user_file_name]
                # and [other_logic_name == current_user_logic_name]
                if (temp_other_work[1] == temp_user_work[0]
                    and temp_other_work[2] == temp_user_work[1]):
                    print("*** Conflict ***")
                    print("project name : " + project_name)
                    print("file name : " + temp_other_work[1])
                    print("logic name : " + temp_other_work[2] + '\n')

                    # severity
                    if (temp_user_work[1][:3] == "def"):
                        severity = 3
                    elif (temp_user_work[1][:5] == "class"):
                        severity = 2
                    else:
                        severity = 1

                    # Alert conflict
                    # Detect getting severity
                    if (database_user_conflict_list != []):
                        for temp_db_user_conflict in database_user_conflict_list:

                            print(temp_db_user_conflict)

                            # same project name and same file name
                            if (temp_db_user_conflict[0] == project_name
                                and temp_db_user_conflict[1] == temp_user_work[0]):

                                # After 30 minutes
                                if (d.datetime.today() - temp_db_user_conflict[6] > d.timedelta(minutes=30)):
                                    if (temp_db_user_conflict[5] < severity):
                                        print("getting severity : " + str(severity))
                                    elif (temp_db_user_conflict[5] == severity):
                                        print("same severity : " + str(severity))
                                    else:
                                        print("weak severity : " + str(severity))

                                    try:
                                        sql = "delete " \
                                              "from conflict_table " \
                                              "where project_name = '%s' " \
                                              "and file_name = '%s' " \
                                              "and logic_name = '%s' " \
                                              "and user_name = '%s' " % (
                                              project_name, temp_user_work[0], temp_user_work[1], user_name)
                                        self.cursor.execute(sql)
                                        self.conn.commit()
                                    except:
                                        self.conn.rollback()
                                        print("ERROR : delete current user conflict data")
                    else:
                        # First conflict
                        # 컨플릭트 데이터 넣기 끝
                        print("first conflict")
                        pass

        #### 3. insert_conflict_data ####

        result = "conflict"

    else:
        # NON-CONFLICT
        # delete conflict current user data
        result = "non-conflict"

    #######################################################################

    #### 2.
    if (all_rows_list != []):
        # Conflict

        # temp_other_work : ["project_name", "file_name", "logic_name", "user_name", "timestamp"]
        for temp_other_work in all_rows_list:
            # temp_user_work : ["file_name", "logic_name", "work_line", "work_amount"]
            for temp_user_work in working_list:
                # Search already conflict data
                already_conflict_list = list()
                change_conflict_list = list()

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

                    already_conflict_list = self.cursor.fetchall()
                    already_conflict_list = list(already_conflict_list)

                except:
                    self.conn.rollback()
                    print("ERROR : get conflict_table")

                try:
                    sql = "select * " \
                          "from working_table " \
                          "where project_name = '%s' " \
                          "and file_name = '%s' " \
                          "and logic_name = '%s' " \
                          "and user_name = '%s' " % (
                          project_name, temp_other_work[1], temp_user_work[1], temp_other_work[3])
                    print(sql)
                    self.cursor.execute(sql)
                    self.conn.commit()

                    change_conflict_list = self.cursor.fetchall()
                    change_conflict_list = list(change_conflict_list)

                except:
                    self.conn.rollback()
                    print("ERROR : get conflict_table")

                if (already_conflict_list != [] and change_conflict_list != []):
                    print("already conflict list")
                    for temp_already_conflict in already_conflict_list:
                        # already_conflict_list

                        # calculate severity
                        if (temp_user_work[1][:3] == "def"):
                            severity = 3
                        elif (temp_user_work[1][:5] == "class"):
                            severity = 2
                        else:
                            severity = 1

                        # After 30 minutes
                        # if (d.datetime.today() - temp_already_conflict[7] > d.timedelta(minutes=30)):
                        if (temp_already_conflict[6] < severity):
                            print("getting severity : " + str(severity))
                        elif (temp_already_conflict[6] == severity):
                            print("same severity : " + str(severity))
                        else:
                            print("weak severity : " + str(severity))

                        # update current conflict
                        print(temp_user_work)
                        print(temp_other_work)

                        self.update_conflict_data(project_name, temp_user_work[0], temp_user_work[1], user_name,
                                                  temp_other_work[3], severity)

        # Get the data of current user: same proj_name, file_name from conflict_table
        # temp_other_work : ["project_name", "file_name", "logic_name", "user_name", "timestamp"]
        for temp_other_work in all_rows_list:

            # temp_user_work : ["file_name", "logic_name", "work_line", "work_amount"]
            for temp_user_work in working_list:
                print(temp_other_work)
                print(temp_user_work)

                # Condition
                # [other_file_name == current_user_file_name]
                # and [other_logic_name == current_user_logic_name]
                if (temp_other_work[1] == temp_user_work[0]
                    and temp_other_work[2] == temp_user_work[1]):
                    print("*** Conflict ***")
                    print("project name : " + project_name)
                    print("file name : " + temp_other_work[1])
                    print("logic name : " + temp_other_work[2] + '\n')

                    # calculate severity
                    if (temp_user_work[1][:3] == "def"):
                        severity = 3
                    elif (temp_user_work[1][:5] == "class"):
                        severity = 2
                    else:
                        severity = 1

                    # insert current conflict
                    self.insert_conflict_data(project_name, temp_user_work[0], temp_user_work[1], user_name,
                                              temp_other_work[3], severity)
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

    content = {
        'git_id' : 'chan_j@naver.com',
        'git_diff': {
            'b project': {
                'b file': [
                    [
                        'class:AClass:function1188888',
                        4,
                         16
                    ],
                    [
                        'function:function44442',
                        4,
                        16
                    ]
                ],
                'f file': [
                    [
                        'function:edd',
                        145,
                        42
                    ]
                ]
            }
        }
    }


if __name__ == "__main__":
    print("#### START temp.py ####")

    # Load mysql database connection config
    host, user, password, db, charset = load_database_connection_config()

    # get mysql database connection
    conn = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                db=db,
                                charset=charset)
    # get cursor
    cursor = conn.cursor()

    raw_list = list()
    try:
        sql = "select * " \
              "from ignore_table " \
              "where project_name = '%s' " \
              "and slack_code = '%s' " % ("a", "b")

        cursor.execute(sql)
        conn.commit()
        print(sql)

        raw_list = cursor.fetchone()
    except:
        conn.rollback()
        print("ERROR : read project name")

    print(raw_list[2], raw_list[3])
    # content = {
    #     'git_id' : 'chan_j@naver.com',
    #     'git_diff': {
    #         'a': {
    #             'a/c': [
    #                 [
    #                     'f2',
    #                     4,
    #                     16
    #                 ]
    #             ]
    #         }
    #     }
    # }
    #
    #
    # # Create user git diff data
    # user_data = user_git_diff(content)
    #
    # # Create direct and indirect database connection
    # dw_db = direct_work_database()
    # iw_db = indirect_work_database()
    # w_db = work_database()
    #
    # # Remove lock list
    # w_db.auto_remove_lock_list()
    #
    # # Inform to the user about lock file
    # w_db.inform_lock_file(user_data.get_proj_name(),
    #                       user_data.get_working_data(),
    #                       user_data.get_user_name())
    #
    # # Delete current user data
    # dw_db.delete_user_data(user_data.get_user_name())
    #
    # # Detect direct conflict
    # dw_db.detect_direct_conflict(user_data.get_proj_name(),
    #                             user_data.get_working_data(),
    #                             user_data.get_user_name())
    #
    # # Detect indirect conflict
    # iw_db.detect_indirect_conflict(user_data.get_proj_name(),
    #                                user_data.get_working_data(),
    #                                user_data.get_user_name())
    #
    # # Insert current user data
    # dw_db.insert_user_data(user_data.get_proj_name(),
    #                       user_data.get_working_data(),
    #                       user_data.get_user_name())
    #
    # # Close direct and indirect database connection
    # dw_db.close_db()
    # iw_db.close_db()