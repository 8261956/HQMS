# -*- coding: utf-8 -*-

import json
import sys
import traceback
import web
from common.func import packOutput, checkSession, CachedGetValue, CahedSetValue
from DBIO import DBBase as DB


class PrinterManager(object):

    def __init__(self):
        self.db = DB.DBLocal

    def get_next_visitor(self, stationID):
        """获取某分诊台新增患者的信息

        Args:
            stationID: 分诊台ID
        """

        key = "print_stationID_{0}".format(stationID)
        queue = CachedGetValue(json.dumps(key))
        visitor_info = {}

        if len(queue):
            visitor_info = queue.popleft()
            CahedSetValue(json.dumps(key), queue, timeout=0)

            visitor_id = visitor_info["id"]
            where = {"stationID": stationID, "id": visitor_id}
            visitor = self.db.select("visitor_local_data", where=where).first()
            if visitor:
                where = "stationID = $stationID AND queueID = $queueID " \
                        "AND status IN $status AND ( (finalScore = " \
                        "$finalScore AND originScore < $originScore) " \
                        "OR (finalScore < $finalScore) )"
                vars = {
                    "stationID": stationID,
                    "queueID": visitor_info["queueID"],
                    "status": ('doing', 'waiting', 'unactive',
                               'unactivewaiting'),
                    "finalScore": visitor.finalScore,
                    "originScore": visitor.originScore
                }
                what = "COUNT(*) AS count"
                query = self.db.select("visitor_local_data", where=where,
                                       vars=vars, what=what).first()
                visitor_info.update({
                    "waitNum": query.count,
                    "waitTime": query.count * 15
                })
            else:
                visitor_info = {}

        return visitor_info


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


class PrinterInterface(object):

    support_action = {
        "getNextVisitor": "getNextVisitor"
    }

    def POST(self):
        data = json.loads(web.data())
        result = checkPostAction(self, data, self.support_action)
        return result

    def getNextVisitor(self, data):
        stationID = data.get("stationID", None)
        if stationID is None:
            raise Exception("stationID required")
        result = PrinterManager().get_next_visitor(stationID)
        return result
