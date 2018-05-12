# -*- coding: UTF-8 -*-
import sys,os

import time,datetime,json,web,re
from suds.client import Client
from suds.xsd.doctor import Import, ImportDoctor
import xml.etree.ElementTree as ET
from collections import OrderedDict
import common.xmlDict as XML
from common.DBBase import DBLocal
from  common.func import getCurrentTime,checkPostAction,getCurrentYear

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from controller.visitor import VisitorManager
#import modules.visitor 

YX_url = "http://192.168.11.77:8082/HISWebService.asmx?WSDL"
TYPE_FAYAO = "01"
TYPE_YIJI = "02"
TYPE_ZHUYUAN = "03"

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

def getResultList(xmlRet):
    RspCode = xmlRet["RspCode"]["_text"]
    retList = []
    if RspCode == "0":
        print "DATA INQUIRE OK"
        data = xmlRet["dataset"]
        xmlItem =  data["row"]
        if isinstance(xmlItem, dict):
            retList.append(xmlItem)
        elif isinstance(xmlItem, list):
            retList = xmlItem
        return retList
    else:
        print "FAILED" + xmlRet["RspMsg"]["_text"]
        return  []


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
    xmlRet = XML.build_dict(_xml)
    retList = getResultList(xmlRet)
    return retList

def InqDoctorList(type,inPara1 = "",inPara2 = "",inPara3 = "",inPara4 = "",inPara5 = "",inPara6 = ""):
    """
    查询医生列表
    :param type:  01 查询医生信息字典  02为查询医技队列字典 03为查询出入院队列字典
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
    xmlRet = XML.build_dict(_xml)
    retList = getResultList(xmlRet)
    return retList

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
    xmlRet = XML.build_dict(_xml)
    retList = getResultList(xmlRet)
    return retList

def PostRegist(blh,ywlx,dldm,fydl,inPara1 = "",inPara2 = "",inPara3 = "",inPara4 = "",inPara5 = "",inPara6 = ""):
    """
    报到机发送登记请求
    :param blh:   病例号
    :param ywlx:   业务类型
    :param dldm:   队列代码
    :return:
    """
    d = OrderedDict()
    d["blh"] = str(blh)
    d["ywlx"] = str(ywlx)
    d["dldm"] = str(dldm)
    d["fydl"] = str(fydl)
    d["inPara1"] = str(inPara1)
    d["inPara2"] = str(inPara2)
    d["inPara3"] = str(inPara3)
    d["inPara4"] = str(inPara4)
    d["inPara5"] = str(inPara5)
    d["inPara6"] = str(inPara6)
    data = XML.dict2xml("data", d)
    ret = MainMethod("qh", "004", ET.tostring(data), "")
    print "start dict"
    _xml = ET.fromstring(ret.encode('utf-8'))
    xmlRet = XML.build_dict(_xml)
    retList = getResultList(xmlRet)
    return retList

def InqVInfo(blh,trmtno,vid,sfzh,inPara1 = "",inPara2 = "",inPara3 = "",inPara4 = "",inPara5 = "",inPara6 = ""):
    """
    请求患者信息
    :param blh:   病例号
    :param trmtno:   就诊卡号
    :param vid:   就诊号
    :param sfzh:   身份证号码
    :return:
    """
    d = OrderedDict()
    d["blh"] = str(blh)
    d["trmtno"] = str(trmtno)
    d["vid"] = str(vid)
    d["sfzh"] = str(sfzh)

    d["inPara1"] = str(inPara1)
    d["inPara2"] = str(inPara2)
    d["inPara3"] = str(inPara3)
    d["inPara4"] = str(inPara4)
    d["inPara5"] = str(inPara5)
    d["inPara6"] = str(inPara6)
    data = XML.dict2xml("data", d)
    ret = MainMethod("qh", "005", ET.tostring(data), "")
    print "start dict"
    _xml = ET.fromstring(ret.encode('utf-8'))
    xmlRet = XML.build_dict(_xml)
    retList = getResultList(xmlRet)
    return retList

vManager = VisitorManager()

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
            if dbTimeStr != -1:
                dbTime = datetime.datetime.strptime(dbTimeStr, '%Y/%m/%d %H:%M:%S')
                sync_time = dbTime - datetime.timedelta(seconds=3)
                self.sync_time = sync_time.strftime('%Y/%m/%d %H:%M:%S')
            time.sleep(12)
            #同步本地源
            vManager.syncLocal()
            vManager.backupOld()
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
    vList = InqQueueList(ksdm=ksdm,ghrq = currentDate,time_flag=sync_time)
    DBTIME = sync_time
    for item in vList:
        if "REGISTTIME" not in item:
            continue
        registTime = item["REGISTTIME"].get("_text","")

        print  "current year : " ,int(getCurrentYear())
        print  "birth : ", int(item["BRITHDAY"].get("_text","2018")[0:4])
        age = int(getCurrentYear()) + 1 - int(item["BRITHDAY"].get("_text","2018")[0:4])
        print  "age :",  age

        visitor = {
            "id" : item["ID"]["_text"] + ":" + registTime,
            "name": item["NAME"]["_text"],
            "age" :  age,
            "queue" : item["DEPARTMENT"]["_text"] + item["DOCTORNAME"]["_text"],
            "registDate" : registTime,
            "registTime" : registTime,
            "snumber" : item["SNUMBER"].get("_text","0"),
            "orderType" : item["ORDERTYPE"].get("_text",""),
            "workerID" : item["DOCTORID"].get("_text",""),
            "workerName" : item["DOCTORNAME"].get("_text",""),
            "department" : item["DEPARTMENT"].get("_text",""),
            "cardID" : item["CARDID"].get("_text",""),
            "personID": item["PERSONID"].get("_text",""),
            "phone" : item["PHONE"].get("_text",""),
            "urgent_lev1" : int(item["EMERGENCY"].get("_text","0"))
        }
        THF = item["THF"].get("_text","N")
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
        print "sigVisitorFinished ok :" + visitor["name"] + visitor["id"]

def ExternSourceQueueList():
    doctorList = InqDoctorList("01")
    qList = []
    for d in doctorList:
        qName = d["KSMC"].get("_text","")
        dName = d["NAME"].get("_text","") 
        qList.append(qName+dName)
        print qName+dName

    classList = InqDoctorList("02")
    cDict = {}
    for item in classList:
        cCode = item["DM"].get("_text","")
        cName = item["MC"].get("_text","")
        cDict[cCode] = cName
        print cCode,cName


    doctorList = InqDoctorList("03")
    for d in doctorList:
        qCode = d["DM"].get("_text", "")
        qName = d["PYM"].get("_text","")
        dName = d["MC"].get("_text","")
        qList.append(qCode + "|" + qName + "|" + dName)
        print qName+dName

    doctorList = InqDoctorList("04")
    for d in doctorList:
        qCode = d["DM"].get("_text", "")
        qName = d["PYM"].get("_text","")
        dName = d["MC"].get("_text","")
        classCode = d["DLDM"].get("_text", "")
        className = cDict.get(classCode,"")
        qList.append(className + "|" + qCode + "|" + dName)
        print className+qCode + classCode

    return qList

def GetQueueName(type,queueCode):
    if type == "03":
        retList = InqDoctorList(type)
        for q in retList:
            if queueCode == q["DM"].get("_text",""):
                qCode = q["DM"].get("_text","")
                qName = q["PYM"].get("_text","")
                dName = q["MC"].get("_text","")
                return qCode+"|"+qName+"|"+dName
    elif type == "02":
        classList = InqDoctorList("02")
        cDict = {}
        for item in classList:
            cCode = item["DM"].get("_text", "")
            cName = item["MC"].get("_text", "")
            cDict[cCode] = cName
            print cCode, cName

        itemList = InqDoctorList("04")
        for d in itemList:
            if queueCode == d["DM"].get("_text", ""):
                qCode = d["DM"].get("_text", "")
                qName = d["PYM"].get("_text", "")
                dName = d["MC"].get("_text", "")
                classCode = d["DLDM"].get("_text", "")
                className = cDict.get(classCode, "")
                return className + "|" + qCode + "|" + dName

    return queueCode

def getAgeValue(ageStr):
    if ageStr == "/30天": #未给年龄信息
        return 30
    elif "天" in ageStr:
        return 0
    elif "岁" in ageStr:
        ageStr = re.sub("\D", "", ageStr)
        print "Get　Age : ",ageStr
        return int(ageStr)
    else:
        return 30

def httpReqInfo(blh = "",trmtno = "",vid = "",sfzh = "",inPara1 = "",inPara2 = "",inPara3 = "",inPara4 = "",inPara5 = "",inPara6 = "") :
    retList = InqVInfo(blh,trmtno,vid,sfzh,inPara1,inPara2,inPara3,inPara4,inPara5,inPara6)
    vInfo = {}
    for v in retList:
        blh = v["BLH"].get("_text","") #病例号
        vInfo["name"] = v["XM"].get("_text","")  #姓名
        ageStr = v["AGE"].get("_text", "") #年龄
        vInfo["age"] = getAgeValue(ageStr)
        vInfo["genders"] = v["XB"].get("_text", "") #性别
        vInfo["rev1"] = v["XB"].get("_text", "") #病患联系地址
        vInfo["phone"] = v["DHHM"].get("_text", "") #病人电话
        vInfo["personID"] = v["SFZHM"].get("_text", "") #病人身份证号码
        vInfo["cardID"] = trmtno  # 卡面号码
        return blh,vInfo
    return "",{}

def httpPostRegist(blh,ywlx,dldm,fydl,sourceInfo,inPara1 = "",inPara2 = "",inPara3 = "",inPara4 = "",inPara5 = "",inPara6 = ""):
    """
    报到机发送登记请求
    :param blh:   病例号
    :param ywlx:   业务类型
    :param dldm:   队列代码
    :return:
    """
    retList = PostRegist(blh,ywlx,dldm,fydl,inPara1,inPara2,inPara3,inPara4,inPara5,inPara6)
    sourceItem = {}
    retInfo = {}
    registTime = getCurrentTime()
    num = 0
    for item in retList:
        if ywlx == TYPE_FAYAO:
            sourceItem["id"] = blh + registTime
        elif ywlx == TYPE_YIJI:
            queueCode = item["XMDM"].get("_text", "") #队列代码，实际签到的队列
            sourceItem["queue"] = GetQueueName("02",queueCode)
            sourceItem["examMethod"] = item["XMMC"].get("_text", "")  #医技项目名称
            sourceItem["id"] = queueCode + item["LSH"].get("_text", "")  # 医技流水号
        elif ywlx == TYPE_ZHUYUAN :
            sourceItem["id"] = item["VID"].get("_text", "") + registTime # 住院号
            sourceItem["name"] = item["XM"].get("_text", "")  #患者姓名
            queueCode = item["DLDM"].get("_text", "")  #队列代码
            sourceItem["queue"] = GetQueueName("03", queueCode)
        sourceInfo.update(sourceItem)
        VisitorManager().visitor_quick_add(sourceInfo)
        retInfo = DBLocal.where("visitor_view_data",id = sourceItem["id"]).first()
        num += 1
    return retInfo


class YXSourceController:
    support_action = {
        "reqInfo": "reqInfo",
        "regist" : "regist"
    }

    def POST(self):
        data = json.loads(web.data())
        return checkPostAction(self, data, self.support_action)

    def reqInfo(self,data):
        blh = data.get("blh","")
        trmtno = data.get("trmtno","")
        vid = data.get("vid","")
        sfzh = data.get("sfzh","")
        regist = data.get("regist",0)
        ywlx = data.get("ywlx","")
        dldm = data.get("dldm","")
        fydl = data.get("fydl","")
        snumber = data.get("snumber", "")
        queue = data.get("queue", "")
        blh,vInfo = httpReqInfo(blh,trmtno,vid,sfzh)
        if snumber != "":
            vInfo["snumber"] = snumber
        if queue != "" :
            vInfo["queue"] = queue
        if regist:
            vInfo = httpPostRegist(blh,ywlx,dldm,fydl,vInfo)
        return vInfo
    def regist(self,data):
        blh = data.get("blh","")
        ywlx = data.get("ywlx","")
        dldm = data.get("dldm","")
        fydl = data.get("fydl","")
        httpPostRegist(blh, ywlx, dldm,fydl)
        return {"result" : "success"}

#print "-----InqOnDuty : ------"
#InqOnDuty("2017.06.01","2017.06.19")

#print "-----InqDoctorList : ------"
#InqDoctorList("01")
#ExternSourceQueueList()

#print "------queueList : test------"
#InqQueueList(ksdm="",ghrq = "2017.10.19",time_flag="2017/10/19 02:00:00")

#print "------SyncSource : run() ------"
#SyncSource().run()

