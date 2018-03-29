
# -*- coding: utf-8 -*-

import sys, copy, time, datetime
import queueInfo
import common.config as cfg
from common.func import LogOut,getNecessaryPara,getCurrentDate,getCurrentTime
from queueData import VisitorLocalInterface,QueueDataController
from mainStation import StationMainController
from queueInfo import QueueInfoInterface
from scene import SceneInterface
from station import StationInterface,visitor_para_name,visitor_alias_name
from queueData import LocalVisitor, finalScoreDef
import common.DBBase as DB
from common.DBBase import ImportTableFromView

reload(sys)
sys.setdefaultencoding('utf-8')

class VisitorManager:
    sql_paras = visitor_para_name

    def __init__(self):
        self.queueList = []
        self.db = DB.DBLocal
        self.queueInfo = queueInfo.QueueInfoInterface()
        self.visitorList = []
        self.innerSourceDict = {}
        self.importSourceDict = []
        pass

    def getInnerSourceDict(self):
        ret = self.db.select("visitor_source_data")
        self.innerSourceDict = {}
        for item in ret:
            self.innerSourceDict[str(item["id"])] = item

    def add(self,data):
        data = dict(data)
        id = str(getNecessaryPara(data, "id"))
        self.importSourceDict.append(id)
        if id not in self.innerSourceDict:
            #患者信息不存在 插入患者信息
            ret = self.db.insert("visitor_source_data", **data)
        else:
            # 患者信息存在 看是否需要更新患者信息
            v_source = self.innerSourceDict[id]
            if self.compSource(data, v_source) != 0:
                print "find visitor %s need update" % str(data["id"])
                interface = VisitorSourceInterface()
                interface.edit(data)
        result = {"result": "success"}
        return result

    def syncSource(self):
        import_list = self.db.select("import_config")
        if len(import_list) == 0:
            return
        self.importSourceDict = []
        #得到最新本地Souce数据
        self.getInnerSourceDict()
        import_list = list(import_list)
        for import_config in import_list:
            type = import_config.get("type")
            DBType = import_config.get("DBType")
            if str(type).startswith("visitor") is False:
                continue
            """添加日期判断"""
            if DBType == 'oracle':
                dataFilter = " registDate > timestamp\'%s\'" %getCurrentDate()
            elif DBType == 'mssql' or DBType == 'mysql':
                dataFilter = " registDate = '%s'" % getCurrentDate()

            """构建导入类实例"""
            importFunc = ImportTableFromView(self, type, self.sql_paras)
            config = importFunc.getConfig("")
            """获得源列表"""
            ret, sourceList = importFunc.imports(config , dataFilter)
            """导入结束 关闭连接"""
            importFunc.close()

    def syncLocal(self):
        stationList = StationInterface().getList()
        for station in stationList:
            stationID = station["id"]
            self.queueList = self.queueInfo.getList({"stationID" : stationID})
            print("station " + str(stationID) + "syncLocal" )
            #scan all queue in a station
            for queue in self.queueList:
                para = {"stationID":stationID , "queueID":queue["id"]}
                QueueDataController().updateVisitor(para)
            print "stationID %d  local sync ok" % stationID

    def sigVisitorFinished(self,name,vID):
        vList = self.db.where("visitor_local_data", name=name ,id = vID)
        if len(vList) != 0:
            v = vList.first()
            vUpdate = {
                "id" : vID,
                "stationID" : v["stationID"],
                "status" : "finish"
            } 
            VisitorLocalInterface.edit(vUpdate)
            #self.db.update("visitor_local_data", where={"id" : vID} ,**vUpdate)

    def backupOld(self):
        stationList = StationInterface().getList()
        for station in stationList:
            stationID = station["id"]

            queueList = self.queueInfo.getList({"stationID": stationID})
            LogOut.info("station %d backupOld" % stationID)

            #遍历分诊台的队列
            for queue in queueList:
                #得到策略的工作时间
                workDays, dateStr = QueueInfoInterface().getWorkDays(stationID, queue["id"])
                joinSql = "select * from visitor_view_data where queueID = %d and registDate < %s" % (queue["id"] , dateStr)
                print ("backupView sql: " + joinSql)

                # find the visitors outof date
                backupList = self.db.query(joinSql)
                for item in backupList:
                    print "find backup item name: " + item["name"] + " registDate: " + str(item["registDate"]) + " workEndTime: " + str(item["workEndTime"])
                    item.pop("lid")
                    BackupTableInterface(stationID).add(item)
                    VisitorSourceInterface().delete(item)
                    VisitorLocalInterface(stationID).delete(item)

    def compSource(self,v_import,v_source):
        for k,v in v_import.iteritems():
            if k == 'registTime' or k == 'registDate':
                continue
            if k == 'orderDate' or k == 'orderTime' or k == 'age':
                continue
            if str(v_source[k]) != str(v):
                print "unmatch ext: %s:%s in %s:%s" %(str(k),str(v),str(k),str(v_source[k]))
                return -1
        return 0

class VisitorSourceInterface:
    def __init__(self):
        pass

    def getList(self,inputData):
        ret = DB.DBLocal.where('visitor_source_data', queue=inputData["queue"])
        return  ret

    def getInfo(self,inputData):
        ret = DB.DBLocal.where('visitor_source_data', id = inputData["id"])
        return ret[0]

    def add(self,inputData):
        data = dict(copy.deepcopy(inputData))
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        print "INSERT INTO visitor_source_data"
        result = DB.DBLocal.insert("visitor_source_data", **values)
        return result

    def delete(self, inputData):
        id = inputData.get("id")
        try:
            result = DB.DBLocal.delete("visitor_source_data",
                                       where="id=$id",
                                       vars={"id": id})
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
        print "UPDATE visitor_source_data"
        result = DB.DBLocal.update("visitor_source_data",
                                   where="id=$id",
                                   vars={"id": id}, **values)
        return result


class BackupTableInterface:
    def __init__(self,stationID):
        self.stationID = stationID

    def getList(self,inputData):
        ret = DB.DBLocal.where('visitor_backup_data', queue=inputData["queue"])
        return  ret

    def getInfo(self,inputData):
        ret = DB.DBLocal.where('visitor_backup_data', id = inputData["id"],stationID = self.stationID)
        return ret[0]

    def add(self,inputData):
        data = dict(copy.deepcopy(inputData))
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        print "INSERT INTO visitor_backup_data"
        result = DB.DBLocal.insert("visitor_backup_data", **values)
        return result

    def delete(self, inputData):
        id = inputData.get("id")
        stationID = self.stationID
        try:
            result = DB.DBLocal.delete("visitor_backup_data",
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
        print "UPDATE visitor_backup_data"
        result = DB.DBLocal.update("visitor_backup_data",
                                   where="id=$id and stationID=$stationID",
                                   vars={"id": id, "stationID": stationID}, **values)
        return result
