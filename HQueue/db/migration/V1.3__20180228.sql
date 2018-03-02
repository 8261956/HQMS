/* 
执行此SQL文件前请做好数据备份工作！！！ 
*/

-- ---------------
-- V1.3版本更新
-- ---------------

SET FOREIGN_KEY_CHECKS=0;

ALTER TABLE `HisQueue`.`account` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`caller` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`callingRecord` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`checkinDev` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`checkinDev` MODIFY COLUMN `lastDateTime` datetime(0) NULL DEFAULT NULL AFTER `stationID`;

ALTER TABLE `HisQueue`.`hospital` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`import_config` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`import_config` ADD COLUMN `importTime` datetime(0) NULL DEFAULT NULL AFTER `importWeeks`;

ALTER TABLE `HisQueue`.`import_config` ADD COLUMN `renewPeriod` int(32) NULL DEFAULT NULL AFTER `importTime`;

ALTER TABLE `HisQueue`.`import_config` MODIFY COLUMN `port` int(11) NULL DEFAULT NULL AFTER `host`;

ALTER TABLE `HisQueue`.`import_config` MODIFY COLUMN `importSQL` varchar(512) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `tableName`;

ALTER TABLE `HisQueue`.`import_config` MODIFY COLUMN `id` int(11) NOT NULL;

ALTER TABLE `HisQueue`.`import_config` DROP PRIMARY KEY;

ALTER TABLE `HisQueue`.`import_config` ADD PRIMARY KEY (`type`) USING BTREE;

ALTER TABLE `HisQueue`.`import_config` DROP COLUMN `id`;

ALTER TABLE `HisQueue`.`publish` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`publish` MODIFY COLUMN `voiceFormate` char(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `id`;

ALTER TABLE `HisQueue`.`publish` MODIFY COLUMN `displayFormate` char(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `voiceFormate`;

ALTER TABLE `HisQueue`.`publish` MODIFY COLUMN `lastDateTime` datetime(0) NULL DEFAULT NULL AFTER `popupPeriod`;

ALTER TABLE `HisQueue`.`queueInfo` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`queueInfo` ADD COLUMN `scene` char(16) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL AFTER `filter`;

ALTER TABLE `HisQueue`.`queueInfo` ADD COLUMN `activeLocal` int(11) NOT NULL AFTER `sceneID`;

ALTER TABLE `HisQueue`.`queueInfo` ADD COLUMN `rankWay` char(15) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `activeLocal`;

ALTER TABLE `HisQueue`.`queueInfo` MODIFY COLUMN `orderAllow` int(11) NOT NULL AFTER `rankWay`;

ALTER TABLE `HisQueue`.`queue_machine` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`queue_machine` MODIFY COLUMN `lastDateTime` datetime(0) NULL DEFAULT NULL AFTER `styleID`;

ALTER TABLE `HisQueue`.`scene` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`scene` MODIFY COLUMN `passedWaitNum` int(5) NULL DEFAULT 0 AFTER `waitNum`;

ALTER TABLE `HisQueue`.`scene` MODIFY COLUMN `reviewWaitNum` int(5) NULL DEFAULT 0 AFTER `passedWaitNum`;

ALTER TABLE `HisQueue`.`scene` MODIFY COLUMN `priorNum` int(5) NULL DEFAULT 0 AFTER `reviewWaitNum`;

ALTER TABLE `HisQueue`.`scene` MODIFY COLUMN `InsertPassedSeries` int(5) NULL DEFAULT NULL AFTER `priorNum`;

ALTER TABLE `HisQueue`.`scene` MODIFY COLUMN `InsertPassedInterval` int(5) NULL DEFAULT NULL AFTER `InsertPassedSeries`;

ALTER TABLE `HisQueue`.`scene` MODIFY COLUMN `InsertReviewSeries` int(5) NULL DEFAULT NULL AFTER `InsertPassedInterval`;

ALTER TABLE `HisQueue`.`scene` MODIFY COLUMN `InsertReviewInterval` int(5) NULL DEFAULT NULL AFTER `InsertReviewSeries`;

ALTER TABLE `HisQueue`.`scene` MODIFY COLUMN `InsertPriorSeries` int(5) NULL DEFAULT NULL AFTER `InsertReviewInterval`;

ALTER TABLE `HisQueue`.`scene` MODIFY COLUMN `InsertPriorInterval` int(5) NULL DEFAULT NULL AFTER `InsertPriorSeries`;

ALTER TABLE `HisQueue`.`scene` MODIFY COLUMN `workDays` int(5) NULL DEFAULT NULL AFTER `InsertPriorInterval`;

ALTER TABLE `HisQueue`.`schedule` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`schedule_temp` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`schedule_temp` MODIFY COLUMN `isExpert` tinyint(4) NOT NULL AFTER `queue`;

ALTER TABLE `HisQueue`.`stationSet` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`stationSet` ADD COLUMN `importSource` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `DBType`;

ALTER TABLE `HisQueue`.`stationSet` MODIFY COLUMN `id` int(32) NOT NULL FIRST;

ALTER TABLE `HisQueue`.`stationSet` MODIFY COLUMN `name` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL AFTER `id`;

ALTER TABLE `HisQueue`.`stationSet` MODIFY COLUMN `descText` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `name`;

ALTER TABLE `HisQueue`.`stationSet` MODIFY COLUMN `DBType` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `descText`;

ALTER TABLE `HisQueue`.`stationSet` MODIFY COLUMN `id` int(32) NOT NULL AUTO_INCREMENT FIRST;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `host`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `port`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `charset`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `user`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `passwd`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `DBName`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `tableName`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasName`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasAge`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasQueue`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasID`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasOrderDate`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasOrderTime`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasRegistDate`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasRegistTime`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasSnumber`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasVIP`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasOrderType`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasWorkerID`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasWorkerName`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasDepartment`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasDescText`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasStatus`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasCardID`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasPersonID`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `aliasPhone`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `renewPeriod`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `queueList`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `workerList`;

ALTER TABLE `HisQueue`.`stationSet` DROP COLUMN `callerList`;

ALTER TABLE `HisQueue`.`style` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`visitor_backup_data` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`visitor_backup_data` ADD COLUMN `activeLocal` int(11) NULL DEFAULT NULL AFTER `workEndTime`;

ALTER TABLE `HisQueue`.`visitor_backup_data` ADD COLUMN `activeLocalTime` datetime(0) NULL DEFAULT NULL AFTER `activeLocal`;

ALTER TABLE `HisQueue`.`visitor_backup_data` ADD COLUMN `locked` int(11) NULL DEFAULT NULL AFTER `activeLocalTime`;

ALTER TABLE `HisQueue`.`visitor_backup_data` ADD COLUMN `localVip` int(11) NULL DEFAULT NULL AFTER `locked`;

ALTER TABLE `HisQueue`.`visitor_backup_data` ADD COLUMN `prior` int(11) NULL DEFAULT NULL AFTER `localVip`;

ALTER TABLE `HisQueue`.`visitor_backup_data` ADD COLUMN `originScore` int(32) NULL DEFAULT NULL AFTER `prior`;

ALTER TABLE `HisQueue`.`visitor_backup_data` ADD COLUMN `finalScore` int(32) NULL DEFAULT NULL AFTER `originScore`;

ALTER TABLE `HisQueue`.`visitor_backup_data` ADD COLUMN `workerOnline` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `finalScore`;

ALTER TABLE `HisQueue`.`visitor_backup_data` MODIFY COLUMN `id` char(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL FIRST;

ALTER TABLE `HisQueue`.`visitor_backup_data` MODIFY COLUMN `orderDate` datetime(0) NULL DEFAULT NULL AFTER `snumber`;

ALTER TABLE `HisQueue`.`visitor_backup_data` MODIFY COLUMN `orderTime` datetime(0) NULL DEFAULT NULL AFTER `orderDate`;

ALTER TABLE `HisQueue`.`visitor_backup_data` MODIFY COLUMN `registDate` datetime(0) NULL DEFAULT NULL AFTER `orderTime`;

ALTER TABLE `HisQueue`.`visitor_backup_data` MODIFY COLUMN `registTime` datetime(0) NULL DEFAULT NULL AFTER `registDate`;

ALTER TABLE `HisQueue`.`visitor_local_data` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`visitor_local_data` ADD COLUMN `property` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `registDate`;

ALTER TABLE `HisQueue`.`visitor_local_data` ADD COLUMN `reserve1` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `property`;

ALTER TABLE `HisQueue`.`visitor_local_data` ADD COLUMN `reserve2` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `reserve1`;

ALTER TABLE `HisQueue`.`visitor_local_data` ADD COLUMN `reserve3` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `reserve2`;

ALTER TABLE `HisQueue`.`visitor_local_data` ADD COLUMN `reserve4` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `reserve3`;

ALTER TABLE `HisQueue`.`visitor_local_data` ADD COLUMN `reserve5` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `reserve4`;

ALTER TABLE `HisQueue`.`visitor_local_data` MODIFY COLUMN `id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL FIRST;

ALTER TABLE `HisQueue`.`visitor_local_data` MODIFY COLUMN `status` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `finalScore`;

ALTER TABLE `HisQueue`.`visitor_local_data` MODIFY COLUMN `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `status`;

ALTER TABLE `HisQueue`.`visitor_local_data` MODIFY COLUMN `workerOnline` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `name`;

ALTER TABLE `HisQueue`.`visitor_local_data` MODIFY COLUMN `registDate` datetime(0) NULL DEFAULT NULL AFTER `workEndTime`;

ALTER TABLE `HisQueue`.`visitor_source_data` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`visitor_source_data` ADD COLUMN `rev1` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `phone`;

ALTER TABLE `HisQueue`.`visitor_source_data` ADD COLUMN `rev2` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `rev1`;

ALTER TABLE `HisQueue`.`visitor_source_data` ADD COLUMN `rev3` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `rev2`;

ALTER TABLE `HisQueue`.`visitor_source_data` ADD COLUMN `rev4` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `rev3`;

ALTER TABLE `HisQueue`.`visitor_source_data` ADD COLUMN `rev5` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `rev4`;

ALTER TABLE `HisQueue`.`visitor_source_data` ADD COLUMN `rev6` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `rev5`;

ALTER TABLE `HisQueue`.`visitor_source_data` MODIFY COLUMN `id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL FIRST;

ALTER TABLE `HisQueue`.`visitor_source_data` MODIFY COLUMN `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL AFTER `id`;

ALTER TABLE `HisQueue`.`visitor_source_data` MODIFY COLUMN `queue` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL AFTER `age`;

ALTER TABLE `HisQueue`.`visitor_source_data` MODIFY COLUMN `snumber` int(32) NULL DEFAULT NULL AFTER `queue`;

ALTER TABLE `HisQueue`.`visitor_source_data` MODIFY COLUMN `orderTime` datetime(0) NULL DEFAULT NULL AFTER `orderDate`;

ALTER TABLE `HisQueue`.`visitor_source_data` MODIFY COLUMN `registTime` datetime(0) NULL DEFAULT NULL AFTER `registDate`;

ALTER TABLE `HisQueue`.`visitor_source_data` MODIFY COLUMN `workerID` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `orderType`;

ALTER TABLE `HisQueue`.`visitor_source_data` MODIFY COLUMN `workerName` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `workerID`;

ALTER TABLE `HisQueue`.`visitor_source_data` MODIFY COLUMN `descText` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `workerName`;

ALTER TABLE `HisQueue`.`visitor_source_data` MODIFY COLUMN `status` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `descText`;

ALTER TABLE `HisQueue`.`visitor_source_data` MODIFY COLUMN `department` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `status`;

ALTER TABLE `HisQueue`.`visitor_source_data` MODIFY COLUMN `cardID` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `department`;

ALTER TABLE `HisQueue`.`visitor_source_data` MODIFY COLUMN `personID` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `cardID`;

ALTER TABLE `HisQueue`.`visitor_source_data` MODIFY COLUMN `phone` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `personID`;

ALTER TABLE `HisQueue`.`visitor_source_data` DROP PRIMARY KEY;

ALTER TABLE `HisQueue`.`visitor_source_data` ADD PRIMARY KEY (`id`) USING BTREE;

ALTER TABLE `HisQueue`.`visitor_source_data` DROP COLUMN `stationID`;

ALTER TABLE `HisQueue`.`visitor_source_data` DROP COLUMN `queueID`;

ALTER TABLE `HisQueue`.`visitors` ROW_FORMAT = Compact;

ALTER TABLE `HisQueue`.`visitors` MODIFY COLUMN `orderTime` datetime(0) NULL DEFAULT NULL AFTER `orderDate`;

ALTER TABLE `HisQueue`.`visitors` MODIFY COLUMN `registTime` datetime(0) NULL DEFAULT NULL AFTER `registDate`;

ALTER TABLE `HisQueue`.`workers` ROW_FORMAT = Compact;

CREATE ALGORITHM = UNDEFINED DEFINER = `root`@`%` SQL SECURITY DEFINER VIEW `HisQueue`.`visitor_view_data_new` AS select `s`.`id` AS `id`,`s`.`name` AS `name`,`s`.`age` AS `age`,`s`.`queue` AS `queue`,`s`.`snumber` AS `snumber`,`s`.`orderDate` AS `orderDate`,`s`.`orderTime` AS `orderTime`,`s`.`registDate` AS `registDate`,`s`.`registTime` AS `registTime`,`s`.`VIP` AS `VIP`,`s`.`orderType` AS `orderType`,`s`.`workerID` AS `workerID`,`s`.`workerName` AS `workerName`,`s`.`descText` AS `descText`,`s`.`status` AS `status`,`s`.`department` AS `department`,`s`.`cardID` AS `cardID`,`s`.`personID` AS `personID`,`s`.`phone` AS `phone`,`s`.`rev1` AS `rev1`,`s`.`rev2` AS `rev2`,`s`.`rev3` AS `rev3`,`s`.`rev4` AS `rev4`,`s`.`rev5` AS `rev5`,`s`.`rev6` AS `rev6`,`l`.`id` AS `lid`,`l`.`stationID` AS `stationID`,`l`.`queueID` AS `queueID`,`l`.`activeLocal` AS `activeLocal`,`l`.`activeLocalTime` AS `activeLocalTime`,`l`.`workerOnline` AS `workerOnline`,`l`.`prior` AS `prior`,`l`.`locked` AS `locked`,`l`.`vip` AS `localVip`,`l`.`status` AS `localStatus`,`l`.`finalScore` AS `finalScore`,`l`.`originScore` AS `originScore`,`l`.`workStartTime` AS `workStartTime`,`l`.`workEndTime` AS `workEndTime`,`l`.`property` AS `property` from (`visitor_source_data` `s` join `visitor_local_data` `l` on((`s`.`id` = `l`.`id`))) order by `l`.`finalScore`;

CREATE ALGORITHM = UNDEFINED DEFINER = `root`@`%` SQL SECURITY DEFINER VIEW `HisQueue`.`visitor_view_local` AS select `visitor_local_data`.`id` AS `lid`,`visitor_local_data`.`stationID` AS `stationID`,`visitor_local_data`.`queueID` AS `queueID`,`visitor_local_data`.`activeLocal` AS `activeLocal`,`visitor_local_data`.`activeLocalTime` AS `activeLocalTime`,`visitor_local_data`.`workerOnline` AS `workerOnline`,`visitor_local_data`.`prior` AS `prior`,`visitor_local_data`.`locked` AS `locked`,`visitor_local_data`.`vip` AS `localVip`,`visitor_local_data`.`status` AS `localStatus`,`visitor_local_data`.`finalScore` AS `finalScore`,`visitor_local_data`.`originScore` AS `originScore`,`visitor_local_data`.`workStartTime` AS `workStartTime`,`visitor_local_data`.`workEndTime` AS `workEndTime`,`visitor_local_data`.`property` AS `property` from `visitor_local_data`;

CREATE ALGORITHM = UNDEFINED DEFINER = `root`@`%` SQL SECURITY DEFINER VIEW `HisQueue`.`visitor_view_data` AS select `s`.`id` AS `id`,`s`.`name` AS `name`,`s`.`age` AS `age`,`s`.`queue` AS `queue`,`s`.`snumber` AS `snumber`,`s`.`orderDate` AS `orderDate`,`s`.`orderTime` AS `orderTime`,`s`.`registDate` AS `registDate`,`s`.`registTime` AS `registTime`,`s`.`VIP` AS `VIP`,`s`.`orderType` AS `orderType`,`s`.`workerID` AS `workerID`,`s`.`workerName` AS `workerName`,`s`.`descText` AS `descText`,`s`.`status` AS `status`,`s`.`department` AS `department`,`s`.`cardID` AS `cardID`,`s`.`personID` AS `personID`,`s`.`phone` AS `phone`,`s`.`rev1` AS `rev1`,`s`.`rev2` AS `rev2`,`s`.`rev3` AS `rev3`,`s`.`rev4` AS `rev4`,`s`.`rev5` AS `rev5`,`s`.`rev6` AS `rev6`,`l`.`lid` AS `lid`,`l`.`stationID` AS `stationID`,`l`.`queueID` AS `queueID`,`l`.`activeLocal` AS `activeLocal`,`l`.`activeLocalTime` AS `activeLocalTime`,`l`.`workerOnline` AS `workerOnline`,`l`.`prior` AS `prior`,`l`.`locked` AS `locked`,`l`.`localVip` AS `localVip`,`l`.`localStatus` AS `localStatus`,`l`.`finalScore` AS `finalScore`,`l`.`originScore` AS `originScore`,`l`.`workStartTime` AS `workStartTime`,`l`.`workEndTime` AS `workEndTime`,`l`.`property` AS `property` from (`visitor_source_data` `s` join `visitor_view_local` `l` on((`s`.`id` = `l`.`lid`))) order by `l`.`finalScore`;

SET FOREIGN_KEY_CHECKS=1;