# -*- coding: UTF-8 -*-

import json, random,time, sys, traceback
from datetime import datetime, date, timedelta
from web import SQLQuery, SQLParam
import common.config as cfg
from common.memcachewrapper import memcached_wrapper

class JsonExtendEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        if isinstance(o, timedelta):
            tsec = int(o.seconds)
            hour = tsec/3600
            min = (tsec - hour*3600)/60
            sec = tsec%60
            return str(hour) + ":" + str(min) + ":" + str(sec)
        else:
            return json.JSONEncoder.default(self, o)

def packOutput(detail,code = "200",errorInfo = "none"):
    if code == "200":
        resultJson = {"rescode": "200", "errInfo": "none ", "detail":{}}
        resultJson["detail"]  =detail
    else:
        resultJson = {"rescode": code, "errInfo":errorInfo, "detail": {}}
        resultJson["detail"] = detail
    return json.dumps(resultJson, cls=JsonExtendEncoder)

class LogOut:
    @classmethod
    def warning(cls,arg):
        print arg

    @classmethod
    def debug(cls,arg):
        print arg

    @classmethod
    def error(cls,arg):
        print arg

    @classmethod
    def info(cls, arg):
        pass#print arg

def unicode2str(unicodeStr):
    if type(unicodeStr) == unicode:
        return unicodeStr.encode("utf-8")
    elif type(unicodeStr) == str:
        return unicodeStr
    else:
        return unicodeStr

def list2Str(list):
    strOut = ""
    first = 1
    for id in list:
        if first == 0:
            strOut += ","
        strOut += str(id)
        first = 0
    return strOut

def str2List(str):
    if str == "" or str is None:
        return []
    else:
        return str.split(',')

def createRandomStr32(length=32):
    """产生随机字符串，不长于32位"""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    strs = []
    for x in range(length):
        strs.append(chars[random.randrange(0, len(chars))])
    return "".join(strs)

def getToken(username, password):
    key = '_'.join(['hqms_adv', 'user', username, createRandomStr32(8)])

    value_json = {}
    value_json['username'] = username
    value = json.dumps(value_json)

    mc = memcached_wrapper.getMemcached()
    mc.set(str(key), value, cfg.memcached_timeout)
    mc.disconnect_all()
    return key

def checkSession( token):
    key = str(token)
    mc = memcached_wrapper.getMemcached()
    value = mc.get(key)
    mc.disconnect_all()
    if value == None:
        return False
    else:
        return True

def convertDBConfig(**config):
    """将配置信息转换为web.py数据库连接可以直接使用的配置信息"""

    db_paras = {
        "DBType": "dbn",
        "host": "host",
        "port": "port",
        "user": "user",
        "passwd": "pw",
        "DBName": "db",
        "charset": "charset"
    }

    # 如果数据库是Oracle，则去掉charset, DBName, port
    db_type = config.get("DBType", None)
    if not db_type:
        raise Exception("[ERR] database type required")
    if db_type == "oracle":
        db_paras.pop("charset")
        db_paras.pop("DBName")
        db_paras.pop("port")
        db_paras.update({"host": "db"})

    print db_paras

    for key in db_paras.keys():
        if key not in config:
            raise Exception("[ERR]: database parameter {0} not exists".format(key))

    db_config = {}
    for key, value in config.items():
        if key in db_paras and value:
            if key == "port" and not isinstance(value, int):
                value = int(value)
            db_config.update({db_paras[key]: value})

    return db_config


def multiple_insert_sql(tablename, values):
    """生成批量插入或者更新数据的SQL语句，改编自web.py的multiple_insert方法"""

    if not values:
        return []

    keys = values[0].keys()
    # @@ make sure all keys are valid

    for v in values:
        if v.keys() != keys:
            raise ValueError, 'Not all rows have the same keys'

    sql_query = SQLQuery('INSERT INTO %s (%s) VALUES ' % (tablename, ', '.join(keys)))

    for i, row in enumerate(values):
        if i != 0:
            sql_query.append(", ")
        SQLQuery.join([SQLParam(row[k]) for k in keys], sep=", ", target=sql_query, prefix="(", suffix=")")

    tmp = []
    for key in keys:
        update = "%s=VALUES(%s)" % (key, key)
        tmp.append(update)
    update_sql = ' ON DUPLICATE KEY UPDATE %s' % ', '.join(tmp)

    SQLQuery.join(update_sql, sep="", target=sql_query)

    return sql_query

def CachedGetValue(key):
    try:
        mc = memcached_wrapper.getMemcached()
        value = mc.get(str(key).replace(' ',''))
        mc.disconnect_all()
        if value == None:
            return False
        else:
            return value
    except Exception, e:
        print "Memcached get val error "
        print Exception, ":", e
        print key
        print value

def CahedSetValue(key,value, timeout):
    try:
        mc = memcached_wrapper.getMemcached()
        ret  = mc.set(str(key).replace(' ',''), value, timeout)
        mc.disconnect_all()
        return ret
    except Exception, e:
        print "Memcached set error "
        print Exception, ":", e
        print key
        print value

def CachedClearValue(key):
    try:
        mc = memcached_wrapper.getMemcached()
        mc.delete(str(key).replace(' ',''))
        mc.disconnect_all()
    except Exception, e:
        print "Memcached clear error ,key"
        print Exception, ":", e
        print key

def getNecessaryPara(data, para, required=True):
    temp = data.get(para, None)
    if temp is None and required:
        raise Exception("%s is required" %para)
    return temp

def getCurrentDate():
    return time.strftime("%Y-%m-%d", time.localtime())

def getCurrentTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def list2Dict(list):
    d = {}
    for item in list:
        d[str(item["id"])] = item
    return d


def checkPostAction(object,data,suppostAction):
    token = data.pop("token", None)
    if token:
        if not checkSession(token):
            return packOutput({}, "401", "Token authority failed")
    action = data.pop("action", None)
    if action is None:
        return packOutput({}, code="400", errorInfo='action required')
    if action not in suppostAction:
        return packOutput({}, code="400", errorInfo='unsupported action')

    # result = getattr(object, suppostAction[action])(data)
    # return packOutput(result)
    try:
        result = getattr(object, suppostAction[action])(data)
        return packOutput(result)
    except Exception as e:
        exc_traceback = sys.exc_info()[2]
        error_trace = traceback.format_exc(exc_traceback)
        error_args = e.args
        if len(error_args) == 2:
            code = error_args[0]
            error_info = str(error_args[1])
        else:
            code = "500"
            error_info = str(e)
        return packOutput({"errorInfo": str(error_info), "rescode": code},
                          code=code, errorInfo=error_trace)