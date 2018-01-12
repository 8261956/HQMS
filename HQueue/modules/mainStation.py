# -*- coding: utf-8 -*-

import web, re, json, datetime, time
import common.func
import common.config as cfg
from common.func import packOutput, LogOut
from queueData import QueueDataController, VisitorLocalInterface
from queueInfo import QueueInfoInterface
from scene import SceneInterface
import HQueue.DBIO.DBBase as DB


class StationMainController:
    def __init__(self):
        pass

    def POST(self,name):
        webData = json.loads(web.data())
        action = webData["action"]

        LogOut.info("Station Post Request action : "+action)

        if action == "getQueueListInfo":
            try:
                jsonData = self.getQueueListInfo(webData)
                return packOutput(jsonData)
            except Exception as e:
                return packOutput({}, code="500", errorInfo=str(e))

        elif action == "getQueueListAll":
            try:
                jsonData = self.getQueueListAll(webData , useCache = 0)
                return packOutput(jsonData)
            except Exception as e:
                return packOutput({}, code="500", errorInfo=str(e))

        elif action == "getVisitorInfo":
            try:
                jsonData = self.getVisitorInfo(webData)
            except Exception as e:
                print Exception, ":", e
                ret = {"result": "failed"}
                return packOutput(ret, "500", str(e))
            return packOutput(jsonData)

        elif action == "visitorFuzzySearch":
            try:
                list = self.visitorFuzzySearch(webData)
                ret = {"resultList": list}
            except Exception, e:
                print Exception, ":", e
                ret = {"result": "faild"}
                return packOutput(ret, "500", str(e))
            return packOutput(ret)

        elif action == "visitorMoveto":
            try:
                self.visitorMoveto(webData)
                ret = {"result":"success"}
            except Exception, e:
                print Exception, ":", e
                ret = {"result": "faild"}
                return packOutput(ret,"500",str(e))
            return packOutput(ret)

        elif action == "visitorMoveby":
            try:
                self.visitorMoveby(webData)
                ret = {"result": "success"}
            except Exception, e:
                print Exception, ":", e
                ret = {"result": "faild"}
                return packOutput(ret,"500",str(e))
            return packOutput(ret)

        elif action == "visitorProirSet":
            try:
                self.visitorProirSet(webData)
                ret = {"result": "success"}
            except Exception, e:
                print Exception, ":", e
                ret = {"result": "faild"}
                return packOutput(ret,"500",str(e))
            return packOutput(ret)

        elif action == "visitorVIPSet":
            try:
                self.visitorVIPSet(webData)
                ret = {"result": "success"}
            except Exception, e:
                print Exception, ":", e
                ret = {"result": "faild"}
                return packOutput(ret,"500",str(e))
            return packOutput(ret)

        elif action == "visitorLockSet":
            try:
                self.visitorLockSet(webData)
                ret = {"result": "success"}
            except Exception, e:
                print Exception, ":", e
                ret = {"result": "faild"}
                return packOutput(ret,"500",str(e))
            return packOutput(ret)

        elif action == "visitorFinishSet":
            try:
                self.visitorFinishSet(webData)
                ret = {"result": "success"}
            except Exception, e:
                print Exception, ":", e
                ret = {"result": "faild"}
                return packOutput(ret,"500",str(e))
            return packOutput(ret)

        elif action == "visitorSearch":
            #try:
            ret = self.visitorSearch(webData)
            """except Exception, e:
                print Exception, ":", e
                ret = {"result": "faild"}
                return packOutput(ret,"500",str(e))"""
            return packOutput(ret)

        elif action == "visitorActiveSet":
            try:
                self.visitorActiveSet(webData)
                ret = {"result": "success"}
            except Exception, e:
                print Exception, ":", e
                ret = {"result": "faild"}
                return packOutput(ret,"500",str(e))
            return packOutput(ret)

        elif action == "addVisitor":
            try:
                result = self.addVisitor(webData)
                return packOutput(result)
            except Exception as e:
                return packOutput({}, code="400", errorInfo=str(e))

        else:
            return packOutput({},"500","unsupport action")



    def getQueueListInfo(self,inputData):
        stationID = inputData.get("stationID")
        station = DB.DBLocal.select("stationSet", where="id=$id", vars={"id": stationID})
        if len(station) == 0:
            raise Exception("[ERR]: station not exists.")
        # sql = "SELECT q.id, q.name, q.workerOnline, s.activeLocal FROM queueInfo AS q " \
        #       "INNER JOIN scene AS s ON q.sceneID = s.id WHERE q.stationID=%s" % stationID
        # # list = DB.DBLocal.where('queueInfo', stationID=inputData["stationID"])
        # list = DB.DBLocal.query(sql)
        list = QueueInfoInterface().getList({"stationID": stationID})
        ret = {"num": len(list) , "list": []}
        for item in list:
            queueInfo = {}
            queueInfo["id"] =  item["id"]
            queueInfo["name"] = item["name"]
            queueInfo["workerOnline"] = item["workerOnline"]
            if item["activeLocal"] == 1:
                queueInfo["tab"] = ["unactive","waiting","finish"]
            else:
                queueInfo["tab"] = ["waiting", "finish"]
            ret["list"].append(queueInfo)
        return ret

    def sqlStatusView(self,stationID,queueID,status):
        # 联合查询之后再排序
        #select * from visitor_source_data s inner join  (select id,activeLocal,activeLocalTime, workerOnline, prior, locked,vip as localVip,status as localStatus, finalScore,originScore from visitor_local_data ) as l on s.id=l.id
        return

    def sqlVisitorView(self,stationID,visitorID):
        joinView = "(select id,activeLocal,activeLocalTime, workerOnline, prior, locked,queueID,vip as localVip,status as localStatus from visitor_local_data where stationID =" + str(stationID) + " and " \
            + "id= \'"+ str(visitorID) + "\') as joinView"
        LogOut.info("joinView " +joinView)
        joinSql = "select * from visitor_source_data a inner join "+ joinView + " on a.id=joinView.id and a.stationID=" +str(stationID)

        LogOut.info("join sql: " + joinSql)
        return joinSql

    def getQueueList(self,inputData):
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]
        qlist = DB.DBLocal.where('queueInfo', stationID = inputData["stationID"],id = queueID)
        if len(qlist) == 0:
            raise Exception("[ERR]: queue not exists")
        queue = qlist[0]
        ret = {"name": queue["name"], "workerOnline": queue["workerOnline"], "doingList":[], "waitingList":[],"finishList":[]}

        doingList = DB.DBLocal.where("visitor_view_data",stationID = stationID,queueID = queueID ,localStatus = "doing")  # 进行中的所有访客
        ret["doingList"] = list(doingList)

        waitList = DB.DBLocal.where("visitor_view_data",stationID = stationID,queueID = queueID ,localStatus = "waiting")  # 等待中的所有访客
        ret["waitingList"] = list(waitList)

        return ret

    def getQueueListAll(self,inputData,useCache):
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]

        #if can get from Memcached
        key = "_getQueueListAll_stationID" + str(stationID)+"_queueID"+str(queueID)
        value = common.func.CachedGetValue(json.dumps(key))
        if value != False:
            if useCache:
                return value

        ret = {"name": "", "workerOnline": "", "waitingList": [], "finishList": []}
        queue = QueueInfoInterface().getInfo({"stationID": stationID, "id": queueID})
        ret.update({"name": queue["name"], "workerOnline": queue["workerOnline"]})

        if queue["activeLocal"] == 1:
            joinSql = self.sqlStatusView(stationID, queueID,"unactive")
            unactiveList = DB.DBLocal.query(joinSql)  # 未激活的所有访客
            ret["unactiveList"] = []
            for item in unactiveList:
                ret["unactiveList"].append(item)

        doingList = DB.DBLocal.where("visitor_view_data",stationID = stationID,queueID = queueID ,localStatus = "doing")  # 进行中的所有访客
        ret["doingList"] = list(doingList)

        waitList = DB.DBLocal.where("visitor_view_data",stationID = stationID,queueID = queueID ,localStatus = "waiting")  # 等待中的所有访客
        ret["waitingList"] = list(waitList)

        finishList = DB.DBLocal.where("visitor_view_data",stationID = stationID,queueID = queueID ,localStatus = "pass") # 过号的所有访客
        for item in finishList:
            ret["finishList"].append(item)

        finishList = DB.DBLocal.where("visitor_view_data",stationID = stationID,queueID = queueID ,localStatus = "finish")  # 已完成的所有访客
        for item in finishList:
            ret["finishList"].append(item)

        #缓存 value
        common.func.CahedSetValue(json.dumps(key),ret,2)

        return ret

    def getVisitorInfo(self,inputData):
        stationID = inputData["stationID"]
        id  = inputData["id"]
        visitorList = DB.DBLocal.where("visitor_view_data", stationID = stationID, id = id)
        if len(visitorList) == 0:
            raise Exception("[ERR]: visitor not exists. id:"+ id)
        return visitorList[0]

    def visitorMoveto(self, inputData):
        # TODO 修改BUG：根据传入的参数查找指定的访客，如果查找不到它也会返回success
        QueueDataController().visitorMoveto(inputData)
        return

    def visitorMoveby(self, inputData):
        QueueDataController().visitorMoveby(inputData)
        return

    def visitorProirSet(self, inputData):
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]
        visitor = {}
        visitor["id"] = inputData["id"]
        visitor["prior"] = inputData["prior"]
        # if inputData["prior"]:
        #     visitor["prior"] = 1
        # else:
        #     visitor["prior"] = 0
        VisitorLocalInterface(stationID).edit(visitor)
        return

    def visitorVIPSet(self, inputData):
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]
        visitor = {}
        visitor["id"] = inputData["id"]
        visitor["stationID"] = stationID
        if inputData["vip"]:
            visitor["vip"] = 1
        else:
            visitor["vip"] = 0
        VisitorLocalInterface(stationID).edit(visitor)
        return

    def visitorLockSet(self,inputData):
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]
        visitor = {}
        visitor["id"] = inputData["id"]
        visitor["stationID"] = stationID
        if inputData["locked"]:
            visitor["locked"] = 1
        else:
            visitor["locked"] = 0
        VisitorLocalInterface(stationID).edit(visitor)
        return

    def visitorFinishSet(self,inputData):
        id = inputData["id"]
        stationID = inputData["stationID"]
        visitorList = DB.DBLocal.select("visitor_local_data",
                                    where="stationID=$stationID and id=$id",
                                    vars={"stationID": stationID, "id": id})
        if len(visitorList) != 0:
            visitor = visitorList[0]
        else:
            raise Exception("[ERR]: visitor not exists.id:" + id)
        if inputData["finish"]:
            # 判断访客当前的状态
            if visitor["status"] == "finish":
                return
            # 设置访客完成的情况
            visitor["status"] = "finish"
        else:
            # 访客复诊的情况
            if visitor["status"] == "finish":
                visitor["status"] = "waiting"
                visitor["prior"] = 1
                self.setVisitorStatus(visitor, action="review")
            # 访客过号的情况
            elif visitor["status"] == "pass":
                visitor["status"] = "waiting"
                visitor["prior"] = 2
                self.setVisitorStatus(visitor, action="pass")
            else:
                visitor["status"] = "waiting"
        VisitorLocalInterface(stationID).edit(visitor)
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
        workDays, date = QueueInfoInterface().getWorkDays(stationID, queueID)
        fliter = "stationID=$stationID and queueID=$queueID and status=$status"
        if cfg.currentDayOnly == "1":
            fliter += " and registDate >=$date"
        visitorList = DB.DBLocal.select("visitor_local_data",
                                        where=fliter,
                                        vars={"stationID": stationID, "queueID": queueID, "status": "waiting" ,"date" : date},
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

        joinView = "(select id,activeLocal,activeLocalTime,locked,queueID,vip as localVip,status as localStatus from visitor_local_data where stationID =" + str(stationID) +\
            " ) as joinView"
        LogOut.info("joinView " +joinView)

        joinSql = "select * from visitor_source_data a inner join "+ joinView + " on a.id=joinView.id and a.stationID=" +str(stationID)
        joinSql += " where " + str(paraName) + " = \'" + str(paraVal) +"\'"

        visitorList = DB.DBLocal.query(joinSql)
        visitorDictList = []
        for item in visitorList:
            item["waitingNum"] = QueueDataController().getWaitingNum({"stationID":stationID,"queueID":item["queueID"],"id":item["id"]})
            item["waitingTime"] = item["waitingNum"] * 15
            visitorDictList.append(item)
        return visitorDictList

    def visitorActiveSet(self,inputData):
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]
        visitor = {}
        visitor["id"] = inputData["id"]
        visitor["stationID"] = stationID
        if inputData["active"]:
            activeTime = datetime.datetime.now()
            visitor["activeLocal"] = 1
            visitor["activeLocalTime"] = activeTime
            queueInfo = QueueInfoInterface().getInfo({"stationID": stationID, "id": queueID})
            sceneID = queueInfo["sceneID"]
            scene = SceneInterface().getSceneInfo({"sceneID": sceneID})
            if scene["delayTime"] == 0:
                visitor["status"] = "waiting"
            else:
                visitor["status"] = "unactivewaiting"
        else:
            visitor["activeLocal"] = 0
            visitor["status"] = "unactive"
        VisitorLocalInterface(stationID).edit(visitor)

        QueueDataController().sortVisitor(stationID,queueID,scene)

        return

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
        VIP = inputData.get("VIP", 0)
        descText = inputData.get("descText", None)
        cardID = inputData.get("cardID", None)
        age = inputData.get("orderType", None)
        orderType = inputData.get("orderType", 0)
        personID = inputData.get("personID", None)
        phone = inputData.get("phone", None)
        if stationID is None:
            raise Exception("[ERR]: stationID required to add visitor")
        if queueID is None:
            raise Exception("[ERR]: queueID required to add visitor")
        if action is None:
            action = "nurser_add"

        # 自动生成患者ID
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
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
        workDays, date = QueueInfoInterface().getWorkDays(stationID, queueID)
        if not snumber:
            where = "stationID=$stationID"
            if cfg.currentDayOnly == "1":
                where += " AND registDate>=$date"
            visitor_all = DB.DBLocal.select("visitor_source_data", where=where,
                                            vars={"stationID": stationID, "date": date})
            visitor_all_count = len(visitor_all)
            snumber =  visitor_all_count + 1
        # 如果name不存在，则根据snumber生成一个名字
        if name is None:
            name = "{0}号".format(snumber)

        # 根据队列中的等待、未激活、等待激活的人数，确定总的等待人数
        where = "stationID=$stationID AND queueID=$queueID AND status IN $status"
        if cfg.currentDayOnly == "1":
            where += " AND registDate>=$date"
        visitor_wait = DB.DBLocal.select("visitor_local_data", where=where,
                                         vars={"stationID": stationID, "queueID": queueID, "date": date,
                                               "status": ('waiting', 'unactive', 'unactivewaiting')})
        waitNum = len(visitor_wait)

        # 获取队列关键字
        queueInfo = QueueInfoInterface().getInfo({"stationID": stationID, "id": queueID})
        filter = queueInfo["filter"]
        filter = re.findall(r'queue=\'(.*)\'', filter)
        queue = filter[0]

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
            "stationID": stationID,
            "queueID": queueID,
            "name": name,
            "age": age,
            "queue": queue,
            "snumber": snumber,
            "orderDate": current_date,
            "orderTime": current_time,
            "registDate": current_date,
            "registTime": current_time,
            "VIP": VIP,
            "orderType": orderType,
            "workerID": workerID,
            "workerName": workerName,
            "descText": descText,
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
        except:
            raise Exception("[ERR]: insert into visitor_source_data failed.")

        para = {"stationID": stationID, "queueID": queueID}
        QueueDataController().updateVisitor(para)

        # visitorInfo = (id, name, cardID, snumber, waitNum)
        visitor.update({"waitNum": waitNum})

        return visitor
