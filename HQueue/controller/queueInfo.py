# -*- coding: utf-8 -*-
import sys

import os, datetime, time, math, web, json, copy, re
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
from common.func import packOutput, str2List, list2Str, checkSession, \
    CachedGetValue, CahedSetValue,json2Str,str2Json
from common.config import integrateType
import common.DBBase as DB
from scene import SceneInterface

class QueueInfoInterface:
    def POST(self,name):

        webData = json.loads(web.data())
        action = webData["action"]
        if "token" in webData:
            token = webData["token"]
            if checkSession(token) == False:
                return packOutput({}, "401", "Tocken authority failed")

        if action == "getList":
            list = self.getList(webData)
            num = len(list)
            resultJson = {"num": num, "list": []}
            for item in list:
                queue = item.copy()
                queue["workerLimit"] = str2List(queue["workerLimit"])
                queue["filter"] = "queue=\'%s\'" %queue["filter"]
                resultJson["list"].append(queue)
            return packOutput(resultJson)

        elif action == "getInfo":
            try:
                queueInfo = self.getInfo(webData)
                queueInfo["workerLimit"] = str2List(queueInfo["workerLimit"])
                queueInfo["filter"] = "queue=\'%s\'" %queueInfo["filter"]
                return packOutput(queueInfo)
            except Exception as e:
                return packOutput({}, code="500", errorInfo=str(e))

        elif action == "add":
            webData["workerLimit"] = list2Str( webData["workerLimit"])
            qFilter = webData["filter"]
            if str(qFilter).startswith("queue="):
                webData["filter"] = qFilter[7:-1]
            ret = self.add(webData)
            return packOutput({})

        elif action == "edit":
            webData["workerLimit"] = list2Str( webData["workerLimit"])
            qFilter = webData["filter"]
            if str(qFilter).startswith("queue="):
                webData["filter"] = qFilter[7:-1]
            id = self.edit(webData)
            return packOutput({})

        elif action == "delete":
            ret = self.delete(webData)
            if ret == -1:
                resultJson = {"result": "failed"}
            else:
                resultJson = {"result": "success"}
            return packOutput(resultJson)

        elif action == "getSourceQueueList":
            ret= self.getSourceQueueList(webData)
            jsonData = {"num":len(ret), "list": ret}
            return packOutput(jsonData)

        elif action == "getSceneSupportList":
            ret = self.getSceneSupportList(webData)
            list = []
            for item in ret:
                list.append(item)
            jsonData = {"num":len(ret), "list":list}
            return packOutput(jsonData)

        elif action == "getAvgWaitTime":
            try:
                result = self.getAvgWaitTime(webData)
                return packOutput(result)
            except Exception as errorInfo:
                return packOutput({}, code="400", errorInfo=str(errorInfo))

        elif action == "fuzzySearchQueue":
            try:
                result = self.fuzzySearchQueue(webData)
                return packOutput(result)
            except Exception as errorInfo:
                return packOutput({}, code="400", errorInfo=str(errorInfo))
        elif action == "getWorkerLimit":
            try:
                result = self.getWorkerLimit(webData)
                return packOutput(result)
            except Exception as errorInfo:
                return packOutput({}, code="400", errorInfo=str(errorInfo))
        elif action == "changeWorkerLimit":
            try:
                result = self.changeWorkerLimit(webData)
                return packOutput(result)
            except Exception as errorInfo:
                return packOutput({}, code="400", errorInfo=str(errorInfo))

        else:
            return packOutput({}, "500", "unsupport action")

    def getList(self,inputData):
        # ret = DB.DBLocal.where('queueInfo', stationID=inputData["stationID"])
        stationID = inputData["stationID"]
        sql = "SELECT q.id, q.name, q.stationID, q.descText, q.filter, " \
              "q.workerOnline, q.workerLimit, q.department, q.isExpert, " \
              "s.id as sceneID, s.name as scene, s.activeLocal " \
              "FROM queueInfo AS q LEFT JOIN scene " \
              "AS s ON q.sceneID = s.id WHERE q.stationID=%s" % stationID
        ret = DB.DBLocal.query(sql)
        return  ret

    def getInfo(self,inputData):
        # TODO: 如果队列的orderAllow属性以后要放在策略配置中，那此处的查询语句要修改
        # TODO: 如果手动在数据库中删除策略，也应该要能获取到队列信息(sceneID在scene表中不存在如何处理)
        stationID = inputData["stationID"]
        id = inputData["id"]

        # 获取缓存
        key = {"type": "queueInfo", "queueID": id, "stationID": stationID}
        value = CachedGetValue(json.dumps(key))
        if value != False:
            return value

        sql = "SELECT q.id, q.name, q.stationID, q.descText, q.filter, " \
              "q.workerOnline, q.workerLimit, q.department, q.isExpert, " \
              "s.id as sceneID, s.name as scene, s.activeLocal " \
              "FROM queueInfo AS q LEFT JOIN scene " \
              "AS s ON q.sceneID = s.id WHERE q.id=%s" % id
        # ret = DB.DBLocal.where('queueInfo', stationID=inputData["stationID"],id = inputData["id"])
        ret = DB.DBLocal.query(sql).first()
        if not ret:
            raise Exception("[ERR]: queue not exists.")

        # 缓存 value
        CahedSetValue(json.dumps(key), ret, 3)

        return ret

    def checkQueueInfo(self,queue):
        """
        根据患者队列关键字获取队列信息   患者队列关键字是队列队列关键字中的一项
        :param queue: 患者队列关键字
        :return: 所属队列信息
        """
        qList = DB.DBLocal.select("queueInfo").list()
        for item in qList:
            fstr = item.get("filter","")
            if queue == fstr:
                return item
            fList = fstr.split(",")
            if queue in fList:
                return item
        return None


    def loadScenePara(self,inputData):
        sceneList = DB.DBLocal.where("scene", name = inputData["scene"])
        scene = sceneList[0]
        inputData["activeLocal"] = scene["activeLocal"]
        inputData["orderAllow"] = scene["orderAllow"]
        inputData["rankWay"] = scene["rankWay"]
        #inputData["output"] =

    def getSourceQueueList(self,inputData):
        stationID = inputData["stationID"]
        if integrateType == "VIEW":
            from station import importConfigInterface
            res = importConfigInterface().getSourceDistinct(stationID)
            sourceQueueList = []
            for item in res:
                sourceQueueList.append(item["queue"])
            choseQueueList = self.getChoseQueueList(stationID)
            print sourceQueueList
            print choseQueueList
            queueList = list(set(sourceQueueList) - set(choseQueueList))
            return queueList
        elif integrateType == "WEBSERVICE":
            sys.path.append("../..")
            from project.yaxin.YX_Interface import ExternSourceQueueList
            print "import YX_Interface ok "
            sourceQueueList = ExternSourceQueueList()
            choseQueueList = self.getChoseQueueList(stationID)
            queueList = sourceQueueList#list(set(sourceQueueList) - set(choseQueueList))
            return queueList

    def getChoseQueueList(self, stationID):
        queueList = self.getList({"stationID": stationID})
        choseQueueList = []
        for item in queueList:
            # TODO: 验证改动的影响
            filter = item["filter"].split(",")
            choseQueueList.append(filter)
        return choseQueueList

    def getSceneSupportList(self,inputData):
        sceneList = DB.DBLocal.select("scene",what="id,name,descText")
        return sceneList

    def add(self,inputData):
        data = dict(copy.deepcopy(inputData))
        data.pop("token", None)
        data.pop("action", None)
        data.pop("scene", None)
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        print "INSERT INTO queueInfo"
        result = DB.DBLocal.insert("queueInfo", **values)
        return result

    def delete(self, inputData):
        id = inputData.get("id")
        try:
            result = DB.DBLocal.delete("queueInfo", where="id=$id", vars={"id": id})
            return result
        except Exception, e:
            print Exception, ":", e
            return -1

    def edit(self,inputData):
        data = dict(copy.deepcopy(inputData))
        data.pop("token", None)
        data.pop("action", None)
        data.pop("scene", None)
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        id = values.get("id")
        print "UPDATE queueInfo"
        result = DB.DBLocal.update("queueInfo", where="id=$id", vars={"id": id}, **values)
        return result

    def getAvgWaitTime(self, inputData):
        stationID = inputData.get("stationID", None)
        if stationID is None:
            raise Exception("stationID required.")
        queueID = inputData.get("queueID", None)
        if queueID is None:
            raise Exception("queueID required.")
        queueList = DB.DBLocal.where("queueInfo", stationID=stationID, id=queueID)
        if len(queueList) == 0:
            raise Exception("queue not exists.")

        backupDate = datetime.date.today() - datetime.timedelta(days=60)
        sqlLocalData = "SELECT id, workStartTime, workEndTime FROM visitor_local_data " \
                       "WHERE stationID=%s AND queueID=%s" % (stationID, queueID)
        sqlBackupData = "SELECT id, workStartTime, workEndTime FROM visitor_backup_data " \
                        "WHERE stationID=%s AND queueID=%s AND registDate>='%s'"\
                        % (stationID, queueID, backupDate)
        sql = "(%s) UNION ALL (%s)" % (sqlLocalData, sqlBackupData)
        visitorList = DB.DBLocal.query(sql)

        waitTimeList = []
        count = 0
        for visitor in visitorList:
            try:
                id = visitor["id"]
                workStartTime = visitor["workStartTime"]
                workEndTime = visitor["workEndTime"]
                waitTime = (workEndTime - workStartTime).total_seconds()
                if waitTime <= 0:
                    print "[ignored] visitor %s error: workEndTime should larger than workStartTime" % id
                    count += 1
                    continue
                if waitTime >= 36000:
                    print "[ignored] visitor %s error: workEndTime is much larger" % id
                    count += 1
                    continue
                waitTimeList.append(waitTime)
            except (ValueError, TypeError) as e:
                print "[ignored] visitor %s error: %s" % (id, str(e))
                count += 1
                continue

        print "[station %s, queue %s] total visitors: %d, ignored: %d" % \
              (stationID, queueID, len(visitorList), count)
        if len(waitTimeList) == 0:
            avgWaitTime = 0
        else:
            tmp = (sum(waitTimeList)/len(waitTimeList))/60.0
            avgWaitTime = math.ceil(tmp)
        result = {"stationID": stationID, "queueID": queueID, "avgWaitTime": str(avgWaitTime)}
        return result

    def getInfoByFilter(self, inputData):
        queue = inputData.get("queue")
        queueInfo = self.checkQueueInfo(queue)
        if queueInfo is None:
            raise Exception("[ERR] queue not exists for filter: {0}".format(queue))
        result = queueInfo
        return result

    def getWorkerLimit(self, inputData):
        queueInfo = self.getInfo(inputData)
        workerLimit = str2List(queueInfo["workerLimit"])

        departments = []
        result = []
        if not workerLimit:
            return result
        workerInfo = DB.DBLocal.select("workers", where="id IN $workerLimit",
                                       vars={"workerLimit": workerLimit},
                                       order="department")

        workerInfo = workerInfo.list()
        for item in workerInfo:
            department = item["department"]
            if department not in departments:
                departments.append(department)

        for d in departments:
            tmp = {"department": d, "workers": []}
            for item in workerInfo:
                if item["department"] == d:
                    id = item["id"]
                    name = item["name"]
                    worker = {"id": id, "name": name}
                    tmp["workers"].append(worker)
                else:
                    continue
            result.append(tmp)
        return result

    def updateWorkerLimit(self, inputData):
        stationID = inputData.get("stationID", None)
        if stationID is None:
            raise Exception("[ERR]: stationID required")
        queueID = inputData.get("queueID", None)
        if queueID is None:
            raise Exception("[ERR]: queueID required")
        workers = inputData.get("workers")
        if not isinstance(workers, list):
            raise Exception("[ERR]: workers should be a list")
        queueInfo = DB.DBLocal.select("queueInfo", where="stationID=$stationID AND id=$queueID",
                                      vars={"stationID": stationID, "queueID": queueID})
        if len(queueInfo) == 0:
            raise Exception("[ERR]: queue not exists")
        queue = queueInfo[0]
        if not queue["workerLimit"]:
            workerLimit = []
        else:
            workerLimit = str2List(queue["workerLimit"])
        try:
            for worker in workers:
                if worker in workerLimit:
                    continue
                else:
                    workerLimit.append(worker)
                    workerLimit_str = list2Str(workerLimit)
                    DB.DBLocal.update("queueInfo", where="stationID=$stationID AND id=$queueID",
                                      vars={"stationID": stationID, "queueID": queueID},
                                      workerLimit=workerLimit_str)
        except:
            raise
        else:
            result = {"result": "success"}
            return result

    def changeWorkerLimit(self, inputData):
        stationID = inputData.get("stationID", None)
        if stationID is None:
            raise Exception("[ERR]: stationID required")
        queueID = inputData.get("queueID", None)
        if queueID is None:
            raise Exception("[ERR]: queueID required")
        workers = inputData.get("workers")
        if not isinstance(workers, list):
            raise Exception("[ERR]: workers should be a list")
        queueInfo = DB.DBLocal.select("queueInfo", where="stationID=$stationID AND id=$queueID",
                                      vars={"stationID": stationID, "queueID": queueID})
        if len(queueInfo) == 0:
            raise Exception("[ERR]: queue not exists")
        try:
            workerLimit = list2Str(workers)
            DB.DBLocal.update("queueInfo", where="stationID=$stationID AND id=$queueID",
                              vars={"stationID": stationID, "queueID": queueID},
                              workerLimit=workerLimit)
        except:
            raise
        else:
            result = {"result": "success"}
            return result

    def fuzzySearchQueue(self, inputData):
        keyword = inputData.get("keyword")
        queueList = DB.DBLocal.select("queueInfo", what="id, stationID, name, filter")
        collection = []
        suggestions = []
        for queue in queueList:
            queue = dict(queue)
            collection.append(queue)
        pattern = '.*?'.join(keyword)
        regex = re.compile(pattern)
        for item in collection:
            filter = item["filter"]
            #TODO: 验证改动的影响
            filter = filter.spilt(",") #re.findall(r'queue=\'(.*)\'', filter)
            queue = filter[0]
            tmp = queue + item["name"]
            match = regex.search(tmp)
            if match:
                suggestions.append((len(match.group()), match.start(), item))
        result = [x for _, _, x in sorted(suggestions)]
        return result

    def getWorkDays(self,stationID,queueID):
        queueInfo = self.getInfo({"stationID":stationID ,"id":queueID})
        sceneID = queueInfo["sceneID"]
        sceneInfo = SceneInterface().getSceneInfo({"sceneID":sceneID})
        workDays = sceneInfo["workDays"]
        if not workDays >= 1 :
            workDays = 1
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=(-workDays+1))
        n_days = now + delta
        date = n_days.strftime("%Y%m%d")
        return workDays,date

    def addWorkerOnline(self,queueID,workerID):
        queue = DB.DBLocal.where('queueInfo', id=queueID).first()
        if queue is None:
            raise "queue %d not exist" %queueID
        workerOnline = str2List(queue["workerOnline"])
        if workerID not in workerOnline:
            workerOnline.append(workerID)
            queue["workerOnline"] = list2Str(workerOnline)
            self.edit(queue)