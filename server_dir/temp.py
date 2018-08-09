from server_dir.server_git import *

if __name__ == "__main__":

    content = {
        'a' : {
            'user1' : {
                'b' : [
                    [
                        'c',
                        3,
                        4
                    ]
                ],
                'c' : [
                    [
                        'd',
                        4,
                        3
                    ]
                ]
            }
        }
    }

    temp = user_git_diff(content)
    print(temp.get_working_data())

    # # file name, logic name
    # temp_work = [["b", "c"], ["c", "d"]]
    #
    w_db = work_database()
    #
    w_db.delete_user_data(temp.get_user_name())
    # #
    w_db.detect_direct_conflict(temp.get_proj_name(),
                                temp.get_working_data(),
                                temp.get_user_name())

    w_db.insert_user_data(temp.get_proj_name(),
                            temp.get_working_data(),
                            temp.get_user_name())

    w_db.close_db()