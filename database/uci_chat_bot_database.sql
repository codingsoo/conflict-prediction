
/*
1. Create Database
create database uci_chat_bot;
use uci_chat_bot;
*/

/*
2.
CREATE TABLE working_table (
	project_name varchar(20) not null,
    file_name varchar(20) not null,
    logic_name varchar(20) not null,
    user_name varchar(20) not null,
    log_time timestamp,
    
    primary key(project_name, file_name, logic_name, user_name)
);
*/


use uci_chat_Bot;
CREATE TABLE conflict_table (
	project_name varchar(20) not null,
    file_name varchar(20) not null,
    logic_name varchar(20) not null,
    user_name varchar(20) not null,
    log_time timestamp,
    
    primary key(project_name, file_name, logic_name, user_name)
);
