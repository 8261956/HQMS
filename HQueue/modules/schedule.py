# -*- coding: utf-8 -*-

import sys, json, re, copy, datetime, time, traceback
import web
from common.func import packOutput, str2List, list2Str, convertDBConfig, multiple_insert_sql
from queueInfo import QueueInfoInterface
from HQueue.DBIO import DBBase as DB


class ScheduleInterface(object):

    support_action = {
        "getQueueSchedule": "getQueueSchedule",
        "getStationSchedule": "getStationSchedule",
        "addSchedule": "addSchedule",
        "editSchedule": "editSchedule",
        "deleteSchedule": "deleteSchedule",
        "fuzzySearchSchedule": "fuzzySearchSchedule",
        "getConfig": "getConfig",
        "testSource": "testSource",
        "testSourceConfig": "testSourceConfig",
        "importSchedule": "importSchedule",
        "getExpertSchedule": "getExpertSchedule"
    }
    # 排班信息循环次数
    repeat_count = 4

    # 排班信息循环一次的间隔
    repeat_interval = 7

    # 数据库配置项
    db_paras = ("DBType", "host", "port", "user", "passwd", "DBName", "charset", "tableName")

    # SQL语句配置项
    sql_paras = ("queue", "isExpert", "workDate", "workTime", "weekday", "onDuty", "workerID", "importWeeks")


    def POST(self, inputData):
        data = json.loads(web.data())

        token = data.pop("token", None)
        action = data.pop("action", None)
        if token is None and action != "getExpertSchedule":
            return packOutput({}, code='400', errorInfo='token required')
        if action is None:
            return packOutput({}, code='400', errorInfo='action required')
        if action not in self.support_action:
            return packOutput({}, code='400', errorInfo='unsupported action')

        try:
            result = getattr(self, self.support_action[action])(data)
            return packOutput(result)
        except Exception as e:
            exc_traceback = sys.exc_info()[2]
            errorInfo = traceback.format_exc(exc_traceback)
            return packOutput({"errorInfo": str(e), "rescode": "500"}, code='500', errorInfo=errorInfo)

    def getQueueSchedule(self, data):
        stationID = data.get("stationID", None)
        queueID = data.get("queueID", None)
        if queueID is None:
            raise Exception("[ERR]: queueID required")
        startTime = data.get("startTime", None)
        endTime = data.get("endTime", None)
        if not startTime or not endTime:
            raise Exception("[ERR]: startTime or endTime required")
        if endTime < startTime:
            raise Exception("[ERR]: endTime should larger than startTime")

        queueInfo = QueueInfoInterface().getInfo({"stationID": stationID, "id": queueID})
        queue = queueInfo["filter"]

        try:
            self.autoGenSchedule(startTime, endTime)
        except:
            raise

        scheduleList = DB.DBLocal.select("schedule", where="queue=$queue AND workDate BETWEEN $startTime AND $endTime",
                                         vars={"queue": queue, "startTime": startTime, "endTime": endTime})
        schedule = []
        isExpert = None
        for item in scheduleList:
            tmp = {}
            scheduleTempList = DB.DBLocal.select("schedule_temp", where={"queue": item["queue"],
                                                                      "workDate": item["workDate"].strftime("%Y-%m-%d"),
                                                                      "workTime": item["workTime"]})
            if len(scheduleTempList) > 0:
                schedule_temp = scheduleTempList[0]
                item = self._cmpOnDuty(item, schedule_temp)
            tmp["workDate"] = item["workDate"]
            tmp["workTime"] = item["workTime"]
            tmp["weekday"] = item["weekday"]
            tmp["onDuty"] = item["onDuty"]
            tmp["workerID"] = str2List(item["workerID"])
            isExpert = item["isExpert"]
            schedule.append(tmp)
        result = {}
        result["stationID"] = queueInfo["stationID"]
        result["queueID"] = queueID
        result["name"] = queueInfo["name"]
        result["filter"] = queue
        #TODO： 专家队列信息是否和队列信息放在一起
        result["isExpert"] = isExpert
        result["schedule"] = schedule
        return result

    def getStationSchedule(self, data):
        stationID = data.get("stationID", None)
        startTime = data.get("startTime", None)
        endTime = data.get("endTime", None)
        if not startTime or not endTime:
            raise Exception("[ERR]: startTime or endTime required")
        if endTime < startTime:
            raise Exception("[ERR]: endTime should larger than startTime")
        pageNum = data.get("pageNum", None)
        pageSize = data.get("pageSize", None)

        where = None
        if stationID is not None and stationID != "":
            where = {}
            where.update({"stationID": stationID})
        else:
            stationList = DB.DBLocal.select("stationSet", what="id")
            stationIDList = []
            for item in stationList:
                stationIDList.append(item["id"])
            if stationIDList:
                stationIDList = list2Str(stationIDList)
                where = "stationID IN ({0})".format(stationIDList)

        tmp = DB.DBLocal.select("queueInfo", where=where)
        count = len(tmp)

        if pageNum and pageSize:
            if not isinstance(pageSize, int) or not isinstance(pageSize, int):
                raise Exception("[ERR]: pagination parameters should be int")
            queueList = DB.DBLocal.select("queueInfo", what="id", where=where,
                                          limit=pageSize, offset=(pageNum-1)*pageSize)
        else:
            queueList = DB.DBLocal.select("queueInfo", what="id", where=where)

        list = []
        for item in queueList:
            data.update({"queueID": item["id"]})
            schedule = self.getQueueSchedule(data)
            list.append(schedule)
        result = {}
        result["list"] = list
        result["count"] = count
        return result

    def addSchedule(self, data):
        scheduleList = data.get("scheduleList")
        schedule_values = []
        queue_workers = []
        for schedule in scheduleList:
            # 获取某个队列需要插入数据库的所有数据，以及添加到该队列的医生
            stationID = schedule.get("stationID")
            queueID = schedule.get("queueID")
            schedule_value, workers = self.convertSchedule(schedule)
            schedule_values.extend(schedule_value)
            schedule_values = sorted(schedule_values, key=lambda value: (value["queue"], value["workDate"]))
            queue_workers.append({"stationID": stationID, "queueID": queueID, "workers": workers})

        try:
            start = time.time()
            DB.DBLocal.multiple_insert("schedule", values=schedule_values)
            print "TIME COST FOR INSERT SCHEDULES: {0} ms".format((time.time() - start) * 1000)
            for item in queue_workers:
                QueueInfoInterface().updateWorkerLimit(item)
        except:
            raise
        else:
            result = {}
            result["result"] = "success"
            return result

    def editSchedule(self, data):
        scheduleList = data.get("scheduleList")
        schedule_values = []
        schedule_temp_values = []
        queue_workers = []

        # 生成可以插入数据库的排班数据，以及医生更新列表数据
        for schedule in scheduleList:
            schedule_value, schedule_temp_value, workers = self.convertSchedule(schedule)
            schedule_values.extend(schedule_value)
            schedule_temp_values.extend(schedule_temp_value)
            schedule_values = sorted(schedule_values, key=lambda value: (value["queue"], value["workDate"]))
            schedule_temp_values = sorted(schedule_temp_values, key=lambda value: (value["queue"], value["workDate"]))
            queue_workers.append(workers)

        try:
            start = time.time()
            if schedule_values:
                schedule_sql = multiple_insert_sql("schedule", schedule_values)
                DB.DBLocal.query(schedule_sql)
            if schedule_temp_values:
                schedule_temp_sql = multiple_insert_sql("schedule_temp", schedule_temp_values)
                DB.DBLocal.query(schedule_temp_sql)
            print "TIME COST FOR UPDATE SCHEDULES: {0} ms".format((time.time() - start) * 1000)
        except:
            raise
        else:
            result = {}
            result["result"] = "success"
            return result

    def convertSchedule(self, schedules):
        """将JSON格式的排班数据转换为可以插入数据库的数据

        JSON格式的排班数据：某分诊台某队列一周、二周或四周的排班数据。
        经过转换后，默认可以得到这个队列四周的排班记录，可以直接插入数据库
        """

        stationID = schedules.get("stationID")
        queueID = schedules.get("queueID")
        isExpert = schedules.get("isExpert")
        schedule = schedules.get("schedule")
        queueInfo = QueueInfoInterface().getInfo({"stationID": stationID, "id": queueID})
        queue = queueInfo["filter"]
        max_date = DB.DBLocal.select("schedule", what="MAX(workDate) as max_date")[0]["max_date"]
        schedule_value = []
        schedule_temp_value = []
        workers = {"stationID": stationID, "queueID": queueID, "workers": []}
        for item in schedule:
            date = datetime.datetime.strptime(item.get("workDate"), "%Y-%m-%d")
            weekday = item.get("weekday")
            time_state = item.get("workTime")
            onDuty = item.get("onDuty")
            workerList = item.get("workerID")
            isTemporary = item.get("isTemporary")
            value = {
                "queue": queue,
                "isExpert": isExpert,
                "workDate": date,
                "weekday": weekday,
                "workTime": time_state,
                "onDuty": onDuty,
                "workerID": list2Str(workerList)
            }

            # 计算某一条排班数据要循环的次数
            if max_date is None:
                count = self.repeat_count
            else:
                interval = int(datetime.datetime.strftime(max_date, '%W')) - int(datetime.datetime.strftime(date, '%W'))
                if interval in range(self.repeat_count):
                    count = interval + 1
                else:
                    count = self.repeat_count

            # 获取排班信息以几周为最小编辑单位
            edit_period = self._getImportWeeks()

            # 根据循环次数生成多条数据
            for i in range(0, count, edit_period):
                value_copy = copy.deepcopy(value)
                start_date = date + datetime.timedelta(self.repeat_interval*i)
                value_copy.update({"workDate": start_date})
                schedule_info = DB.DBLocal.select("schedule", where="queue=$queue AND workDate=$workDate AND workTime=$workTime",
                                                  vars={"queue": queue, "workDate": start_date, "workTime": time_state})
                # 如果是临时更改数据，则保存到临时排班表中
                if isTemporary:
                    if i == 0:
                        schedule_temp_value.append(copy.deepcopy(value_copy))
                    if len(schedule_info) == 0:
                        value_copy.update({"onDuty": 0})
                    else:
                        continue
                else:
                    if len(schedule_info) > 0:
                        value_copy = self._cmpOnDuty(value_copy, schedule_info[0])
                schedule_value.append(value_copy)

            for worker in workerList:
                if worker not in workers["workers"]:
                    workers["workers"].append(worker)

        return schedule_value, schedule_temp_value, workers

    def deleteSchedule(self, data):
        stationID = data.get("stationID", None)
        if stationID is None:
            raise Exception("[ERR]: stationID required")
        queueID = data.get("queueID", None)
        if queueID is None:
            raise Exception("[ERR]: queueID required")
        date = data.get("workDate", None)
        if date is None:
            raise Exception("[ERR]: date required")
        weekday = data.get("weekday", None)
        if weekday is None:
            raise Exception("[ERR]: weekday required")
        isTemporary = data.get("isTemporary", 0)

        queueInfo = QueueInfoInterface().getInfo({"stationID": stationID, "id": queueID})
        queue = queueInfo["filter"]

        if isTemporary == 0:
            DB.DBLocal.delete("schedule", where="queue=$queue AND weekday=$weekday AND workDate>=$workDate",
                              vars={"queue": queue, "weekday": weekday, "workDate": date})
        else:
            DB.DBLocal.delete("schedule", where="queue=$queue AND workDate=$workDate",
                              vars={"queue": queue, "workDate": date})

        result = {}
        result["result"] = "success"
        return result

    def fuzzySearchSchedule(self, data):
        related_queue = QueueInfoInterface().fuzzySearchQueue(data)
        suggestions = []
        for item in related_queue:
            stationID = item.get("stationID")
            queueID = item.get("id")
            startTime = data.get("startTime")
            endTime  =data.get("endTime")
            result = self.getQueueSchedule({"stationID": stationID, "queueID": queueID,
                                            "startTime": startTime, "endTime": endTime})
            suggestions.append(result)
        return suggestions

    def _getImportWeeks(self):
        """获取排班信息最小导入周期"""

        import_config = DB.DBLocal.select("import_config", where={"type": "schedule"})
        if not import_config:
            edit_period = 1
        else:
            edit_period = int(import_config[0]["importWeeks"])

        return edit_period

    def getConfig(self, inputData):
        config, sql = self._getConfig()
        return config

    def _getConfig(self):
        configList = DB.DBLocal.select("import_config", where={"type": "schedule"})
        keys = self.db_paras + self.sql_paras
        config = dict.fromkeys(keys, "")
        config.update({"importWeeks": 1})
        sql = None
        if len(configList) == 0:
            pass
        else:
            configInfo = dict(configList[0])
            configInfo.pop("id")
            configInfo.pop("type")
            sql = configInfo.pop("importSQL")
            sql = re.sub(".*SELECT", '', sql)
            sql = re.sub("FROM.*", '', sql)
            sql = sql.strip()

            paras = sql.split(',')
            result = {}
            for item in paras:
                tmp = item.split("AS")
                value = tmp[0].strip()
                key = tmp[1].strip()
                result[key] = value

            configInfo.update(result)

            for key, value in configInfo.items():
                if config.has_key(key):
                    config[key] = value
                else:
                    continue
        return config, sql

    def getAliasSql(self, config):
        tableName = config.get("tableName")
        tmp = []
        for key, value in config.items():
            if key in self.sql_paras and value != "":
                para = "{0} AS {1}".format(value, key)
                tmp.append(para)

        sql_paras = ', '.join(tmp)
        sql = "(SELECT {0} FROM {1}) scheduleView".format(sql_paras, tableName)
        return sql

    def testSource(self, config):
        """测试数据源能否正常连接"""

        db_config = convertDBConfig(**config)
        result = {}
        try:
            if config["DBType"] == "mssql":
                DBSource = DB.MSSQLController(config).MSSQLDB
            else:
                DBSource = web.database(**db_config)
            tableName = config["tableName"]
            res = DBSource.select(tableName)
        except Exception,e:
            print Exception,":",e
            result.update({"result": "failed"})
        else:
            print "DBSource connect ok " + tableName
            config.update({"type": "schedule"})
            import_config = DB.DBLocal.select("import_config", where={"type": "schedule"})
            if len(import_config) == 0:
                DB.DBLocal.insert("import_config", **config)
            else:
                DB.DBLocal.update("import_config", where={"type": "schedule"}, **config)
            result.update({"result": "success"})

        return result

    def testSourceConfig(self, config):
        """测试数据源SQL语句能够执行成功"""

        db_config = convertDBConfig(**config)
        sql = self.getAliasSql(config)
        result = {"result": "success", "sql": sql}
        try:
            if config["DBType"] == "mssql":
                DBSource = DB.MSSQLController(config).MSSQLDB
            else:
                DBSource = web.database(**db_config)
            res = DBSource.where(sql)
        except Exception, e:
            print Exception, ":", e
            result.update({"result": "failed"})
        else:
            values = copy.deepcopy(config)
            for key, value in config.items():
                if key in self.sql_paras:
                    values.pop(key)
            values.update({"importSQL": sql, "type": "schedule"})
            import_config = DB.DBLocal.select("import_config", where={"type": "schedule"})
            if len(import_config) == 0:
                DB.DBLocal.insert("import_config", **values)
            else:
                DB.DBLocal.update("import_config", where={"type": "schedule"}, **values)
            return result

    def importSchedule(self, config):
        """导入排班信息

        排班信息导入支持导入1周、2周、4周的数据，在导入时需要确认数据源排班信息的周数
        是否和选择导入的周数相匹配。

        在导入时，导入数据会完全覆盖数据库中对应的数据。
        """

        db_config = convertDBConfig(**config)
        if config["DBType"] == 'mssql':
            DBSource = DB.MSSQLController(config).MSSQLDB
        else:
            DBSource = web.database(**db_config)

        # 导入数据的周数，默认1周，可选1周、2周、4周数据
        import_weeks = config.pop("importWeeks", 1)

        # 数据源连接测试
        connect_test = self.testSourceConfig(config)
        if connect_test["result"] == "failed":
            raise Exception("[ERR]: import failed, please check the config")
        else:
            sql = connect_test["sql"]

        tmp = DBSource.select(sql, what="MAX(workDate) as MAX_DATE, MIN(workDate) as MIN_DATE")[0]
        max_date = tmp["MAX_DATE"]
        min_date = tmp["MIN_DATE"]
        if not max_date or not min_date:
            # raise Exception("[ERR]: import failed, please check whether the source has {0} week(s) data".format(import_weeks))
            raise Exception("importWeeks error")
        # MSSQL 查询出来是Unicode，需要进行转换
        if isinstance(max_date, str) or isinstance(max_date, unicode):
            max_date = datetime.datetime.strptime(max_date, "%Y-%m-%d")
        if isinstance(min_date, str) or isinstance(min_date, unicode):
            min_date = datetime.datetime.strptime(min_date, "%Y-%m-%d")
        # 判断是否是最新的数据
        current_date = datetime.datetime.today()
        isNewData = int(datetime.datetime.strftime(current_date, '%W')) - int(datetime.datetime.strftime(min_date, '%W'))
        if isNewData !=0:
            raise Exception("importWeeks error")
        # 判断导入数据的周数和配置的导入周数是否相同
        interval = int(datetime.datetime.strftime(max_date, '%W')) - int(datetime.datetime.strftime(min_date, '%W'))
        count = interval + 1
        if count != import_weeks:
            # raise Exception("[ERR]: import failed, please check whether the source has {0} week(s) data".format(import_weeks))
            raise Exception("importWeeks error")

        # 数据源排班数据
        scheduleList = DBSource.select(sql)

        # 插入到排班表中的排班数据列表，可使用multiple_insert方法实现多条插入
        insert_items = []

        # 每个队列关键字对应的分诊台ID、队列ID、可登陆医生等信息
        queue_workers = []

        # 根据循环的次数，生成相应的排班数据
        for item in scheduleList:
            if config["DBType"] == "oracle":
                item = self.convertItem(item)
            for i in range(0, self.repeat_count, import_weeks):
                # 生成排班信息
                workDate = item["workDate"]
                if isinstance(workDate, str) or isinstance(workDate, unicode):
                    workDate = datetime.datetime.strptime(workDate, "%Y-%m-%d")
                date = workDate + datetime.timedelta(self.repeat_interval*i)
                item_copy = copy.deepcopy(item)
                item_copy["workDate"] = date
                insert_items.append(dict(item_copy))
                # 导入数据时也要覆盖临时调班数据
                schedule_temp = DB.DBLocal.select("schedule_temp", where={"queue": item_copy["queue"], "workTime": item_copy["workTime"],
                                                                          "workDate": item_copy["workDate"].strftime("%Y-%m-%d")})
                if len(schedule_temp) != 0:
                    DB.DBLocal.delete("schedule_temp", where={"queue": item_copy["queue"], "workTime": item_copy["workTime"],
                                                              "workDate": item_copy["workDate"].strftime("%Y-%m-%d")})

            # 生成每个队列的医生数据
            workers = str2List(item["workerID"])
            queue = item["queue"]
            try:
                queueInfo = QueueInfoInterface().getInfoByFilter({"queue": queue})
                worker_paras = {"stationID": queueInfo["stationID"], "queueID": queueInfo["id"], "workers": workers}
            except:
                continue
            if not queue_workers:
                queue_workers.append(worker_paras)
            else:
                for item in queue_workers:
                    if item["stationID"] == queueInfo["stationID"] and item["queueID"] == queueInfo["id"]:
                        item["workers"] = list(set(item["workers"] + workers))
                        break
                else:
                    queue_workers.append(worker_paras)

        insert_items = sorted(insert_items, key=lambda value: (value["queue"], value["workDate"]))

        try:
            start = time.time()
            # 批量插入或者更新排班数据
            if insert_items:
                insert_sql = multiple_insert_sql("schedule", insert_items)
                DB.DBLocal.query(insert_sql)

            print "Worker: {0}".format(queue_workers)
            # 更新每个队列可登陆医生
            for item in queue_workers:
                QueueInfoInterface().updateWorkerLimit(item)
            # 如果导入成功，将import_weeks写入数据库配置中
            DB.DBLocal.update("import_config", where={"type": "schedule"}, importWeeks=import_weeks)
        except:
            raise
        else:
            print "IMPORT TIME COST: {0} ms".format((time.time() - start) * 1000)
            print "INSERT/UPDATE: {0}".format(len(insert_items))
            result = {}
            result["result"] = "success"
            result["successCount"] = len(insert_items)
            result["totalImport"] = len(insert_items)
            result["failedCount"] = result["totalImport"] - result["successCount"]
            return result

    def convertItem(self, item):
        """转换Oracle数据库的字段为小写"""

        result = {}
        for key in self.sql_paras:
            key_upper = key.upper()
            if key_upper in item:
                result.update({key: item[key_upper]})
        return result

    def _cmpOnDuty(self, sourceItem, localItem):
        source_onDuty = sourceItem["onDuty"]
        local_onDuty = localItem["onDuty"]

        # 本地数据加班 + 数据源不上班 = 数据源加班
        if local_onDuty == 3 and source_onDuty == 0:
            sourceItem["onDuty"] = 3
        # 本地数据加班 + 数据源上班 = 数据源上班
        elif local_onDuty == 3 and source_onDuty == 1:
            sourceItem["onDuty"] = 1
        # 本地数据请假 + 数据源不上班 = 数据源不上班
        elif local_onDuty == 2 and source_onDuty == 0:
            sourceItem["onDuty"] = 0
        # 本地数据请假 + 数据源上班 = 数据源请假
        elif local_onDuty == 2 and source_onDuty == 1:
            sourceItem["onDuty"] = 2

        return sourceItem

    def syncSchedule(self, inputData):
        """暂时不使用同步"""
        config, sql = self._getConfig()

        if sql is None:
            raise Exception("[ERR]: sync config not exists, please configure it")

        # 重新从数据源导入数据，进行同步。如果已经在排班管理中执行过一些临时调班，
        # 同步会根据情况确定是否执行更新操作。
        try:
            self.importSchedule(config)
        except:
            raise

        max_date = DB.DBLocal.select("schedule", what="MAX(date) as max_date")[0]["max_date"]
        current_date = datetime.datetime.today()
        interval = int(datetime.datetime.strftime(max_date, '%W')) - int(datetime.datetime.strftime(current_date, '%W'))
        import_weeks = config["importWeeks"]

        auto_insert_items = []
        if interval + 1 <= self.repeat_count - import_weeks:
            start_date = max_date - datetime.timedelta(import_weeks*self.repeat_interval-1)
            start_date = start_date.strftime("%Y-%m-%d")
            end_date = max_date.strftime("%Y-%m-%d")
            copyed_items = DB.DBLocal.select("schedule", where="date BETWEEN $start_date AND $end_date",
                                                  vars={"start_date": start_date, "end_date": end_date})

            for item in copyed_items:
                item["workDate"] += datetime.timedelta(import_weeks * self.repeat_interval)
                auto_insert_items.append(item)

        try:
            start = time.time()
            if auto_insert_items:
                auto_insert_sql = multiple_insert_sql("schedule", auto_insert_items)
                DB.DBLocal.query(auto_insert_sql)
        except:
            raise
        else:
            print "SYNC TIME COST: {0} ms".format((time.time() - start) * 1000)
            result = {}
            result["result"] = "success"
            return result

    def _autoGenSchedule(self, start_date, end_date):
        """根据查询的时间周期，确定是否自动生成排班数据"""

        current_date = datetime.datetime.today()
        current_week = int(datetime.datetime.strftime(current_date, '%W'))
        search_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        search_end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        search_week = int(datetime.datetime.strftime(search_start_date, '%W'))

        interval = search_week - current_week + 1
        importWeeks = self._getImportWeeks()
        copy_items = []
        if 0 < interval <= self.repeat_count:
            scheduleList = DB.DBLocal.select("schedule", where="workDate BETWEEN $start_date AND $end_date",
                                             vars={"start_date": start_date, "end_date": end_date})
            if len(scheduleList) == 0:
                copy_start_date = search_start_date - datetime.timedelta(self.repeat_interval*importWeeks)
                copy_end_date = search_end_date - datetime.timedelta(self.repeat_interval*importWeeks)
                copy_items = DB.DBLocal.select("schedule", where="workDate BETWEEN $start_date AND $end_date",
                                               vars={"start_date": copy_start_date, "end_date": copy_end_date})
                if len(copy_items) == 0:
                    copy_items = self._autoGenSchedule(copy_start_date.strftime("%Y-%m-%d"), copy_end_date.strftime("%Y-%m-%d"))

        return copy_items

    def autoGenSchedule(self, start_date, end_date):
        start = time.time()
        copy_items = self._autoGenSchedule(start_date, end_date)

        auto_gen_items = []
        importWeeks = self._getImportWeeks()
        for item in copy_items:
            copy_item = copy.deepcopy(item)
            # 删除主键id，否则会更新数据而不是复制数据
            copy_item.pop("id")
            copy_item["workDate"] += datetime.timedelta(self.repeat_interval*importWeeks)
            auto_gen_items.append(copy_item)

        try:
            if auto_gen_items:
                auto_gen_sql = multiple_insert_sql("schedule", auto_gen_items)
                DB.DBLocal.query(auto_gen_sql)
                print "AUTO GENERATE SCHEDULE TIME COST: {0} ms".format((time.time() - start) * 1000)
        except:
            raise
        else:
            result = {}
            result["result"] = "success"
            return result

    def _isExpertQueue(self, queueID):
        queueList = DB.DBLocal.select("queueInfo", where={"id": queueID})
        queueInfo = queueList[0]
        queue = queueInfo["filter"]
        sql = "SELECT * FROM (SELECT DISTINCT queue, isExpert FROM schedule) view WHERE view.queue='{0}'".format(queue)
        result = DB.DBLocal.query(sql)
        isExpert = result[0]["isExpert"]
        return isExpert

    def getExpertSchedule(self, data):
        """获取专家队列的上班情况"""

        stationID = data.get("stationID", None)
        where = None
        if stationID:
            where = {}
            where.update({"stationID": stationID})

        # 判断哪些队列属于专家队列
        queueID = data.get("queueID", None)
        if not queueID:
            queueID = []
            queueList = DB.DBLocal.select("queueInfo", what="id", where=where)
            for item in queueList:
                id = item["id"]
                try:
                    isExpert = self._isExpertQueue(id)
                except:
                    continue
                if isExpert:
                    queueID.append(id)
        if not isinstance(queueID, list):
            raise Exception("[ERR] queueID must be a list")

        isExpert = data.get("isExpert", 1)
        startTime = data.get("startTime", None)
        endTime = data.get("endTime", None)
        if not startTime or not endTime:
            current_date = datetime.datetime.today()
            startTime = (current_date - datetime.timedelta(current_date.weekday())).strftime("%Y-%m-%d")
            endTime = (current_date + datetime.timedelta(6 - current_date.weekday())).strftime("%Y-%m-%d")
        if endTime < startTime:
            raise Exception("[ERR]: endTime should larger than startTime")
        data.update({"isExpert": isExpert, "startTime": startTime, "endTime": endTime})

        result = {"list":[]}
        for item in queueID:
            data.update({"queueID": item})
            queueInfo = QueueInfoInterface().getInfo({"stationID":"", "id": item})
            queue_schedule = self.getQueueSchedule(data)
            schedule = queue_schedule.pop("schedule")

            workerID = None
            if queueInfo["workerLimit"]:
                workerID = str2List(queueInfo["workerLimit"])[0]
            tmp = []
            for s in schedule:
                if s["onDuty"] == 1:
                    s.pop("workerID")
                    tmp.append(s)

            queue_schedule.update({"schedule": tmp})
            if not queue_schedule["schedule"]:
                continue

            workerList = DB.DBLocal.select("workers", where={"id": workerID})
            workerInfo = {"name": "", "department": "", "title": "", "descText": "", "headPic": "", "speciality": ""}
            if len(workerList) !=0:
                worker = workerList[0]
                for key in workerInfo.keys():
                    if worker[key]:
                        workerInfo.update({key: worker[key]})
            queue_schedule.update({"workerInfo": workerInfo})
            if queue_schedule["workerInfo"]["name"]:
                result["list"].append(queue_schedule)

        return result
