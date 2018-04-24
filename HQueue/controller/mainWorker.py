# -*- coding: UTF-8 -*-

import web, json, re, datetime, time, socket
import common.func
import queueInfo
import mainStation
from queueData import QueueDataController, VisitorLocalInterface
from common.func import packOutput, LogOut, str2List,list2Str,getCurrentTime,checkPostAction,str2Json,takeVal
from publish import callRecordInterface, PublishDevInterface
from worker import WorkerInterface
from mainStation import StationMainController
from scene import SceneInterface
from mediabox import MediaBoxInterface
import common.DBBase as DB


class WorkerMainController:
    support_action = {
        "getCallerInfo":"getCallerInfo",
        "getQueueList" : "getQueueList",
        "getQueueListAll":"getQueueListAll",
        "getMovetoList":"getMovetoList",
        "visitorMoveto": "visitorMoveto",
        "callNext" : "callNext",    #呼叫下一位
        "reCall" : "reCall",         #重呼
        "callSel" : "callSel",       #选叫
        "visitorPropertySet" : "visitorPropertySet",
        "setWorkerStatus" : "setWorkerStatus",
    }

    def POST(self,name):
        data = json.loads(web.data())
        return checkPostAction(self, data, self.support_action)

    def getCallerInfo(self,inputData):
        stationID = inputData.get("stationID", None)
        ip = web.ctx.ip
        if "localIP" in inputData:
            ip = inputData["localIP"]
        print "Login at ip: {0}".format(ip)
        where = {"ip": ip}
        if stationID:
            where.update({"stationID": stationID})

        cInfo = DB.DBLocal.select("caller", where=where).first()
        if cInfo is not None:
            cInfo["workerLimit"] = str2List(cInfo["workerLimit"])
            return cInfo
        return {}

    def getQueueList(self,inputData):
        queueList = queueInfo.QueueInfoInterface().getList(inputData)
        workerID = inputData["id"]
        matchQueue = []
        for queue in queueList:
            if queue["workerLimit"] == "none":
                matchQueue.append(queue)
            else:
                workerLimit = str2List(queue["workerLimit"])
                if (workerID in workerLimit) or (workerID.upper() in workerLimit) or (workerID.lower() in workerLimit):
                    matchQueue.append(queue)

        ret = {"num": len(matchQueue), "list": []}
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%p")
        if current_time == "AM":
            current_time = 1
        else:
            current_time = 2
        for item in matchQueue:
            info = {}
            # 判断队列、医生的排班情况
            #TODO : 判断队列医生的排班情况，统一放到排班方法中提供接口
            queue = item["filter"]
            scheduleList = DB.DBLocal.select("schedule", where={"queue": queue, "workDate": current_date,
                                                                "workTime": current_time})
            if len(scheduleList) == 0:
                state = "not queue"
            else:
                schedule = scheduleList[0]
                onDuty = schedule["onDuty"]
                schedule_workerLimit = str2List(schedule["workerID"])
                if onDuty in (1, 3) and workerID in schedule_workerLimit:
                    state = "queue and worker"
                elif onDuty in (1, 3) and workerID not in schedule_workerLimit:
                    state = "queue not worker"
                else:
                    state = "not queue"

            info["id"] = item["id"]
            info["name"] = item["name"]
            info["workerOnline"] = item["workerOnline"]
            info["state"] = state
            ret["list"].append(info)
        return ret

    def getQueueListAll(self,inputData):
        inputData["useCache"] = 1
        ret = mainStation.StationMainController().getQueueListAll(inputData)
        return ret

    def getMovetoList(self,inputData):
        list = DB.DBLocal.where('queueInfo', stationID=inputData["stationID"])
        ret = {"num": len(list) , "list": []}
        for item in list:
            queueInfo = {}
            queueInfo["id"] =  item["id"]
            queueInfo["name"] = item["name"]
            ret["list"].append(queueInfo)
        return ret

    def visitorMoveto(self,inputData):
        QueueDataController().visitorMoveto(inputData)
        return {"result" : "success"}

    def visitorMoveby(self,inputData):
        QueueDataController().visitorMoveby(inputData)
        return {"result" : "success"}

    def callNext(self,inputData):
        ret = {}
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]
        workerID = inputData["id"]

        #修改队列最后在线医生
        queueInfo.QueueInfoInterface().addWorkerOnline(queueID,workerID)
        #修改队列进行中人员 且医生为当前医生的 为已完成
        lastOne = self.workerFinish(stationID,queueID,workerID)
        #修改呼叫人员状态改为Doing 呼叫医生改为当前医生
        #TODO : 完善呼叫 跳过目标不是自身呼叫器的患者，排队列表中是准备状态的患者 患者锁定等属性的判断
        waitList = QueueDataController().getQueueVisitor(inputData,["waiting","prepare"])
        nextOne = parpareOne = {}
        callerInfo = self.getCallerInfo(inputData)
        for item in waitList:
            if item["dest"] not in {None,""}:
                if callerInfo["pos"] != item["dest"]:
                    continue
            #判断locked 等属性
            property = str2Json(item["property"])
            locked = property.get("locked","0")
            if locked == "0":
                nextOne = item
                nextOne["status"] = "doing"
                nextOne["workerOnline"] = workerID
                nextOne["workStartTime"] = getCurrentTime()
                VisitorLocalInterface(stationID).edit(nextOne)
                #TODO: 准备人员根据策略判定
                parpareOne = {}
                self.publishNew(inputData,callerInfo,lastOne,nextOne,parpareOne,ret)
                break
        return  ret

    def callSel(self,inputData):
        ret = {}
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]
        workerID = inputData["id"]
        visitorID = inputData["visitorID"]

        callerInfo = self.getCallerInfo(inputData)
        # TODO : 完善呼叫 跳过目标不是自身呼叫器的患者，排队列表中是准备状态的患者 患者锁定等属性的判断
        # 修改队列最后在线医生
        queueInfo.QueueInfoInterface().addWorkerOnline(queueID, workerID)
        if inputData.get("mode") == "ONE":
            lastOne = self.workerFinish(stationID, queueID, workerID)
        # 修改呼叫人员状态改为Doing 呼叫医生改为当前医生
        selectOne = VisitorLocalInterface(stationID).getInfo({"id": visitorID})
        nextOne = {"id": visitorID, "stationID" :stationID}
        nextOne["status"] = "doing"
        nextOne["workerOnline"] = workerID
        nextOne["workStartTime"] = getCurrentTime()
        VisitorLocalInterface(stationID).edit(nextOne)
        nextOne["name"] = selectOne["name"]
        lastOne = parpareOne = {}
        self.publishNew(inputData,callerInfo,lastOne,nextOne,parpareOne,ret)
        return ret

    def reCall(self,inputData):
        ret = {}
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]
        workerID = inputData["id"]

        #修改队列最后在线医生
        queueInfo.QueueInfoInterface().addWorkerOnline(queueID, workerID)
        callerInfo = self.getCallerInfo(inputData)
        #修改队列进行中人员 且医生为当前医生的 为已完成
        doingOne = DB.DBLocal.where('visitor_local_data', stationID=stationID ,queueID = queueID\
                                     ,status = "doing", workerOnline = workerID).first()
        lastOne = {"id": "","stationID":stationID, "name": "", "status": "waiting"}
        if doingOne is not None:
            lastOne["id"] = doingOne["id"]
            lastOne["name"] = doingOne["name"]
            #再次呼叫人员
            nextOne = lastOne
            parpareOne = {}
            self.publishNew(inputData,callerInfo,lastOne,nextOne,parpareOne,ret)
        return  ret

    def publishNew(self, inputData, caller,lastOne, nextOne, prepareOne, ret):
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]
        workerID = inputData["id"]

        # 获得叫号器信息，位置
        pos = caller["pos"]

        #记录到呼叫记录表中
        record = {}
        record["stationID"] = stationID
        record["callerID"] = caller["id"]
        record["workerID"] = workerID
        record["queueID"] = queueID
        record["currentVisitorID"] = nextOne["id"]
        record["currentVisitorName"] = nextOne["name"]
        curDateTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        record["dateTime"] = curDateTime
        record["showCnt"] = 10
        callRecordInterface().record(record)

        key = {"type":"publish","stationID":stationID,"callerID":caller["id"],"action":"getCallerList"}
        common.func.CachedClearValue(json.dumps(key))
        key = {"type":"publish","stationID": stationID,"callerID": caller["id"], "action": "getStationList"}
        common.func.CachedClearValue(json.dumps(key))

        #更新nextOne和prepareOne的信息
        if nextOne:
            where = {"id": nextOne["id"]}
            next_visitor = DB.DBLocal.select("visitor_source_data",
                                             where=where).first()
            nextOne.update({"snumber": next_visitor.snumber})
            nextOne.update({"cardID": next_visitor.cardID})
        if prepareOne:
            where = {"id": prepareOne["id"]}
            prepare_visitor = DB.DBLocal.select("visitor_source_data",
                                                where=where).first()
            prepareOne.update({"snumber": prepare_visitor.snumber})
            prepareOne.update(({"cardID": prepare_visitor.cardID}))

        # 转换呼叫音频
        cid = str(stationID) + "_" + nextOne["id"]

        qInfo = DB.DBLocal.select("queueInfo",where = {"stationID": stationID, "id": queueID}).first()
        sceneID = qInfo["sceneID"]
        scene = SceneInterface().getSceneInfo({"sceneID": sceneID})

        #TODO:解析sceneOutput
        doingOutput = ""
        prepareOutput = ""
        if nextOne:
            doingOutput = scene["output"]
            doingOutput = doingOutput.replace("$name",nextOne.get("name"))
            doingOutput = doingOutput.replace("$snumber",nextOne.get("snumber"))
            doingOutput = doingOutput.replace("$cardID",nextOne.get("cardID"))
            doingOutput = doingOutput.replace("$pos", pos)
        if prepareOne :
            prepareOutput = scene["prepareOutput"]
            prepareOutput = prepareOutput.replace("$name", prepareOne.get("name"))
            prepareOutput = prepareOutput.replace("$snumber", prepareOne.get("snumber"))
            prepareOutput = prepareOutput.replace("$cardID", prepareOne.get("cardID"))
            prepareOutput = prepareOutput.replace("$pos", pos)
        soundDoingTimes = takeVal(scene,"soundDoingTimes",2)
        soundPrepareTimes = takeVal(scene,"soundDoingTimes",1)
        text = doingOutput * soundDoingTimes + prepareOutput * soundPrepareTimes

        publishDev = PublishDevInterface()
        mediaBoxInterface = MediaBoxInterface()
        modiaBoxList = publishDev.getInfo({"stationID":stationID}).list()
        ret["list"] = []
        ret["result"] = "success"
        for box in modiaBoxList:
            # 增加语音盒在线判断
            mediabox = mediaBoxInterface.mediaBoxStatus(box)
            callerLimit = mediabox["callerLimit"]
            if callerLimit:
                callerLimit = str2List(callerLimit)
                if caller["id"] not in callerLimit:
                    continue
            if mediabox["status"] == "offline":
                continue
            ret["list"].append({"soundUrl":box["deviceIP"] , "text" : text, "id": nextOne["id"]})
            #publishDev.Announce(dev["deviceIP"], cid, text)

    def setVisitorStatus(self, inputData, action=None):
        stationID = inputData.get("stationID", None)
        if stationID is None:
            raise Exception("[ERR]: stationID required")
        queueID = inputData.get("queueID", None)
        if queueID is None:
            raise Exception("[ERR]: queueID required")
        workerID = inputData.get("id", None)
        if workerID is None:
            raise Exception("[ERR]: workerID required")

        # 修改队列最后登录医生
        queueInfo.QueueInfoInterface().edit({"stationID": stationID, "id": queueID, "workerOnline": workerID})

        where = {"stationID": stationID, "queueID": queueID, "workerOnline": workerID, "status": "doing"}
        doingList = DB.DBLocal.select("visitor_local_data", where=where)

        doing = doingList[0]
        if action == "delay":
            # 为当前需要设置延后的访客重新设置originScore、finalScore
            doing["prior"] = 3
            doing = mainStation.StationMainController().setVisitorStatus(doing, action=action)
            # 修改需要设置延后的访客状态为"延后"
            doing["status"] = "waiting"
        elif action == "pass":
            doing["prior"] = 2
            doing = mainStation.StationMainController().setVisitorStatus(doing, action=action)
            doing["status"] = "pass"
        doing["workEndTime"] = getCurrentTime()
        VisitorLocalInterface(stationID).edit(doing)

    def visitorFinishSet(self,inputData):
        result = {"result": "unused action"}
        return result

    def visitorPropertySet(self,inputData):
        ret = StationMainController().visitorPropertySet(inputData)
        return ret

    def setWorkerStatus(self,inputData):
        stationID = inputData["stationID"]
        id = inputData["id"]
        status = inputData["status"]
        worker = { "id":id, "status":status }
        WorkerInterface().editWorker(worker)
        return {"result" : "success"}

    def workerFinish(self,stationID,queueID,workerID):
        filter = {
            "stationID" : stationID,
            "workerOnline" : workerID,
            "status" : "doing"
        }
        if queueID is not None:
            filter.update({"queueID" : queueID})
        doingList = DB.DBLocal.select('visitor_local_data', where = filter)
        lastOne = {"id": "", "stationID": stationID, "queueID": queueID, "name": "", "status": "finish"}
        for item in doingList:
            lastOne["id"] = item["id"]
            lastOne["queueID"] = item["queueID"]
            lastOne["name"] = item["name"]
            lastOne["workEndTime"] = getCurrentTime()
            VisitorLocalInterface(stationID).edit(lastOne)
        return lastOne