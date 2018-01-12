# -*- coding: UTF-8 -*-

import os, sys, time
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
import DBIO.DBBase as DB
from modules.visitor import VisitorManager
from common.config import integrateType
from YX_Interface import SyncSource

reload(sys)
sys.setdefaultencoding('utf-8')


def sourceSync(threadName, delay, station):
    print "Source Sync process"
    # 获得分诊台的列表
    stationList = []
    if not station:
        ret = DB.DBLocal.select('stationSet')
        for item in ret:
            stationList.append(item["id"])
    elif all([x < 0 for x in station]):
        ret = DB.DBLocal.select('stationSet')
        for item in ret:
            id = item["id"]
            if id in map(abs, station):
                continue
            else:
                stationList.append(id)
    else:
        stationList = station
    print stationList

    num = len(stationList)

    counter = 0
    while 1:
        start_time = time.time()
        time.sleep(delay)
        # try:
        # 同步每个分诊台数据

        #try:
        if 1:
            if integrateType == "VIEW":
                VisitorManager().syncSource()
                VisitorManager().syncLocal()
            elif integrateType == "WEBSERVICE":
                SyncSource().run()
        #except Exception as e:
        #    print "Exception:" + str(e)
        # 计数
        print "%s: %s" % (threadName, time.ctime(time.time()))
        counter += 1

        if (counter / num) >= 10:
            # counter = 0
            VisitorManager().backupOld()
            print "auto exit to clean up."
            break

        print "TIME COST: %s" % (time.time() - start_time)


if __name__ == '__main__':
    args = sys.argv[1:]
    station = map(int, args)
    print station
    print "Source Sync process"
    sourceSync("Sync Process", 5, station=station)
