
# -*- coding: UTF-8 -*-

import os, sys
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
import web

reload(sys)
sys.setdefaultencoding('utf-8')

# URL
urls = (
    '/(hqueue/main)', 'MainPage',
    '/(hqueue/login)' , 'controller.account.LoginInterface',
    '/(hqueue/manager/station)', 'controller.station.StationInterface',
    '/(hqueue/manager/worker)', 'controller.worker.WorkerInterface',
    '/(hqueue/manager/stationAccount)', 'controller.account.StationAccountInterface',
    '/(hqueue/manager/caller)', 'controller.caller.CallerInterface',
    '/(hqueue/manager/queueInfo)', 'controller.queueInfo.QueueInfoInterface',
    '/(hqueue/manager/queueData)', 'controller.queueData.QueueDataController',
    '/(hqueue/manager/headpicUpload)', 'controller.worker.NginxUploadController',
    '/(hqueue/main/station)', 'controller.mainStation.StationMainController',
    '/(hqueue/main/worker)', 'controller.mainWorker.WorkerMainController',
    '/(hqueue/main/publish)', 'controller.publish.PublishTVInterface',
    '/(hqueue/mediaBox/heartBeat)', 'controller.mediabox.MediaBoxHeartBeat',
    '/(hqueue/manager/mediabox)', 'controller.mediabox.MediaBoxInterface',
    '/(hqueue/manager/CheckInDev)', 'controller.checkInDev.CheckInDevInterface',
    '/(hqueue/manager/scene)', "controller.scene.SceneInterface",
    '/(hqueue/manager/schedule)', "controller.schedule.ScheduleInterface",
    '/(hqueue/manager/queueMachine)', "controller.queueMachine.QueueMachineInterface",
    '/(hqueue/manager/database)', "common.DBBase.DBInterface",
    '/(hqueue/manager/weixin)', "controller.weixin.WXInterface",

    '/hqueue/main/extInterface', "project.ruici.extInterface.ExtInterface",
    '/hqueue/main/stationPrinter', "project.ruici.printerInterface.PrinterInterface",
)

def OracleTest():
    dbTest = web.database(
        dbn='oracle',
        db="hrp",#172.16.1.13/orcl
        user="queue",
        pw="bsoftqueue",
    )
    ret = dbTest.where("hrp.clientlist",queue = "中医儿科")
    return ret


class MainPage:
    def GET(self, name):
        return "清鹤排队叫号系统"

# startup
if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
else:
    app = web.application(urls, globals())
    application = app.wsgifunc()
