# -*- coding: utf-8 -*-

import json
import sys
import traceback
import re
import web
from common import DBBase as DB
from common.func import packOutput, checkSession


class WXWorker(object):

    db = DB.hqms_cloud_db()

    def __init__(self, hospital_name):
        self.hospital_name = hospital_name

    def fuzzySearchWorker(self, keyword, department=None):
        """根据姓名关键字，在API中获取医生信息"""

        where = {"hospitalName": self.hospital_name}
        if department:
            where.update({"department": department})
        workerList = self.db.select("workers", where=where,
                                       what="workerID AS id, name, department, "
                                            "title, descText, speciality, status")
        suggestions = []
        collections = []
        for item in workerList:
            worker = dict(item)
            collections.append(worker)
        pattern = '.*?'.join(keyword)
        regex = re.compile(pattern)
        for item in collections:
            match = regex.search(item["name"])
            if match:
                suggestions.append((len(match.group()), match.start(), item))
        workerInfo = [x for _, _, x in sorted(suggestions)]

        result = []
        for item in workerInfo:
            result.append(item)
        return result

    def getDepartment(self):
        """获取科室列表"""

        departments = self.db.select("workers", what="DISTINCT department",
                                        where={"hospitalName": self.hospital_name})
        result = []
        for item in departments:
            result.append(item["department"])

        return result

    def getWorkerInfo(self, workerID):
        """根据workerID获取医生信息"""

        where_dict = {"hospitalName": self.hospital_name, "workerID": workerID}
        worker = self.db.select("workers", where=where_dict,
                                what="name, title, descText, department, "
                                     "speciality, headPic"
                                ).first()
        return worker


class WXWorkerInterface(object):
    support_action = {
        "fuzzySearchWorker": "fuzzySearchWorker",
        "getDepartment": "getDepartment"
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

    def fuzzySearchWorker(self, data):

        hospitalName = data.get("hospitalName", None)
        if hospitalName is None:
            raise Exception("hospital name required")
        keyword = data.get("keyword", None)
        department = data.get("department", None)
        if keyword is None:
            raise Exception("keyword required")

        worker_info = WXWorker(hospitalName).fuzzySearchWorker(keyword, department)

        return worker_info

    def getDepartment(self, data):

        hospitalName = data.get("hospitalName", None)
        if hospitalName is None:
            raise Exception("hospital name required")

        department = WXWorker(hospitalName).getDepartment()
        return department