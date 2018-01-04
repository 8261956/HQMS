# -*- coding: utf-8 -*-

import json
import os
import sys
import traceback
import web
from common.func import packOutput, checkSession
from common import DBBase as DB
from common import config as cfg

class SyncManager(object):

    db = DB.hqms_cloud_db()
    # db = DB.DBLocal_WX

    def syncVisitorsData(self, visitor_data_list):
        if not visitor_data_list:
            return
        hospitalName = visitor_data_list[0]["hospitalName"]
        self.db.delete("visitorsInfo", where={"hospitalName": hospitalName})
        try:
            self.db.multiple_insert("visitorsInfo", values=visitor_data_list)
        except:
            raise

    def syncQueueData(self, queue_data_list):
        if not queue_data_list:
            return

        hospitalName = queue_data_list[0]["hospitalName"]
        self.db.delete("queueInfo", where={"hospitalName": hospitalName})
        try:
            self.db.multiple_insert("queueInfo", values=queue_data_list)
        except:
            raise

    def syncWorkersData(self, worker_data_list):
        if not worker_data_list:
            return
        hospitalName = worker_data_list[0]["hospitalName"]
        self.db.delete("workers", where={"hospitalName": hospitalName})
        try:
            self.db.multiple_insert("workers", values=worker_data_list)
        except:
            raise

    def syncStationSetData(self, stationSet_data_list):
        if not stationSet_data_list:
            return

        hospitalName = stationSet_data_list[0]["hospitalName"]
        self.db.delete("stationSet", where={"hospitalName": hospitalName})
        try:
            self.db.multiple_insert("stationSet", values=stationSet_data_list)
        except:
            raise

    def syncScheduleData(self, schedule_data_list):
        if not schedule_data_list:
            return

        hospitalName = schedule_data_list[0]["hospitalName"]
        self.db.delete("schedule", where={"hospitalName": hospitalName})
        try:
            self.db.multiple_insert("schedule", values=schedule_data_list)
        except:
            raise

    def syncHospitalInfoData(self, hospitalInfo_data_list):
        if not hospitalInfo_data_list:
            return

        hospitalInfo = hospitalInfo_data_list[0]
        hospitalName = hospitalInfo["hospitalName"]
        where_dict = {"hospitalName": hospitalName}
        hospital = self.db.select("hospital", where=where_dict).first()

        try:
            if not hospital:
                self.db.insert("hospital", **hospitalInfo)
            else:
                self.db.update("hospital", where=where_dict, **hospitalInfo)
        except:
            raise



class SyncInterface(object):
    support_action = {
        "syncVisitorsData": "syncVisitorsData",
        "syncQueueData": "syncQueueData",
        "syncWorkersData": "syncWorkersData",
        "syncStationSetData": "syncStationSetData",
        "syncScheduleData": "syncScheduleData",
        "syncHospitalInfoData": "syncHospitalInfoData",
        "uploadAvatar": "uploadAvatar"
    }

    def POST(self, input_data):
        data = json.loads(web.data())

        token = data.pop("token", None)
        if token:
            if not checkSession(token):
                return packOutput({}, "401", "Token authority failed")
        action = data.pop("action", None)
        print action
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

    def syncVisitorsData(self, data):
        visitor_data_list = data.get("visitorsData", None)
        if visitor_data_list is None:
            raise Exception("visitor data required")
        if not isinstance(visitor_data_list, list):
            raise Exception("visitor data must be a list")

        result = {"result": ""}
        try:
            SyncManager().syncVisitorsData(visitor_data_list)
            result.update({"result": "success"})
        except:
            result.update({"result": "failed"})
        return result

    def syncQueueData(self, data):
        queue_data_list = data.get("queueData", None)
        if queue_data_list is None:
            raise Exception("queue data required")
        if not isinstance(queue_data_list, list):
            raise Exception("queue data must be a list")

        result = {"result": ""}
        try:
            SyncManager().syncQueueData(queue_data_list)
            result.update({"result": "success"})
        except:
            result.update({"result": "failed"})
        return result

    def syncWorkersData(self, data):
        worker_data_list = data.get("workersData", None)
        if worker_data_list is None:
            raise Exception("worker data required")
        if not isinstance(worker_data_list, list):
            raise Exception("worker data must be a list")

        # 更换医生的头像地址为微信云服务器上相应的地址
        for worker in worker_data_list:
            headPicPath = worker["headPic"]
            if not headPicPath:
                continue
            filename = os.path.basename(headPicPath)
            url_base = cfg.wx_upload_http_base
            worker["headPic"] = os.path.join(url_base, filename)

        result = {"result": ""}
        try:
            SyncManager().syncWorkersData(worker_data_list)
            result.update({"result": "success"})
        except:
            result.update({"result": "failed"})
        return result

    def syncStationSetData(self, data):
        station_data_list = data.get("stationSetData", None)
        if station_data_list is None:
            raise Exception("stationSet data required")
        if not isinstance(station_data_list, list):
            raise Exception("stationSet data must be a lists")

        result = {"result": ""}
        try:
            SyncManager().syncStationSetData(station_data_list)
            result.update({"result": "success"})
        except:
            result.update({"result": "failed"})
        return result

    def syncScheduleData(self, data):
        schedule_data_list = data.get("scheduleData", None)
        if schedule_data_list is None:
            raise Exception("schedule data required")
        if not isinstance(schedule_data_list, list):
            raise Exception("schedule data must be a list")

        result = {"result": ""}
        try:
            SyncManager().syncScheduleData(schedule_data_list)
            result.update({"result": "success"})
        except:
            result.update({"result": "failed"})

        return result

    def syncHospitalInfoData(self, data):
        hospitalInfo_data_list = data.get("hospitalInfoData", None)
        if hospitalInfo_data_list is None:
            raise Exception("hospitalInfo data required")
        if not isinstance(hospitalInfo_data_list, list):
            raise Exception("hospitalInfo data must be a list")

        result = {"result": ""}
        try:
            SyncManager().syncHospitalInfoData(hospitalInfo_data_list)
            result.update({"result": "success"})
        except:
            result.update({"result": "failed"})

        return result


class AvatarUploader(object):

    def POST(self, input_data):
        """上传医生头像"""

        file = web.input(image={})
        avatar = file["image"].file.read()
        filename = file["image"].filename
        filepath = os.path.join(cfg.headPicPath, filename)

        result = {"result": ""}
        try:
            if not os.path.exists(filepath):
                with open(filepath, 'wb') as f:
                    f.write(avatar)
            result.update({"result": "success"})
        except:
            result.update({"result": "failed"})

        return packOutput(result)