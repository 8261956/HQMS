# -*- coding: utf-8 -*-

import web, json, copy
from common.func import packOutput, list2Str, str2List
from common import DBBase as DB
import common


class SceneInterface(object):

    support_property = {
        "noPrepare": 0,
        "morningPrior": 0,
        "orderNoPrior": 0,
        "autoSyncFinish": 0,
        "callMode": "callByName"
    }

    callMode = ["callByName", "callBySnumber", "callByCardID"]

    def POST(self, data):

        webData = json.loads(web.data())
        action = webData["action"]

        if action == "addScene":
            try:
                result = self.addScene(webData)
                return packOutput(result)
            except Exception as e:
                return packOutput({}, code="400", errorInfo=str(e))

        elif action == "editScene":
            try:
                result = self.editScene(webData)
                return packOutput(result)
            except Exception as e:
                return packOutput({}, code="400", errorInfo=str(e))

        elif action == "getSceneInfo":
            try:
                result = self.getSceneInfo(webData)
                return packOutput(result)
            except Exception as e:
                return packOutput({}, code="400", errorInfo=str(e))

        else:
            return packOutput({}, "500", "unsupport action")

    def addScene(self, inputData):
        values = self.genSceneData(**inputData)
        sceneID = DB.DBLocal.insert("scene", **values)
        result = {"result": "success", "sceneID": sceneID}
        return result

    def editScene(self, inputData):
        sceneID = inputData.get("sceneID", None)
        if sceneID is None:
            raise Exception("[ERR]: sceneID required.")

        sceneList = DB.DBLocal.where("scene", id=sceneID)
        if len(sceneList) == 0:
            raise Exception("[ERR] scene not exists.")

        values = self.genSceneData(**inputData)
        DB.DBLocal.update("scene", where="id=$id", vars={"id": sceneID}, **values)
        result = {"result": "success"}
        return result

    def genSceneData(self, **kwargs):
        sceneName = kwargs.get("name", None)
        if sceneName is None:
            raise Exception("[ERR]: sceneName required.")
        sceneNameText = "%s场景" % sceneName

        activeLocal = kwargs.get("activeLocal")
        tmp = {"0": "不需要", "1": "需要"}
        activeLocalText = "%s本地激活" % tmp[activeLocal]

        rankWay = kwargs.get("rankWay")
        tmp = {"registTime": "挂号时间", "snumber": "序号", "activeTime": "激活时间"}
        rankWayText = "使用%s进行排序" % tmp[rankWay]

        delayTime = kwargs.get("delayTime")
        waitNum = kwargs.get("waitNum")
        passedWaitNum = kwargs.get("passedWaitNum", 2)
        reviewWaitNum = kwargs.get("reviewWaitNum", 2)
        priorNum = kwargs.get("priorNum", 2)
        output = kwargs.get("outputText")
        outputText = "播报请**到**%s" % output
        workDays = kwargs.get("workDays", 1)
        InsertPassedSeries = kwargs.get("InsertPassedSeries", 2)
        InsertPassedInterval = kwargs.get("InsertPassedInterval", 3)
        InsertReviewSeries = kwargs.get("InsertReviewSeries", 2)
        InsertReviewInterval = kwargs.get("InsertReviewInterval", 3)
        InsertPriorSeries = kwargs.get("InsertPriorSeries", 2)
        InsertPriorInterval = kwargs.get("InsertPriorInterval", 3)
        support_property = kwargs.get("property", self.support_property)
        property = []
        for key, value in support_property.items():
            if key == 'callMode':
                property.append(value)
            else:
                if value:
                    property.append(key)

        descText = ', '.join([sceneNameText, activeLocalText, rankWayText, outputText])

        values = {
            "name": sceneName,
            "descText": descText,
            "activeLocal": activeLocal,
            "rankWay": rankWay,
            "delayTime": delayTime,
            "waitNum": waitNum,
            "output": output,
            "passedWaitNum": passedWaitNum,
            "reviewWaitNum": reviewWaitNum,
            "priorNum": priorNum,
            "orderAllow": 0,
            "workDays" : workDays,
            "InsertPassedSeries":  InsertPassedSeries,
            "InsertPassedInterval" : InsertPassedInterval,
            "InsertReviewSeries" : InsertReviewSeries,
            "InsertReviewInterval" : InsertReviewInterval,
            "InsertPriorSeries" : InsertPriorSeries,
            "InsertPriorInterval" : InsertPriorInterval,
            "property" : list2Str(property)
        }

        return values

    def getSceneInfo(self, inputData):
        sceneID = inputData.get("sceneID", None)
        if sceneID is None:
            raise Exception("[ERR]: sceneID required.")

        # if can get from Memcached
        key = "_getSceneInfo_sceneID" +str(sceneID)
        value = common.func.CachedGetValue(json.dumps(key))
        if value != False:
            return value

        sceneList = DB.DBLocal.select("scene", where="id=$id", vars={"id": sceneID})
        if len(sceneList) == 0:
            raise Exception("[ERR]: scene not exists.")

        scene = sceneList[0]
        if not scene["property"]:
            scene["property"] = ""
        property = str2List(scene["property"])
        support_property = copy.deepcopy(self.support_property)
        for item in property:
            if item in self.callMode:
                support_property.update({"callMode": item})
            else:
                if item:
                    support_property.update({item: 1})

        result = {
            "id": scene["id"],
            "name": scene["name"],
            "descText": scene["descText"],
            "activeLocal": scene["activeLocal"],
            "rankWay": scene["rankWay"],
            "delayTime": scene["delayTime"],
            "waitNum": scene["waitNum"],
            "outputText": scene["output"],
            "passedWaitNum": scene["passedWaitNum"],
            "reviewWaitNum": scene["reviewWaitNum"],
            "priorNum": scene["priorNum"],
            "workDays": scene["workDays"],
            "InsertPassedSeries": scene["InsertPassedSeries"],
            "InsertPassedInterval": scene["InsertPassedInterval"],
            "InsertReviewSeries": scene["InsertReviewSeries"],
            "InsertReviewInterval": scene["InsertReviewInterval"],
            "InsertPriorSeries": scene["InsertPriorSeries"],
            "InsertPriorInterval": scene["InsertPriorInterval"],
            # "property" : scene["property"]
            "property": support_property
        }

        # 缓存 value
        common.func.CahedSetValue(json.dumps(key), result, 3)
        return result

    def getSceneInfoByQueueID(self, inputdata):
        stationID = inputdata.get("stationID", None)
        queueID = inputdata.get("queueID", None)
        if stationID is None:
            raise Exception("stationID required")
        if queueID is None:
            raise Exception("queueID required")

        key = {"type": "sceneInfo", "stationID": stationID, "queueID": queueID}
        value = common.func.CachedGetValue(json.dumps(key))
        if value != False:
            return value

        where = {"stationID": stationID, "id": queueID}
        queueInfo = DB.DBLocal.select("queueInfo", where=where).first()
        if not queueInfo:
            raise Exception("queue not exists")
        sceneID = queueInfo["sceneID"]
        scene = self.getSceneInfo({"sceneID": sceneID})

        common.func.CahedSetValue(json.dumps(key), scene, 3)
        return scene
