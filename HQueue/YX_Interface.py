# -*- coding: UTF-8 -*-

import time,datetime
from suds.client import Client
from suds.xsd.doctor import Import, ImportDoctor
import xml.etree.ElementTree as ET
from collections import OrderedDict
import common.xmlDict as XML
from DBIO.DBBase import DBLocal
#from modules.visitor import VisitorManager
import modules.visitor 

YX_url = "http://192.168.11.77:8082/HISWebService.asmx?WSDL"


def getClient():
    print "getWebService func In"
    tClient = Client(YX_url)
    print "Client Init ok"
    #print (tClient)
    return tClient

def MainMethod(SourceName , OpNum , OpControl ,OpData , Picture = None):
    """
    基础输入参数入口
    :param SourceName: STRING  调用接口的平台名称(yyt)
    :param OpNum:      STRING  相关业务功能编号
    :param OpControl:  STRING  调用接口入参xml格式
    :param OpData:     STRING  调用接口入参xml格式
    :param Picture:     图片转化的字节数组
    :return:
    """
    d = OrderedDict()
    d["SourceName"] = SourceName
    d["OpNum"] = OpNum
    d["OpControl"] = OpControl
    d["OpData"] = OpData
    c = getClient()
    print "OpControl :  " + OpControl
    # 调用方法访问数据
    res = c.service.MainMethod(d)
    print "MainMethod res:"
    print res
    return res

def InqOnDuty(starttime,endtime,inPara1 = "",inPara2 = "",inPara3 = "",inPara4 = "",inPara5 = "",inPara6 = ""):
    """
    获得排班接口
    :param time: time格式 2017.08.01
    :param inPara: 预留参数
    :return: 排班数据字典
    """
    d = OrderedDict()
    d["starttime"] = str(starttime)
    d["endtime"] = str(endtime)
    d["inPara1"] = str(inPara1)
    d["inPara2"] = str(inPara2)
    d["inPara3"] = str(inPara3)
    d["inPara4"] = str(inPara4)
    d["inPara5"] = str(inPara5)
    d["inPara6"] = str(inPara6)
    data = XML.dict2xml("data",d)
    data_str = ET.tostring(data)
    print "OpCtrl:\r\n"
    print data_str
    ret = MainMethod("qh","003",data_str,"")
    print "start dict"
    _xml = ET.fromstring(ret.encode('utf-8'))
    duty = XML.build_dict(_xml)
    print "duty Dict:"
    print (duty)
    RspCode = duty["RspCode"]["_text"]
    if RspCode == "0":
        print "DUTY DATA INQUIRE OK"
        data = duty["dataset"]
        return data["row"]
    else:
        print "FAILED" + duty["RspMsg"]["_text"]
        return  {}


def InqDoctorList(type,inPara1 = "",inPara2 = "",inPara3 = "",inPara4 = "",inPara5 = "",inPara6 = ""):
    """
    查询医生列表
    :param type:  01 查询医生信息字典
    :param inPara: 预留字段
    :return:
    """
    d = OrderedDict()
    d["type"] = str(type)
    d["inPara1"] = str(inPara1)
    d["inPara2"] = str(inPara2)
    d["inPara3"] = str(inPara3)
    d["inPara4"] = str(inPara4)
    d["inPara5"] = str(inPara5)
    d["inPara6"] = str(inPara6)
    date = XML.dict2xml("data",d)
    ret = MainMethod("qh","002",ET.tostring(date),"")
    print "start dict"
    _xml = ET.fromstring(ret.encode('utf-8'))
    retDict = XML.build_dict(_xml)
    RspCode = retDict["RspCode"]["_text"]
    if RspCode == "0":
        print "DUTY DATA INQUIRE OK"
        data = retDict["dataset"]
        return data["row"]
    else:
        print "FAILED" + retDict["RspMsg"]["_text"]
        return  {}

def InqQueueList(ksdm,ghrq,time_flag,ysdm = "",inPara1 = "",inPara2 = "",inPara3 = "",inPara4 = "",inPara5 = "",inPara6 = ""):
    """
    查询队列患者列表
    :param ksdm:   科室代码
    :param ysdm:   医生代码
    :param ghrq:   挂号日期
    :param time_flag:   查询时间  >时间的条件查询 为空时查所有
    :param inPara: 预留字段
    :return:
    """
    d = OrderedDict()
    d["ksdm"] = str(ksdm)
    d["ysdm"] = str(ysdm)
    d["ghrq"] = str(ghrq)
    d["time_flag"] = str(time_flag)
    d["inPara1"] = str(inPara1)
    d["inPara2"] = str(inPara2)
    d["inPara3"] = str(inPara3)
    d["inPara4"] = str(inPara4)
    d["inPara5"] = str(inPara5)
    d["inPara6"] = str(inPara6)
    data = XML.dict2xml("data", d)
    ret = MainMethod("qh", "001", ET.tostring(data), "")
    print "start dict"
    _xml = ET.fromstring(ret.encode('utf-8'))
    ret = XML.build_dict(_xml)

    RspCode = ret["RspCode"]["_text"]
    if RspCode == "0":
        print "DATA INQUIRE OK"
        data = ret["dataset"]
        return data["row"]
    else:
        print "FAILED" + ret["RspMsg"]["_text"]
        return  {}

vManager = modules.visitor.VisitorManager()

class SyncSource():
    def __init__(self):
        self.sync_time = time.strftime("%Y/%m/%d", time.localtime()) + " 00:00:01"

    def run(self):
        while(1):
            #更新本地资源表
            vManager.getInnerSourceDict()
            #同步外部源
            print "Sync Time : " + self.sync_time
            dbTimeStr = visitorSync("",self.sync_time)
            dbTime = datetime.datetime.strptime(dbTimeStr, '%Y/%m/%d %H:%M:%S')
            sync_time = dbTime - datetime.timedelta(seconds=3)
            self.sync_time = sync_time.strftime('%Y/%m/%d %H:%M:%S')
            time.sleep(12)
            #同步本地源
            vManager.syncLocal()
            #test end
            #return

def visitorSync(ksdm,sync_time):
    """
    同步队列 患者
    :param ksdm:  科室代码  空时查询所有科室
    :param sync_time:       查询时刻之后的新增患者
    :return:
    """
    currentDate = time.strftime("%Y.%m.%d", time.localtime())
    vList = []
    ret = InqQueueList(ksdm=ksdm,ghrq = currentDate,time_flag=sync_time)
    if isinstance(ret, dict):
        vList.append(ret)
    elif isinstance(ret, list):
        vList = ret
    DBTIME = sync_time
    for item in vList:
        registTime = item["REGISTTIME"]["_text"]

        visitor = {
            "id" : item["ID"]["_text"],
            "name": item["NAME"]["_text"],
            "age" : item["BRITHDAY"]["_text"],
            "queue" : item["DEPARTMENT"]["_text"] + item["DOCTORNAME"]["_text"],
            "registDate" : registTime,
            "registTime" : registTime,
            "snumber" : item["SNUMBER"]["_text"],
            "orderType" : item["ORDERTYPE"]["_text"],
            "workerID" : item["DOCTORID"]["_text"],
            "workerName" : item["DOCTORNAME"]["_text"],
            "department" : item["DEPARTMENT"]["_text"],
            "cardID" : item["CARDID"]["_text"],
            "personID": item["PERSONID"]["_text"],
            "phone" : item["PHONE"]["_text"],
            "VIP" : int(item["EMERGENCY"].get("_text","0"))
        }
        THF = item["THF"]["_text"]
        DBTIME = item["DBTIME"]["_text"]
        visitor_append(THF,visitor)

    return DBTIME

    #同步得到医生信息，得到医生代码
    #根据排班情况同步科室中队列的患者信息

def visitor_append(THF,visitor):
    if THF == 'N':
        vManager.add(visitor)
    else:
        # 处理退号
        vManager.sigVisitorFinished(visitor["name"],visitor["id"])

def ExternSourceQueueList():
    doctorList = InqDoctorList("01")
    qList = []
    for d in doctorList:
        qName = d["DEPARTMENT"].get("_text","") 
        dName = d["NAME"].get("_text","") 
        qList.append(qName+dName)
        print qName+dName
    return qList


def getWeatherTest():
    # WebService的地址
    url = 'http://ws.webxml.com.cn/WebServices/WeatherWS.asmx?wsdl'
    # 解决找不到schema的问题
    imp = Import('http://www.w3.org/2001/XMLSchema', location='http://www.w3.org/2001/XMLSchema.xsd')
    imp.filter.add('http://WebXml.com.cn/')
    # 生成客户端
    client = Client(url, doctor=ImportDoctor(imp))
    #print (client)
    # 调用方法访问数据
    weather_result = client.service.getWeather(u'上海')
    print weather_result



#print "-----InqOnDuty : ------"
#InqOnDuty("2017.06.01","2017.06.19")

#print "-----InqDoctorList : ------"
#InqDoctorList("01")
#ExternSourceQueueList()

#print "------queueList : test------"
#InqQueueList(ksdm="",ghrq = "2017.10.19",time_flag="2017/10/19 02:00:00")

#print "------SyncSource : run() ------"
#SyncSource().run()

