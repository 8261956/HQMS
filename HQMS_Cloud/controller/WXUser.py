# -*- coding: utf-8 -*-

import datetime
import json
import re
import sys
import traceback
import web
from common import DBBase as DB
from common import config as cfg
from common.func import packOutput, checkSession, getToken, APIRequest


def verify_personID(personID):
    """根据校验码验证身份证号是否输入正确，并且是否可以注册。"""

    c = 0
    for (d, p) in zip(map(int, personID[:-1]), range(17, 0, -1)):
        c += d * (2 ** p) % 11
    check_code = '10X98765432'[c % 11]
    if personID[-1] != check_code:
        raise ValueError("Invalid personID")

    db_wx = DB.hqms_cloud_db()
    user = db_wx.select("users", where={"personID": personID})
    if user:
        raise ValueError("personID already registered")


def verify_phone(phone):
    """验证手机号码是否合法，并且是否可以注册。"""

    pattern = re.compile(r'^1[34578]\d{9}$')
    match = pattern.search(phone)
    if not match:
        raise Exception("Invalid phone number")

    db_wx = DB.hqms_cloud_db()
    user = db_wx.select("users", where={"phone": phone})
    if user:
        raise Exception("phone already registered")


class WXUser(object):

    db = DB.hqms_cloud_db()

    def __init__(self, where_dict):

        if not where_dict:
            raise Exception("required at least one parameter ")
        user = self.db.select("users", where=where_dict).first()
        if not user:
            raise Exception("user not exists")

        self.uid = user.uid
        self.name = user.name
        self.phone = user.phone
        self.personID = user.personID
        self.cardID = user.cardID

    def getVisitorQueueInfo(self):
        """根据医保卡号获取患者的排队信息"""

        where_dict = {"cardID": self.cardID}
        visitors = self.db.select("visitorsInfo", where=where_dict)

        result = {"num": 0, "list": []}
        visitors = list(visitors)
        if not visitors:
            return result

        for visitor in visitors:
            hospitalName = visitor.hospitalName
            stationID = visitor.stationID
            queueID = visitor.queueID
            finalScore = visitor.finalScore
            localStatus = visitor.localStatus

            # 获得患者所在的队列信息
            where_dict = {"stationID": stationID, "queueID": queueID,
                          "hospitalName": hospitalName}
            queue_info = self.db.select("queueInfo", where=where_dict).first()

            status = "(\'waiting\', \'doing\', " \
                     "\'unactive\', \'unactivewaiting\')"
            sql = "SELECT COUNT(*) AS waitNum FROM visitorsInfo WHERE " \
                  "hospitalName = \'%s\' AND stationID = %s AND queueID = %s " \
                  "AND localStatus IN %s" \
                  % (hospitalName, stationID, queueID, status)
            if localStatus in ("waiting", "doing", "unactive",
                               "unactivewaiting"):
                sql += " AND finalScore <= %s" % finalScore

            waitNum = self.db.query(sql).first().waitNum
            waitTime = waitNum * 15

            queueInfo = {}
            queueInfo.update({
                "name": queue_info.name,
                "department": queue_info.department,
                "status": visitor.localStatus,
                "waitNum": waitNum,
                "waitTime": waitTime
            })
            result["list"].append(queueInfo)
        result.update({"num": len(result["list"])})
        return result

    def getUserInfo(self):
        user_info = self.to_json()
        return user_info

    def to_json(self):
        user_info = {
            "uid": self.uid,
            "name": self.name,
            "phone": self.phone,
            "personID": self.personID,
            "cardID": self.cardID
        }
        return user_info


class WXUserInterface(object):

    support_action = {
        "register": "register",
        "login": "login",
        "getUserInfo": "getUserInfo",
        "editUserInfo": "editUserInfo",
        "getUserQueueInfo": "getUserQueueInfo"
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

    def register(self, data):
        """注册微信程序用户
        :param data: name, phone, personID, cardID等构成的字典
        :return: 注册成功返回success和token，否则返回failed
        """

        name = data.get("name", None)
        phone = data.get("phone", None)
        personID = data.get("personID", None)
        cardID = data.get("cardID", None)
        if name is None:
            raise Exception("name required")
        if phone is None:
            raise Exception("phone required")
        if personID is None:
            raise Exception("personID required")
        if cardID is None:
            raise Exception("cardID required")

        verify_phone(phone)
        verify_personID(personID)

        registTime = datetime.datetime.now()
        userInfo = {
            "name": name,
            "phone": phone,
            "personID": personID,
            "cardID": cardID,
            "registTime": registTime
        }
        try:
            uid = self.db.insert("users", **userInfo)
            userInfo.update({"uid": uid})
            token = getToken(phone, cardID)
            result = {"result": "success", "token": token, "userInfo": userInfo}
        except:
            result = {"result": "failed"}

        return result

    def login(self, data):
        """微信用户登录
        :param data: phone和cardID构成的字典
        :return: 注册成功返回success和token，否则返回failed
        """

        phone = data.get("phone", None)
        cardID = data.get("cardID", None)
        if phone is None:
            raise Exception("phone number required")
        if cardID is None:
            raise Exception("cardID required")

        where = {"phone": phone, "cardID": cardID}
        userInfo = self.db.select("users", where=where).first()
        if userInfo:
            token = getToken(phone, cardID)
            result = {"result": "success", "token": token, "userInfo": userInfo}
        else:
            result = {"result": "failed"}

        return result

    def getUserInfo(self, data):
        """获取用户信息，可以使用uid, phone, cardID, personID查询。"""

        wx_user = WXUser(data)
        user_info = wx_user.getUserInfo()

        return user_info

    def editUserInfo(self, data):
        """编辑用户信息"""

        uid = data.get("uid", None)
        name = data.get("name", None)
        phone = data.get("phone", None)
        personID = data.get("personID", None)
        cardID = data.get("cardID", None)
        if uid is None:
            raise Exception("uid required")
        if name is None:
            raise Exception("name required")
        if phone is None:
            raise Exception("phone required")
        if personID is None:
            raise Exception("personID required")
        if cardID is None:
            raise Exception("cardID required")

        user = self.db.select("users", where={"uid": uid}).first()
        if phone != user.phone:
            verify_phone(phone)
        if personID != user.personID:
            verify_personID(personID)

        values = {
            "name": name,
            "phone": phone,
            "personID": personID,
            "cardID": cardID
        }

        where_dict = {"uid": uid}
        result = {}
        try:
            self.db.update("users", where=where_dict, **values)
            result.update({"result": "success"})
        except:
            result.update({"result": "failed"})

        return result

    def getUserQueueInfo(self, data):
        """根据条件查询注册用户的排队信息"""

        wx_user = WXUser(data)
        user_info = wx_user.to_json()
        queue_info = wx_user.getVisitorQueueInfo()
        result = {"userInfo": user_info, "queueInfo": queue_info}
        return result
