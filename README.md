Direct conflict
---------------
##Class user_git_diff

 - variable : content, proj_name, user_name
 - function
    - get_proj_name : return project name
    - get_user_name : return user name
    - get_working_data : return working data

##Class work_database
 - function
    - detect_direct_conflict : detect direct conflict (input : project name, working list, user name)
    - delete_user_data : delete past user data from working table (input : user name)
    - search_working_table : search user's project name and file name in working table (input : project name, file list / output : working table row)
    - search_already_conflict_table : check if current conflict has already occurred from working table (input : project name, conflict file list, user's working file list, user name / output : working table row about already occurred conflict )
    - search_best_conflict : search the best value of severity in current (input : project name, conflict file list, user's working file list, user name / output : severity list including severity level and logic name per files)
    - compare_current_conflict_and_db_conflict : compare current conflict and database conflict and send direct messages to users (input : already conflict list, severity list including severity level and logic name per files)
    - update_first_best_conflict_list : update conflict list with best severity conflict when conflict occurs first time(input : severity list including severity level and logic name per files)
    - non_conflict_logic : if there is no conflict, delete user data from working table (input : project name, user name)
    - insert_user_data : insert user data to working table (input : project name, working list, user name)
    - update_conflict_data : update conflict information to working table after compares current conflict to conflict in the working table (input : project name, file name, user1 logic name, user2 logic name, user1 name, user2 name, severity)
    - increase_alert_count : increase 1 alert count in working table each time you give a notification (input : project name, file name, user1 logic name, user2 logic name, user1 name, user2 name)
    - insert_conflict_data : save conflict data in the database when the first conflict occurs. (input : project name, file name, user1 logic name, user2 logic name, user1 name, user2 name, severity)
    - delete_conflict_list : remove conflict information from the conflict list, if 24 hours have elapsed and the alarm is more than 2 times
    - close_db : close database
