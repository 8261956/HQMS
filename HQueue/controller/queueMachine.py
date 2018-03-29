# -*- coding: utf-8 -*-

import web, datetime, json, sys, traceback
from common.func import packOutput, str2List, checkSession, list2Str
from mainStation import StationMainController
from queueInfo import QueueInfoInterface
import common.DBIO.DBBase as DB


class QueueMachineInterface(object):

    support_action = {
        "getReceipt": "getReceipt",
        "heartBeat": "heartBeat",
        "getListAll": "getListAll",
        "getInfo": "getInfo",
        "editQueueMachine": "editQueueMachine",
        "delQueueMachine": "delQueueMachine",
        "getAvaliableQueue": "getAvaliableQueue",
        "getStyleList": "getStyleList"
    }

    support_feature = {
        "showHomePage": 0,
        "showQueueList": 0,
        "allowNoCard": 0,
        "allowOrder": 0,
        "allowSwipe": 0
    }

    feature_keywords = {
        "showHomePage": "SHP",
        "showQueueList": "SQL",
        "allowNoCard": "ANC",
        "allowOrder": "AO",
        "allowSwipe": "AS"
    }

    def POST(self, inputData):
        data = json.loads(web.data())

        token = data.pop("token", None)
        if token:
            if checkSession(token) == False:
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
            return packOutput({"errorInfo": str(e), "rescode": "500"}, code='500', errorInfo=errorInfo)

    def getReceipt(self, data):
        """通过某一取号机打印小票"""

        stationID = data.get("stationID", None)
        if stationID is None:
            raise Exception("[ERR]: stationID required")
        queueID = data.get("queueID", None)
        if queueID is None:
            raise Exception("[ERR]: queueID required")
        taskType = data.get("taskType", None)
        if taskType is None:
            raise Exception("[ERR]: taskType required")
        cardID = data.get("cardID", None)
        if taskType == "RegistByCard" and cardID is None:
            raise Exception("[ERR]: cardID required when register by card")

        # 获取队列信息
        queueInfo = {}
        station = DB.DBLocal.select("stationSet", where={"id": stationID})
        if len(station) == 0:
            raise Exception("[ERR]: station {0} not exists".format(stationID))
        queue = DB.DBLocal.select("queueInfo", where={"stationID": stationID, "id": queueID})
        if len(queue) == 0:
            raise Exception("[ERR] queue {0} not exist at station {1}".format(queueID, stationID))
        queueInfo.update({
            "stationID": stationID,
            "stationName": station[0]["name"],
            "queueID": queueID,
            "queueName": queue[0]["name"]
        })

        # 获取患者信息
        visitorInfo = {}
        with DB.DBLocal.transaction():
            inputData = {"stationID": stationID, "queueID": queueID, "cardID": cardID}
            visitor = StationMainController()._addVisitor(inputData, action="self_pick_up")
        visitorInfo.update(visitor)

        # 获取小票打印样式信息
        styleInfo = {}
        queue_machine = self.getInfo({"stationID": stationID})
        tmp = queue_machine["printSettings"].pop("styleInfo")
        styleInfo.update(tmp)
        styleInfo.update(queue_machine["printSettings"])

        result = {"queueInfo": queueInfo, "visitorInfo": visitorInfo, "styleInfo": styleInfo}

        return result

    def heartBeat(self, data):
        """取号机心跳请求"""

        stationID = data.get("stationID", None)
        if not stationID:
            raise Exception("[ERR]: stationID required.")
        station = DB.DBLocal.select("stationSet", where="id=$id", vars={"id": stationID})
        if len(station) == 0:
            raise Exception("[ERR]: station not exists for id %s" % stationID)

        deviceIP = web.ctx.ip
        queue_machine = DB.DBLocal.select("queue_machine", where="deviceIP=$deviceIP", vars={"deviceIP": deviceIP})
        current_time = datetime.datetime.now()
        values = {
            "stationID": stationID,
            "deviceIP": deviceIP,
            "lastDateTime": current_time,
        }
        if len(queue_machine) == 0:
            values.update({
                "styleID": 1,
                "supportFeature": list2Str([value for value in self.feature_keywords.values()])
            })
            DB.DBLocal.insert("queue_machine", **values)
        else:
            if queue_machine[0]["stationID"] != stationID:
                values.update({"queueLimit": ""})
            DB.DBLocal.update("queue_machine", where="deviceIP=$deviceIP", vars={"deviceIP": deviceIP}, **values)

        Date = current_time.date().strftime("%Y-%m-%d")
        time = current_time.time().strftime("%H:%M:%S")
        result = {"Date": Date, "time": time}
        return result

    def queueMachineStatus(self, dict):
        """判断取号机的在线情况"""

        id = dict.get("id", None)
        if id is None:
            raise Exception("[ERR]: id required.")
        lastDateTime = dict.pop("lastDateTime", None)
        if lastDateTime is None:
            raise Exception("[ERR]: lastDateTime required for queue_machine %s" % id)
        now = datetime.datetime.now()
        try:
            interval = (now - lastDateTime).seconds
        except:
            raise Exception("[ERR]: Invalid lastDateTime for queue_machine %s" % id)
        if interval >= 20:
            dict["status"] = "offline"
        else:
            dict["status"] = "online"
        return dict

    def getListAll(self, data):
        sql = "SELECT q.id, q.deviceIP AS ip, q.queueLimit, q.lastDateTime, q.stationID, s.name AS stationName " \
              "FROM queue_machine q INNER JOIN stationSet s ON q.stationID = s.id"
        queue_machine_list = DB.DBLocal.query(sql)
        num = len(queue_machine_list)
        result = {"num": num, "list": []}
        for queue_machine in queue_machine_list:
            queueLimit = queue_machine["queueLimit"]
            if queueLimit is None:
                queue_machine["queueLimit"] = []
            else:
                queue_machine["queueLimit"] = str2List(queue_machine["queueLimit"])
            out = self.queueMachineStatus(queue_machine)
            result["list"].append(out)

        return result

    def getInfo(self, data):
        """获取某个取号机的详细信息"""

        stationID = data.get("stationID", None)
        if stationID is None:
            raise Exception("[ERR]: stationID required for queue_machine")
        where = {"stationID": stationID}
        id = data.get("id", None)
        if id is None:
            where.update({"deviceIP": web.ctx.ip})
        else:
            where.update({"id": id})

        queue_machine_list = DB.DBLocal.select("queue_machine", where=where)
        queue_machine = queue_machine_list[0]
        for key, value in queue_machine.items():
            if value is None:
                queue_machine.update({key:""})

        result = {}

        # 取号机选择的队列信息
        queueLimit = str2List(queue_machine["queueLimit"])
        queue_machine["queueLimit"] = []
        for queueID in queueLimit:
            try:
                queueInfo = QueueInfoInterface().getInfo({"stationID": stationID, "id": queueID})
            except:
                continue
            else:
                queue_machine["queueLimit"].append({"queueID": queueInfo["id"], "name": queueInfo["name"]})

        # 取号机支持的特性
        supportFeature = str2List(queue_machine.pop("supportFeature"))
        queue_machine["supportFeature"] = {}
        for key, value in self.support_feature.items():
            keyword = self.feature_keywords[key]
            if keyword in supportFeature:
                queue_machine["supportFeature"].update({key: 1})
            else:
                queue_machine["supportFeature"].update({key: value})

        # 取号机打印设置项
        printSettings = {}
        printSettings["title"] = queue_machine.pop("title")
        printSettings["subtitle"] = queue_machine.pop("subtitle")
        printSettings["footer1"] = queue_machine.pop("footer1")
        printSettings["footer2"] = queue_machine.pop("footer2")

        styleID = queue_machine.pop("styleID", 1)
        styleList = DB.DBLocal.select("style", where={"id": styleID})
        printSettings["styleInfo"] = {"id": "", "name": "", "styleURL": "", "previewURL": ""}
        for item in styleList:
            printSettings["styleInfo"] = item

        queue_machine["printSettings"] = printSettings


        queue_machine = self.queueMachineStatus(queue_machine)
        queue_machine.update({"queueNum": len(queue_machine["queueLimit"])})
        result.update(queue_machine)
        return result

    def editQueueMachine(self, data):
        """编辑一个取号机的信息"""

        stationID = data.get("stationID", None)
        if stationID is None:
            raise Exception("[ERR]: stationID required to edit queueMachine")
        id = data.get("id", None)
        if id is None:
            raise Exception("[ERR]: id required to edit queueMachine")
        queueLimit = data.get("queueLimit", None)
        if queueLimit and not isinstance(queueLimit, list):
            raise Exception("[ERR]: queueLimit must be a list")

        supportFeature = []
        for key in self.support_feature.keys():
            keyword = self.feature_keywords[key]
            value = data.pop(key, None)
            if value:
                supportFeature.append(keyword)
        data.update({"supportFeature": supportFeature})

        values = {}
        for key, value in data.items():
            if value is not None:
                if key == "queueLimit":
                    value = list2Str(value)
                if key == "supportFeature":
                    value = list2Str(value)
                values.update({key: value})

        result = {}
        try:
            DB.DBLocal.update("queue_machine", where={"stationID": stationID, "id": id}, **values)
        except:
            raise
        else:
            result.update({"result": "success"})
            return result

    def delQueueMachine(self, data):
        """删除一个取号机"""

        stationID = data.get("stationID", None)
        if stationID is None:
            raise Exception("[ERR]: stationID required to delete queue machine")
        id = data.get("id", None)
        if id is None:
            raise Exception("[ERR]: id required to delete queue machine")

        queue_machine = self.getInfo(data)
        if queue_machine["status"] == "online":
            raise Exception("[ERR]: queue machine {0} is online, you can't delete")

        result = {}
        try:
            DB.DBLocal.delete("queue_machine", where={"stationID": stationID, "id": id})
            result.update({"result": "success"})
        except:
            result.update({"result": "failed"})

        return result

    def getAvaliableQueue(self, data):
        stationID = data.get("stationID", None)
        if stationID is None:
            raise Exception("[ERR]: stationID required")

        queueList = DB.DBLocal.select("queueInfo", where={"stationID": stationID}, what="id")
        queueIDList = []
        for item in queueList:
            queueIDList.append(item["id"])

        choseQueueList = DB.DBLocal.select("queue_machine", where={"stationID": stationID}, what="queueLimit")
        choseQueueIDList = []
        for item in choseQueueList:
            queueLimit = str2List(item["queueLimit"])
            for queueID in queueLimit:
                if queueID not in choseQueueIDList:
                    choseQueueIDList.append(queueID)
        choseQueueIDList = map(int, choseQueueIDList)

        avaliableQueue = [item for item in queueIDList if item not in choseQueueIDList]
        result = {"list": []}
        for item in avaliableQueue:
            try:
                queueInfo = QueueInfoInterface().getInfo({"stationID": stationID, "id": item})
            except:
                pass
            else:
                result["list"].append({"queueID": queueInfo["id"], "name": queueInfo["name"]})
        result["num"] = len(result["list"])
        return result

    def getStyleList(self, data):
        """获取打印样式表"""

        styleList = DB.DBLocal.select("style")
        result = []
        for item in styleList:
            result.append(item)

        return result
