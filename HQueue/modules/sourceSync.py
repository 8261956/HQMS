# -*- coding: UTF-8 -*-

import os, sys, urllib, threading, time
import visitor
import HQueue.DBIO.DBBase as DB
from common.func import LogOut
from mainWorker import SendMediaConvert


exitFlag = 0

class myThread (threading.Thread):   #继承父类threading.Thread
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        print "Starting " + self.name
        sourceSync(self.name, self.counter, 5)
        print "Exiting " + self.name

def threadExit():
    try:
        sys.exit(0)
    except:
        print 'die'
    finally:
        print 'cleanup'

def sourceSync(threadName, delay, counter):
    print "Source Sync Thread"
    # 获得分诊台的列表
    ret = DB.DBLocal.select('stationSet')
    stationList = []
    for item in ret:
        stationList.append(item)
    num = len(stationList)

    counter = 0
    while 1:
        time.sleep(delay)
        try:
            #同步每个分诊台数据
            station = stationList[counter%num]
            visitorManager= visitor.VisitorManager()
            visitorManager.stationID = station["id"]
            visitorManager.backupOld()
            visitorManager.syncSource()
            #wavPreload(station["id"]).load()
            #计数
        except Exception, e:
            print Exception, ":", e
        print "%s: %s" % (threadName, time.ctime(time.time()))
        counter += 1
        if (counter % num) == 0:
            #更新分诊台的列表
            ret = DB.DBLocal.select('stationSet')
            stationList = []
            for item in ret:
                stationList.append(item)
            num = len(stationList)

        if(counter /num) >=20:
            threadExit()


class wavPreload:
    def __init__(self, stationID):
        self.stationID = stationID
        return

    def load(self):
        vlist = DB.DBLocal.where("visitor_source_data", stationID=self.stationID)
        print "station :" + str(self.stationID) + " num: " + str(len(vlist))
        cnt = 0
        for vitem in vlist:
            vName = vitem["name"]
            cnt += 1
            print "vName" + vName + str(cnt)
            callerList = DB.DBLocal.where('caller', stationID=self.stationID)
            for caller in callerList:
                cName = caller["pos"]
                cid = str(self.stationID) + "_" + str(vitem["id"]) + "_" + str(caller["id"])
                wavText = "请" + vName + "到" + cName + "就诊"
                path = "/var/www/html/media/" + wavText + ".wav"
                if os.path.exists(path) == False:
                    fo = open(path, "w")
                    mediaList = SendMediaConvert(cid, wavText)
                    # url from response
                    if len(mediaList) > 0:
                        for media in mediaList:
                            if str(media["id"]) == str(cid):
                                url = media["path"]
                                urllib.urlretrieve(url, path)
                                LogOut.debug("get media conver result " + cid + " text " + wavText + " url " + url)
                else:
                    print path + " exist !"
                pass
            pass

        pass
# 创建新线程
thread1 = myThread(1, "Source Sync Thread", 2)

# 开启线程
thread1.start()
