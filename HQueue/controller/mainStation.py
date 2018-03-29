﻿# -*- coding: utf-8 -*-

import web, re, json, datetime, time
import common.func
import common.config as cfg
from common.func import packOutput, LogOut, checkPostAction,str2List,str2Json,json2Str
from queueData import QueueDataController, VisitorLocalInterface
from queueInfo import QueueInfoInterface
from scene import SceneInterface
import common.DBBase as DB


class StationMainController:
    support_action = {
        "getQueueListInfo" : "getQueueListInfo",
        "getQueueListAll" : "getQueueListAll",
        "getVisitorInfo" : "getVisitorInfo",
        "callPrepare" : "callPrepare",
        "visitorPropertySet" : "visitorPropertySet",
        "visitorTopSet" : "visitorTopSet",
        "visitorFuzzySearch" : "visitorFuzzySearch",
        "visitorMoveto" : "visitorMoveto",
        "visitorMoveby" : "visitorMoveby",
        "visitorSearch" : "visitorSearch",
        "addVisitor" : "addVisitor"
    }

    def POST(self,name):
        data = json.loads(web.data())
        return checkPostAction(self, data, self.support_action)

    def getQueueListInfo(self,inputData):
        stationID = inputData.get("stationID")
        station = DB.DBLocal.select("stationSet", where="id=$id", vars={"id": stationID})
        if len(station) == 0:
            raise Exception("[ERR]: station not exists.")
        list = QueueInfoInterface().getList({"stationID": stationID})
        ret = {"num": len(list) , "list": []}
        for item in list:
            queueInfo = {}
            queueInfo["id"] =  item["id"]
            queueInfo["name"] = item["name"]
            queueInfo["workerOnline"] = str2List(item["workerOnline"]) #支持多个医生同时在线看一个队列
            ret["list"].append(queueInfo)
        return ret

    def getQueueList(self,inputData):
        # 用于前端模版显示调用
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]
        qlist = DB.DBLocal.where('queueInfo', stationID = inputData["stationID"],id = queueID)
        if len(qlist) == 0:
            raise Exception("[ERR]: queue not exists")
        queue = qlist[0]
        ret = {"name": queue["name"], "workerOnline": queue["workerOnline"], "doingList":[], "waitingList":[],"finishList":[]}

        vList = DB.DBLocal.where("visitor_view_data",stationID = stationID,queueID = queueID)
        for item in vList:
            if item.localStatus == "doing":
                ret["doingList"].append(item)
            elif item.localStatus == "prepare":
                ret["waitingList"].append(item)
            elif item.localStatus == "waiting" :
                ret["waitingList"].append(item)
        return ret

    def getQueueListAll(self,inputData):
        #用于分诊台护士站调用
        useCache = inputData.get("useCache",True)
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]

        #if can get from Memcached
        key = "_getQueueListAll_stationID" + str(stationID)+"_queueID"+str(queueID)
        value = common.func.CachedGetValue(json.dumps(key))
        if useCache and value != False:
            return value

        ret = {"name": "", "workerOnline": [], "waitingList": [], "finishList": [] , "unactiveList" : []}
        queue = QueueInfoInterface().getInfo({"stationID": stationID, "id": queueID})
        ret.update({"name": queue["name"], "workerOnline": str2List(queue["workerOnline"])})

        vList = DB.DBLocal.where("visitor_view_data",stationID = stationID,queueID = queueID)
        for item in vList:
            if item.localStatus == "unactive" :
                ret["unactiveList"].append(item)
            elif item.localStatus == "doing":
                ret["waitingList"].append(item)
            elif item.localStatus == "prepare":
                ret["waitingList"].append(item)
            elif item.localStatus == "waiting" :
                ret["waitingList"].append(item)
            elif item.localStatus == "finish" :
                ret["finishList"].append(item)

        #缓存 value
        common.func.CahedSetValue(json.dumps(key),ret,2)
        return ret

    def getVisitorInfo(self,inputData):
        stationID = inputData["stationID"]
        id  = inputData["id"]
        vInfo = DB.DBLocal.where("visitor_view_data", stationID = stationID, id = id).first()
        if vInfo is None:
            raise Exception("[ERR]: visitor not exists. id:"+ id)
        return vInfo

    def callPrepare(self,data):
        stationID = data["stationID"]
        queueID = data["queueID"]
        visitor = {}
        vList = data["vid"]
        vManager = VisitorLocalInterface(stationID)
        for vid in vList:
            visitor["id"] = vid
            visitor["status"] = "prepare"
            visitor["dest"] = data["dest"]
            vManager.edit(visitor)
        return {"result" : "success"}

    def visitorPropertySet(self , data):
        stationID = data["stationID"]
        vManager = VisitorLocalInterface(stationID)
        vList = data["vid"]
        property = data["property"]
        value = data["value"]
        for vid in vList:
            vInfo = vManager.getInfo({"id":vid})
            if property == "passed":
                #TODO:  添加过号的排序设置
                vInfo["status"] = "passed" if value else "waiting"
            elif property == "finish":
                #TODO:  添加复诊的排序设置
                vInfo["status"] = "finish" if value else "waiting"
            elif property == "active":
                # TODO:  添加立即激活的排序设置
                vInfo["status"] = "waiting" if value else "unactive"
                if value:
                    vInfo["activeLocalTime"] = datetime.datetime.now()
            elif property == "urgentLev" :
                vInfo["urgentLev"] = value
            else:
                oldProperty = str2Json(vInfo["property"])
                oldProperty.update({property: value})
                vInfo["property"] = json2Str(oldProperty)
            vManager.edit(value)

    def visitorMoveto(self, data):
        QueueDataController().visitorMoveto(data)

    def visitorMoveby(self, data):
        QueueDataController().visitorMoveby(data)
        return

    def setVisitorStatus(self, inputData, action=None):
        stationID = inputData.get("stationID")
        queueID = inputData.pop("queueID")
        # 根据访客所处队列选择的策略信息，获取缓冲人数
        queueInfo = QueueInfoInterface().getInfo({"stationID": stationID, "id": queueID})
        sceneID = queueInfo["sceneID"]
        scene = SceneInterface().getSceneInfo({"sceneID": sceneID})
        if action == "pass" or action == "delay":
            waitNum = scene["passedWaitNum"]
        elif action == "review":
            waitNum = scene["reviewWaitNum"]
        else:
            # raise Exception("[ERR]: visitor status action not support.")
            waitNum = 0
        # 获取队列访客信息，如果等待队列中已经有过号或者复诊的访客，则调整缓冲人数
        fliter = "stationID=$stationID and queueID=$queueID and status=$status"
        visitorList = DB.DBLocal.select("visitor_local_data",
                                        where=fliter,
                                        vars={"stationID": stationID, "queueID": queueID, "status": "waiting" },
                                        order="finalScore, originScore")
        visitorNum = len(visitorList)

        if action == "pass" or action == "delay":
            InsertSeries = scene["InsertPassedSeries"]
            InsertInterval = scene["InsertPassedInterval"]
        elif action == "review":
            InsertSeries = scene["InsertReviewSeries"]
            InsertInterval = scene["InsertReviewInterval"]
        else:       #default val
            InsertSeries = 2
            InsertInterval = 3

        destPos,destScore = QueueDataController().getInsertPos(visitor=inputData,vList=visitorList,numNormal=InsertInterval,numHigher=InsertSeries,numWaitting=waitNum)
        inputData["finalScore"] = destScore

        return inputData

    def visitorSearch(self,inputData):
        visitor = self.getVisitorInfo(inputData)
        inputData["queueID"] = visitor["queueID"]
        visitor["waitingNum"] = QueueDataController().getWaitingNum(inputData)
        visitor["waitingTime"] = visitor["waitingNum"] * 15
        return  visitor

    def visitorFuzzySearch(self,inputData):
        stationID = inputData["stationID"]
        paraName = inputData["paraName"]
        paraVal = inputData["paraVal"]

        searchAllow = ["a.id","cardID","personID","phone"]
        if paraName not in searchAllow:
            raise Exception("[ERR]: paraName "+ paraName + " not allow.")

        filter = {
            "stationID" : stationID,
            str(paraName) : str(paraVal)
        }

        visitorList = DB.DBLocal.select("visitor_view_data",where = filter,)

        visitorDictList = []
        for item in visitorList:
            item["waitingNum"] = QueueDataController().getWaitingNum({"stationID":stationID,"queueID":item["queueID"],"id":item["id"]})
            item["waitingTime"] = item["waitingNum"] * 15
            visitorDictList.append(item)
        return visitorDictList

    def addVisitor(self, inputData):
        stationID = inputData.get("stationID", None)
        queueID = inputData.get("queueID", None)

        if stationID is None:
            raise Exception("[ERR]: stationID required to add visitor")
        if queueID is None:
            raise Exception("[ERR]: queueID required to add visitor")

        action = "nurser_add"

        try:
            self._addVisitor(inputData, action=action)
        except:
            raise
        else:
            result = {"result": "success"}
            return result

    def _addVisitor(self, inputData, action=None):
        stationID = inputData.get("stationID", None)
        queueID = inputData.get("queueID", None)
        name = inputData.get("name", None)
        snumber = inputData.get("snumber", None)
        age = inputData.get("age", 0)

        cardID = inputData.get("cardID", None)
        phone = inputData.get("phone",None)
        orderType = inputData.get("orderType", 0)
        personID = inputData.get("personID", None)
        urgentLev  = inputData.get("urgentLev",0)
        property = json2Str(inputData.get("property",{}))

        if stationID is None:
            raise Exception("[ERR]: stationID required to add visitor")
        if queueID is None:
            raise Exception("[ERR]: queueID required to add visitor")
        if action is None:
            action = "nurser_add"

        # 自动生成患者ID
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        timestamp = int(time.time() * 1000000)
        id = str(stationID) + str(queueID) + str(timestamp)

        # 如果cardID不存在，从id中获取；如果存在，查询数据获得病人的姓名
        if cardID is None:
            cardID = id[-16:]
        else:
            visitor_list = DB.DBLocal.select("visitor_source_data", where="cardID=$cardID AND name NOT LIKE $name",
                                        vars={"cardID": cardID, "name": "%号"})
            visitor_bak_list = DB.DBLocal.select("visitor_backup_data", where="cardID=$cardID AND name NOT LIKE $name",
                                            vars={"cardID": cardID, "name": "%号"})
            if visitor_list:
                name = visitor_list[0]["name"]
            else:
                if visitor_bak_list:
                    name = visitor_bak_list[0]["name"]

        # 如果snumber不存在，则根据分诊台下的患者数自动生成一个序号
        if not snumber:
            where = "stationID=$stationID"
            visitor_all = DB.DBLocal.select("visitor_local_data", where=where,
                                            vars={"stationID": stationID})
            visitor_all_count = len(visitor_all)
            snumber =  visitor_all_count + 1
        # 如果name不存在，则根据snumber生成一个名字
        if name is None:
            name = "{0}号".format(snumber)

        # 根据队列中的等待、未激活、等待激活的人数，确定总的等待人数
        where = "stationID=$stationID AND queueID=$queueID AND status IN $status"
        visitor_wait = DB.DBLocal.select("visitor_local_data", where=where,
                                         vars={"stationID": stationID, "queueID": queueID,
                                               "status": ('waiting', 'unactive', 'unactivewaiting')})
        waitNum = len(visitor_wait)

        # 获取队列关键字
        queueInfo = QueueInfoInterface().getInfo({"stationID": stationID, "id": queueID})
        queue = queueInfo["filter"]

        workerID = queueInfo["workerOnline"]
        workerList = DB.DBLocal.select("workers", where="id=$id", vars={"id": workerID})
        workerName = None
        department = None
        if len(workerList) != 0:
            worker = workerList[0]
            workerName = worker["name"]
            department = worker["department"]

        # 修改患者来源
        status = None
        if action == "nurser_add":
            status = "护士新增"
        elif action == "self_pick_up":
            status = "自助取号"

        visitor = {
            "id": id,
            "name": name,
            "age": age,
            "queue": queue,
            "snumber": snumber,
            "orderDate": current_date,
            "orderTime": current_time,
            "registDate": current_date,
            "registTime": current_time,
            "urgentLev": urgentLev,
            "orderType": orderType,
            "workerID": workerID,
            "workerName": workerName,
            "department": department,
            "cardID": cardID,
            "personID": personID,
            "phone": phone,
            "status": status
        }

        values = {}
        for key, value in visitor.items():
            if value is not None:
                values.update({key: value})
            if value is None:
                visitor.update({key: ""})
        try:
            DB.DBLocal.insert("visitor_source_data", **values)
        except Exception,e:
            print "Exception : %s " %str(e)
            raise Exception("[ERR]: insert into visitor_source_data failed. %s " %str(e))

        para = {"stationID": stationID, "queueID": queueID}
        QueueDataController().updateVisitor(para)

        visitor.update({"waitNum": waitNum})

        return visitor
