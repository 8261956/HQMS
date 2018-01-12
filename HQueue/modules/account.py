# -*- coding: UTF-8 -*-

import web
import json

import common.func
import mainWorker
from common.func import packOutput
from caller import CallerInterface
import HQueue.DBIO.DBBase as DB


def unicode2str(unicodeStr):
    if type(unicodeStr) == unicode:
        return unicodeStr.encode("utf-8")
    elif type(unicodeStr) == str:
        return unicodeStr
    else:
        return unicodeStr

class LoginInterface(object):

    support_action = {
        "GetToken": "login"
    }

    def POST(self,name):

        # webData = json.loads(web.data())
        #
        # user = webData["user"]
        # passwd = webData["passwd"]
        #
        # if user == "root" and passwd == "clear!@#":
        #     ret = {"token": common.func.getToken(user,passwd),
        #            "userType": "Manager"
        #            }
        #     return packOutput(ret)
        #
        # #判断是否为分诊台帐号
        # ret = DB.DBLocal.where("account", user=user,password = passwd)
        # if len(ret) != 0:
        #     account = ret[0]
        #     ret = { "userType": "station","stationID":account["stationID"]}
        #     ret["token"] = common.func.getToken(user,passwd)
        # else:
        #     #判断是否为医生账号
        #     ret = DB.DBLocal.where("workers", user=user, password=passwd)
        #
        #     if len(ret) != 0:
        #         for account in ret:
        #             # 判断是否在允许的叫号器上登录
        #             if "localIP" in webData:
        #                 account["localIP"] = webData["localIP"]
        #             caller = mainWorker.WorkerMainController().getCallerInfo(account)
        #             if caller != {}:            #不合法的医生账户登录
        #                 ret = {"userType": "worker","stationID": account["stationID"]}
        #                 ret["callerID"] = caller["id"]
        #                 onlineMsg = {"stationID":account["stationID"],"callerID":caller["id"],\
        #                              "workerID":account["id"],"status":"online"}
        #                 CallerInterface().setWorkerStatus(onlineMsg)
        #                 ret["token"] = common.func.getToken(user,passwd)
        #                 return packOutput(ret)
        #         if "localIP" in webData:
        #             return packOutput({}, "500", "not allowed caller，ip: " + webData["localIP"])
        #         else:
        #             return packOutput({}, "500", "not allowed caller，ip: " + web.ctx.ip)
        #     else:
        #         return packOutput({},"500","uncorrect user and password")
        #
        # return packOutput(ret)
        data = json.loads(web.data())

        action = data.pop("action", None)
        if action is None:
            return packOutput({}, code='400', errorInfo='action required')
        if action not in self.support_action:
            return packOutput({}, code='400', errorInfo="unsupport action")

        try:
            result = getattr(self, self.support_action[action])(data)
            return packOutput(result)
        except Exception as e:
            # exc_traceback = sys.exc_info()[2]
            # errorInfo = traceback.format_exc(exc_traceback)
            return packOutput({}, code='500', errorInfo=str(e))

    def login(self, data):
        user = data.get("user", None)
        if user is None:
            raise Exception("user required to login")
        passwd = data.get("passwd", None)
        if passwd is None:
            raise Exception("passwd required to login")
        type = data.get("type", None)
        if type:
            result = self.newLogin(data)
        else:
            result = self.oldLogin(data)
        return result

    def oldLogin(self, data):
        # 尝试后台登录
        try:
            result = self._managerLogin(data)
        except:
            pass
        else:
            return result

        # 尝试分诊台登录
        try:
            result = self._stationLogin(data)
        except:
            pass
        else:
            return result

        # 尝试叫号器登录
        try:
            result = self._workerLogin(data)
        except:
            raise
        else:
            return result

    def newLogin(self, data):
        type = data.pop("type", None)
        if type is None:
            raise Exception("[ERR]: type required to login")

        if type == "manager":
            result = self._managerLogin(data)
        elif type == "station":
            result = self._stationLogin(data)
        elif type == "worker":
            result = self._workerLogin(data)
        else:
            raise Exception("[ERR]: unsupport type to login")

        return result

    def _managerLogin(self, data):
        user = data.get("user")
        passwd = data.get("passwd")
        token = common.func.getToken(user, passwd)

        if user == "root" and passwd == "clear!@#":
            result = {"userType": "Manager", "token": token}
        else:
            raise Exception("incorrect user or password to login as manager")

        return result

    def _stationLogin(self, data):
        user = data.get("user")
        passwd = data.get("passwd")
        token = common.func.getToken(user, passwd)

        accountList = DB.DBLocal.select("account", where={"user": user, "password": passwd})
        if len(accountList) > 0:
            account = accountList[0]
            result = {"userType": "station", "token": token, "stationID": account["stationID"]}
        else:
            raise Exception("incorrect user or password to login stationSet")

        return result

    def _workerLogin(self, data):
        inputData = {}
        if "localIP" in data:
            inputData.update({"localIP": data["localIP"]})
        caller = mainWorker.WorkerMainController().getCallerInfo(inputData)
        if len(caller) == 0:
            if "localIP" in data:
                raise Exception("not allowed ip: {0} to login caller".format(data["localIP"]))
            else:
                raise Exception("not allowed ip: {0} to login caller".format(web.ctx.ip))

        user = data.get("user")
        passwd = data.get("passwd")
        token = common.func.getToken(user, passwd)

        workerList = DB.DBLocal.select("workers", where={"user": user, "password": passwd})
        if len(workerList) == 0:
            raise Exception("incorrect user or password to login caller")

        worker = workerList[0]
        stationID = caller["stationID"]
        callerID = caller["id"]
        workerID = worker["id"]
        onlineMsg = {"stationID": stationID, "callerID": callerID, "workerID": workerID, "status": "online"}
        CallerInterface().setWorkerStatus(onlineMsg)
        # WorkerMainController().setWorkerStatus({"stationID": stationID, "id": workerID, "status": "online"})
        result = {"userType": "worker", "token": token, "stationID": stationID, "callerID": callerID}

        return result

    def GET(self,name):
        return 1

class StationAccountInterface:
    def POST(self,name):
        webData = json.loads(web.data())
        action = webData["action"]
        if "token" in webData:
            token = webData["token"]
            if common.func.checkSession(token) == False:
                return packOutput({}, "401", "Tocken authority failed")

        if action == "edit":
            account = {}
            stationID = webData["stationID"]
            account["user"] = webData["user"]
            account["password"] = webData["password"]
            account["descText"] = webData["descText"]
            stationAccount = StationAccount()
            stationAccount.edit(stationID,account)
            return packOutput({})

        elif action == "getList":
            stationAccount = StationAccount()
            resultJson = {"accountList":[]}
            list = stationAccount.getList()
            for item in list:
                resultJson["accountList"].append(item)
            return packOutput(resultJson)

        elif action == "getInfo":
            stationID = webData["stationID"]
            stationAccount = StationAccount()
            info = stationAccount.getInfo(stationID)
            return packOutput(info)

class StationAccount:
    def add(self,account):
        DB.DBLocal.insert("account", stationID=account["stationID"],user=account["user"],password=account["password"], \
                       type=account["type"],descText=account["descText"])
        return 1

    def getInfo(self,id):
        try:
            ret = DB.DBLocal.where("account", stationID=id)
            return ret[0]
        except Exception, e:
            print Exception, ":", e
            return -1

    def getList(self):
        try:
            ret = DB.DBLocal.select("account")
            return ret
        except Exception, e:
            print Exception, ":", e
            return -1

    def edit(self,stationID,account):
        filter = "stationID = \'" + str(stationID) +"\'"
        try:
            DB.DBLocal.update("account",filter,user=account["user"],password=account["password"],descText=account["descText"])
            return 1
        except Exception, e:
            print Exception, ":", e
            return -1

    def delete(self,stationID):
        filter = "stationID = \'" + str(stationID) + "\'"
        try:
            DB.DBLocal.delete("account", filter)
        except Exception, e:
            print Exception, ":", e
            return -1