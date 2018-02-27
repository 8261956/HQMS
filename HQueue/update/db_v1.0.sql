/*
Navicat MySQL Data Transfer

Source Server         : 192.168.17.184
Source Server Version : 50173
Source Host           : 192.168.17.184:3306
Source Database       : HisQueue_empty

Target Server Type    : MYSQL
Target Server Version : 50173
File Encoding         : 65001

Date: 2017-09-07 16:08:51
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `account`
-- ----------------------------
DROP TABLE IF EXISTS `account`;
CREATE TABLE `account` (
  `id` int(32) NOT NULL AUTO_INCREMENT,
  `stationID` int(32) NOT NULL,
  `user` text NOT NULL,
  `password` text NOT NULL,
  `type` text NOT NULL,
  `descText` text NOT NULL,
  PRIMARY KEY (`id`,`stationID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of account
-- ----------------------------

-- ----------------------------
-- Table structure for `caller`
-- ----------------------------
DROP TABLE IF EXISTS `caller`;
CREATE TABLE `caller` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `stationID` int(11) NOT NULL,
  `name` text NOT NULL,
  `ip` char(16) NOT NULL,
  `type` char(16) NOT NULL,
  `pos` text,
  `workerLimit` text,
  `workerOnline` char(50) DEFAULT NULL,
  `priorQueue` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of caller
-- ----------------------------

-- ----------------------------
-- Table structure for `callingRecord`
-- ----------------------------
DROP TABLE IF EXISTS `callingRecord`;
CREATE TABLE `callingRecord` (
  `id` int(32) NOT NULL AUTO_INCREMENT,
  `stationID` int(32) NOT NULL,
  `callerID` int(32) NOT NULL,
  `workerID` char(32) NOT NULL,
  `queueID` int(32) NOT NULL,
  `currentVisitorID` char(32) DEFAULT NULL,
  `currentVisitorName` char(32) DEFAULT NULL,
  `nextVisitorID` char(32) DEFAULT NULL,
  `nextVisitorName` char(32) DEFAULT NULL,
  `waitingNum` int(11) DEFAULT NULL,
  `showCnt` int(11) DEFAULT NULL,
  `soundOut` int(11) DEFAULT NULL,
  `soundText` char(100) DEFAULT NULL,
  `dateTime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of callingRecord
-- ----------------------------

-- ----------------------------
-- Table structure for `checkinDev`
-- ----------------------------
DROP TABLE IF EXISTS `checkinDev`;
CREATE TABLE `checkinDev` (
  `id` int(32) NOT NULL AUTO_INCREMENT,
  `deviceIP` char(50) NOT NULL,
  `stationID` int(32) NOT NULL,
  `lastDateTime` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of checkinDev
-- ----------------------------

-- ----------------------------
-- Table structure for `import_config`
-- ----------------------------
DROP TABLE IF EXISTS `import_config`;
CREATE TABLE `import_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(50) NOT NULL,
  `DBType` varchar(50) NOT NULL,
  `host` varchar(50) NOT NULL,
  `port` int(11) DEFAULT NULL,
  `user` varchar(50) NOT NULL,
  `passwd` varchar(255) NOT NULL,
  `charset` varchar(50) DEFAULT NULL,
  `DBName` varchar(50) DEFAULT NULL,
  `tableName` varchar(50) NOT NULL,
  `importSQL` varchar(255) DEFAULT NULL,
  `importWeeks` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of import_config
-- ----------------------------

-- ----------------------------
-- Table structure for `publish`
-- ----------------------------
DROP TABLE IF EXISTS `publish`;
CREATE TABLE `publish` (
  `id` int(32) NOT NULL AUTO_INCREMENT,
  `voiceFormate` char(100) NOT NULL,
  `displayFormate` char(100) NOT NULL,
  `deviceIP` char(50) DEFAULT NULL,
  `stationID` int(32) DEFAULT NULL,
  `soundTimes` int(11) DEFAULT NULL,
  `popupPeriod` int(11) DEFAULT NULL,
  `lastDateTime` datetime NOT NULL,
  `speed` int(3) DEFAULT NULL,
  `pitch` int(3) DEFAULT NULL,
  `volume` int(3) DEFAULT NULL,
  `speechState` char(4) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of publish
-- ----------------------------

-- ----------------------------
-- Table structure for `queue_machine`
-- ----------------------------
DROP TABLE IF EXISTS `queue_machine`;
CREATE TABLE `queue_machine` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `deviceIP` varchar(255) NOT NULL,
  `stationID` int(11) NOT NULL,
  `queueLimit` varchar(255) DEFAULT NULL,
  `supportFeature` varchar(255) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `subtitle` varchar(255) DEFAULT NULL,
  `footer1` varchar(255) DEFAULT NULL,
  `footer2` varchar(255) DEFAULT NULL,
  `styleID` int(11) NOT NULL,
  `lastDateTime` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ip` (`deviceIP`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of queue_machine
-- ----------------------------

-- ----------------------------
-- Table structure for `queueInfo`
-- ----------------------------
DROP TABLE IF EXISTS `queueInfo`;
CREATE TABLE `queueInfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `stationID` int(11) NOT NULL,
  `name` char(30) NOT NULL,
  `descText` char(60) DEFAULT NULL,
  `filter` char(100) NOT NULL,
  `scene` char(16) NOT NULL,
  `sceneID` int(11) NOT NULL,
  `activeLocal` int(11) NOT NULL,
  `rankWay` char(15) DEFAULT NULL,
  `orderAllow` int(11) NOT NULL,
  `workerOnline` text,
  `workerLimit` text,
  PRIMARY KEY (`id`,`stationID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of queueInfo
-- ----------------------------

-- ----------------------------
-- Table structure for `scene`
-- ----------------------------
DROP TABLE IF EXISTS `scene`;
CREATE TABLE `scene` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` char(32) NOT NULL,
  `descText` char(200) DEFAULT NULL,
  `activeLocal` int(8) NOT NULL,
  `orderAllow` int(8) NOT NULL,
  `rankWay` char(20) NOT NULL,
  `output` char(50) DEFAULT NULL,
  `delayTime` int(11) DEFAULT '0',
  `waitNum` int(11) DEFAULT '0',
  `passedWaitNum` int(5) DEFAULT '0',
  `reviewWaitNum` int(5) DEFAULT '0',
  `priorNum` int(5) DEFAULT '0',
  `workDays` int(5) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of scene
-- ----------------------------
INSERT INTO `scene` VALUES ('1', '常规', '常规场景，不需要本地激活，开放预约，使用登记时间进行排序，播报请**到**就诊', '0', '1', 'registTime', '就诊', '0', '0', '0', '0', '0', null);
INSERT INTO `scene` VALUES ('2', '智能', '常规场景，不需要本地激活，开放预约，使用登记时间进行排序,预约与普通按31比例分布，播报请**到**就诊', '0', '1', 'registTimeAndSmart', '就诊', '0', '0', '0', '0', '0', null);
INSERT INTO `scene` VALUES ('3', '序号', '常规场景，不需要本地激活，开放预约，使用序号进行排序,预约与普通按31比例分布，播报请**到**就诊', '0', '1', 'snumber', '就诊', '0', '0', '0', '0', '0', null);
INSERT INTO `scene` VALUES ('4', '药房', '药房场景，不需要本地激活，不开放预约，使用号码进行排序，播报请**到**取药', '0', '0', 'snumber', '取药', '0', '0', '0', '0', '0', null);

-- ----------------------------
-- Table structure for `schedule`
-- ----------------------------
DROP TABLE IF EXISTS `schedule`;
CREATE TABLE `schedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `queue` varchar(255) NOT NULL,
  `isExpert` tinyint(4) NOT NULL,
  `weekday` tinyint(4) NOT NULL,
  `workDate` date NOT NULL,
  `workTime` tinyint(4) NOT NULL,
  `onDuty` tinyint(4) NOT NULL,
  `workerID` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `queue_schedule` (`queue`,`workDate`,`workTime`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of schedule
-- ----------------------------

-- ----------------------------
-- Table structure for `schedule_temp`
-- ----------------------------
DROP TABLE IF EXISTS `schedule_temp`;
CREATE TABLE `schedule_temp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `queue` varchar(255) NOT NULL,
  `isExpert` tinyint(4) NOT NULL,
  `weekday` tinyint(4) NOT NULL,
  `workDate` date NOT NULL,
  `workTime` tinyint(4) NOT NULL,
  `onDuty` tinyint(4) NOT NULL,
  `workerID` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `queue_schedule` (`queue`,`workDate`,`workTime`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of schedule_temp
-- ----------------------------

-- ----------------------------
-- Table structure for `stationSet`
-- ----------------------------
DROP TABLE IF EXISTS `stationSet`;
CREATE TABLE `stationSet` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` char(20) NOT NULL,
  `descText` char(30) DEFAULT NULL,
  `DBType` char(15) DEFAULT NULL,
  `host` char(20) DEFAULT NULL,
  `port` char(15) DEFAULT NULL,
  `charset` char(15) DEFAULT NULL,
  `user` char(50) DEFAULT NULL,
  `passwd` char(50) DEFAULT NULL,
  `DBName` char(30) DEFAULT NULL,
  `tableName` char(30) DEFAULT NULL,
  `aliasName` char(20) DEFAULT NULL,
  `aliasAge` char(20) DEFAULT NULL,
  `aliasQueue` char(20) DEFAULT NULL,
  `aliasID` char(20) DEFAULT NULL,
  `aliasOrderDate` char(20) DEFAULT NULL,
  `aliasOrderTime` char(20) DEFAULT NULL,
  `aliasRegistDate` char(20) DEFAULT NULL,
  `aliasRegistTime` char(20) DEFAULT NULL,
  `aliasSnumber` char(20) DEFAULT NULL,
  `aliasVIP` char(20) DEFAULT NULL,
  `aliasOrderType` char(20) DEFAULT NULL,
  `aliasWorkerID` char(20) DEFAULT NULL,
  `aliasWorkerName` char(20) DEFAULT NULL,
  `aliasDepartment` char(20) DEFAULT NULL,
  `aliasDescText` char(20) DEFAULT NULL,
  `aliasStatus` char(20) DEFAULT NULL,
  `aliasCardID` char(20) DEFAULT NULL,
  `aliasPersonID` char(20) DEFAULT NULL,
  `aliasPhone` char(20) DEFAULT NULL,
  `renewPeriod` int(11) DEFAULT NULL,
  `queueList` text,
  `workerList` text,
  `callerList` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of stationSet
-- ----------------------------

-- ----------------------------
-- Table structure for `style`
-- ----------------------------
DROP TABLE IF EXISTS `style`;
CREATE TABLE `style` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `styleURL` varchar(255) NOT NULL,
  `previewURL` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of style
-- ----------------------------
INSERT INTO `style` VALUES ('1', '样式一', 'ticket/html/style1.html', 'ticket/img/style1.png');
INSERT INTO `style` VALUES ('2', '样式二', 'ticket/html/style2.html', 'ticket/img/style2.png');
INSERT INTO `style` VALUES ('3', '样式三', 'ticket/html/style3.html', 'ticket/img/style3.png');

-- ----------------------------
-- Table structure for `visitor_backup_data`
-- ----------------------------
DROP TABLE IF EXISTS `visitor_backup_data`;
CREATE TABLE `visitor_backup_data` (
  `id` char(30) NOT NULL,
  `stationID` int(11) NOT NULL,
  `queueID` int(11) NOT NULL,
  `name` char(20) NOT NULL,
  `age` int(11) DEFAULT NULL,
  `queue` char(20) NOT NULL,
  `snumber` int(11) DEFAULT NULL,
  `orderDate` date DEFAULT NULL,
  `orderTime` time DEFAULT NULL,
  `registDate` date DEFAULT NULL,
  `registTime` time DEFAULT NULL,
  `VIP` int(11) DEFAULT NULL,
  `orderType` int(11) DEFAULT NULL,
  `workerID` char(30) DEFAULT NULL,
  `workerName` char(20) DEFAULT NULL,
  `descText` char(60) DEFAULT NULL,
  `status` char(10) DEFAULT NULL,
  `department` text,
  `cardID` char(50) DEFAULT NULL,
  `personID` char(50) DEFAULT NULL,
  `phone` char(15) DEFAULT NULL,
  `localStatus` char(30) DEFAULT NULL,
  `logID` int(64) NOT NULL AUTO_INCREMENT,
  `workStartTime` datetime DEFAULT NULL,
  `workEndTime` datetime DEFAULT NULL,
  PRIMARY KEY (`logID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of visitor_backup_data
-- ----------------------------

-- ----------------------------
-- Table structure for `visitor_local_data`
-- ----------------------------
DROP TABLE IF EXISTS `visitor_local_data`;
CREATE TABLE `visitor_local_data` (
  `id` char(32) NOT NULL,
  `activeLocal` int(10) DEFAULT NULL,
  `activeLocalTime` datetime DEFAULT NULL,
  `locked` int(10) DEFAULT NULL,
  `prior` int(10) DEFAULT NULL,
  `vip` int(10) DEFAULT NULL,
  `stationID` int(11) NOT NULL,
  `queueID` int(32) NOT NULL,
  `history` text,
  `originLevel` int(11) DEFAULT NULL,
  `originScore` int(32) DEFAULT NULL,
  `finalScore` int(32) DEFAULT NULL,
  `status` char(15) DEFAULT NULL,
  `name` char(32) DEFAULT NULL,
  `workerOnline` char(32) DEFAULT NULL,
  `historyPath` text,
  `workStartTime` datetime DEFAULT NULL,
  `workEndTime` datetime DEFAULT NULL,
  `registDate` date DEFAULT NULL,
  PRIMARY KEY (`id`,`stationID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of visitor_local_data
-- ----------------------------

-- ----------------------------
-- Table structure for `visitor_source_data`
-- ----------------------------
DROP TABLE IF EXISTS `visitor_source_data`;
CREATE TABLE `visitor_source_data` (
  `id` char(30) NOT NULL,
  `stationID` int(11) NOT NULL,
  `queueID` int(11) NOT NULL,
  `name` char(20) NOT NULL,
  `age` int(11) DEFAULT NULL,
  `queue` char(20) NOT NULL,
  `snumber` int(11) DEFAULT NULL,
  `orderDate` date DEFAULT NULL,
  `orderTime` time DEFAULT NULL,
  `registDate` date DEFAULT NULL,
  `registTime` time DEFAULT NULL,
  `VIP` int(11) DEFAULT NULL,
  `orderType` int(11) DEFAULT NULL,
  `workerID` char(30) DEFAULT NULL,
  `workerName` char(20) DEFAULT NULL,
  `descText` char(60) DEFAULT NULL,
  `status` char(10) DEFAULT NULL,
  `department` text,
  `cardID` char(50) DEFAULT NULL,
  `personID` char(50) DEFAULT NULL,
  `phone` char(15) DEFAULT NULL,
  PRIMARY KEY (`id`,`stationID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of visitor_source_data
-- ----------------------------

-- ----------------------------
-- Table structure for `visitors`
-- ----------------------------
DROP TABLE IF EXISTS `visitors`;
CREATE TABLE `visitors` (
  `id` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `age` int(11) DEFAULT NULL,
  `queue` varchar(64) NOT NULL,
  `snumber` int(32) DEFAULT NULL,
  `orderDate` date DEFAULT NULL,
  `orderTime` time DEFAULT NULL,
  `registDate` date DEFAULT NULL,
  `registTime` time DEFAULT NULL,
  `emergency` int(11) DEFAULT NULL,
  `orderType` int(11) DEFAULT NULL,
  `workerID` varchar(30) DEFAULT NULL,
  `workerName` varchar(64) DEFAULT NULL,
  `descText` varchar(255) DEFAULT NULL,
  `status` varchar(10) DEFAULT NULL,
  `department` varchar(64) DEFAULT NULL,
  `cardID` varchar(64) DEFAULT NULL,
  `personID` varchar(64) DEFAULT NULL,
  `phone` varchar(32) DEFAULT NULL,
  `reserve1` varchar(64) DEFAULT NULL,
  `reserve2` varchar(64) DEFAULT NULL,
  `reserve3` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of visitors
-- ----------------------------
INSERT INTO `visitors` VALUES ('D0011', '内测1', '31', 'AM_US', '3', '2017-03-31', '00:13:12', '2017-03-31', '23:13:44', '0', '1', 'D002', '王医生', '胃痛', '已预约', '内科', null, null, null, null, null, null);

-- ----------------------------
-- Table structure for `workers`
-- ----------------------------
DROP TABLE IF EXISTS `workers`;
CREATE TABLE `workers` (
  `id` char(30) NOT NULL,
  `stationID` int(11) DEFAULT '0',
  `name` char(20) NOT NULL,
  `user` char(30) DEFAULT NULL,
  `password` char(30) DEFAULT NULL,
  `title` char(10) DEFAULT NULL,
  `department` char(20) DEFAULT NULL,
  `descText` char(100) DEFAULT NULL,
  `speciality` varchar(255) DEFAULT NULL,
  `headPic` char(100) DEFAULT NULL,
  `callerList` char(20) DEFAULT NULL,
  `status` char(20) DEFAULT NULL,
  `source` char(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of workers
-- ----------------------------

-- ----------------------------
-- View structure for `viewtest`
-- ----------------------------
DROP VIEW IF EXISTS `viewtest`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `viewtest` AS select `visitors`.`name` AS `name` from `visitors` ;
