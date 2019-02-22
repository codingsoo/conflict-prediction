-- --------------------------------------------------------
-- 호스트:                          127.0.0.1
-- 서버 버전:                        5.7.17-log - MySQL Community Server (GPL)
-- 서버 OS:                        Win64
-- HeidiSQL 버전:                  9.4.0.5125
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- uci_chat_bot 데이터베이스 구조 내보내기
CREATE DATABASE IF NOT EXISTS `uci_chat_bot` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `uci_chat_bot`;

-- 테이블 uci_chat_bot.approved_list 구조 내보내기
CREATE TABLE IF NOT EXISTS `approved_list` (
  `slack_code` varchar(50) DEFAULT NULL,
  `approved_file` varchar(255) DEFAULT NULL,
  KEY `인덱스 1` (`slack_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.direct_conflict_table 구조 내보내기
CREATE TABLE IF NOT EXISTS `direct_conflict_table` (
  `project_name` varchar(50) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `logic1_name` varchar(50) NOT NULL,
  `logic2_name` varchar(50) NOT NULL,
  `user1_name` varchar(50) NOT NULL,
  `user2_name` varchar(50) NOT NULL,
  `alert_count` int(11) DEFAULT '1',
  `severity` int(11) DEFAULT '1',
  `severity_percentage` float(5,2) DEFAULT '0',
  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_name`,`file_name`,`logic1_name`,`user1_name`,`user2_name`,`logic2_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.ignore_table 구조 내보내기
CREATE TABLE IF NOT EXISTS `ignore_table` (
  `project_name` varchar(50) NOT NULL,
  `slack_code` varchar(50) NOT NULL,
  `direct_ignore` int(11) NOT NULL DEFAULT '0',
  `indirect_ignore` int(11) NOT NULL DEFAULT '0',
  `prediction_ignore` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`project_name`,`slack_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.indirect_conflict_table 구조 내보내기
CREATE TABLE IF NOT EXISTS `indirect_conflict_table` (
  `project_name` varchar(50) NOT NULL,
  `def_file` varchar(255) NOT NULL,
  `def_func` varchar(255) NOT NULL,
  `call_file` varchar(255) NOT NULL,
  `call_func` varchar(255) NOT NULL,
  `length` int(11) NOT NULL DEFAULT '0',
  `user1_name` varchar(50) NOT NULL,
  `user2_name` varchar(50) NOT NULL,
  `alert_count` int(11) NOT NULL DEFAULT '1',
  `call_user` int(11) NOT NULL DEFAULT '0',
  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(`project_name`, `def_func`, `call_file`, `call_func`, `user1_name`, `user2_name`, `call_user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.lock_list 구조 내보내기
CREATE TABLE IF NOT EXISTS `lock_list` (
  `project_name` varchar(50) DEFAULT NULL,
  `lock_file` varchar(255) DEFAULT NULL,
  `slack_code` varchar(50) DEFAULT NULL,
  `delete_time` int(11) DEFAULT NULL,
  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.lock_notice_list 구조 내보내기
CREATE TABLE IF NOT EXISTS `lock_notice_list` (
  `project_name` varchar(50) NOT NULL,
  `lock_file` varchar(255) NOT NULL,
  `noticed_user` varchar(50) NOT NULL,
  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(`project_name`, `lock_file`, `noticed_user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.logic_dependency 구조 내보내기
CREATE TABLE IF NOT EXISTS `logic_dependency` (
  `project_name` varchar(50) NOT NULL,
  `def_func` varchar(255) NOT NULL,
  `call_func` varchar(255) NOT NULL,
  `length` int(11) NOT NULL DEFAULT '0',
  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_name`,`def_func`,`call_func`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.function_list 구조 내보내기
CREATE TABLE IF NOT EXISTS `function_list` (
  `project_name` varchar(50) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `logic` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.user_table 구조 내보내기
CREATE TABLE IF NOT EXISTS `user_table` (
  `git_id` varchar(50) DEFAULT NULL,
  `slack_id` varchar(50) DEFAULT NULL,
  `slack_code` varchar(50) DEFAULT NULL UNIQUE,
  `repository_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.user_last_connection 구조 내보내기
CREATE TABLE IF NOT EXISTS `user_last_connection` (
  `slack_code` varchar(50) NOT NULL,
  `last_connection` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`slack_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.working_table 구조 내보내기
CREATE TABLE IF NOT EXISTS `working_table` (
  `project_name` varchar(50) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `logic_name` varchar(50) NOT NULL,
  `user_name` varchar(50) NOT NULL,
  `work_line` int(11) DEFAULT NULL,
  `work_amount` int(11) DEFAULT NULL,
  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_name`,`file_name`,`logic_name`,`user_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.calling_table 구조 내보내기
CREATE TABLE IF NOT EXISTS `calling_table` (
  `project_name` varchar(50) NOT NULL,
  `user_name` varchar(50) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `calling_file` varchar(255) NOT NULL,
  `calling_logic` varchar(255) NOT NULL,
  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_name`,`user_name`,`file_name`,`calling_file`, `calling_logic`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.user_last_connection 구조 내보내기
CREATE TABLE IF NOT EXISTS `user_last_connection` (
  `slack_code` varchar(50) NOT NULL,
  `last_connection` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`slack_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.user_last_connection 구조 내보내기
CREATE TABLE IF NOT EXISTS `lock_try_history` (
  `project_name` varchar(50) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `slack_code` varchar(50) NOT NULL,
  `delete_time` int(11) DEFAULT NULL,
  `lock_try_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.edit_amount 구조 내보내기
CREATE TABLE IF NOT EXISTS `edit_amount` (
  `project_name` varchar(50) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `user_name` varchar(50) NOT NULL,
  `total_plus` int(11) DEFAULT 0,
  `total_minus` int(11) DEFAULT 0,
  `git_diff_code` longtext,
  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_name`,`file_name`,`user_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.file_information 구조 내보내기
CREATE TABLE IF NOT EXISTS `file_information` (
  `project_name` varchar(50) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `total_lines` int(11) DEFAULT 0,
  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_name`,`file_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.git_log_name_only 구조 내보내기
CREATE TABLE IF NOT EXISTS `git_log_name_only` (
  `project_name` varchar(50) NOT NULL,
  `commit_order` int(11),
  `file_list` JSON,
  PRIMARY KEY (`project_name`,`commit_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.git_log_name_only 구조 내보내기
CREATE TABLE IF NOT EXISTS `last_commit_date` (
  `project_name` varchar(50) NOT NULL,
  `last_commit_date` varchar(50),
  PRIMARY KEY (`project_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.git_log_name_only 구조 내보내기
CREATE TABLE IF NOT EXISTS `prediction_list` (
  `project_name` varchar(50) NOT NULL,
  `user_name` varchar(50) NOT NULL,
  `target` varchar(50) NOT NULL,
  `other_name` varchar(50) NOT NULL,
  `order_num` int(11) NOT NULL,
  `file_name` varchar(50) NOT NULL,
  `percentage` int(11) NOT NULL,
  `related_file_list` text NOT NULL,
  PRIMARY KEY (`project_name`, `user_name`, `target`, `order_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;