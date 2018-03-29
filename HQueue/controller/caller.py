# -*- coding: utf-8 -*-

import web, json, copy
from common.func import packOutput, checkSession
import common.DBBase as DB


class CallerInterface:

    def POST(self,name):

        webData = json.loads(web.data())
        action = webData["action"]
        if "token" in webData:
            token = webData["token"]
            if checkSession(token) == False:
                return packOutput({}, "401", "Token authority failed")

        if action == "getList":
            list = self.getList(webData)
            num = len(list)
            resultJson = {"num": num, "list": []}
            for item in list:
                caller = item.copy()
                resultJson["list"].append(caller)
            return packOutput(resultJson)

        elif action == "getInfo":
            caller = self.getInfo(webData)
            return packOutput(caller)

        elif action =="add":
            ret = self.add(webData)
            return packOutput({})

        elif action == "edit":
            id = self.edit(webData)
            return packOutput({})

        elif action == "delete":
            ret = self.delete(webData)
            if ret == -1:
                resultJson = {"result" : "failed"}
            else:
                resultJson = {"result" : "success"}
            return packOutput(resultJson)

        elif action == "setWorkerStatus":
            ret = self.setWorkerStatus(webData)
            if ret == -1:
                resultJson = {"result" : "failed"}
            else:
                resultJson = {"result" : "success"}
            return packOutput(resultJson)

        elif action == "checkIP":
            try:
                result = self.checkIP(webData)
                return packOutput(result)
            except Exception as e:
                return packOutput({}, code=500, errorInfo=str(e))

        else:
            return packOutput({}, "500", "unsupport action")

    def getList(self,inputData):
        ret = DB.DBLocal.where('caller', stationID=inputData["stationID"])
        return ret

    def getInfo(self,inputData):
        ret = DB.DBLocal.where('caller', stationID=inputData["stationID"],id = inputData["id"])
        return ret[0]

    def add(self,inputData):
        data = dict(copy.deepcopy(inputData))
        data.pop("token", None)
        data.pop("action", None)
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        print "INSERT INTO caller"
        result = DB.DBLocal.insert("caller", **values)
        return result

    def delete(self, inputData):
        # id = inputData["id"]
        # try:
        #     filter = "id=" + '\''+ str(id) + '\''
        #     ret = DB.DBLocal.delete('caller',filter)
        #     return ret
        # except Exception, e:
        #     print Exception, ":", e
        #     return -1
        id = inputData.get("id")
        try:
            result = DB.DBLocal.delete("caller", where="id=$id", vars={"id": id})
            return result
        except Exception, e:
            print Exception, ":", e
            return -1

    def edit(self,inputData):
        # stationID = inputData["stationID"]
        # data = copy.deepcopy(inputData)
        # if inputData.has_key("token"):
        #     del data["token"]
        # if inputData.has_key("action"):
        #     del data["action"]
        #
        # first = 1
        # sql = "update caller set "
        # for key, v in data.iteritems():
        #     if key != "id":
        #         if first != 1:
        #             sql += ','
        #         sql += key
        #         restr = str(v).replace("'", "\\'")
        #         sql += ' = ' + '\'' + restr + '\' '
        #         first = 0
        # sql += " where id = " + '\'' + str(data["id"]) + '\' '
        # print  "auto sql update caller : sql " + sql
        #
        # ret = DB.DBLocal.query(sql)
        # return ret
        data = dict(copy.deepcopy(inputData))
        data.pop("token", None)
        data.pop("action", None)
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        id = values.get("id")
        print "UPDATE caller: %s" % id
        result = DB.DBLocal.update("caller", where="id=$id", vars={"id": id}, **values)
        return result

    #设置登录的在线工作人员
    def setWorkerStatus(self,inputData):
        if inputData["status"] == "online":
            self.edit({"id": inputData["callerID"], "workerOnline": inputData["workerID"], "stationID":inputData["stationID"]})
        else:
            self.edit({"id": inputData["callerID"], "workerOnline": " ", "stationID":inputData["stationID"]})

    def checkIP(self, inputData):
        ip = inputData.get("ip", None)
        if ip is None:
            raise Exception("[ERR]: ip required")
        caller = DB.DBLocal.select("caller", where={"ip": ip})

        result = {"conflict": 0}
        if len(caller) != 0:
            result.update({"conflict": 1})
        return result