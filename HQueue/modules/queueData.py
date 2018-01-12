# -*- coding: utf-8 -*-

import web, json, datetime, copy
import common.config as cfg
from common.func import packOutput, checkSession ,str2List,list2Dict
from queueInfo import QueueInfoInterface
from scene import SceneInterface
import HQueue.DBIO.DBBase as DB


finalScoreMax = 999999999
finalScoreMin = 0
finalScoreDef = finalScoreMax
levelMask = 100000000

class LocalVisitor:
    def __init__(self):
        pass

    @classmethod
    def collectScore(cls,scene,sourceData,localData):  #收集访客的优先信息
        stationID = localData["stationID"]
        queueID = localData["queueID"]
        workDays, date = QueueInfoInterface().getWorkDays(stationID, queueID)
        date = datetime.datetime.strptime(date, "%Y%m%d")
        level = LocalVisitor.collectLevel(scene,sourceData, localData)
        rankWay = scene["rankWay"]

        registDateTime = sourceData["registTime"]
        activeLocalTime = localData["activeLocalTime"]
        if rankWay == "snumber":
            num = sourceData["snumber"]
            # TODO: V1.21  Test. scene property add morningPrior
            sceneProperty = str2List(scene.get("property", ""))
            if "morningPrior" in sceneProperty:
                if registDateTime.hours >= 12:
                    level = level + 1
            score = (level*levelMask) + (num) * 160
        elif rankWay == "registTime" or rankWay == "registTimeAndSmart":
            second = (registDateTime - date).total_seconds()
            score = (level * levelMask) + int(second) * 160
        else:
            if activeLocalTime < date:
                second = (registDateTime - date).total_seconds()
            else:
                second = (activeLocalTime - date).total_seconds()
            score = (level * levelMask) + int(second) * 160
        return score

    @classmethod
    def collectLevel(cls,scene,sourceData,localData):  #收集访客的优先信息
        level = 7
        if sourceData["VIP"] == 1 or localData["vip"] == 1:
            level = 1
        elif (sourceData["orderType"] != 0) and (sourceData["orderType"] is not None):  #访客为预约访客
            # TODO: V1.21  scene property add orderNoPrior
            sceneProperty = str2List(scene.get("property", ""))
            if "orderNoPrior" in sceneProperty:
                level = 7
            else:
                level = 3
        else:
            level = 7
        return level

    def load(self,sourceData,localData):
        pass

class QueueDataController:

    def POST(self,name):
        webData = json.loads(web.data())
        action = webData["action"]

        if "token" in webData:
            token = webData["token"]
            if checkSession(token) == False:
                return packOutput({}, "401", "Tocken authority failed")

        if action == "getListWaiting":
            ret = self.getQueueVisitor(webData)
            jsonData = {"num":len(ret), "list": []}
            for item in ret:
                visitor = {}
                visitor["id"] = item["id"]
                visitor["name"] = item["name"]
                visitor["status"] = item["status"]
                visitor["originScore"] = item["originScore"]
                visitor["finalScore"] = item["finalScore"]
                visitor["originLevel"] = item["originLevel"]
                jsonData["list"].append(visitor)
            return packOutput(jsonData)

        elif action == "getListUnactive":
            pass

        elif action == "getListOver":
            pass

        else:
            return packOutput({}, "500", "unsupport action")

    def getQueueVisitor(self,inputData,status = "waiting"):
        # moved updateVisitor to sync process
        #self.updateVisitor(inputData)
        queueID = inputData["queueID"]       #本队列ID
        stationID = inputData["stationID"]
        filter = "stationID = " + str(stationID) + " and queueID = " + str(queueID) + " and status = \'" + status + "\'"
        visitorRank = DB.DBLocal.select("visitor_local_data", where=filter, order="finalScore,originScore")  # 本队列所有访客
        return visitorRank

    def updateVisitor(self, inputData):
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]

        queueInfo = QueueInfoInterface().getInfo({"stationID": stationID, "id": queueID})
        sceneID = queueInfo["sceneID"]
        scene = SceneInterface().getSceneInfo({"sceneID": sceneID})
        visitorLocalInterface = VisitorLocalInterface(stationID)

        filter = str(queueInfo["filter"])
        sourceList = DB.DBLocal.where("visitor_source_data", queue = filter)
        sourceList = list(sourceList)
        localList = DB.DBLocal.where("visitor_local_data", stationID=stationID ,queueID = queueID)
        localDict = list2Dict(localList)
        # 遍历 sourceList
        for sourceItem in sourceList:
            if str(sourceItem["id"]) not in localDict:
                localData = {
                    "id": sourceItem["id"],
                    "name": sourceItem["name"],
                    "registDate": sourceItem["registDate"],
                    "stationID": stationID,
                    "queueID": queueID,
                    "activeLocal": 0,
                    "activeLocalTime": datetime.datetime(2000,1,1),
                    "prior": 0,
                    "vip": 0,
                    "locked": 0
                }
                status = "unactive" if scene["activeLocal"] else "waiting"
                originLevel = LocalVisitor.collectLevel(scene, sourceItem, localData)
                originScore = LocalVisitor.collectScore(scene, sourceItem, localData)
                finalScore = finalScoreDef
                localData.update({
                    "status": status,
                    "originLevel": originLevel,
                    "originScore": originScore,
                    "finalScore": finalScore
                })
                localDict[str(sourceItem["id"])] = localData
                visitorLocalInterface.add(localData)
            else:
                localData = localDict[str(sourceItem["id"])]
                # 更新访客的分数
                originScore = LocalVisitor.collectScore(scene, sourceItem, localData)
                originLevel = LocalVisitor.collectLevel(scene, sourceItem, localData)
                if localData["originScore"] != originScore or localData["originLevel"] != originLevel:
                    localData.update({
                        "originLevel": originLevel,
                        "originScore": originScore,
                        "finalScore": finalScoreDef
                    })
                    localDict[str(sourceItem["id"])] = localData
                    visitorLocalInterface.edit(localData)

                # 如果队列需要激活且访客处于等待激活的状态，根据激活时间更新访客的状态
                if scene["activeLocal"] and localData["status"] == "unactivewaiting":
                    now = datetime.datetime.now()
                    activeTime = localData["activeLocalTime"]
                    interval = (now - activeTime).total_seconds()
                    if interval >= scene["delayTime"] * 60:
                        localData.update({"status": "waiting"})
                    visitorLocalInterface.edit(localData)

        self.sortVisitor(stationID, queueID, scene)

    def sortVisitor(self, stationID, queueID, scene):
        filter = "stationID=%s and queueID=%s" % (str(stationID), str(queueID))
        ret = DB.DBLocal.select("visitor_local_data", where=filter, order="finalScore, originScore")
        localList = list(ret)
        rankWay = scene["rankWay"]

        if rankWay in ("snumber", "registTime", "activeTime"):
            pos = 0
            priorWaitNum = scene.get("priorNum", 0)
            InsertSeries = scene.get("InsertPriorSeries", 2)
            InsertInterval = scene.get("InsertPriorInterval", 3)

            for localItem in localList:
                if scene["activeLocal"] and not localItem["activeLocal"]:
                    continue
                if localItem["finalScore"] != finalScoreDef:
                    pass
                else:
                    #策略配置中不需要优先延后策略 或普通患者
                    if (priorWaitNum == 0 and InsertInterval == 0) or localItem["originLevel"] != 3:
                        localItem["finalScore"] = localItem["originScore"] + pos * 5
                    # 策略配置中配置了优先延后策略 且预约患者
                    else:
                        localItem["prior"] = 4
                        destPos,destScore = self.getInsertPos(localItem, localList, InsertInterval, InsertSeries, priorWaitNum)
                        localItem["finalScore"] = destScore
                    VisitorLocalInterface(stationID).edit(localItem)
                pos += 1

        elif rankWay == "registTimeAndSmart":
            pos = 0
            orderPos = 0
            normalPos = 0
            for localItem in localList:
                if scene["activeLocal"] == 0 or localItem["activeLocal"] == 1:
                    if localItem["finalScore"] != finalScoreDef:
                        currentScore = localItem["finalScore"]
                        if localItem["originLevel"] == 3:
                            orderPos = (currentScore / 100) * 3 + (currentScore % 100) / 20
                        if localItem["originLevel"] == 7:
                            normalPos = currentScore / 100
                    else:
                        if localItem["originLevel"] == 1:
                            localItem["finalScore"] = 0
                        elif localItem["originLevel"] == 3:
                            orderPos += 1
                            if orderPos % 3 == 0:
                                orderPos += 1
                            localItem["finalScore"] = (orderPos / 3) * 100 + (orderPos % 3) * 20
                        elif localItem["originLevel"] == 7:
                            normalPos += 1
                            localItem["finalScore"] = 100 * normalPos
                        VisitorLocalInterface(stationID).edit(localItem)
                    pos += 1

    # 按照患者状态得到细分的优先级 level大优先级高
    def getLevel(self,visitor):
        level = 0
        if visitor["prior"] == 1:   #"review"
            level = 2
        elif visitor["prior"] == 2: #"pass"
            level = 1
        elif visitor["prior"] == 3: #"delay"
            level = 1
        elif visitor["prior"] == 4: #order
            level = 3
        return  level

    # 按照优先级 和策略计算插入在队列中的位置
    def getInsertPos(self,visitor,vList,numNormal,numHigher,numWaitting):
        if numNormal is None:
            numNormal = 3
        if numHigher is None:
            numHigher = 2
        if numWaitting is None:
            numWaitting = 0
        #先得到当前队列中优先级高于本优先级的总数，
        level = self.getLevel(visitor)
        cntHigherLevel = 0      # 队列中高优先级患者计数
        cntNormalStart = 0      # 队列中低优先级患者计数
        lastHigherPos = 0       #队列中最后一位高优先级患者的位置
        currentPos = 0          #位置指针
        posDest = 0             #目标位置
        scoreDest = 0           #目标分值
        topScore = 0            #队列最高分值
        cntHigherSeries = 0     # 得到最后一个连续特殊患者个数
        numTotalVisitor = 0     # 当前队列的总个数
        vListTemp = list(vList)
        tempNormalLast = 1      #上一个患者是否为常规
        for item in vListTemp:
            if item["finalScore"] == finalScoreDef:
                continue
            if self.getLevel(item) >= level:
                cntHigherLevel += 1
                lastHigherPos = currentPos
                if tempNormalLast:
                    cntHigherSeries = 1
                else:
                    cntHigherSeries += 1
                tempNormalLast = 0
            #同时得到第一个特殊患者前普通患者的个数
            else:
                if cntHigherLevel == 0:
                    cntNormalStart += 1
                tempNormalLast = 1
            if item["finalScore"] > topScore:
                topScore = item["finalScore"]
            #同时得到最后一个特殊患者的位置
            currentPos += 1
            if  item["finalScore"] != finalScoreDef:
                numTotalVisitor += 1
        #计算得到当前应当插入的位置
        if lastHigherPos == 0:
            posDest = numWaitting
        elif cntHigherLevel < numHigher:
            posDest = lastHigherPos + 1
        else:
            if cntHigherSeries < numHigher:
                posDest = lastHigherPos + 1
            else:
                posDest = lastHigherPos + numNormal + 1
        # 计算目标分值
        if posDest >= numTotalVisitor:
            posDest = numTotalVisitor
            scoreDest = topScore + 5
        elif posDest == 0:
            scoreDest = levelMask * 7 + (15 -level) * 10
        else:
            pre = vListTemp[posDest - 1]["finalScore"]
            next = vListTemp[posDest]["finalScore"]
            scoreDest = (pre + next) / 2
        return posDest,scoreDest

    def getVisitorScore(self,stationID,queueID,visitorID):
        list = DB.DBLocal.where('visitor_local_data', id = visitorID)
        visitor = list[0]
        ret = {}
        if visitor["status"] == "unactive" or visitor["status"] == "finish" or visitor["status"] == "pass":
            ret["finalScore"] = finalScoreDef
            ret["finalScoreUp"] = finalScoreDef
            ret["finalScoreDown"] = finalScoreDef
        else:
            ret["finalScore"] = visitor["finalScore"]
            list = self.getQueueVisitor({"stationID":stationID,"queueID":queueID},"waiting")
            ret["finalScore"] = ret["finalScoreUp"] = ret["finalScoreDown"] = finalScoreDef
            if len(list) == 0:
                return ret
            iterp = iter(list)
            ret["finalScoreUp"] = 0
            for item in list:
                if item["id"] == visitorID:
                    ret["finalScore"] = item["finalScore"]
                    try:                #判断是否还有下一个
                        next = iterp.next()
                        ret["finalScoreDown"] = next["finalScore"]
                    except:
                        ret["finalScoreDown"] = ret["finalScore"] + 100
                    break
                ret["finalScoreUp"] = item["finalScore"]
            return ret

    def visitorMoveto(self,inputData):
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]
        id = inputData["id"]
        dest = inputData["dest"]
        visitor = {}
        visitor["id"] = id
        visitor["stationID"] = stationID
        visitor["queueID"] = dest["queueID"]
        visitor["status"] = dest["status"]
        if dest["id"] == "":
            if dest["queueID"] != queueID:
                vInfo = DB.DBLocal.where('visitor_local_data', id=id).first()
                visitor["finalScore"] = vInfo["originScore"]
        else:
            destScore = self.getVisitorScore(stationID,dest["queueID"],dest["id"])
            visitor["finalScore"] = (destScore["finalScore"] + destScore["finalScoreUp"]) / 2
        VisitorLocalInterface(stationID).edit(visitor)
        return

    def visitorMoveby(self, inputData):
        stationID = inputData["stationID"]
        queueID = inputData["queueID"]
        id = inputData["id"]
        val = inputData["value"]
        visitor = {}
        visitor["id"] = id
        visitor["stationID"] = stationID
        ret = self.getQueueVisitor({"stationID":stationID,"queueID":queueID},"waiting")
        list = []
        pos = 0
        destPos = 0
        found = 0
        for item in ret:
            if item["id"] == id:
                found = 1
                destPos = pos
            pos += 1
            list.append(item)
        if found == 0:
            return 0
        destPos =  destPos + val
        if destPos >= len(ret):
            destPos = len(ret) - 1
        if destPos < 0:
            destPos = 0
        destVist = list[destPos]
        destScore = self.getVisitorScore(stationID,queueID,destVist["id"])
        if val >= 0:
            visitor["finalScore"] = (destScore["finalScore"] + destScore["finalScoreDown"]) / 2
        else:
            visitor["finalScore"] = (destScore["finalScore"] + destScore["finalScoreUp"]) / 2
        VisitorLocalInterface(stationID).edit(visitor)
        return 1

    def getWaitingNum(self,inputData):
        list = self.getQueueVisitor(inputData)
        num = 0
        for item in list:
            if item["id"] == inputData["id"]:
                return num
            num += 1
        return 0

    def isRankLoad(self,pos,scene):

        pass


class VisitorLocalInterface:
    def __init__(self,stationID):
        self.stationID = stationID
    def getList(self,inputData):
        ret = DB.DBLocal.where('visitor_local_data', queue=inputData["queue"])
        return  ret

    def getInfo(self,inputData):
        ret = DB.DBLocal.where('visitor_local_data', id = inputData["id"],stationID = self.stationID)
        return ret[0]

    def add(self,inputData):

        data = dict(copy.deepcopy(inputData))
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        print "INSERT INTO visitor_local_data"
        result = DB.DBLocal.insert("visitor_local_data", **values)
        return result

    def delete(self, inputData):

        id = inputData.get("id")
        stationID = self.stationID
        try:
            result = DB.DBLocal.delete("visitor_local_data",
                                       where="id=$id and stationID=$stationID",
                                       vars={"id": id, "stationID": stationID})
            return result
        except Exception, e:
            print Exception, ":", e
            return -1

    def edit(self,inputData):

        data = dict(copy.deepcopy(inputData))
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        id = values.get("id")
        stationID = values.get("stationID")
        print "UPDATE visitor_local_data: [Station]%s, [ID]%s" % (stationID, id)
        result = DB.DBLocal.update("visitor_local_data",
                                   where="id=$id and stationID=$stationID",
                                   vars={"id": id, "stationID": stationID}, **values)
        #source_update = {"queueID": values["queueID"]}
        # TODO: 重要！！ 核对此处注释问题，患者转移时会不会影响，视图应该使用右连接？
        """
        DB.DBLocal.update("visitor_source_data",
                          where="id=$id and stationID=$stationID",
                          vars={"id": id, "stationID": stationID},
                          **source_update)
        """
        return result
