# -*- coding: utf-8 -*-

import sys
import json
import datetime
import traceback
import web
from common import DBBase as DB
from common.func import checkSession, packOutput
from worker import WorkerInterface
from schedule import ScheduleInterface


class WXInterface(object):

    support_action = {
        "getQueueInfo": "getQueueInfo",
        "getVisitorInfo": "getVisitorInfo",
        "getScheduleByWorkerID": "getScheduleByWorkerID",
        "getScheduleByDepartment": "getScheduleByDepartment",
        "fuzzySearchWorker": "fuzzySearchWorker",
        "getDepartment": "getDepartment",
        "getVisitorsData": "getVisitorsData",
        "getQueueData": "getQueueData",
        "getWorkersData": "getWorkersData",
        "getStationSetData": "getStationSetData",
        "getScheduleData": "getScheduleData",
        "getHospitalInfoData": "getHospitalInfoData",
        "getAvatarURL": "getAvatarURL"
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

    def getQueueInfo(self, data):
        """获取某个分诊台某个队列当天的排队信息"""
        print data
        stationID = data.get("stationID", None)
        queueID = data.get("queueID", None)
        registDate = data.get("registDate", None)
        if stationID is None:
            raise Exception("stationID required")
        if queueID is None:
            raise Exception("queueID required")
        if registDate is None:
            registDate = datetime.date.today().strftime("%Y-%m-%d")

        where_dict = {"stationID": stationID, "id": queueID}
        queue = DB.DBLocal.select("queueInfo", where=where_dict).first()
        if not queue:
            raise Exception("queue {0} not exists at station {1}".format(
                stationID, queueID))

        currentVisitor = None
        waitNum = 0
        finishNum = 0
        where_dict = {"stationID": stationID, "queueID": queueID,
                      "registDate": registDate}
        visitors = DB.DBLocal.select("visitor_local_data", where=where_dict)
        for visitor in visitors:
            if visitor.status == "doing":
                currentVisitor = visitor.id[-5:]
            elif visitor.status in ("waiting", "unactive"):
                waitNum += 1
            elif visitor.status == "finish":
                finishNum += 1

        queue_info = {
            "id": queue.id,
            "stationID": queue.stationID,
            "name": queue.name,
            "department": queue.department,
            "isExpert": queue.isExpert,
            "currentVisitor": currentVisitor,
            "waitNum": waitNum,
            "finishNum": finishNum
        }
        return queue_info

    # def getVisitorInfo(self, data):
    #     cardID = data.get("cardID", None)
    #     if cardID is None:
    #         raise Exception("cardID required")
    #     visitor_info = VisitorInterface().getVisitorInfoByCardID(cardID)
    #     return visitor_info

    def fuzzySearchWorker(self, data):
        """根据关键字，模糊查询医生信息。"""

        keyword = data.get("keyword", None)
        if keyword is None:
            raise Exception("keyword required")

        workerInterface = WorkerInterface()
        result = workerInterface.fuzzySearchWorker(data)

        return result

    def getDepartment(self, data):
        """查询科室信息"""

        result = WorkerInterface().getDepartment(data)
        return result

    def getScheduleByWorkerID(self, data):
        """根据专家名称获取排班信息"""

        workerID = data.get("workerID", None)
        if not workerID:
            raise Exception("required workerName")

        schedule = ScheduleInterface()
        result = schedule.getExpertSchedule({"workerID": workerID})

        return result

    def getScheduleByDepartment(self, data):
        """根据科室名称获取排班信息"""

        department = data.get("department", None)
        if not department:
            raise Exception("required department")

        schedule = ScheduleInterface()
        result = schedule.getExpertSchedule({"department": department})

        return result

    def getVisitorsData(self, data):
        hospital = DB.DBLocal.select("hospital").first()
        if not hospital:
            raise Exception("hospital detail required")
        hospitalName = hospital.name

        sql = "SELECT vs.id as visitorID, vs.stationID, vs.queueID, " \
              "vs.name, vs.queue, vs.snumber, vs.orderDate, vs.orderTime, " \
              "vs.registDate, vs.registTime, vs.VIP, vs.descText, vs.cardID, " \
              "vs.personID, vs.phone, vs.status, vs.department, vs.workerID, " \
              "vs.workerName, vl.originScore, vl.finalScore, vl.status as " \
              "localStatus, vl.workStartTime, vl.workEndTime FROM " \
              "visitor_source_data vs INNER JOIN visitor_local_data vl ON " \
              "vs.id = vl.id"

        visitorData = DB.DBLocal.query(sql)
        visitors_list = []
        for item in visitorData:
            item.update({"hospitalName": hospitalName})
            visitors_list.append(item)
        result = {"visitorsData": visitors_list, "num": len(visitors_list)}
        return result

    def getQueueData(self, data):
        hospital = DB.DBLocal.select("hospital").first()
        if not hospital:
            raise Exception("hospital detail required")
        hospitalName = hospital.name

        queueData = DB.DBLocal.select("queueInfo",
                                      what="id AS queueID, stationID, name, "
                                           "descText, filter, department, "
                                           "isExpert, workerOnline, "
                                           "workerLimit")
        queue_list = []
        for item in queueData:
            item.update({"hospitalName": hospitalName})
            queue_list.append(item)
        result = {"queueData": queue_list, "num": len(queue_list)}
        return result

    def getWorkersData(self, data):
        hospital = DB.DBLocal.select("hospital").first()
        if not hospital:
            raise Exception("hospital detail required")
        hospitalName = hospital.name

        workersData = DB.DBLocal.select("workers",
                                       what="id AS workerID, name, title, "
                                            "department, speciality, "
                                            "descText, status, headPic")
        workers_list = []
        for item in workersData:
            item.update({"hospitalName": hospitalName})
            workers_list.append(item)
        result = {"workersData": workers_list, "num": len(workers_list)}
        return result

    def getStationSetData(self, data):
        hospital = DB.DBLocal.select("hospital").first()
        if not hospital:
            raise Exception("hospital detail required")
        hospitalName = hospital.name

        stationSetData = DB.DBLocal.select("stationSet",
                                           what="id AS stationID, name, "
                                                "descText")
        stations_list = []
        for item in stationSetData:
            item.update({"hospitalName": hospitalName})
            stations_list.append(item)
        result = {"stationSetData": stations_list, "num": len(stations_list)}
        return result

    def getScheduleData(self, data):
        hospital = DB.DBLocal.select("hospital").first()
        if not hospital:
            raise Exception("hospital detail required")
        hospitalName = hospital.name

        current_date = datetime.date.today()
        startTime = (current_date - datetime.timedelta(current_date.weekday())).strftime("%Y-%m-%d")
        endTime = (current_date + datetime.timedelta(13-current_date.weekday())).strftime("%Y-%m-%d")

        try:
            ScheduleInterface().autoGenSchedule(startTime, endTime)
        except:
            raise

        where = "isExpert=%s AND workDate BETWEEN \'%s\' AND \'%s\'" % (1, startTime, endTime)
        scheduleData = DB.DBLocal.select("schedule", where=where,
                                         what="queue, isExpert, weekday, "
                                              "workDate, workTime, onDuty, "
                                              "workerID"
                                         )

        schedule_list = []
        for item in scheduleData:
            item.update({"hospitalName": hospitalName})
            schedule_list.append(item)

        result = {"scheduleData": schedule_list, "num": len(schedule_list)}
        return result

    def getHospitalInfoData(self, data):
        hospital_info = DB.DBLocal.select("hospital",
                                         what="name AS hospitalName, descText"
                                         ).first()
        hospitalData = []
        num = 0
        if hospital_info:
            hospitalData.append(hospital_info)
            num = 1

        result = {"hospitalInfoData": hospitalData, "num": num}
        return result

    def getAvatarURL(self, data):
        hospital = DB.DBLocal.select("hospital").first()
        if not hospital:
            raise Exception("hospital detail required")
        hospitalName = hospital.name

        workers = DB.DBLocal.select("workers", what="headPic")
        avatar_url_list = []
        for item in workers:
            avatar_url = item["headPic"]
            if avatar_url:
                avatar_url_list.append(avatar_url)

        result = {"hospitalName": hospitalName, "avatarURL": avatar_url_list,
                  "num": len(avatar_url_list)}

        return result
