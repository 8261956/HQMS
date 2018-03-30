# -*- coding: utf-8 -*-
import datetime
import web
from uwsgidecorators import *

from common.DBBase import DBLocal


class TaskManager(object):

    def __init__(self):
        self.db = DBLocal

    def backupQueueVisitors(self, date, queue_list=None):
        """备份指定队列的患者信息

        Args:
            date: 日期
            queue_list: 指定队列列表
        """

        where = "registDate < \'{0}\'".format(date)
        if queue_list:
            where += " AND queueID IN {0}".format(str(web.db.sqlquote(
                queue_list)))
        # expired_visitor_data = self.db.select("visitor_source_data",
        #                                          where=where).list()
        sql = "SELECT vs.*, vl.status AS localStatus, vl.workStartTime, " \
              "vl.workEndTime FROM visitor_source_data vs INNER JOIN " \
              "(SELECT * FROM visitor_local_data WHERE {0}) vl " \
              "ON vs.id = vl.id".format(where)
        expired_visitor_data = self.db.query(sql).list()
        self.db.printing = False
        if expired_visitor_data:
            visitor_group = web.group(expired_visitor_data, 1000)
            for item in visitor_group:
                self.db.multiple_insert("visitor_backup_data", item)
        self.db.printing = True
        self.db.delete("visitor_source_data", where)
        self.db.delete("visitor_local_data", where)

    def backupAllVisitors(self):
        """备份所有患者信息"""

        queueList =self.db.select("queueInfo", what="id AS queueID, sceneID").list()
        sceneList = self.db.select("scene", what="id, workDays").list()

        tmp = []
        for q in queueList:
            workDays = 1
            sceneID = q.pop("sceneID")
            for s in sceneList:
                if s["id"] == sceneID:
                    workDays = s["workDays"]
                    if not workDays:
                        workDays = 1
                    break
            date = datetime.datetime.now() - datetime.timedelta(days=workDays)
            date_str = date.strftime("%Y-%m-%d")
            q.update({"date": date_str})
            tmp.append(tuple(q.values()))

        import collections
        d = collections.defaultdict(list)
        for k, v in tmp:
            if not isinstance(k, int):
                d[k].append(v)
            else:
                d[v].append(k)

        for date, queue_list in d.items():
            self.backupQueueVisitors(date, queue_list)


task= TaskManager()


@cron(40, 12, -1, -1, -1)
def backupVisitorData(signum):
    task.backupAllVisitors()
