
# -*- coding: UTF-8 -*-

import os, sys
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
import web
import DBIO.DBBase as DB

reload(sys)
sys.setdefaultencoding('utf-8')

# URL
urls = (
    '/(hqueue/main)', 'MainPage',
    '/(hqueue/manager)', 'ManagerPage',
    '/(hqueue/login)' , 'modules.account.LoginInterface',
    '/(hqueue/manager/station)', 'modules.station.StationInterface',
    '/(hqueue/manager/worker)', 'modules.worker.WorkerInterface',
    '/(hqueue/manager/stationAccount)', 'modules.account.StationAccountInterface',
    '/(hqueue/manager/caller)', 'modules.caller.CallerInterface',
    '/(hqueue/manager/queueInfo)', 'modules.queueInfo.QueueInfoInterface',
    '/(hqueue/manager/queueData)', 'modules.queueData.QueueDataController',
    '/(hqueue/manager/headpicUpload)', 'modules.worker.NginxUploadController',
    '/(hqueue/manager/upload)', 'modules.worker.WebUploadController',
    '/(hqueue/main/station)', 'modules.mainStation.StationMainController',
    '/(hqueue/main/worker)', 'modules.mainWorker.WorkerMainController',
    '/(hqueue/main/publish)', 'modules.publish.PublishTVInterface',
    '/(hqueue/mediaBox/heartBeat)', 'modules.mediabox.MediaBoxHeartBeat',
    '/(hqueue/manager/mediabox)', 'modules.mediabox.MediaBoxInterface',
    '/(hqueue/manager/CheckInDev)', 'modules.checkInDev.CheckInDevInterface',
    '/(hqueue/manager/scene)', "modules.scene.SceneInterface",
    '/(hqueue/manager/schedule)', "modules.schedule.ScheduleInterface",
    '/(hqueue/manager/queueMachine)', "modules.queueMachine.QueueMachineInterface",
    '/(hqueue/manager/database)', "DBIO.DBBase.DBInterface",
    '/(hqueue/manager/weixin)', "modules.weixin.WXInterface",

    '/hqueue/main/extInterface', "project.ruici.extInterface.ExtInterface"
)

def OracleTest():
    dbTest = web.database(
        dbn='oracle',
        db="hrp",#172.16.1.13/orcl
        user="queue",
        pw="bsoftqueue",
    )
    #ret = dbTest.where("hrp.clientlist",queue = "中医儿科")
    #ret = dbTest.query("select * from hrp.clientlist where queue='中医儿科'")
    ret = dbTest.query("SELECT * FROM (SELECT DEPTNAME as name , QUEUE as queue , LOG_ID as id , TIMES as registDate , TIMES as registTime , SNUMBER as snumber , YUYUE as orderType , DOCNAME as workerName , ID as cardID from hrp.clientlist) visitorsView WHERE queue='中医儿科' and registTime > timestamp'2017-04-24 23:28:07'")
    return ret

def UrlPraseTest():
    url = "http://172.16.11.180:19000/media/20150102/60_978824.wav"
    s = url.find("media/")
    date = url[s+6:s+6+8]
    return date

class MainPage:
    def GET(self, name):
        if not name: name = 'world'
        web.header('Content-Type', 'text/html; charset=UTF-8')
        print (" 清鹤排队叫号系统")
        outStr = " 清鹤排队叫号系统"
        print("Init end")
        ret = OracleTest()
        return {"res":"121","error":ret}

class ManagerPage:
    def GET(self, name):
        if not name: name = 'world'
        web.header('Content-Type', 'text/html; charset=UTF-8')
        print(" ManagerPage")

        config = {"name" : "分诊台2" ,"descText" : "软件新建分诊台", "DBType":"mysql", "host":"192.168.17.184", "port":"3306", "charset":"utf8","DBName":"HisQueue","tableName":"visitors",
            "user":"root", "passwd":"123456", "aliasName":"name", "aliasAge":"age", "aliasQueue":"queue", "aliasID":"ID", "aliasOrderDate":"orderDate", "aliasOrderTime":"orderTime",
            "aliasRegistDate":"RegistDate", "aliasRegistTime":"registTime", "aliasSnumber":"snumber","aliasVIP":"emergency", "aliasOrderType":"orderType", "aliasWorkerID":"workerID",
            "aliasWorkerName":"workerName", "aliasDepartment":"department", "aliasDescText":"descText", "aliasStatus":"status", "renewPeriod":10
        }

        visitorSource = DB.StationVisitor()
        if visitorSource.testAliasSql(config):
            print("Add DBSource test Source success")
            id = visitorSource.newSource(config)
            visitorSource.SourceLoad(id)
        else:
            return "test Source failed"
        outStr = visitorSource.getAliasSql(config)
        return outStr

class StationPage:
    def GET(self,name):
        if not name: name = 'world'
        web.header('Content-Type', 'text/html; charset=UTF-8')
        print(" StationPage")
        outStr = "StationPage!"
        return outStr



# startup
if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
else:
    app = web.application(urls, globals())
    application = app.wsgifunc()
