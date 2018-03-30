# -*- coding: UTF-8 -*-

import web, json, re, datetime, time, socket
import common.func
import queueInfo
import mainStation
from queueData import QueueDataController, VisitorLocalInterface
from common.func import packOutput, LogOut, str2List,list2Str,getCurrentTime,checkPostAction
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
        "callNext" : "callNext",
        "reCall" : "reCall",
        "setDelay" : "setDelay",
        "callPass" : "callPass",
        "callVisitor" : "callVisitor",
        "callEmergency" : "callEmergency",
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

        callerList = DB.DBLocal.select("caller", where=where)
        if len(callerList) > 0:
            caller = callerList[0]
            return dict(caller)
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
            info["tab"] = ["waiting", "finish"]
            info["state"] = state
            ret["list"].append(info)
        return ret

    def getQueueListAll(self,inputData):
        ret = mainStation.StationMainController().getQueueListAll(inputData ,useCache = 1)
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
        queue = DB.DBLocal.where('queueInfo', queueID=queueID).first()
        if queue is None:
            raise "queue %d not exist" %queueID
        workerOnline = str2List(queue["workerOnline"])
        queue["workerOnline"] = list2Str(workerOnline.append(workerID))
        queueInfo.QueueInfoInterface().edit(queue)
        #修改队列进行中人员 且医生为当前医生的 为已完成
        doingList = DB.DBLocal.where('visitor_local_data', stationID=inputData["stationID"] ,queueID = inputData["queueID"]\
                                     ,status = "doing", workerOnline = workerID)
        lastOne = {"id": "","stationID":stationID, "queueID": queueID, "name": "", "status": "finish"}
        # if passed == 1:
        #     lastOne["status"] = "pass"
        for item in doingList:
            lastOne["id"] = item["id"]
            lastOne["name"] = item["name"]
            lastOne["workEndTime"] = getCurrentTime()
            VisitorLocalInterface(stationID).edit(lastOne)
        #修改呼叫人员状态改为Doing 呼叫医生改为当前医生
        waitList = QueueDataController().getQueueVisitor(inputData)
        nextOne = parpareOne = {}
        for item in waitList:
            if item["locked"] != 1:
                nextOne = item
                nextOne["status"] = "doing"
                nextOne["workerOnline"] = workerID
                nextOne["workStartTime"] = getCurrentTime()
                VisitorLocalInterface(stationID).edit(nextOne)
                try:
                    parpareOne = iter(waitList).next()
                except:
                    parpareOne = {}
                self.publish(inputData,lastOne,nextOne,parpareOne,ret)
                break
        return  ret

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

    def callVisitor(self,inputData):
        ret = {}
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]
        workerID = inputData["id"]
        visitorID = inputData["visitorID"]
        # 修改队列最后在线医生
        queue = {}
        queue["id"] = queueID
        queue["stationID"] = stationID
        queue["workerOnline"] = workerID
        queueInfo.QueueInfoInterface().edit(queue)
        # 修改呼叫人员状态改为Doing 呼叫医生改为当前医生
        selectOne = VisitorLocalInterface(stationID).getInfo({"id": visitorID})
        if selectOne["locked"] != 1:
            nextOne = {"id": visitorID, "stationID" :stationID}
            nextOne["status"] = "doing"
            nextOne["workerOnline"] = workerID
            nextOne["workStartTime"] = getCurrentTime()
            VisitorLocalInterface(stationID).edit(nextOne)
            nextOne["name"] = selectOne["name"]
            lastOne = parpareOne = {}
            self.publish(inputData,lastOne,nextOne,parpareOne,ret)
        return ret

    def callEmergency(self,inputData):
        ret = {}
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]
        workerID = inputData["id"]
        visitorID = inputData["visitorID"]

        #修改队列最后在线医生
        queue = {}
        queue["id"] = queueID
        queue["stationID"] = stationID
        queue["workerOnline"] = workerID
        queueInfo.QueueInfoInterface().edit(queue)
        #修改队列进行中人员 且医生为当前医生的 为已完成
        doingList = DB.DBLocal.where('visitor_local_data', stationID=inputData["stationID"] ,queueID = inputData["queueID"]\
                                     ,status = "doing", workerOnline = workerID)
        lastOne = {"id": "","stationID":stationID, "name": "", "status": "finish"}
        for item in doingList:
            lastOne["id"] = item["id"]
            lastOne["name"] = item["name"]
            lastOne["workEndTime"] = getCurrentTime()
            VisitorLocalInterface(stationID).edit(lastOne)

        # 修改呼叫人员状态改为Doing 呼叫医生改为当前医生
        selectOne = VisitorLocalInterface(stationID).getInfo({"id": visitorID})
        if selectOne["locked"] != 1:
            nextOne = {"id": visitorID, "stationID" :stationID}
            nextOne["status"] = "doing"
            nextOne["workerOnline"] = workerID
            nextOne["workStartTime"] = getCurrentTime()
            VisitorLocalInterface(stationID).edit(nextOne)
            nextOne["name"] = selectOne["name"]
            lastOne = parpareOne = {}
            self.publish(inputData,lastOne,nextOne,parpareOne,ret)
        return ret

    def reCall(self,inputData):
        ret = {}
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]
        workerID = inputData["id"]

        #修改队列最后在线医生
        queue = {}
        queue["id"] = queueID
        queue["stationID"] = stationID
        queue["workerOnline"] = workerID
        queueInfo.QueueInfoInterface().edit(queue)
        #修改队列进行中人员 且医生为当前医生的 为已完成
        doingList = DB.DBLocal.where('visitor_local_data', stationID=inputData["stationID"] ,queueID = inputData["queueID"]\
                                     ,status = "doing", workerOnline = workerID)
        lastOne = {"id": "","stationID":stationID, "name": "", "status": "waiting"}
        if len(doingList) == 1:
            item = doingList[0]
            lastOne["id"] = item["id"]
            lastOne["name"] = item["name"]
            #再次呼叫人员
            nextOne = lastOne
            parpareOne = {}
            self.publish(inputData,lastOne,nextOne,parpareOne,ret)
        return  ret

    def publishNew(self, inputData, lastOne, nextOne, prepareOne, ret):
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]
        workerID = inputData["id"]

        # 获得叫号器信息，位置
        caller = self.getCallerInfo(inputData)
        pos = caller["pos"]
        if prepareOne != {} and lastOne != {}:
            LogOut.info("caller next req pos " + pos + " last " + lastOne["name"] + " doing " + nextOne["name"])
            LogOut.info("parpare One : " + prepareOne["name"])

        worker = WorkerInterface().getInfo({"stationID":stationID,"id":workerID})

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
        key = {"type": "publish", "stationID": stationID, "callerID": caller["id"], "action": "getStationList"}
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

        qInfo = queueInfo.QueueInfoInterface().getInfo({"stationID": stationID, "id": queueID})
        sceneID = qInfo["sceneID"]
        scene = SceneInterface().getSceneInfo({"sceneID": sceneID})
        # V1.2.1 增加按照名字、序号、卡号等语音播报方式
        # V1.2.1 将"请***准备"设置为可配置项
        property = scene["property"]
        callMode = property["callMode"]
        if callMode == 'callByName':
            nextOneText = nextOne.get("name")
            prepareOneText = prepareOne.get("name", "")
        elif callMode == 'callBySnumber':
            nextOneText = "%s号" % nextOne.get("snumber")
            prepareOneText = "%s号" % prepareOne.get("snumber", "")
        elif callMode == 'callByCardID':
            nextOneText = nextOne.get("cardID")
            prepareOneText = prepareOne.get("cardID", "")
        else:
            raise Exception("unsupport callMode")
        text = "请%s到%s%s" % (nextOneText, pos, scene["outputText"])
        # TODO: V1.21  scene property add noPrepare
        if not property["noPrepare"]:
            if prepareOne != {}:
                text += ", 请%s准备" % prepareOneText

        publishDev = PublishDevInterface()
        mediaBoxInterface = MediaBoxInterface()
        devList = publishDev.getInfo({"stationID":stationID})
        ret["list"] = []
        for dev in devList:
            # 增加语音盒在线判断
            mediabox = mediaBoxInterface.mediaBoxStatus(dev)
            callerLimit = mediabox["callerLimit"]
            if callerLimit:
                callerLimit = str2List(callerLimit)
                if caller["id"] not in callerLimit:
                    continue
            if mediabox["status"] == "offline":
                continue
            ret["list"].append({"soundUrl":dev["deviceIP"] , "text" : text, "id": nextOne["id"]})
            #publishDev.Announce(dev["deviceIP"], cid, text)

    def publish(self,inputData,lastOne,nextOne,parpareOne,ret):
        self.publishNew(inputData,lastOne,nextOne,parpareOne,ret)

    def visitorFinishSet(self,inputData):
        id = inputData.get("visitorID", None)
        stationID = inputData.get("stationID", None)
        queueID = inputData.get("queueID", None)
        finish = inputData.get("finish", None)
        para = {"id": id, "stationID": stationID, "queueID": queueID, "finish": finish}
        StationMainController().visitorFinishSet(para)
        return

    def setWorkerStatus(self,inputData):
        stationID = inputData["stationID"]
        id = inputData["id"]
        status = inputData["status"]
        worker = { "id":id, "status":status }
        WorkerInterface().editWorker(worker)
        return
