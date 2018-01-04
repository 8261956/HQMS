# -*- coding: UTF-8 -*-

import web, json, re, datetime, time, socket
import common.func
import queueInfo
import mainStation
from queueData import QueueDataController, VisitorLocalInterface
from common.func import packOutput, LogOut, str2List
from publish import callRecordInterface, PublishDevInterface
from worker import WorkerInterface
from mainStation import StationMainController
from scene import SceneInterface
from mediabox import MediaBoxInterface
import HQueue.DBIO.DBBase as DB

def GetServiceIP(self):
    myname = socket.getfqdn(socket.gethostname())
    myaddr = socket.gethostbyname(myname)
    return myaddr

def SendMediaConvert(cid,text):
    return []

androidDate = ""

def getAndriodDate():
    if androidDate == "":
        date = time.strftime("%Y%m%d", time.localtime())
        return date
    else:
        return androidDate

def praseAnnounceUrl(url):
    s = url.find("media/")
    date = url[s+6:s+6+8]
    return date

annoceCache = {}
def RecodeAnnounce(stationID,cid,text,url):
    if stationID in annoceCache:
        annoceCache[stationID].append({"cid":cid,"text":text,"url":url})
    else:
        annoceCache[stationID] = []
        annoceCache[stationID].append({"cid":cid,"text":text,"url":url})

def AskAnnounce(stationID):
    if stationID in annoceCache:
        if len(annoceCache[stationID]) > 0:
            ret = annoceCache[stationID][0]
            annoceCache[stationID].pop(0)
            return ret
    return ""

def ClearAnnounce(stationID):
    annoceCache[stationID] = []

class WorkerMainController:
    def __init__(self):
        pass

    def POST(self,name):
        webData = json.loads(web.data())
        action = webData["action"]

        LogOut.info("worker Post Request action : "+action)

        if action == "getCallerInfo":
            ret = self.getCallerInfo(webData)
            return packOutput(ret)
        elif action == "getQueueList":
            ret = self.getQueueList(webData)
            return packOutput(ret)

        elif action == "getQueueListAll":
            try:
                ret = self.getQueueListAll(webData)
                return packOutput(ret)
            except Exception as e:
                return packOutput({}, code="400", errorInfo=str(e))

        elif action == "getMovetoList":
            ret = self.getMovetoList(webData)
            return packOutput(ret)

        elif action == "visitorAppendQueue":
            try:
                self.visitorAppendQueue(webData)
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

        elif action == "callNext":
            try:
                ret = self.callNext(webData)
                ret["result"] = "success"
            except Exception, e:
                print Exception, ":", e
                ret = {"result": "faild"}
                return packOutput(ret,"500",str(e))
            return packOutput(ret)

        elif action == "reCall":
            try:
                ret = self.reCall(webData)
                ret["result"] = "success"
            except Exception, e:
                print Exception, ":", e
                ret = {"result": "faild"}
                return packOutput(ret,"500",str(e))
            return packOutput(ret)

        elif action == "callPass":
            result = {}
            try:
                self.setVisitorStatus(webData, action="pass")
                result.update({"result": "success"})
                return packOutput(result)
            except Exception as e:
                result.update({"result": "failed"})
                return packOutput(result, "500", str(e))

        elif action == "setDelay":
            result = {}
            try:
                self.setVisitorStatus(webData, action="delay")
                result.update({"result": "success"})
                return packOutput(result)
            except Exception as e:
                result.update({"result": "failed"})
                return packOutput(result, "500", str(e))

        elif action =="callVisitor":
            try:
                ret = self.callVisitor(webData)
                ret["result"] = "success"
            except Exception, e:
                print Exception, ":", e
                ret = {"result": "faild"}
                return packOutput(ret,"500",str(e))
            return packOutput(ret)

        elif action =="callEmergency":
            try:
                ret = self.callEmergency(webData)
                ret["result"] = "success"
            except Exception, e:
                print Exception, ":", e
                ret = {"result": "faild"}
                return packOutput(ret,"500",str(e))
            return packOutput(ret)

        elif action =="visitorFinishSet":
            try:
                self.visitorFinishSet(webData)
                ret = {"result": "success"}
            except Exception, e:
                print Exception, ":", e
                ret = {"result": "faild"}
                return packOutput(ret,"500",str(e))
            return packOutput(ret)
        elif action == "AnnounceAsk":
            if webData["clear"] == 1:
                ClearAnnounce(webData["stationID"])
                return packOutput({"result":0})
            ret = AskAnnounce(webData["stationID"])
            if ret == "":
                return packOutput({"result":0})
            else:
                return packOutput({"result": 1,"url":ret["url"],"text":ret["text"],"cid":ret["cid"]})

        elif action == "setWorkerStatus":
            try:
                self.setWorkerStatus(webData)
                ret = {"result": "success"}
            except Exception, e:
                print Exception, ":", e
                ret = {"result": "faild"}
                return packOutput(ret,"500",str(e))
            return packOutput(ret)

        else:
            return packOutput({}, "500", "unsupport action")

    def getCallerInfo(self,inputData):
        # stationID = inputData["stationID"]
        # id = inputData["id"]
        # ipAddr = web.ctx.ip
        # if "localIP" in inputData:
        #     ipAddr = inputData["localIP"]
        # print "Login ip: " + ipAddr
        # ret = DB.DBLocal.where('caller', stationID=inputData["stationID"], ip=ipAddr)
        # if len(ret) > 0:
        #     callerLogin = ret[0]
        #     callerLogin["workerLimit"] = str2List(callerLogin["workerLimit"] )
        #     if id in callerLogin["workerLimit"]:
        #         return callerLogin
        # return {}
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
            filter = item["filter"]
            filter = re.findall(r'queue=\'(.*)\'', filter)
            queue = filter[0]
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

    def visitorAppendQueue(self,inputData):
        inputData["dest"]["id"] = ""
        ctrl = mainStation.StationMainController()
        ctrl.visitorMoveto(inputData)
        if inputData["queueID"] != inputData["dest"]["queueID"]:
            #移到最后
            inputData["queueID"] = inputData["dest"]["queueID"]
            inputData["value"] = 99999
            ctrl.visitorMoveby(inputData)
        return

    def visitorMoveby(self,inputData):
        mainStation.StationMainController().visitorMoveby(inputData)
        return

    def getCurrentTime(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def callNext(self,inputData):
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
        lastOne = {"id": "","stationID":stationID, "queueID": queueID, "name": "", "status": "finish"}
        # if passed == 1:
        #     lastOne["status"] = "pass"
        for item in doingList:
            lastOne["id"] = item["id"]
            lastOne["name"] = item["name"]
            lastOne["workEndTime"] = self.getCurrentTime()
            VisitorLocalInterface(stationID).edit(lastOne)
        #修改呼叫人员状态改为Doing 呼叫医生改为当前医生
        waitList = QueueDataController().getQueueVisitor(inputData)
        nextOne = parpareOne = {}
        for item in waitList:
            if item["locked"] != 1:
                nextOne = item
                nextOne["status"] = "doing"
                nextOne["workerOnline"] = workerID
                nextOne["workStartTime"] = self.getCurrentTime()
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
        doing["workEndTime"] = self.getCurrentTime()
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
            nextOne["workStartTime"] = self.getCurrentTime()
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
            lastOne["workEndTime"] = self.getCurrentTime()
            VisitorLocalInterface(stationID).edit(lastOne)

        # 修改呼叫人员状态改为Doing 呼叫医生改为当前医生
        selectOne = VisitorLocalInterface(stationID).getInfo({"id": visitorID})
        if selectOne["locked"] != 1:
            nextOne = {"id": visitorID, "stationID" :stationID}
            nextOne["status"] = "doing"
            nextOne["workerOnline"] = workerID
            nextOne["workStartTime"] = self.getCurrentTime()
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
