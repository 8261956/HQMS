# -*- coding: utf-8 -*-

import datetime
from collections import defaultdict
import json
import sys
import traceback
import web
from common.func import packOutput, checkSession, CachedGetValue, CahedSetValue
from DBIO import DBBase as DB
from modules.publish import PublishTVInterface


class ExtManager(object):

    def __init__(self):
        self.db = DB.DBLocal

    def getPatientsInfo(self, startDate=None, endDate=None):
        """查询所有队列所有排队的患者信息。

        Returns: 所有队列所有患者的排队信息。

        """
        key = "_getPatientsInfo_ext"
        value = CachedGetValue(json.dumps(key))
        if value != False:
            return value

        if startDate and endDate:
            where = "registDate BETWEEN \'{0}\' AND \'{1}\'".format(
                startDate, endDate)
        else:
            where = "registDate = \'{0}\'".format(datetime.datetime.now().strftime("%Y-%m-%d"))
        what = "id, name, age, snumber, cardID AS userPid, registDate, " \
               "queueID, department, localStatus, " \
               "prior, locked, localVip, VIP, orderType"
        order = "stationID, queueID, finalScore, originScore"
        patients = self.db.select("visitor_view_data", what=what,
                                  order=order).list()

        queue_id_list = []
        counter = 0
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
                counter = 0
                queue_id_list.append(queueID)

            localStatus = p.localStatus
            if localStatus in ('finish', 'doing', 'pass'):
                pass
            else:
                counter += 1

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

        CahedSetValue(json.dumps(key), patients, 10)

        return patients


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


class ExtInterface(object):

    support_action = {
        "allSearch": "allSearch"
    }

    def POST(self):
        data = json.loads(web.data())
        result = checkPostAction(self, data, self.support_action)
        return result

    def allSearch(self, data):
        startDate = data.get("startDate", None)
        endDate = data.get("endDate", None)
        result = ExtManager().getPatientsInfo(startDate, endDate)
        return result
