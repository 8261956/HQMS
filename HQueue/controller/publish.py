# -*- coding: UTF-8 -*-

import web, datetime, time, json, copy, requests
import common.func
from common.func import packOutput,str2Json

from caller import CallerInterface
from worker import WorkerInterface
from queueInfo import QueueInfoInterface
from mainStation import StationMainController
from scene import SceneInterface

import common.DBBase as DB

class PublishTVInterface:

    def __init__(self):
        self.callerInterface = CallerInterface()
        self.workerInterface = WorkerInterface()
        self.stationController = StationMainController()

    def POST(self,name):

        webData = json.loads(web.data())
        action = webData["action"]

        if action == "getCallerList":
            try:
                ret = self.getCallerList(webData)
                return packOutput(ret)
            except Exception as e:
                return packOutput({}, code="400", errorInfo=str(e))
        elif action == "getStationList":
            try:
                ret = self.getStationList(webData)
                return packOutput(ret)
            except Exception as e:
                return packOutput({}, code="400", errorInfo=str(e))
        elif action == "getWinList":
            try:
                ret = self.getWinList(webData)
                return packOutput(ret)
            except Exception as e:
                return packOutput({},code="400", errorInfo=str(e))

    def getValidDateTime(self):
        now = int(time.time())
        ValidSec = now - int(4*60*60)
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ValidSec))

    def getCallerPublish(self,inputData):
        retlistInfo = {}
        retWorker = {}
        retQueue =  {}
        ret = {}
        stationID = inputData["stationID"]
        callerID = inputData["callerID"]
        selCaller = CallerInterface().getInfo({"stationID":stationID ,"id" :callerID})
        workerOnlineID = selCaller["workerOnline"]
        if workerOnlineID:
            workerOnline = WorkerInterface().getInfo({"stationID":stationID, "id" :workerOnlineID})
            #显示呼叫记录表单中的项目，有效时间内
            validDataTime = "timestamp\'" + self.getValidDateTime() + "\'"
            callRecordList = DB.DBLocal.where("callingRecord",stationID = stationID, callerID = callerID)
            if len(callRecordList) > 0:
                record = callRecordList[0]
                # 从窗口的最后一次呼叫 得到队列信息
                queueID = record["queueID"]
                queueList = StationMainController().getQueueList({"stationID":stationID, "queueID" :queueID})
                queueInfo = QueueInfoInterface().getInfo({"stationID":stationID, "id" :queueID})
                doingList = queueList["doingList"]
                waitingList = queueList["waitingList"]
                retQueue["listNum"] = len(waitingList)
                retQueue["department"] = workerOnline["department"]
                retQueue["pos"] = selCaller["pos"]
                #获得Seeing数据 从记录中的ID中得到呼叫的患者信息 呼叫显示次数递减
                seeing = StationMainController().getVisitorInfo({"stationID":stationID,"id":record["currentVisitorID"]})
                retlistInfo["seeing"] = {}
                retlistInfo["seeing"]["name"] = seeing["name"]
                retlistInfo["seeing"]["id"] = seeing["snumber"]
                if record["showCnt"] > 0:
                    retlistInfo["seeing"]["show"] = 1
                    record["showCnt"] -= 1
                    callRecordInterface().edit(record)
                else:
                    retlistInfo["seeing"]["show"] = 0

                #获得waiting数据
                retlistInfo["waiting"] = []
                for item in waitingList:
                    waitItem = {}
                    waitItem["name"] = item["name"]
                    waitItem["id"] = item["snumber"]
                    retlistInfo["waiting"].append(waitItem)

            # 获得医生数据
            retWorker["name"] = workerOnline["name"]
            retWorker["id"] = workerOnline["id"]
            retWorker["department"] = workerOnline["department"]
            retWorker["title"] = workerOnline["title"]
            retWorker["headpic"] = workerOnline["headPic"]

            ret["workerInfo"] = retWorker
            ret["queueInfo"] = retQueue
            ret["listInfo"] = retlistInfo
        return ret

    # 获取药房呼叫队列
    def getCallerListPublish(self,inputData):
        retlistInfo = {}
        ret = {}
        stationID = inputData["stationID"]
        callerID = inputData["callerID"]
        callerList = DB.DBLocal.select("caller", where="id=$id", vars={"id": callerID})
        if len(callerList) == 0:
            raise Exception("[ERR]: caller not exists.")
        validDateTime = datetime.datetime.strptime(self.getValidDateTime(), "%Y-%m-%d %H:%M:%S")
        callRecordList = DB.DBLocal.select("callingRecord",
                                         where="stationID=$stationID AND callerID=$callerID AND dateTime>$dateTime",
                                         vars={"stationID": stationID, "callerID": callerID, "dateTime": validDateTime})
        if len(callRecordList) > 0:
            record = callRecordList[0]
            # 从窗口的最后一次呼叫 得到队列信息
            queueID = record["queueID"]
            queueList = StationMainController().getQueueList({"stationID":stationID, "queueID" :queueID})
            queueInfo = QueueInfoInterface().getInfo({"stationID":stationID, "id" :queueID})
            doingList = queueList["doingList"]
            waitingList = queueList["waitingList"]
            retlistInfo["seeingList"] = []
            for item in doingList:
                seeingItem = {}
                seeingItem["name"] = item["name"]
                seeingItem["id"] = item["snumber"]
                retlistInfo["seeingList"].append(seeingItem)

            retlistInfo["watingList"] = []
            for item in waitingList:
                waitItem = {}
                if item["locked"]:
                    continue
                waitItem["name"] = item["name"]
                waitItem["id"] = item["snumber"]
                retlistInfo["watingList"].append(waitItem)
        callRecordList = DB.DBLocal.where("callingRecord", stationID=stationID, callerID=callerID)
        retlistInfo["calling"] = []
        if len(callRecordList) > 0:
            record = callRecordList[0]
            # 病人ID显示为snumber
            currentVisitor = self.stationController.getVisitorInfo(
                {"stationID": stationID, "id": record["currentVisitorID"]})
            calling = {}
            calling["name"] = record["currentVisitorName"]
            calling["id"] = currentVisitor["snumber"]
            calling["pos"] = callerList[0]["pos"]
            retlistInfo["calling"] = calling
        ret = retlistInfo
        return ret

    # def getCallerList(self,inputData):
    #     retList = {"list":[]}
    #     stationID = inputData["stationID"]
    #     callerList = inputData["callerID"]
    #     for caller in callerList:
    #         ret = self.getCallerPublish({"stationID" : stationID, "callerID" : caller})
    #         retList["list"].append(ret)
    #     return retList
    def getCallerList(self, inputData):
        stationID = inputData.get("stationID", None)
        callerList = inputData.get("callerID", None)
        action = inputData.get("action", None)
        if stationID is None:
            raise Exception("[ERR]: stationID required.")
        station = DB.DBLocal.select("stationSet", where="id=$id", vars={"id": stationID})
        if len(station) == 0:
            raise Exception("[ERR]: station not exists.")
        # if not callerList:
        #     raise Exception("[ERR]: callerID required.")
        if action is None:
            raise Exception("[ERR]: action required.")

        # 获取叫号器下的医生、队列等信息
        publishList = []
        result = {}
        for caller in callerList:
            try:
                out = self.getPublishList({"stationID": stationID, "callerID": caller, "action": action})
            except:
                continue
            else:
                if not out: continue
            publishList.append(out)
        result["list"] = publishList
        if not publishList:
            return result

        # 判断叫号器叫号时，是否显示弹窗信息
        current_time = datetime.datetime.now()
        tmp = []
        for item in publishList:
            listInfo = item["listInfo"]
            seeing = listInfo["seeing"]
            if not isinstance(seeing, dict):
                continue
            dateTime = seeing.pop("dateTime", None)
            if not dateTime:
                continue
            interval = (current_time - dateTime).seconds
            if interval < 10:
                tmp.append((interval, seeing))
        tmp.sort(key=lambda x: x[0], reverse=True)
        # tmp的格式类似于：
        # tmp = [(9, seeing), (5, seeing), (4, seeing), (1, seeing)]
        # 然后根据interval的值确定seeing字典中的show的值
        if len(tmp) == 1:
            tmp[0][1]["show"] = 1
        elif len(tmp) ==2 :
            if tmp[0][0] < 5:
                tmp[0][1]["show"] = 1
            else:
                tmp[1][1]["show"] = 1
        elif len(tmp) > 2:
            if tmp[0][0] < 4:
                tmp[0][1]["show"] = 1
            elif tmp[1][0] < 8:
                tmp[1][1]["show"] = 1
            else:
                tmp[2][1]["show"] = 1
        return result

    def getWinList(self,inputData):
        retList = {"list":[]}
        stationID = inputData["stationID"]
        callerList = inputData["callerID"]
        for caller in callerList:
            ret = self.getCallerListPublish({"stationID" : stationID, "callerID" : caller})
            retList["list"].append(ret)
        return retList

    # def getStationList(self,inputData):
    #     retList = {"list": []}
    #     stationID = inputData["stationID"]
    #     callList = CallerInterface().getList({"stationID": stationID })
    #     for item in callList:
    #         ret = self.getCallerPublish({"stationID": stationID ,"callerID" : item["id"]})
    #         if "listInfo" in ret:
    #             if ret["listInfo"] != {}:
    #                 retList["list"].append(ret)
    #     return retList

    def getStationList(self, inputData):
        action = inputData.get("action", None)
        if action is None:
            raise Exception("[ERR]: action required.")
        stationID = inputData.get("stationID", None)
        if stationID is None:
            raise Exception("[ERR]: stationID required.")
        # 这里还是要判断station是否存在，否则删除掉分诊台后，由于不会删除和分诊台相关的其他信息，所以还是会显示
        station = DB.DBLocal.select("stationSet", where="id=$id", vars={"id": stationID})
        if len(station) == 0:
            raise Exception("[ERR]: station not exists.")

        callerList = self.callerInterface.getList({"stationID": stationID})
        callerID = []
        for item in callerList:
            id = item["id"]
            callerID.append(id)
        result = self.getCallerList({"stationID": stationID, "callerID": callerID, "action": action})
        return result

    def getPublishList(self, inputData):
        stationID = inputData.get("stationID", None)
        if stationID is None:
            raise Exception("[ERR]: stationID required.")
        callerID = inputData.get("callerID", None)
        action = inputData.get("action", None)
        if action is None:
            raise Exception("[ERR]: action required.")

        # if can get from Memcached
        key = "_getPublishList_stationID" + str(stationID) +"_callerID"+ str(callerID) + "_action" + action
        value = common.func.CachedGetValue(json.dumps(key))
        if value != False:
            return value

        # TODO： 试验删掉医生的情况
        # 如果获取叫号器信息时发生异常，在上层函数中处理
        caller = self.callerInterface.getInfo({"stationID": stationID, "id": callerID})
        workerID = caller["workerOnline"]
        try:
            workerOnline = self.workerInterface.getInfo({"stationID": stationID, "id": workerID})
            workerInfo = {
                "id": workerOnline["id"],
                "name": workerOnline["name"],
                "title": workerOnline["title"],
                "descText": workerOnline["descText"],
                "department": workerOnline["department"],
                "headpic": workerOnline["headPic"],
                "status": workerOnline["status"],
                "speciality": workerOnline["speciality"]
            }

            if action == 'getStationList' and workerInfo["status"] == "离开":
                return None
        except:
            workerInfo = {"id": "", "name": "", "title": "", "descText": "", "department": "", "headpic": ""}

        # 获取呼叫队列的信息
        queueInfo = {
            "department": workerInfo["department"],
            "pos": caller["pos"],
            "listNum": 0
        }

        # 获取正在就诊、正在排队的信息
        seeing = {"id": "", "name": "", "show": 0, "status": ""}
        waiting = []
        validDateTime = datetime.datetime.strptime(self.getValidDateTime(), "%Y-%m-%d %H:%M:%S")
        callerRecord = DB.DBLocal.select("callingRecord",
                                         where="stationID=$stationID AND callerID=$callerID AND dateTime>$dateTime",
                                         vars={"stationID": stationID, "callerID": callerID, "dateTime": validDateTime})

        try:
            record = callerRecord[0]
            queueID = record["queueID"]
            queue = QueueInfoInterface().getInfo({"stationID": stationID, "id": queueID})
            sceneID = queue["sceneID"]
            scene = SceneInterface().getSceneInfo({"sceneID": sceneID})
            queueList = self.stationController.getQueueList({"stationID": stationID, "queueID": queueID})
        except:
            if action == 'getStationList':
                result = {}
                return result
        else:
            # 获取呼叫队列中当前看诊的信息
            currentVisitor = self.stationController.getVisitorInfo({"stationID": stationID, "id": record["currentVisitorID"]})
            if currentVisitor["status"] == 'doing':
                seeing["id"] = currentVisitor["snumber"]
                seeing["name"] = currentVisitor["name"]
                seeing["status"] = self.getVisitorStatus(**currentVisitor)
                output = scene["output"].split("pos")
                seeing["outputText"] = output[-1]
                seeing["show"] = 0
            seeing["dateTime"] = record["dateTime"]

            # 获取呼叫队列中当前排队的信息
            waitingList = queueList["waitingList"]
            queueInfo.update({"listNum": len(waitingList)})
            for item in waitingList:
                property = str2Json(item["property"])
                if property.get("lock","0") != "0":
                    continue
                waitingVisitor = {}
                waitingVisitor["id"] = item["snumber"]
                waitingVisitor["name"] = item["name"]
                waitingVisitor["status"] = self.getVisitorStatus(**item)
                waiting.append(waitingVisitor)

        result = {}
        result["workerInfo"] = workerInfo
        result["queueInfo"] = queueInfo
        result["listInfo"] = {"seeing": seeing, "waiting": waiting}

        # 缓存 value
        common.func.CahedSetValue(json.dumps(key), result, 3)

        return result

    def getVisitorStatus(self, **kwargs):
        prior = kwargs.get("prior", None)
        locked = kwargs.get("locked", None)
        VIP = kwargs.get("VIP", None)
        localVip = kwargs.get("localVip", None)
        orderType = kwargs.get("orderType", None)

        if locked:
            result = "locked"
        elif prior == 1:
            result = "review"
        elif prior == 2:
            result = "pass"
        elif prior == 3:
            result = "delay"
        elif VIP or localVip:
            result = "VIP"
        elif orderType:
            result = "order"
        else:
            result = "normal"

        return result


class PublishDevInterface:
    """
        电视发布设备接口 声音和显示
    """
    def getInfo(self,inputData):
        stationID = inputData["stationID"]
        ret = DB.DBLocal.where("publish",stationID = stationID)
        return ret

    def Announce(self,dev,cid,text):
        headers = {"Content-Type": "application/json"}
        data = [ {"id": cid, "text": text} ]
        r = requests.post(dev, headers=headers, data=json.dumps(data))
        res = json.loads(r.content)
        return  res

class callRecordInterface:
    """
        呼叫记录的接口
    """
    def __init__(self):
        self.tableName = 'callingRecord'

    def record(self,inputData):
        stationID = inputData["stationID"]
        callerID = inputData["callerID"]
        ret = DB.DBLocal.where(self.tableName, stationID=stationID, callerID=callerID)
        if len(ret) > 0:
            item = ret[0]
            inputData["id"] = item["id"]
            self.edit(inputData)
        else:
            self.add(inputData)

    def getList(self,inputData):
        ret = DB.DBLocal.where(self.tableName, stationID=inputData["stationID"])
        return  ret

    def getInfo(self,inputData):
        ret = DB.DBLocal.where(self.tableName, stationID = inputData["stationID"],callerID = inputData["callerID"])
        return ret[0]

    def add(self,inputData):
        # data = copy.deepcopy(inputData)
        # first = 1
        # sql = "insert into callingRecord ( "
        # for key, v in data.iteritems():
        #     if first != 1:
        #         sql += ','
        #     sql += key
        #     first = 0
        # sql += " ) values ( "
        # first = 1
        # for k, value in data.iteritems():
        #     if first != 1:
        #         sql += ','
        #     sql += '\''
        #     restr = str(value).replace("'", "\\'")
        #     sql += restr
        #     sql += '\''
        #     first = 0
        # sql += ")"
        # print  "auto sql insert callingRecord : sql " + sql
        # ret = DB.DBLocal.query(sql)
        # return ret
        data = dict(copy.deepcopy(inputData))
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        print "INSERT INTO callingRecord"
        result = DB.DBLocal.insert("callingRecord", **values)
        return result

    def delete(self, inputData):
        # id = inputData["id"]
        # try:
        #     filter = "id=" + '\''+ str(id) + '\''
        #     ret = DB.DBLocal.delete('callingRecord',filter)
        #     return ret
        # except Exception, e:
        #     print Exception, ":", e
        #     return -1
        id = inputData.get("id")
        try:
            result = DB.DBLocal.delete("callingRecord", where="id=$id", vars={"id": id})
            return result
        except Exception, e:
            print Exception, ":", e
            return -1

    def edit(self,inputData):
        # data = copy.deepcopy(inputData)
        # first = 1
        # sql = "update callingRecord set "
        # for key, v in data.iteritems():
        #     if key != "id":
        #         if first != 1:
        #             sql += ','
        #         sql += key
        #         restr = str(v).replace("'", "\\'")
        #         sql += ' = ' + '\'' + restr + '\' '
        #         first = 0
        # sql += " where id = " + '\'' + str(data["id"]) + '\' '
        # print  "auto sql update callingRecord : sql " + sql
        #
        # ret = DB.DBLocal.query(sql)
        # return ret
        data = dict(copy.deepcopy(inputData))
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        id = data.get("id")
        result = DB.DBLocal.update("callingRecord", where="id=$id", vars={"id": id}, **values)
        return result
