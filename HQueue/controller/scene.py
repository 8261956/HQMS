# -*- coding: utf-8 -*-

import web, json, copy
from common.func import packOutput,checkPostAction,str2Json,json2Str
from common import DBBase as DB
import common

class SceneInterface(object):
    support_action = {
        "addScene" : "addScene",
        "editScene" : "editScene",
        "getSceneInfo" : "getSceneInfo",
    }

    support_property = {
        "morningPrior": 0,
        "orderNoPrior": 0
    }

    def POST(self, data):
        data = json.loads(web.data())
        return checkPostAction(self, data, self.support_action)

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

        values = {
            "name": kwargs.get("name", None),
            "descText": "",
            "activeLocal": kwargs.get("activeLocal"),
            "rankWay": kwargs.get("rankWay"),
            "output" : kwargs.get("output" , "请$name到$pos就诊"),
            "prepareOutput" : kwargs.get("prepareOutput" , "请$name等候"),
            "soundDoingTimes" : kwargs.get("soundDoingTimes" , 2),
            "soundPrepareTimes": kwargs.get("soundPrepareTimes", 1),
            "autoPrepare" : kwargs.get("autoPrepare", 0),
            "defaultPrepareNum" : kwargs.get("defaultPrepareNum", 1),
            "InsertPassedSeries":  kwargs.get("InsertPassedSeries", 2),
            "InsertPassedInterval" : kwargs.get("InsertPassedInterval", 3),
            "InsertReviewSeries" : kwargs.get("InsertReviewSeries", 2),
            "InsertReviewInterval" : kwargs.get("InsertReviewInterval", 3),
            "InsertPriorSeries" : kwargs.get("InsertPriorSeries", 2),
            "InsertPriorInterval" :  kwargs.get("InsertPriorInterval", 3),
            "priorOlderAge" : kwargs.get("priorOlderAge" , 65),
            "priorCldAge" : kwargs.get("priorCldAge" , 8),
            "workDays": kwargs.get("workDays", 1),

            "property" : json2Str(kwargs.get("property", {}))
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

        sInfo = DB.DBLocal.select("scene", where="id=$id", vars={"id": sceneID}).first()
        if sInfo is None:
            raise Exception("[ERR]: scene not exists.")

        sInfo["property"] = str2Json(sInfo["property"])
        sInfo = dict(sInfo)

        # 缓存 value
        common.func.CahedSetValue(json.dumps(key), sInfo, 3)
        return sInfo

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
