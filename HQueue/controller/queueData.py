# -*- coding: utf-8 -*-

import web, json, datetime, copy
import common.config as cfg
from common.func import packOutput, checkSession ,str2List,list2Dict,str2Json,json2Str,takeVal,dotdict
from queueInfo import QueueInfoInterface
from scene import SceneInterface
import common.DBBase as DB


finalScoreMax = 1999999999
finalScoreMin = 0
finalScoreDef = finalScoreMax
levelMask = 100000000
POS_STEP = 5
SCORE_STEP = 160
NORMAL_LEVEL = 7
URGENT_LEV1_NUM =  2
URGENT_LEV2_NUM =  3
PRIOR_LEV_NUM = 5  #老幼 > 复诊 > 过号 > 预约 > 普通

class LocalVisitor:
    def __init__(self):
        pass

    @classmethod
    def collectScore(cls,scene,sourceData,localData):  #收集访客的优先信息
        stationID = localData["stationID"]
        queueID = localData["queueID"]
        date = datetime.datetime.strptime("20180101", "%Y%m%d")
        level = LocalVisitor.collectLevel(scene,sourceData, localData)
        rankWay = scene["rankWay"]

        registDateTime = sourceData["registTime"]
        activeLocalTime = localData["activeLocalTime"]
        if rankWay == "snumber":
            num = sourceData["snumber"]
            numStr = str(num) #num.encode('gbk')
            num = int(filter(str.isdigit, numStr))
            score = (level*levelMask) + (num) * SCORE_STEP
        elif rankWay == "registTime":
            second = (registDateTime - date).total_seconds()
            score = (level * levelMask) + int(second) * SCORE_STEP
        else:       # rankWay == "activeTime":
            if activeLocalTime < date:
                second = (registDateTime - date).total_seconds()
            else:
                second = (activeLocalTime - date).total_seconds()
            score = (level * levelMask) + int(second) * SCORE_STEP
        return score

    @classmethod
    def collectLevel(cls,scene,sourceData,localData):  #收集访客的优先信息
        lev1 = sourceData.get("urgent_lev1",0)
        lev2 = max(sourceData.get("urgent_lev2",0),localData.get("urgentLev",0))
        if lev1 is None:
            lev1 = 0
        if lev2 is None:
            lev2 = 0
        URGENT_LEV1_NUM = 2
        URGENT_LEV2_NUM = 3

        level = (URGENT_LEV1_NUM -1 - lev1) * (PRIOR_LEV_NUM ) + (URGENT_LEV2_NUM  - 1 - lev2)
        return level

class QueueDataController:
    #TODO: 门口屏窗体显示只显示本窗口准备的患者
    def getQueueVisitor(self,inputData,status = ["waiting","prepare"]):
        queueID = inputData["queueID"]       #本队列ID
        stationID = inputData["stationID"]
        vars = {
            "stationID" : stationID,
            "queueID" : queueID,
            "status" : status
        }
        filter = "stationID = $stationID and queueID = $queueID and status IN $status"
        visitorRank = DB.DBLocal.select("visitor_local_data", where=filter,vars = vars, order="finalScore,originScore").list()  # 本队列所有访客
        return visitorRank

    def getVisitorList(self,stationID,queueID,status = ["waiting","prepare"]):
        vars = {
            "stationID" : stationID,
            "queueID" : queueID,
            "status" : status
        }
        filter = "stationID = $stationID and queueID = $queueID and status IN $status"
        visitorRank = DB.DBLocal.select("visitor_view_data", where=filter,vars = vars, order="finalScore,originScore").list()  # 本队列所有访客
        return visitorRank

    def getAgePrior(self,visitor_source,scene):
        age = visitor_source.get("age",30)
        oldAge = takeVal(scene,"priorOlderAge",70)
        youngAge = takeVal(scene,"priorCldAge",2)
        if age>oldAge or age <youngAge:
            return "{\"prior\" : \"1\"}"
        else:
            return ""

    def updateVisitor(self, stationID,queueID,queueInfo = None,scene = None, sourceList = None):
        if queueInfo is None:
            queueInfo = QueueInfoInterface().getInfo({"stationID": stationID, "id": queueID})
        sceneID = queueInfo["sceneID"]
        if scene is None:
            scene = SceneInterface().getSceneInfo({"sceneID": sceneID})
        visitorLocalInterface = VisitorLocalInterface(stationID)

        filterStr = str(queueInfo["filter"])
        filterList = filterStr.split(",")
        if sourceList is None:
            where  = "queue IN $filterList or queue = $filterStr"
            sourceList = DB.DBLocal.select("visitor_source_data", where = where,vars = {"filterList" : filterList,"filterStr": filterStr}).list()
        localList = DB.DBLocal.where("visitor_local_data", stationID=stationID)
        localDict = list2Dict(localList)
        # 遍历 sourceList
        for sourceItem in sourceList:
            if str(sourceItem["id"]) not in localDict:
                if isinstance(sourceItem["registTime"],str):
                    registTime = sourceItem["registTime"]
                else:
                    registTime = sourceItem["registTime"].strftime('%Y-%m-%d %H:%M:%S')
                localData = {
                    "id": sourceItem["id"],
                    "name": sourceItem["name"],
                    "registDate": registTime,
                    "stationID": stationID,
                    "queueID": queueID,
                    "activeLocalTime": datetime.datetime(2000,1,1),
                    "property" : self.getAgePrior(sourceItem,scene)
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

        self.sortVisitor(stationID, queueID, scene)

    def sortVisitor(self, stationID, queueID, scene):
        localList = self.getQueueVisitor({"stationID" : stationID,"queueID" : queueID},["waiting","prepare"])
        rankWay = scene["rankWay"]
        waitNum = takeVal(scene,"defaultPrepareNum", 0)
        InsertSeries = takeVal(scene,"InsertPriorSeries", 2)
        InsertInterval = takeVal(scene,"InsertPriorInterval", 3)

        if rankWay in ("snumber", "registTime", "activeTime"):
            pos = 0
            for localItem in localList:
                prior = self.getLevel(localItem)
                if scene["activeLocal"] and localItem["status"] == "unactive":
                    continue
                if localItem["finalScore"] != finalScoreDef:
                    pass
                else:
                    #策略配置中不需要优先延后策略 或普通患者
                    if (waitNum == 0 and InsertInterval == 0) or prior == 0:
                        localItem["finalScore"] = localItem["originScore"] + pos * POS_STEP
                    # 策略配置中配置了优先延后策略 且预约患者
                    else:
                        destPos,destScore = self.getInsertPos(localItem, localList, InsertInterval, InsertSeries, waitNum)
                        localItem["finalScore"] = destScore
                    VisitorLocalInterface(stationID).edit(localItem)
                pos += 1

    def setVisitorStatus(self, stationID, queueID, visitor, action=None):

        # 根据访客所处队列选择的策略信息，获取缓冲人数
        queueInfo = QueueInfoInterface().getInfo({"stationID": stationID, "id": queueID})
        sceneID = queueInfo["sceneID"]
        scene = SceneInterface().getSceneInfo({"sceneID": sceneID})
        scene = dotdict(scene)
        waitNum = scene.defaultPrepareNum
        # 获取队列访客信息，如果等待队列中已经有过号或者复诊的访客，则调整缓冲人数
        visitorList = self.getVisitorList(stationID, queueID)
        visitorNum = len(visitorList)
        if action == "pass" or action == "delay":
            InsertSeries = takeVal(scene,"InsertPassedSeries",2)
            InsertInterval = takeVal(scene,"InsertPassedInterval",3)
        elif action == "review":
            InsertSeries = takeVal(scene,"InsertReviewSeries",2)
            InsertInterval = takeVal(scene,"InsertReviewInterval",3)
        elif action == "prior":
            InsertSeries = takeVal(scene,"InsertPriorSeries",2)
            InsertInterval = takeVal(scene,"InsertPriorInterval",3)
        else:  # default val
            InsertSeries = 2
            InsertInterval = 3

        destPos, destScore = self.getInsertPos(visitor=visitor, vList=visitorList,
                                                                numNormal=InsertInterval,
                                                                numHigher=InsertSeries, numWaitting=waitNum)
        visitor["finalScore"] = destScore

        return visitor

    # 按照患者状态得到细分的优先级 level大优先级高
    def getLevel(self,visitor):
        property = str2Json(visitor.get("property", ""))
        if int(takeVal(property,"prior","0")):
            return 4
        elif int(takeVal(property,"review","0")):
            return 3
        elif int(takeVal(property,"orderType","0")):
            return 2
        elif int(takeVal(property,"delay","0")):
            return 1
        elif int(takeVal(property,"pass","0")):
            return 1
        return 0

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
        if len(vList) == 0:
            minScore = levelMask * NORMAL_LEVEL
        else:
            minScore = vList[0]["finalScore"]
        cntHigherSeries = 0     # 得到最后一个连续特殊患者个数
        numTotalVisitor = 0     # 当前队列的总个数
        vListTemp = list(vList)
        tempNormalLast = 1      #上一个患者是否为常规
        for item in vListTemp:
            if item["finalScore"] == finalScoreDef:
                continue
            if self.getLevel(item) >= level:
                cntHigherLevel += 1
                lastHigherPos = currentPos + 1
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
            posDest = lastHigherPos
        else:
            if cntHigherSeries < numHigher:
                posDest = lastHigherPos
            else:
                posDest = lastHigherPos + numNormal
        # 计算目标分值
        if posDest >= numTotalVisitor:
            posDest = numTotalVisitor
            scoreDest = topScore + SCORE_STEP + POS_STEP
        elif posDest == 0:
            scoreDest = minScore - POS_STEP
        else:
            pre = vListTemp[posDest - 1]["finalScore"]
            next = vListTemp[posDest]["finalScore"]
            scoreDest = (pre + next) / 2
        return posDest,scoreDest

    def getQueueScoreMax(self,station,queueID):
        item = DB.DBLocal.query("SELECT MAX(finalScore) FROM visitor_local_data where queueID = $queueID and \
                status in (\"waiting\",\"doing\",\"finish\")",vars = {"queueID" : queueID}).first()
        if item is not None:
            if item["MAX(finalScore)"] is not None:
                return item["MAX(finalScore)"]
        return 0

    def visitorMoveto(self, data):
        stationID = data["stationID"]
        queueID = data["queueID"]
        vManager = VisitorLocalInterface(stationID)
        vList = data["vid"]
        dest = data["dest"]

        for vid in vList:
            vInfo = vManager.getInfo({"id": vid})
            vInfo["status"] = dest["status"]
            property_json  =  str2Json(vInfo["property"])
            property_json.update({dest["property"] : dest["value"]})
            vInfo["property"] = json2Str(property_json)
            vInfo["tag"] = dest["tag"]
            if vInfo["queueID"] != dest["queueID"]:
                vInfo["queueID"] = dest["queueID"]
                scoreMax = self.getQueueScoreMax(stationID,dest["queueID"])
                if scoreMax == 0:
                    vInfo["finalScore"] = NORMAL_LEVEL * levelMask + POS_STEP
                else:
                    vInfo["finalScore"] = scoreMax +POS_STEP + SCORE_STEP/2
            vManager.edit(vInfo)
        return

    def visitorMoveby(self, data):
        stationID = data["stationID"]
        queueID = data["queueID"]
        vManager = VisitorLocalInterface(stationID)
        vidList = data["vid"]
        value = data["value"]

        for vid in vidList:
            vInfo = vManager.getInfo({"id": vid})
            vList = DB.DBLocal.select("visitor_view_data",where = "queueID = $queueID and \
            status in (\'waiting\',\'prepare\',\'doing\')",vars = {"queueID" : queueID}).list()
            destScore = vInfo["finalScore"]
            pos = 0
            for item in vList:
                if item["id"] == vid:
                    dest = pos + value
                    if dest == len(vList) - 1:
                        destScore = vList[-1].finalScore + POS_STEP + SCORE_STEP/2
                    elif dest == 0:
                        destScore= vList[0].finalScore - POS_STEP - SCORE_STEP/2
                    elif dest > 0 and dest < len(vList) - 1:
                        if value > 0:
                            destScore = (vList[dest].finalScore + vList[dest+1].finalScore ) /2
                        else:
                            destScore = (vList[dest-1].finalScore + vList[dest].finalScore) / 2
                pos += 1
            vInfo.finalScore = destScore
            vManager.edit(vInfo)

        return 1

    def getWaitingNum(self,inputData):
        list = self.getQueueVisitor(inputData,status= ["waiting","prepare"])
        num = 0
        for item in list:
            if item["id"] == inputData["id"]:
                return num
            num += 1
        return 0


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
        stationID = self.stationID
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
