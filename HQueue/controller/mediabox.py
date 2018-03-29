# -*- coding: utf-8 -*-

import web, json, datetime, requests
from common.func import packOutput, list2Str, str2List
from common.DBBase import DBLocal as DB
from common import config as cfg


class MediaBoxInterface:

    def POST(self, data):
        """Interface to handle different requests to manage media box."""

        data = json.loads(web.data())

        action = data.pop("action", None)
        if action is None:
            return packOutput({}, "400", "action required.")

        if action == "getListAll":
            try:
                result = self.getListAll()
                return packOutput(result)
            except Exception as e:
                print str(e)
                return packOutput({}, code="400", errorInfo=str(e))

        elif action == "getInfo":
            try:
                result = self.getInfo(data)
                return packOutput(result)
            except Exception as e:
                print str(e)
                return packOutput({}, code="400", errorInfo=str(e))

        elif action == "edit":
            try:
                result = self.edit(data)
                return packOutput(result)
            except Exception as e:
                print str(e)
                return packOutput({}, code="400", errorInfo=str(e))

        elif action == "delete":
            try:
                result = self.delete(data)
                return packOutput(result)
            except Exception as e:
                print str(e)
                return packOutput({}, code="400", errorInfo=str(e))

        else:
            return packOutput({}, code="500", errorInfo="unsupport action.")

    def getListAll(self):
        """Interface to get information of all media box in the system."""

        out = self.getListAllQuery()
        num = len(out)
        result = {"num": num, "list": []}
        if num:
            for item in out:
                mediabox = item.copy()
                mediabox = self.mediaBoxStatus(mediabox)
                result["list"].append(mediabox)
        return result

    def getInfo(self, data):
        """Interface to get information of a media box."""

        id = data.get("id", None)
        if not id:
            raise Exception("[ERR]: id required.")

        out = self.getListQuery(id)
        mediabox = out.copy()
        result = self.mediaBoxStatus(mediabox)
        return result

    def mediaBoxStatus(self, dict):
        """Check a media box is online or offline.

        Parameter dict must have `id` and `lastDateTime` field.
        """

        id = dict.get("id", None)
        if id is None:
            raise Exception("[ERR]: id required.")
        lastDateTime = dict.pop("lastDateTime", None)
        if lastDateTime is None:
            raise Exception("[ERR]: lastDateTime requried for mediabox %s." % id)
        now = datetime.datetime.now()
        try:
            interval = (now - lastDateTime).seconds
        except:
            raise Exception("[ERR]: Invalid lastDateTime for mediabox %s." % id)
        if interval >= 10:
            dict["status"] = "offline"
        else:
            dict["status"] = "online"
        return dict

    def getListAllQuery(self):
        """Query all media boxes in the system."""

        sql = "SELECT p.id, p.deviceIP as ip, p.stationID, p.lastDateTime, s.name as stationName " \
              "FROM publish as p INNER JOIN stationSet as s ON p.stationID = s.id"
        out = DB.query(sql)
        return out

    def getListQuery(self, id):
        """Query the media box identified by parameter id."""

        sql = "SELECT p.id, p.deviceIP as ip, p.stationID, p.speed, p.volume, " \
              "p.pitch, p.callerLimit, p.lastDateTime, s.name as stationName " \
              "FROM publish as p INNER JOIN stationSet as s ON p.stationID = " \
              "s.id WHERE p.id = %s" % id
        out = DB.query(sql).first()
        if out:
            if not out.callerLimit:
                out.callerLimit = ""
            out.callerLimit = map(int, str2List(out.callerLimit))
        else:
            raise Exception("[ERR]: mediabox not exists.")
        return out

    def edit(self, data):
        """Interface to edit the information of a media box.

        Args:
            data: JSON format data. For example:

            {
                "token": " safe action",
                "id": "12",
                "speed": "50",
                "volume": "50",
                "pitch" : "50"
            }

            If the data does not have `speed`, `pitch` or `volume` field,
            raise an Exception.

        Returns:
            Apply the settings to the media box and update the database for input data.
            If success, returns JSON format data, otherwise raise an Exception.
        """

        id = data.get("id", None)
        if id is None:
            raise Exception("[ERR]: id required.")

        mediabox = DB.select("publish", what="deviceIP", where="id=$id", vars={"id": id})
        if len(mediabox) == 0:
            raise Exception("[ERR]: mediabox not exists.")
        ip = mediabox[0].deviceIP

        speed = data.get("speed", 50)
        pitch = data.get("pitch", 50)
        volume = data.get("volume", 100)
        callerLimit = data.get("callerLimit", [])
        # if not speed or not pitch or not volume:
        #     raise Exception("[ERR]: speed, pitch, volume required.")

        values = {"callerLimit": list2Str(callerLimit)}
        mediaboxInfo = self.getInfo({"id": id})
        if mediaboxInfo["status"] == 'online':
            values.update({"speed": speed, "pitch": pitch, "volume": volume})
            url = "%s/setting/%s/%s/%s" % (
            str(ip), str(volume), str(pitch), str(speed))
            r = requests.get(url)

        try:
            DB.update("publish", where="id=$id", vars={"id": id}, **values)
            result = {"result": "success"}
        except:
            result = {"result": "failed"}

        return result

    def delete(self, data):
        """Interface to delete a offline media box.

        Args:
            data: JSON format data. For example:

            {
                "token": " safe action",
                "id": "2"
            }

        Returns:
            Query database to get the media box that identified by parameter id.
            If the media box is offline, then delete it from database and returns
            JSON format data, otherwise do not delete it.
        """

        id = data.get("id", None)
        if id is None:
            raise Exception("[ERR]: id required.")

        out = self.getListQuery(id)
        if len(out) == 0:
            raise Exception("[ERR]: mediabox not exists.")
        mediabox = out[0].copy()
        mediabox = self.mediaBoxStatus(mediabox)
        result = {}
        if mediabox["status"] == "offline":
            DB.delete("publish", where="id=$id", vars={"id": id})
            result["result"] = "success"
            return result
        else:
            result["result"] = "failed"
            return result


class MediaBoxHeartBeat:
    """Class `MediaBoxHeartBeat` is used to handle heart beat request."""

    def POST(self, data):

        data = json.loads(web.data())

        try:
            result = self.heartBeat(data)
            return packOutput(result)
        except Exception as errorInfo:
            print errorInfo
            return packOutput({}, code='400', errorInfo=str(errorInfo))

    def heartBeat(self, data):
        """Interface to handle heart beat request.

        It will set status for a media box. We can use the status
        to check a media box is online or offline.
        """

        stationID = data.get("stationId", None)
        if stationID is None:
            raise Exception("[Err]: stationId required.")
        stationSet = DB.select("stationSet", where="id=$id", vars={"id": stationID})
        if len(stationSet) == 0:
            raise Exception("[ERR]: statitonSet not exists.")

        deviceIP = data.get("serverAddress", None)
        if deviceIP is None:
            raise Exception("[Err]: serverAddress required.")

        isHttpServerAlive = data.get("isHttpServerAlive", None)
        isSpeechManagerInit = data.get("isSpeechManagerInit", None)
        if not isHttpServerAlive or not isSpeechManagerInit:
            raise Exception("[Err]: mediaBox is not alive.")

        speakerParams = data.get("speakerParams", None)
        if speakerParams is None:
            speakerParams = {
                "speed": "50",
                "pitch": "50",
                "volume": "100"
            }
        speed = speakerParams["speed"]
        pitch = speakerParams["pitch"]
        volume = speakerParams["volume"]

        speechList = data.get("speechList", None)
        if not speechList or len(speechList) == 0:
            speechState = "free"
        else:
            speechState = "busy"

        current_time = datetime.datetime.now()
        # TODO：下次版本更新时删除这两个字段
        voiceFormate = cfg.voiceFormateDefault
        displayFormate = cfg.displayFormateDefault
        mediaBox = DB.where("publish", deviceIP=deviceIP)
        if len(mediaBox) == 0:
            DB.insert("publish", stationID=stationID, deviceIP=deviceIP,
                      speed=speed, pitch=pitch, volume=volume,
                      speechState=speechState, lastDateTime=current_time,
                      voiceFormate=voiceFormate, displayFormate=displayFormate)
        else:
            DB.update("publish", where="deviceIP=$deviceIP", vars={"deviceIP": deviceIP},
                      stationID=stationID, speechState=speechState,
                      lastDateTime=current_time,
                      voiceFormate=voiceFormate, displayFormate=displayFormate)

        Date = current_time.date().strftime("%Y%m%d")
        time = current_time.time().strftime("%H%M%S")
        result = {"Date": Date, "time": time}
        return result
