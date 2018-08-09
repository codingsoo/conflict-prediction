from server_dir.server_git import *

if __name__ == "__main__":
    temp_work = [["b", "c"], ["c", "d"]]

    w_db = work_database()

    w_db.detect_direct_conflict("a", temp_work, "user")