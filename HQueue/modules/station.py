# -*- coding: UTF-8 -*-

import web, json,copy
from common.func import packOutput, checkSession,getNecessaryPara
import HQueue.DBIO.DBBase as DB
from HQueue.DBIO.DBBase import ImportTableFromView
from common.config import integrateType
from account import StationAccount

visitor_para_name =  ("id","name","age","queue", "snumber" ,"orderDate","orderTime" ,"registDate", "registTime" , "VIP" ,
                      "orderType","workerID","workerName","descText","status","department","cardID","personID",
                      "phone","rev1","rev2","rev3","rev4","rev5","rev6")

visitor_alias_name =  {"id" : "aliasID","name" : "aliasName","age" : "aliasAge","queue" : "aliasQueue", "snumber" : "aliasSnumber"  ,
                       "orderDate" :"aliasOrderDate" ,"orderTime" :"aliasOrderTime" ,"registDate" : "aliasRegistDate", "registTime" :"aliasRegistTime", "VIP" :"aliasVIP",
                      "orderType" : "aliasOrderType","workerID" : "aliasWorkerID","workerName" : "aliasWorkerName","descText" : "aliasDescText","status" : "aliasStatus"
                      ,"department" : "aliasDepartment","cardID" : "aliasCardID","personID" : "aliasPersonID",
                      "phone" : "aliasPhone"}


class importConfigInterface:
    db = DB.DBLocal
    def getInfo(self,data):
        type = getNecessaryPara(data, "type")
        source = self.db.select("import_config", where={"type": type}).first()
        return source

    def add(self,type,data):
        para = {}
        for key, val in visitor_alias_name.iteritems():
            if val in data:
                para[key] = data[val]
                data.pop(val)
        data.update(para)
        importFunc = ImportTableFromView(self, type, visitor_para_name)
        importFunc.testImportSource(data)
        res = importFunc.testImportSourceConfig(data)
        return res

    def ifAdd(self,type,data):
        source = importConfigInterface().getInfo({"type":type})
        if source is None:
            result = self.add(type,data)
            return result

    def sourceTest(self,type,data):
        para = {}
        for key, val in visitor_alias_name.iteritems():
            if val in data:
                para[key] = data[val]
                data.pop(val)
        data.update(para)
        importFunc = ImportTableFromView(self, type, visitor_para_name)
        importFunc.testImportSource(data)
        res = importFunc.testImportSourceConfig(data)
        return res

    def getSourceDistinct(self,stationID):
        s = self.db.select("stationSet",where = {"id":stationID}).first()
        type = s["importSource"]
        importFunc = ImportTableFromView(self, type, visitor_para_name)
        dbSource,sqlView = importFunc.getSource()
        ret = dbSource.select(sqlView,what="DISTINCT(queue)")
        return ret


class StationInterface:
    def __init__(self):
        self.db = DB.DBLocal
        self.accout = StationAccount()
        pass

    def POST(self,name):
        webData = json.loads(web.data())
        action = webData["action"]
        if "token" in webData:
            token = webData["token"]
            if checkSession(token) == False:
                return packOutput({}, "401", "Tocken authority failed")

        if action == "getList":
            slist = self.getList()
            num = len(slist)
            if num == -1:
                return packOutput({},"500", "getStationList Error")
            else:
                resultJson = {"stationNum": num, "stationList": []}
                for item in slist:
                    station = {}
                    station['id'] = item["id"]
                    station['name'] = item["name"]
                    resultJson['stationList'].append(station)
                print " get stationList func ok ,station num " + str(num)
                return packOutput(resultJson)

        elif action == "getInfo":
            print (" Controller get stationInfo ")
            req = json.loads(web.data())
            stationID = req["stationID"]

            ret = self.getInfo({"id":stationID})

            if ret == {}:
                return packOutput({},"500", "getStationInfo Error")
            else:
                return packOutput(ret)

        elif action == "add":
            print(" Controller  Add station ")
            addObj = json.loads(web.data())
            try:
                id = self.add(addObj)
                resultJson = {"stationID": id}
                return packOutput(resultJson)
            except Exception, e:
                print Exception, ":", e
                return packOutput({},"500","Add station error : " + str(e))

        elif action == "delete":
            print(" Controller  del station ")
            req = json.loads(web.data())
            id = req["stationID"]
            ret = self.delete({"id":id})
            if ret == -1:
                return packOutput({}, "500", "del station error" )
            else:
                return packOutput({})

        elif action == "edit":
            print(" Controller  change station ")
            data = json.loads(web.data())
            ret = self.edit(data)
            if ret != "success":
                return packOutput({}, "500", "change station error")
            else:
                return packOutput({})

        elif action == "sourceTest":
            print(" Controller  source Test  ")
            data = json.loads(web.data())
            if integrateType == "VIEW":
                importFunc = ImportTableFromView(self, "test_visitor_Config", visitor_para_name)
                ret = importFunc.testImportSource(data)
            else:
                ret = "success"
            if ret == "success":
                resultJson = {"testResult": "success"}
            else:
                resultJson = {"testResult": "failed"}
            return packOutput(resultJson)

        elif action == "sourceConfigTest":
            print(" Controller  source config test ")
            data = json.loads(web.data())
            if integrateType == "VIEW":
                ret = importConfigInterface().sourceTest("test_visitor_Config",data)
            else:
                ret = {"result" : "success" , "sql" : ""}

            if ret["result"] == "success":
                resultJson = {"testResult": "success", "testSql": ret["sql"]}
            else:
                resultJson = {"testResult": "failed", "testSql": ret["result"]}
            return packOutput(resultJson)

        else:
            return packOutput({},"500","unsupport action")

    def getList(self,data = {}):
        ret = self.db.select("stationSet")
        stationList = list(ret)
        return stationList

    def getInfo(self,data = {}):
        id = getNecessaryPara(data,"id")
        s = self.db.select("stationSet",where = {"id":id}).first()
        type = s["importSource"]
        config = self.getSourceConfig({"type" : type})
        config_alias = copy.copy(config)
        for key,val in config.items():
            if key in visitor_alias_name:
                alias = visitor_alias_name[key]
                config_alias.pop(key)
                config_alias[alias] = val
        s = dict(s)
        s.update(config_alias)
        return s

    def getSourceConfig(self,data = {}):
        source = importConfigInterface().getInfo(data)
        if source is not None:
            importFunc = ImportTableFromView(self, data["type"], visitor_para_name)
            config = importFunc.getConfig("")
            config["renewPeriod"] = source["renewPeriod"]
            return config
        else:
            return {}

    def add(self,data):
        dbName = getNecessaryPara(data,"DBName")
        tableName = getNecessaryPara(data,"tableName")
        sourceType = "visitor_" + dbName + tableName
        stationInfo = {
            "name": data["name"],
            "descText" : data["descText"],
            "DBType" : data["DBType"],
            "importSource" : sourceType
        }
        importConfigInterface().ifAdd(sourceType,data)
        id = self.db.insert("stationSet",**stationInfo)

        # add Accont
        account ={
            "stationID" : id,
            "user" : "station" + str(id),
            "type" : "station",
            "descText" : data["name"]
        }
        self.accout.add(account)
        return id

    def delete(self,data):
        id = getNecessaryPara(data,"id")
        try:
            result = self.db.delete("stationSet", where="id=$id", vars={"id": id})
            self.accout.delete(id)
            return result
        except Exception, e:
            print Exception, ":", e
            return -1

    def edit(self,data):
        id = getNecessaryPara(data,"stationID")
        dbName = getNecessaryPara(data,"DBName")
        tableName = getNecessaryPara(data,"tableName")
        sourceType = "visitor_" + dbName + tableName
        stationInfo = {
            "name": data["name"],
            "descText" : data["descText"],
            "DBType" : data["DBType"],
            "importSource" : sourceType
        }
        importConfigInterface().ifAdd(sourceType,data)
        importConfigInterface().sourceTest(sourceType,data)
        id = self.db.update("stationSet",where = {"id" : id},**stationInfo)
        return "success"

