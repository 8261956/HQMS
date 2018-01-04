# -*- coding: utf-8 -*-

import web, json, datetime
from HQueue.DBIO.DBBase import DBLocal as DB
from common.func import packOutput


class CheckInDevInterface:

    def POST(self, data):

        data = json.loads(web.data())

        action = data.pop("action", None)
        if not action:
            return packOutput({}, code="400", errorInfo="action required.")

        elif action == "heartbeat":
            try:
                result = self.heartBeat(data)
                return packOutput(result)
            except Exception as e:
                return packOutput({}, code="400", errorInfo=str(e))

        elif action == "getListAll":
            try:
                result = self.getListAll()
                return packOutput(result)
            except Exception as e:
                return packOutput({}, code="400", errorInfo=str(e))

        else:
            return packOutput({}, code="500", errorInfo="unsupport action.")

    def heartBeat(self, data):

        stationID = data.get("stationID", None)
        if not stationID:
            raise Exception("[ERR]: stationID required.")
        station = DB.select("stationSet", where="id=$id", vars={"id": stationID})
        if len(station) == 0:
            raise  Exception("[ERR]: station not exists for id %s" % stationID)

        deviceIP = web.ctx.ip
        checkinDev = DB.select("checkinDev", where="deviceIP=$deviceIP", vars={"deviceIP": deviceIP})
        current_time = datetime.datetime.now()
        if len(checkinDev) == 0:
            DB.insert("checkinDev", stationID=stationID, deviceIP=deviceIP, lastDateTime=current_time)
        else:
            DB.update("checkinDev", where="deviceIP=$deviceIP", vars={"deviceIP": deviceIP},
                      stationID=stationID, lastDateTime=current_time)

        Date = current_time.date().strftime("%Y%m%d")
        time = current_time.time().strftime("%H%M%S")
        result = {"Date": Date, "time": time}
        return result

    def getListAll(self):
        out = self.getListAllQuery()
        num = len(out)
        result = {"num": num, "list": []}
        if num:
            for item in out:
                checkinDev = item.copy()
                checkinDev = self.checkinDevStatus(checkinDev)
                result["list"].append(checkinDev)
        return result

    def checkinDevStatus(self, dict):
        id = dict.get("id", None)
        if id is None:
            raise Exception("[ERR]: id required.")
        lastDateTime = dict.pop("lastDateTime", None)
        if lastDateTime is None:
            raise Exception("[ERR]: lastDateTime required for checkinDev %s" % id)
        now = datetime.datetime.now()
        try:
            interval = (now - lastDateTime).seconds
        except:
            raise Exception("[ERR]: Invalid lastDateTime for checkinDev %s" % id)
        if interval >= 20:
            dict["status"] = "offline"
        else:
            dict["status"] = "online"
        return dict

    def getListAllQuery(self):
        sql = "SELECT c.id, c.deviceIP as ip, c.stationID, c.lastDateTime, s.name as stationName " \
              "FROM checkinDev as c INNER JOIN stationSet as s ON c.stationID = s.id"
        out = DB.query(sql)
        return out
