
# -*- coding: utf-8 -*-

import os, sys, re, logging, json, copy, hashlib, traceback
import web
import common.config as cfg
from common.func import packOutput, checkSession, convertDBConfig,checkPostAction
import common.DBBase as DB
from common.DBBase import MSSQLController

class WorkerInterface:

    support_action = {
        "getList": "getListRet",
        "getInfo": "getInfo",
        "addWorker": "manualAddWorker",
        "editWorker": "editWorker",
        "delWorker": "delWorker",
        "testSource": "testSourceRet",
        "testSourceConfig": "testSourceConfig",
        "import":"imports",
        "checkID" : "checkIDRet",
        "fuzzySearchWorker": "fuzzySearchWorker",
        "getDepartment" : "getDepartment",
        "getTitle" : "getTitle",
        "getWorker" : "getWorker",
        "getConfig" : "getConfig"
    }

    # 数据库配置项
    db_paras = ("DBType", "host", "port", "user", "passwd", "DBName", "charset", "tableName")

    # SQL语句配置项
    sql_paras = ("id", "name", "title", "department", "descText", "speciality", "headPic")

    def POST(self,name):
        data = json.loads(web.data())
        return checkPostAction(self, data, self.support_action)

    def getListRet(self,data):
        list = self.getList(data)
        num = len(list)
        resultJson = {"workerNum": num, "workerList": []}
        for item in list:
            worker = item.copy()
            del worker["callerList"]
            resultJson["workerList"].append(worker)
        return resultJson

    def testSourceRet(self,data):
        ret = self.testImportSource(data)
        if ret:
            resultJson = {"result" : "success" }
        else:
            resultJson = {"result": "failed"}
        return resultJson

    def checkIDRet(self,data):
        ret = self.checkConflict(data)
        resultJson = {"conflict": ret}
        return packOutput(resultJson)

    def getList(self,data):
        filter = data["stationID"]
        ret = DB.DBLocal.where('workers',stationID = filter)
        return ret

    def getInfo(self,data):
        worker = DB.DBLocal.where('workers', id = data["id"]).first()
        return worker

    def addWorker(self,inputData):
        data = dict(copy.deepcopy(inputData))
        data.pop("token", None)
        data.pop("action", None)
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        print "INSERT INTO workers"
        try:
            DB.DBLocal.insert("workers", **values)
        except Exception:
            raise

    def delWorker(self, webData):
        id = webData.get("id")
        result = {}
        try:
            DB.DBLocal.delete("workers", where="id=$id", vars={"id": id})
        except Exception, e:
            print "Exception: {0}".format(e)
            result["result"] = "failed"
        else:
            result["result"] = "success"
        return result

    def editWorker(self,webData):
        data = dict(copy.deepcopy(webData))
        data.pop("token", None)
        data.pop("action", None)
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        id = values.get("id")
        print "UPDATE workers"
        result = {}
        try:
            DB.DBLocal.update("workers", where={"id": id}, **values)
        except Exception as e:
            print "Exception: {0}".format(e)
            result["result"] = "failed"
        else:
            result["result"] = "success"
        return result

    def manualAddWorker(self, inputData):
        data = dict(copy.deepcopy(inputData))
        if not data.has_key("source"):
            data.update({"source": "manual_add"})

        result = {}
        try:
            self.addWorker(data)
        except:
            result["result"] = "failed"
        else:
            result["result"] = "success"

        return result

    def getConfig(self, inputData):
        configList = DB.DBLocal.select("import_config", where={"type": "worker"})
        keys = self.db_paras + self.sql_paras
        config = dict.fromkeys(keys, "")
        if len(configList) == 0:
            pass
        else:
            configInfo = dict(configList[0])
            configInfo.pop("id")
            configInfo.pop("type")
            sql = configInfo.pop("importSQL")
            sql = re.sub(".*SELECT", '', sql)
            sql = re.sub("FROM.*", '', sql)
            sql = sql.strip()

            paras = sql.split(',')
            result = {}
            for item in paras:
                tmp = item.split("AS")
                value = tmp[0].strip()
                key = tmp[1].strip()
                result[key] = value

            configInfo.update(result)

            for key, value in configInfo.items():
                if config.has_key(key):
                    config[key] = value
                else:
                    continue

        return config

    def imports(self, config):

        db_config = convertDBConfig(**config)
        if config["DBType"] == "mssql":
            self.DBSource = MSSQLController(config).MSSQLDB
        else:
            self.DBSource = web.database(**db_config)

        connect_test = self.testImportSourceConfig(config)
        if connect_test["result"] == "failed":
            raise Exception("[ERR]: import failed, please check the config")
        else:
            sql = connect_test["sql"]

        workerList = self.DBSource.select(sql)
        count = 0
        for item in workerList:
            if config["DBType"] == "oracle":
                item = self.convertItem(item)
            item["user"] = item["id"]
            item["password"] = "123456"
            item["source"] = "import"
            try:
                self.addWorker(item)
            except:
                count += 1
                continue
        result = {}
        result["totalImport"] = len(workerList)
        result["failedCount"] = count
        result["successCount"] = result["totalImport"] - result["failedCount"]
        print result
        return result

    def convertItem(self, item):

        result = {}
        for key in self.sql_paras:
            key_upper = key.upper()
            if key_upper in item:
                result.update({key: item[key_upper]})
        return result

    def getAliasSql(self , config):
        tableName = config.pop("tableName")
        tmp = []
        for key, value in config.items():
            if key in self.sql_paras and value != "":
                para = "{0} AS {1}".format(value, key)
                tmp.append(para)

        sql_paras = ', '.join(tmp)
        sql = "(SELECT {0} FROM {1}) workerView".format(sql_paras, tableName)
        return sql

    def testImportSource(self, config):
        db_config = convertDBConfig(**config)
        try:
            if config["DBType"] == "mssql":
                self.DBSource = MSSQLController(config).MSSQLDB
            else:
                self.DBSource = web.database(**db_config)
            tableName = config["tableName"]
            print "DBSource connect ok " + tableName
            res = self.DBSource.select(tableName)
        except Exception,e:
            print Exception,":",e
            return 0
        else:
            config.update({"type": "worker"})
            result = DB.DBLocal.select("import_config", where={"type": "worker"})
            if len(result) == 0:
                DB.DBLocal.insert("import_config", **config)
            else:
                DB.DBLocal.update("import_config", where={"type": "worker"}, **config)
            return 1

    def testImportSourceConfig(self,config):

        db_config = convertDBConfig(**config)
        sql = self.getAliasSql(config)
        result = {"result": "success", "sql": sql}
        try:
            if config["DBType"] == "mssql":
                self.DBSource = MSSQLController(config).MSSQLDB
            else:
                self.DBSource = web.database(**db_config)
            res = self.DBSource.select(sql)
        except Exception, e:
            print Exception, ":", e
            result.update({"result": "failed"})
        else:
            values = copy.deepcopy(config)
            for key, value in config.items():
                if key in self.sql_paras:
                    values.pop(key)
            values.update({"importSQL": sql, "type": "worker"})
            DB.DBLocal.update("import_config", where={"type": "worker"}, **values)
        finally:
            return result


    def checkConflict(self,inputData):
        ret = DB.DBLocal.where('workers',id = inputData["id"])
        if len(ret) > 0:
            return 1
        else:
            return 0

    def fuzzySearchWorker(self, inputData):
        keyword = inputData.get("keyword")
        department = inputData.get("department", None)
        where = None
        if department:
            where = {"department": department}
        workerList = DB.DBLocal.select("workers", where=where,
                                       what="id, name, department, title, descText, speciality, status, source")
        suggestions = []
        collections = []
        for item in workerList:
            worker = dict(item)
            collections.append(worker)
        pattern = '.*?'.join(keyword)
        regex = re.compile(pattern)
        for item in collections:
            match = regex.search(item["name"])
            if match:
                suggestions.append((len(match.group()), match.start(), item))
        workerInfo = [x for _, _, x in sorted(suggestions)]

        result = []
        for item in workerInfo:
            result.append(item)
        return result

    def getDepartment(self, inputData):
        departments = DB.DBLocal.select("workers", what="DISTINCT department")
        result = []
        for item in departments:
            result.append(item["department"])
        return result

    def getTitle(self, inputData):
        titles = DB.DBLocal.select("workers", what="DISTINCT title")
        result = []
        for item in titles:
            result.append(item["title"])
        return result

    def getWorker(self, inputData):
        department = inputData.get("department", None)
        title = inputData.get("title", None)
        source = inputData.get("source", None)
        name = inputData.get("name", None)
        pageNum = inputData.get("pageNum", None)
        pageSize = inputData.get("pageSize", None)

        where = {}
        if department:
            where.update({"department": department})
        if title:
            where.update({"title": title})
        if source:
            where.update({"source": source})
        if name:
            where.update({"name": name})
        if not where:
            where = None

        tmp = DB.DBLocal.select("workers", where=where)
        count = len(tmp)

        if pageNum and pageSize:
            if not isinstance(pageNum, int) or not isinstance(pageSize, int):
                raise Exception("[ERR]: pagination parameters should be int")
            workerList = DB.DBLocal.select("workers", where=where, order="department, title",
                                           what="id, name, department, title, descText, speciality, status, source, user, password",
                                           limit=pageSize, offset=(pageNum-1)*pageSize)
        else:
            workerList = DB.DBLocal.select("workers", where=where, order="department, title",
                                           what="id, name, department, title, descText, speciality, status, source, user, password")

        result = {}
        list = []
        for item in workerList:
            list.append(item)
        result["list"] = list
        result["count"] = count
        return result



class NginxUploadController:

    def POST(self, *args, **kargs):
        # try:
        print 'args ', args
        print 'kargs ', kargs

        myfile = web.input(myfile={}, uptype="")
        filename = myfile['filename']
        logging.warning('Upload file ' + filename)
        name, ext = os.path.splitext(filename)
        # avoid none ascii issue
        myMd5 = hashlib.md5()

        if isinstance(name, str):
            myMd5.update(name.decode('utf8').encode('utf8'))
        elif isinstance(name, unicode):
            myMd5.update(name.encode('utf8'))

        dirPath = cfg.headPicPath


        name_md5 = myMd5.hexdigest()
        ext = ext.lower()
        newFileName = "%s%s" % (name_md5,ext)
        dest = os.path.join(dirPath, newFileName)


        print myfile['filepath']
        print dest

        os.rename(myfile['filepath'], dest);
        rst = {'result': 0, 'upload_path': cfg.upload_http_base + newFileName, 'size': myfile.size}
        # return '<script>parent.uploadCallback(%s);window.location.href="upload%s.html";</script>'% (json.dumps(rst),myfile.uptype)
        return json.dumps(rst)

    def GET(self, *args, **kargs):
	    web.header("Content-Type","text/html; charset=utf-8")
	    return """<html><head></head><body>
			  <form method="POST" enctype="multipart/form-data" action="/headpicUpload">
			  <input type="file" name="myfile" />
			  <br/>
			  <input type="submit" />
			  </form>
			  </body></html>"""
