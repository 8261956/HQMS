# -*- coding: utf-8 -*-

import datetime
import json
import sys
import traceback
import re
import web
from common import DBBase as DB
from common.func import packOutput, checkSession, APIRequest


class WXQueue(object):

    db = DB.hqms_cloud_db()

    def __init__(self, hospital_name):
        self.hospitalName = hospital_name

    def getQueueInfo(self, stationID, queueID):
        """根据分诊台和队列, 获取队列当天排队信息"""

        where_dict = {"hospitalName": self.hospitalName,
                      "stationID": stationID, "queueID": queueID}
        queue = self.db.select("queueInfo", where=where_dict).first()

        currentVisitor = None
        waitNum = 0
        finishNum = 0
        visitors = self.db.select("visitorsInfo", where=where_dict)
        for visitor in visitors:
            if visitor.localStatus == "doing":
                currentVisitor = visitor.visitorID[-5:]
            elif visitor.localStatus in ("waiting", "unactive",
                                       "unactivewaiting"):
                waitNum += 1
            elif visitor.localStatus == "finish":
                finishNum += 1

        result = {}
        result.update({
            "id": queue.queueID,
            "name": queue.name,
            "stationID": queue.stationID,
            "department": queue.department,
            "finishNum": finishNum,
            "waitNum": waitNum,
            "currentVisitor": currentVisitor
        })
        return result

    def getQueueFilterByDepartment(self, department):
        """根据科室，查询符合条件的队列关键字"""

        where_dict = {"hospitalName": self.hospitalName, "department": department}
        queue_list = self.db.select("queueInfo", where=where_dict)
        queue_filter = []
        for item in queue_list:
            filter = item["filter"]
            filter = re.findall(r'queue=\'(.*)\'', filter)
            filter = filter[0]
            queue_filter.append(filter)
        return queue_filter

    def getQueueFilterByWorkerID(self, workerID):
        """根据专家的workerID，查询符合条件的队列关键字"""

        where_dict = {"hospitalName": self.hospitalName, "workerLimit": workerID}
        queue_list = self.db.select("queueInfo", where=where_dict)
        queue_filter = []
        for item in queue_list:
            filter = item["filter"]
            filter = re.findall(r'queue=\'(.*)\'', filter)
            filter = filter[0]
            queue_filter.append(filter)
        return queue_filter

    def getQueueInfoByFilter(self, queue_filter):
        """根据队列关键字获取队列基础信息"""

        filter = "queue='%s'" % queue_filter
        where_dict = {"hospitalName": self.hospitalName, "filter": filter}
        queue_info = self.db.select("queueInfo", where=where_dict,
                                    what="queueID, name, stationID, filter, "
                                         "isExpert, department, "
                                         "workerLimit").first()
        return queue_info


class WXQueueInterface(object):

    support_action = {
        "getWXQueueInfo": "getWXQueueInfo"
    }

    db = DB.hqms_cloud_db()

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

    def getWXQueueInfo(self, data):
        """根据科室查询队列信息"""

        hospitalName = data.get("hospitalName", None)
        if hospitalName is None:
            raise Exception("hospital name required")

        stationID_list = []
        stations = self.db.select("stationSet", where={"hospitalName": hospitalName})
        for item in stations:
            stationID_list.append(item.stationID)


        department = data.get("department", "")
        where = {"hospitalName": hospitalName}
        if department and department != "":
            where = {"department": department}
        queue_list = self.db.select("queueInfo", where=where)

        result = {"num": 0, "list": []}
        for item in queue_list:
            stationID = item.stationID
            if stationID not in stationID_list:
                continue
            queueID = item.queueID
            wx_queue = WXQueue(hospitalName)
            queue_info = wx_queue.getQueueInfo(stationID, queueID)
            result["list"].append(queue_info)
        result["num"] = len(result["list"])

        return result
