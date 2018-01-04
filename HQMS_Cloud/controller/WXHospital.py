# -*- coding: utf-8 -*-

import json
import sys
import traceback
import web
from common import DBBase as DB
from common.func import packOutput, checkSession

class WXHospital(object):

    db = DB.hqms_cloud_db()

    def __init__(self, hospital_name):
        self.hospitalName = hospital_name
        self.id = None
        self.descText = None

    def getHospitalInfo(self):
        where_dict = {"hospitalName": self.hospitalName}
        hospital = self.db.select("hospital", where=where_dict).first()

        if hospital:
            self.id = hospital.id
            self.descText = hospital.descText
            result = self.to_dict()
        else:
            raise Exception("hospital %s not exists" % self.hospitalName)

        return result


    def to_dict(self):
        hospital_info = {
            "id": self.id,
            "hospitalName": self.hospitalName,
            "descText": self.descText
        }

        return hospital_info


class WXHospitalInterface(object):

    support_action = {
        "getHospitalList": "getHospitalList"
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

    def getHospitalList(self, data):
        """获取医院列表"""

        hospital_list = self.db.select("hospital")

        result = {"list": []}
        for hospital in hospital_list:
            hospital_name = hospital.hospitalName
            hospital_info = WXHospital(hospital_name).getHospitalInfo()
            result["list"].append(hospital_info)

        result.update({"num": len(result["list"])})

        return result