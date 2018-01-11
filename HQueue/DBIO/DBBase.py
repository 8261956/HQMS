# -*- coding: UTF-8 -*-

import os
from functools import wraps
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
import web,json,sys,traceback,re,copy
import common.config as dbConfig
from common.func import LogOut, convertDBConfig, checkSession, packOutput

DBLocal = web.database (
    dbn = 'mysql',
    host = dbConfig.db_host,
    port = int(dbConfig.db_port),
    db = dbConfig.db_name,
    user = dbConfig.db_user,
    pw = dbConfig.db_pass,
    charset = 'utf8'
)

class MSSQLController(object):
    """对web.py中MSSQLDB的数据库操作方法进行一定的修改"""
    def __init__(self, config):
        db_config = convertDBConfig(**config)
        self.MSSQLDB = web.database(**db_config)
        self.MSSQLDB.ctx.db.autocommit(True)

    def __getattr__(self, item):
        func = None
        if item in ("query", "select", "where", "insert", "update", "delete"):
            if item == 'query':
                func = self.MSSQLDB.query
            elif item == 'select':
                func = self.MSSQLDB.select
            elif item == 'where':
                func = self.MSSQLDB.where
            elif item == 'insert':
                func = self.MSSQLDB.insert
            elif item == 'update':
                func = self.MSSQLDB.update
            elif item == 'delete':
                func = self.MSSQLDB.delete
            func = mssql_wrapper(func)
        elif item == "_db_cursor":
            func = self.MSSQLDB._db_cursor
        elif item == "dbname":
            func = self.MSSQLDB.dbname
        return func


class DBInterface(object):

    support_action = {
        "getDefaultSetting": "getDefaultSetting"
    }

    def POST(self, inputData):
        data = json.loads(web.data())

        token = data.pop("token", None)
        if token:
            if checkSession(token) == False:
                return packOutput({}, "401", "Token authority failed")
        action = data.pop("action", None)
        if action is None:
            return packOutput({}, code='400', errorInfo='action required')
        if action not in self.support_action:
            return packOutput({}, code='400', errorInfo='unsupported action')

        try:
            result = getattr(self, self.support_action[action])(data)
            return packOutput(result)
        except Exception as e:
            exc_traceback = sys.exc_info()[2]
            errorInfo = traceback.format_exc(exc_traceback)
            return packOutput({"errorInfo": str(e), "rescode": "500"}, code='500', errorInfo=errorInfo)

    def getDefaultSetting(self, data):

        db_paras = {
            "DBType": "",
            "host": "",
            "port": "",
            "user": "",
            "passwd": "",
            "charset": "",
            "DBName": "",
            "tableName": ""
        }
        mysql = copy.deepcopy(db_paras)
        mysql.update({
            "DBType": "mysql",
            "user": "root",
            "port": 3306,
            "charset": "utf8"
            })

        mssql = copy.deepcopy(db_paras)
        mssql.update({
            "DBType": "mssql",
            "user": "sa",
            "port": 1433,
            "charset": "utf8"
            })

        oracle = copy.deepcopy(db_paras)
        oracle.update({
            "DBType": "oracle",
            "user": "system",
            "port": 1521
        })

        result = {"mysql": mysql, "mssql": mssql, "oracle": oracle}

        return result


def mssql_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        result = result.list()
        return result
    return wrapper

##
##      DB Import support class
##

class ImportTableFromView:
    # 数据库配置项
    db_paras = ("DBType", "host", "port", "user", "passwd", "DBName", "charset", "tableName")
    def __init__(self, own,type,table_col):
        self.sql_paras = table_col
        self.type = type
        self.own = own

    def getConfig(self, inputData):
        configList = DBLocal.select("import_config", where={"type": self.type})
        keys = self.db_paras + self.sql_paras
        config = dict.fromkeys(keys, "")
        if len(configList) == 0:
            pass
        else:
            configInfo = dict(configList[0])
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

    def imports(self, config ,filter = None):
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

        if filter is None:
            ret = self.DBSource.select(sql)
        else:
            ret = self.DBSource.select(sql,where = filter)
        itemList = list(ret)
        count = 0
        for item in itemList:
            try:
                self.own.add(item)
            except:
                count += 1
                continue
        result = {"result" : "success"}
        result["totalImport"] = len(itemList)
        result["failedCount"] = count
        result["successCount"] = result["totalImport"] - result["failedCount"]
        print result
        return result,itemList

    def getAliasSql(self , config):
        tableName = config.get("tableName")
        tmp = []
        for key, value in config.items():
            if key in self.sql_paras and value != "":
                para = "{0} AS {1}".format(value, key)
                tmp.append(para)

        sql_paras = ', '.join(tmp)
        sql = "(SELECT {0} FROM {1}) aView".format(sql_paras, tableName)
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
            return str(Exception) + str(e)

        else:
            config_temp = {"type": self.type}
            result = DBLocal.select("import_config", where={"type": self.type})
            if len(result) == 0:
                DBLocal.insert("import_config", **config_temp)
        return "success"

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
            result.update({"result": "failed , DB Souce Config Error, " + str(e)})
        else:
            values = {}
            for key, value in config.items():
                if key in self.db_paras:
                    values[key] = value
            values.update({"importSQL": sql, "type": self.type})
            period = config.get("importTime",None)
            if period is not None:
                values.update({"importTime" : config.get("importTime")})   # 默认 1小时 60min *60s
            DBLocal.update("import_config", where={"type": self.type}, **values)
        finally:
            return result

    def getSource(self):
        configList = DBLocal.select("import_config", where={"type": self.type})
        if len(configList) == 0:
            return None
        else:
            configInfo = dict(configList[0])
            db_config = convertDBConfig(**configInfo)
            if config["DBType"] == "mssql":
                self.DBSource = MSSQLController(config).MSSQLDB
            else:
                self.DBSource = web.database(**db_config)
            sql = configInfo["importSQL"]
            return self.DBSource,sql

    def close(self):
        # close cursor
        self.DBSource._db_cursor().close()
        # close connection
        self.DBSource._db_cursor().connection.close()
        del self.DBSource
