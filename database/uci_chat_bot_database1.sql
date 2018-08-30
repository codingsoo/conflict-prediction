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
  `project_name` varchar(50) DEFAULT NULL,
  `approved_file` varchar(50) DEFAULT NULL,
  KEY `인덱스 1` (`project_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.direct_conflict_table 구조 내보내기
CREATE TABLE IF NOT EXISTS `direct_conflict_table` (
  `project_name` varchar(50) NOT NULL,
  `file_name` varchar(50) NOT NULL,
  `logic1_name` varchar(50) NOT NULL,
  `logic2_name` varchar(50) NOT NULL,
  `user1_name` varchar(50) NOT NULL,
  `user2_name` varchar(50) NOT NULL,
  `alert_count` int(11) DEFAULT '1',
  `severity` int(11) DEFAULT '1',
  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_name`,`file_name`,`logic1_name`,`user1_name`,`user2_name`,`logic2_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.ignore_table 구조 내보내기
CREATE TABLE IF NOT EXISTS `ignore_table` (
  `project_name` varchar(50) NOT NULL,
  `slack_code` varchar(50) NOT NULL,
  `direct_ignore` int(11) NOT NULL DEFAULT '0',
  `indirect_ignore` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.indirect_conflict_table 구조 내보내기
CREATE TABLE IF NOT EXISTS `indirect_conflict_table` (
  `project_name` varchar(50) NOT NULL,
  `u` varchar(100) NOT NULL,
  `v` varchar(100) NOT NULL,
  `length` int(11) NOT NULL DEFAULT '0',
  `user1_name` varchar(50) NOT NULL,
  `user2_name` varchar(50) NOT NULL,
  `alert_count` int(11) NOT NULL DEFAULT '1',
  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.lock_list 구조 내보내기
CREATE TABLE IF NOT EXISTS `lock_list` (
  `project_name` varchar(50) DEFAULT NULL,
  `lock_file` varchar(50) DEFAULT NULL,
  `slack_code` varchar(50) DEFAULT NULL,
  `delete_time` int(11) DEFAULT NULL,
  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.logic_dependency 구조 내보내기
CREATE TABLE IF NOT EXISTS `logic_dependency` (
  `project_name` varchar(50) NOT NULL,
  `u` varchar(100) NOT NULL,
  `v` varchar(100) NOT NULL,
  `length` int(11) NOT NULL DEFAULT '0',
  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.user_table 구조 내보내기
CREATE TABLE IF NOT EXISTS `user_table` (
  `git_id` varchar(50) DEFAULT NULL,
  `slack_id` varchar(50) DEFAULT NULL,
  `slack_code` varchar(50) DEFAULT 'NULL'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 uci_chat_bot.working_table 구조 내보내기
CREATE TABLE IF NOT EXISTS `working_table` (
  `project_name` varchar(50) NOT NULL,
  `file_name` varchar(50) NOT NULL,
  `logic_name` varchar(50) NOT NULL,
  `user_name` varchar(50) NOT NULL,
  `work_line` int(11) DEFAULT NULL,
  `work_amount` int(11) DEFAULT NULL,
  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_name`,`file_name`,`logic_name`,`user_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
