# -*- coding: utf-8 -*-

import datetime
from collections import defaultdict
import json
import web
from HQueue.common.func import checkPostAction
from HQueue.DBIO import DBBase as DB
from HQueue.modules.publish import PublishTVInterface


class ExtManager(object):

    def __init__(self):
        self.db = DB.DBLocal

    def getPatientsInfo(self):
        """查询所有队列所有排队的患者信息。

        Returns: 所有队列所有患者的排队信息。

        """
        where = "registDate = \'{0}\'".format(datetime.datetime.now().strftime("%Y-%m-%d"))
        what = "id, name, age, snumber, cardID AS userPid, registDate, " \
               "queueID, department, localStatus, " \
               "prior, locked, localVip, VIP, orderType"
        order = "stationID, queueID, finalScore, originScore"
        patients = self.db.select("visitor_view_data", what=what, where=where,
                                  order=order).list()

        queue_id_list = []
        counter = 1
        queue_counter = defaultdict(int)

        # 获得每个队列的排队人数
        for p in patients:
            queueID = p.queueID
            if queueID not in queue_id_list:
                queue_id_list.append(queueID)
            if p.localStatus not in ('finish', 'doing', 'pass'):
                queue_counter[p.queueID] += 1

        # 获取所有队列名称信息
        queue_info = {}
        if queue_id_list:
            what = "id, name"
            where = "id IN {0}".format(web.sqlquote(queue_id_list))
            queues = self.db.select("queueInfo", where=where, what=what).list()
            for q in queues:
                queue_info[q.id] = q.name
            queue_id_list = []

        # 更新返回值
        for p in patients:
            queueID = p.pop("queueID")
            if queueID not in queue_id_list:
                counter = 1
                queue_id_list.append(queueID)
            elif p.localStatus == 'pass':
                pass
            else:
                counter += 1

            localStatus = p.localStatus
            if localStatus in ('finish', 'doing'):
                waitNum = 0
            elif localStatus == 'pass':
                waitNum = queue_counter[queueID]
            else:
                waitNum = counter

            kw = {
                "prior": p.pop("prior"),
                "locked": p.pop("locked"),
                "localVip": p.pop("localVip"),
                "orderType": p.pop("orderType"),
                "VIP": p.pop("VIP")
            }
            status = PublishTVInterface().getVisitorStatus(**kw)

            if localStatus == 'finish':
                localStatus = '已完成'
            elif localStatus == 'doing':
                localStatus = '正在就诊'
            elif localStatus == 'waiting':
                localStatus = '正在排队'
            elif localStatus == 'pass':
                localStatus = '已过号'
            elif localStatus == 'unactive':
                localStatus = '未激活'
            elif localStatus == 'unactivewaiting':
                localStatus = '激活等待中'

            if status == 'locked':
                status = '锁定'
            elif status == 'review':
                status = '复诊'
            elif status == 'pass':
                status = '过号'
            elif status == 'delay':
                status = '延后'
            elif status == 'VIP':
                status = 'VIP'
            elif status == 'order':
                status = '预约'
            else:
                status = '普通'

            p.update({
                "waitingNum": waitNum,
                "waitingTime": waitNum * 15,
                "queueName": queue_info[queueID],
                "localStatus": localStatus,
                "status": status
            })

        return patients


class ExtInterface(object):

    support_action = {
        "allSearch": "allSearch"
    }

    def POST(self):
        data = json.loads(web.data())
        result = checkPostAction(self, data, self.support_action)
        return result

    def allSearch(self, data):
        result = ExtManager().getPatientsInfo()
        return result
