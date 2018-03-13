# -*-coding: utf-8 -*-

from collections import deque
from functools import wraps
import json
import re

import datetime
import time
import web
from DBIO.DBBase import DBLocal
from modules.queueData import QueueDataController
from common.func import CahedSetValue, CachedGetValue, multiple_insert_sql

import gevent
from gevent import monkey, pool
monkey.patch_all()


def memcached_wrapper(key, timeout):
    """memcached装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kw):
            value = CachedGetValue(json.dumps(key))
            if value:
                return value
            result = func(*args, **kw)
            CahedSetValue(json.dumps(key), result, timeout)
            return result
        return wrapper
    return decorator


class SyncManager(object):

    def __init__(self):
        self.db = DBLocal
        self.source_db_conn = self.get_source_db_conn()
        self.pool = pool.Pool(5)
        self.cache = {}

    def create_db_conn(self, db_type, host, port, charset, user, password,
                       db_name):
        """根据配置创建数据库连接"""

        if db_type == "oracle":
            conn = web.database(
                dbn=db_type,
                user=user,
                pw=password,
                db=host
            )
        else:
            conn = web.database(
                dbn=db_type,
                host=host,
                port=int(port),
                user=user,
                pw=password,
                db=db_name
            )

        return conn

    def get_source_db_sql(self, **config):
        """获取数据源查询的SQL语句"""

        parse_dict = {
            "aliasID": "id",
            "aliasName": "name",
            "aliasAge": "age",
            "aliasQueue": "queue",
            "aliasOrderDate": "orderDate",
            "aliasOrderTime": "orderTime",
            "aliasRegistDate": "registDate",
            "aliasRegistTime": "registTime",
            "aliasSnumber": "snumber",
            "aliasVIP": "VIP",
            "aliasOrderType": "orderType",
            "aliasWorkerID": "workerID",
            "aliasWorkerName": "workerName",
            "aliasDepartment": "department",
            "aliasDescText": "descText",
            "aliasStatus": "status",
            "aliasCardID": "cardID",
            "aliasPersonID": "personID",
            "aliasPhone": "phone"
        }

        as_statement = []
        for key, value in parse_dict.items():
            config_value = config.get(key, None)
            if config_value:
                tmp = "{0} AS {1}".format(config_value, value)
                as_statement.append(tmp)
        sql = ', '.join(as_statement)

        return sql

    def get_source_db_conn(self):
        """获取数据源连接"""

        stations = self.db.select("stationSet").list()

        source_db_list = []
        for s in stations:
            sql = self.get_source_db_sql(**s)
            db_config = {
                "DBType": s.DBType,
                "host": s.host,
                "port": s.port,
                "charset": s.charset,
                "user": s.user,
                "password": s.passwd,
                "DBName": s.DBName,
                "tableName": s.tableName,
                "sql": sql
            }
            if db_config not in source_db_list:
                source_db_list.append(db_config)

        source_db_conn = []
        for db in source_db_list:
            conn = self.create_db_conn(db["DBType"], db["host"], db["port"],
                                       db["charset"], db["user"],
                                       db["password"], db["DBName"])
            query_sql = "SELECT {0} FROM {1}".format(db["sql"], db["tableName"])
            conn_dict = {
                "conn": conn,
                "sql": query_sql
            }
            source_db_conn.append(conn_dict)

        return source_db_conn

    def sync_fast(self):
        self.sync_source_data_fast()
        self.set_memcached_value()
        self.sync_local_data_fast()

    def sync_source_data_fast(self):
        start = datetime.datetime.now()
        for c in self.source_db_conn:
            conn = c["conn"]
            sql = c["sql"]
            self.pool.add(gevent.spawn(self._sync_source_data, conn, sql))

        self.pool.join()
        end = datetime.datetime.now()
        intervals = (end - start).seconds
        print "Sync Source Data Cost: {0} ms".format(intervals * 1000)

    def set_memcached_value(self):
        for key, value in self.cache.items():
            # self.pool.add(gevent.spawn(self._set_memcached_value, key, value))
            self._set_memcached_value(key, value)
        self.pool.join()
        self.cache = {}

    def sync_local_data_fast(self):
        start = datetime.datetime.now()
        for q in self.queue_info:
            stationID = q["stationID"]
            queueID = q["id"]
            # self.pool.add(gevent.spawn(self._sync_local_data, stationID, queueID))
            self._sync_local_data(stationID, queueID)

        # self.pool.join()
        end = datetime.datetime.now()
        intervals = (end - start).seconds
        print "Sync Local Data Cost: {0} ms".format(intervals * 1000)

    @property
    @memcached_wrapper('queue_info_wrapper', 3)
    def queue_info(self):
        """获取队列信息"""

        sql = "SELECT q.id, q.stationID, q.name AS queueName, q.filter, " \
              "s.name AS stationName FROM queueInfo q " \
              "INNER JOIN stationSet s ON q.stationID = s.id"
        queues = self.db.query(sql).list()
        for q in queues:
            filter = re.findall(r'queue=\'(.*)\'', q.pop("filter"))
            queue = filter[0]
            q.update({"queue": queue})
        return queues

    def set_queue_info(self, sync_data):
        """为需要同步的数据设置队列信息

        Args:
            sync_data: 需要同步的数据
        """

        for q in self.queue_info:
            for data in sync_data:
                if q["queue"] == data["queue"]:
                    data.update({"queue_info": q})

        return sync_data

    def _sync_source_data(self, conn, sql):
        """查询数据源获取数据，并同步到当前系统数据库中。

        Args:
            conn: 数据源数据库连接
            sql: 查询SQL语句
        """

        sync_data = conn.query(sql).list()
        sync_data = self.set_queue_info(sync_data)
        # conn._db_cursor().close()
        # conn.ctx.db.close()

        visitor_id_list = [data.id for data in sync_data]
        source_visitor = self.db.select("visitor_source_data",
                            what="id",
                            where="id IN {0}".format(web.sqlquote(visitor_id_list))
                            ).list()

        update_visitor_id = [data.id for data in source_visitor]
        insert_visitor_id = list(set(visitor_id_list) ^ set(update_visitor_id))

        for data in sync_data:
            id = data.id
            queue_info = data.pop("queue_info")
            if not queue_info:
                continue
            stationID = queue_info["stationID"]
            data.update({
                "stationID": queue_info["stationID"],
                "queueID": queue_info["id"]
            })
            if id in insert_visitor_id:
                cached_data = {
                    "id": data.id,
                    "name": data.name,
                    "age": data.age,
                    "snumber": data.snumber,
                    "department": data.department,
                    "stationID": queue_info["stationID"],
                    "queueID": queue_info["id"],
                    "stationName": queue_info["stationName"],
                    "queueName": queue_info["queueName"]
                }
                key = "print_stationID_{0}".format(stationID)
                self.cache.setdefault(key, deque([])).append(cached_data)
            else:
                pass
        insert_update_sql = multiple_insert_sql("visitor_source_data", sync_data)
        self.db.query(insert_update_sql)

    def _sync_local_data(self, stationID, queueID):
        # TODO: updateVisitor方法会使用memcached缓存，针对每个患者同步时会建立socket连接。关闭时会导致出现大量TIME_WAIT状态的连接。
        data = {"stationID": stationID, "queueID": queueID}
        QueueDataController().updateVisitor(data)

    def _set_memcached_value(self, key, data):
        """将需要缓存的分诊台信息写入memcached

        Args:
            key: 键
            **data: 需要写入的数据
        """
        queue = CachedGetValue(json.dumps(key))
        if not queue:
            queue = deque([])
        queue.extend(data)
        CahedSetValue(json.dumps(key), queue, timeout=3600)


def main():
    s = SyncManager()
    while True:
        start = datetime.datetime.now()
        s.sync_fast()
        end = datetime.datetime.now()
        intervals = (end - start).seconds
        print "Totally Cost: {0} ms".format(intervals * 1000)
        time.sleep(5)


if __name__ == '__main__':
    main()
