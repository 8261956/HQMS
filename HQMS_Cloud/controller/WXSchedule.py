# -*- coding: utf-8 -*-

import json
import sys
import traceback
import datetime
import web
from common import DBBase as DB
from common.func import packOutput, checkSession, str2List
from WXQueue import WXQueue
from WXWorker import WXWorker


class WXSchedule(object):

    db = DB.hqms_cloud_db()

    def __init__(self, hospital_name):
        self.hospitalName = hospital_name

    def getScheduleByQueue(self, queue_filter):
        """根据队列关键字获取专家队列的排班信息"""

        result = {}
        current_date = datetime.date.today()
        startTime = (current_date - datetime.timedelta(current_date.weekday())).strftime("%Y-%m-%d")
        endTime = (current_date + datetime.timedelta(6 - current_date.weekday())).strftime("%Y-%m-%d")

        # 获取队列基础信息
        queue_info = WXQueue(self.hospitalName).getQueueInfoByFilter(queue_filter)
        if not queue_info:
            return result

        # 获取专家信息
        workerID = str2List(queue_info.pop("workerLimit"))[0]
        workerInfo = WXWorker(self.hospitalName).getWorkerInfo(workerID)

        # 获取队列排班信息
        where = "queue=\'%s\' AND workDate BETWEEN \'%s\' AND \'%s\'" % (
            queue_filter, startTime, endTime)
        schedule_list = self.db.select("schedule", where=where)
        schedule = []
        for item in schedule_list:
            if item["onDuty"] == 1:
                tmp = {
                    "onDuty": item["onDuty"],
                    "workDate": item["workDate"],
                    "workTime": item["workTime"],
                    "weekday": item["weekday"]
                }
                schedule.append(tmp)

        result.update(queue_info)
        result.update({"schedule": schedule, "workerInfo": workerInfo})
        return result


    def getScheduleByWorkerID(self, workerID):
        """根据专家ID获取排班信息"""

        queue_filter = WXQueue(self.hospitalName).getQueueFilterByWorkerID(workerID)
        result = {"list": []}

        for filter in queue_filter:
            queue_schedule = self.getScheduleByQueue(filter)
            result["list"].append(queue_schedule)

        return result

    def getScheduleByDepartment(self, department):
        """根据科室名称获取排班信息"""

        queue_filter = WXQueue(self.hospitalName).getQueueFilterByDepartment(department)
        result = {"list": []}

        for filter in queue_filter:
            queue_schedule = self.getScheduleByQueue(filter)
            result["list"].append(queue_schedule)

        return result


class WXScheduleInterface(object):

    support_action = {
        "getScheduleByWorkerID": "getScheduleByWorkerID",
        "getScheduleByDepartment": "getScheduleByDepartment"
    }

    def POST(self, input_data):
        data = json.loads(web.data())

        token = data.pop("token", None)
        if token:
            if not checkSession(token):
                return packOutput({}, "401", "Token authority failed")
        action = data.pop("action", None)
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
            return packOutput({"errorInfo": str(e), "rescode": "500"},
                              code='500', errorInfo=errorInfo)

    def getScheduleByWorkerID(self, data):

        hospitalName = data.get("hospitalName", None)
        if hospitalName is None:
            raise Exception("hospital name required")

        workerID = data.get("workerID", None)
        if workerID is None:
            raise Exception("workerName required")

        schedule_info = WXSchedule(hospitalName).getScheduleByWorkerID(workerID)

        return schedule_info

    def getScheduleByDepartment(self, data):

        hospitalName = data.get("hospitalName", None)
        if hospitalName is None:
            raise Exception("hospital name required")

        department = data.get("department", None)
        if department is None:
            raise Exception("department required")

        schedule_info = WXSchedule(hospitalName).getScheduleByDepartment(department)

        return schedule_info