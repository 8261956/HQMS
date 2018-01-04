
# -*- coding: utf-8 -*-

import os, sys, re, logging, json, copy, hashlib, traceback
import web
import common.config as cfg
from common.func import packOutput, checkSession, convertDBConfig
import HQueue.DBIO.DBBase as DB
from HQueue.DBIO.DBBase import MSSQLController

class WorkerInterface:

    # 数据库配置项
    db_paras = ("DBType", "host", "port", "user", "passwd", "DBName", "charset", "tableName")

    # SQL语句配置项
    sql_paras = ("id", "name", "title", "department", "descText", "speciality", "headPic")

    def POST(self,name):

        webData = json.loads(web.data())

        token = webData.pop("token", None)
        if "token" in webData:
            if checkSession(token) == False:
                return packOutput({}, "401", "Token authority failed")
        action = webData.pop("action", None)

        if action == "getList":
            list = self.getList(webData)
            num = len(list)
            resultJson = {"workerNum": num, "workerList": []}
            for item in list:
                worker = item.copy()
                del worker["callerList"]
                resultJson["workerList"].append(worker)
            return packOutput(resultJson)

        elif action == "getInfo":
            worker = self.getInfo(webData)
            return packOutput(worker)

        elif action == "import":
            try:
                result = self.imports(webData)
                return packOutput(result)
            except Exception as e:
                exc_traceback = sys.exc_info()[2]
                errorInfo = traceback.format_exc(exc_traceback)
                return packOutput({}, code="500", errorInfo=errorInfo)

        elif action == "addWorker":
            result = self.manualAddWorker(webData)
            return packOutput(result)

        elif action == "delWorker":
            result = self.delWorker(webData)
            return packOutput(result)

        elif action == "editWorker":
            result = self.editWorker(webData)
            return packOutput(result)

        elif action == "testSource":
            ret = self.testImportSource(webData)
            if ret:
                resultJson = {"result" : "success" }
            else:
                resultJson = {"result": "failed"}
            return packOutput(resultJson)

        elif action == "testSourceConfig":
            result = self.testImportSourceConfig(webData)
            return packOutput(result)

        elif action == "checkID":
            ret = self.checkConflict(webData)
            resultJson = {"conflict": ret}
            return packOutput(resultJson)

        elif action == "fuzzySearchWorker":
            try:
                result = self.fuzzySearchWorker(webData)
                return packOutput(result)
            except Exception as errorInfo:
                return packOutput({}, code="400", errorInfo=str(errorInfo))

        elif action == "getDepartment":
            try:
                result = self.getDepartment(webData)
                return packOutput(result)
            except Exception as errorInfo:
                return packOutput({}, code="400", errorInfo=str(errorInfo))

        elif action == "getTitle":
            try:
                result = self.getTitle(webData)
                return packOutput(result)
            except Exception as errorInfo:
                return packOutput({}, code="400", errorInfo=str(errorInfo))

        elif action == "getWorker":
            try:
                result = self.getWorker(webData)
                return packOutput(result)
            except Exception as errorInfo:
                return packOutput({}, code="400", errorInfo=str(errorInfo))

        elif action == "getConfig":
            try:
                result = self.getConfig(webData)
                return packOutput(result)
            except Exception as errorInfo:
                return packOutput({}, code="400", errorInfo=str(errorInfo))

        else:
            return packOutput({},"500","unsupport action")


    def getList(self,webData):
        filter = webData["stationID"]
        ret = DB.DBLocal.where('workers',stationID = filter)
        return ret

    def getInfo(self,webData):
        ret = DB.DBLocal.where('workers', id = webData["id"])
        worker = ret[0]
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
        # self.DBSource = web.database(
        #     dbn = config["DBType"],
        #     host = config["host"],
        #     port = int(config["port"]),
        #     db = config["DBName"],
        #     user = config["user"],
        #     pw = config["passwd"],
        #     charset = config["charset"]
        # )
        # tableName = config["table"]
        # print "DBSource connect ok " + tableName
        # res = self.DBSource.select(tableName)
        # view = self.getAliasSql(config)
        # print "get view :" + view
        # workerList = self.DBSource.select(view)
        # for item in workerList:
        #     item["stationID"] = config["stationID"]
        #     item["user"] = item["id"]
        #     item["password"] = "123456"
        #     self.addWorker(item)
        # return

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
        # configList = ("aliasID", "aliasName", "aliasTitle", "aliasDepartment", "aliasDescText", "aliasHeadPic")
        # paraList = ("id", "name", "title", "department", "descText", "headPic")
        #
        # sourceTable = "(SELECT "
        # iterPara = iter(paraList)
        # dot = 0
        # for conf in configList :
        #     if config[conf] != "":
        #         if dot == 0:
        #             dot = 1
        #         else:
        #             sourceTable += " , "
        #         sourceTable += config[conf]
        #         sourceTable += " as " + iterPara.next()
        # sourceTable += " from " + config["table"] +") as workerView"
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



class headpicUpload:

    def POST(self):
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
        os.rename(myfile['filepath'], dest);
        rst = {'result': "success", 'upload_path': cfg.upload_http_base + newFileName, 'size': myfile.size}
        # return '<script>parent.uploadCallback(%s);window.location.href="upload%s.html";</script>'% (json.dumps(rst),myfile.uptype)
        return packOutput(rst)


class WebUploadController:

    def POST(self,name):
        x = web.input(myfile={})
        filedir = cfg.headPicPath
        if 'myfile' in x:
            filepath = x.myfile.filename.replace('\\', '/')  # replaces the windows-style slashes with linux ones.
            filename = filepath.split('/')[-1]  # splits the and chooses the last part (the filename with extension)
            fout = open(filedir + '/' + filename, 'w')  # creates the file where the uploaded file should be stored
            fout.write(x.myfile.file.read())  # writes the uploaded file to the newly created file.
            fout.close()  # closes the file, upload complete.
            rst = {'result': "success", 'upload_path': cfg.upload_http_base + filename, 'size': x.myfile.size}
            return packOutput(rst)

        raise web.seeother('/upload')
