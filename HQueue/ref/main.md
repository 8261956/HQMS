#工作站工作主页的接口

测试时每个接口可以不带token 后续使用时需带token

[TOC]

##获取工作站的队列列表

接口地址

http://192.168.17.187:8080/hqueue/main/station

方法: POST

参数:
```

{
  "action" : "getQueueListInfo",
  "stationID": 2
}
```
返回内容: 
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "num": 2,
    "list": [
      {
        "workerOnline": [D001],
        "id": 1,
        "name": "队列1"
      },
      {
        "workerOnline": [D002],
        "id": 2,
        "name": "队列2"
      }
    ]
  }
}
```

##获取队列信息

接口地址: http://192.168.17.187:8080/hqueue/main/station

方法: POST

参数:
```
{
  "action" : "getQueueListAll",
  "stationID": 2,
  "queueID":2
}
```
返回内容:
```
{
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "workerOnline": [],
    "name": "队列2",
    "waitingList": [
      {
      	"snumber": 1,
        "name": "张三",
        "genders" : "男",
        "age": 14,
        "type" : "门诊",
        "cardID" : "1231234",
        "orderType": "预约",
        "urgent_lev1" : 1,
        "urgent_lev2" : 2,
        "redo": "复诊",
        "status": "候诊",
        "other": "",
        "registTime": "2018-0327 23:10:55",
        "waitNum" : 0,
        "waitTime" : 15,
        
        "stationID": 2,
        "queueID": 2,
        "orderTime": "2018-0327 23:10:55",
        "activeLocalTime": "2018-0327 23:10:55",
        "descText": "肠胃不适",
        "queue": "PM_US",
        "workerName": "李医生",
        "department": "内科",
        "id": "V0011",
        "examPart" : "肝脏",
        "examMethod" : "DR",
        "tag" : "属性标签"
		"rev1" : "",
        "rev2" : "",
        "rev3" : "",
        "rev4" : "",
        "rev5" : "",
        "rev6" : "",
      }
    ],
    "finishList": [],
    "passList": [],
    "unactiveList" : [],
  }
}
```

##获取访客信息

接口地址: http://192.168.17.187:8080/hqueue/main/station

方法: POST

参数:
```
{
  "action" : "getVisitorInfo",
  "stationID" : 2,
  "id" : "V001"
}
```
返回内容:
```
{
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
      	"snumber": 1,
        "name": "张三",
        "genders" : "男",
        "age": 14,
        "type" : "门诊",
        "cardID" : "1231234",
        "orderType": "预约",
        "urgent_lev1" : 1,
        "urgent_lev2" : 2,
        "redo": "复诊",
        "status": "候诊",
        "other": "",
        "registTime": "2018-0327 23:10:55",
        "waitNum" : 0,
        "waitTime" : 15,
        
        "stationID": 2,
        "queueID": 2,
        "orderTime": "2018-0327 23:10:55",
        "activeLocalTime": "2018-0327 23:10:55",
        "descText": "肠胃不适",
        "queue": "PM_US",
        "workerName": "李医生",
        "department": "内科",
        "id": "V0011",
        "examPart" : "肝脏",
        "examMethod" : "DR"
		"rev1" : "",
        "rev2" : "",
        "rev3" : "",
        "rev4" : "",
        "rev5" : "",
        "rev6" : "",
  }
}
```
##呼叫指定的患者候者

接口地址: http://192.168.17.187:8080/hqueue/main/station

方法: POST

参数:
```
{
  "action" : "callPrepare",
  "stationID" : 2,
  "queueID" : 1,
  "vid" : ["221521689420224751","221521689552865538"],
  "dest" : "护士站"
}
```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "result": "success"
  }
}
```
说明 : 护士站向服务器发送呼叫候诊请求成功后， 进入发音流程，此处的发声文本内容由护士站软件自行生成 ，例如 请张三到护士站候诊，语音发送到语音盒设备或自行转换在线mp3文件进行播放。

##设置访客过号\锁定\完成\急诊等级\激活\属性标签
接口地址: http://192.168.17.187:8080/hqueue/main/station

方法: POST

参数:
```
{
  "action" : "visitorPropertySet",
  "stationID" : 2,
  "queueID" : 2,
  "vid" : ["221521689420224751","221521689552865538"],
  "property" :  "pass",  	##"locked","finish","urgentLev","active",
  "value" : "1"     		 #"PAINIAO","1","2","1"
}

```
参数说明 : property 包括 :
"pass"  value: 0,1
"locked"  value: "PAINIAO", ("NORMAL","BIENIAO")
"finish":  value: 0,1
"urgentLev" value:  0,1,2,3
"active" : value: 0,1
等

返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "result": "success"
  }
}
```

##移动访客到指定位置

接口地址: http://192.168.17.187:8080/hqueue/main/station

方法: POST

参数:
```
{
  "action" : "visitorMoveto",
  "stationID" : 2,
  "queueID" : 2,
  "vid" : ["221521689420224751"],
  "dest" : {
        "stationID" : 2,
        "queueID" : 46,
        "status" : "waiting",
        "property" : "locked",
        "value" : "1",
        "tag" : "转移患者"
  ｝
}
```
status是目标队列状态，有unactive,waiting,finsh,passed四种。
property是转移后属性设定，value是属性的值

返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "result": "success"
  }
}
```

##访客顺序——前进或后退
接口地址: http://192.168.17.187:8080/hqueue/main/station

方法: POST

参数:
```
{
  "action" : "visitorMoveby",
  "stationID" : 2,
  "queueID" : 46,
  "vid" : ["221521689420224751"],
  "value" : -1
}
```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "result": "success"
  }
}
```

## 添加访客
接口地址: http://192.168.17.187:8080/hqueue/main/station

方法：POST

参数：
```
{
  "action": "addVisitor",
  "stationID": 2,
  
  "snumber": 1,
  "name": "fan",
  "queueID": 2,
  
  "age": 50,
  "cardID": "222222",
  "personID": "111111",
  "phone": "12345678",
  "property" : {
  		"redo": "复诊",
        "locked": 1
  }
}
```
参数说明：
```
选填：
  - age,cardID,personID,phone,property
```
返回参数：
```
{
  "errInfo": "none",
  "rescode": "200",
  "detail": {
    "result": "success"
  }
}
```


##前端查询语音播放地址
接口地址: http://192.168.17.187:8080/hqueue/main/station

方法: POST

参数:
```
{
  "action" : "getMediaBox",
  "stationID" : 2,
}
```
返回内容:
```
{
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "list": [
      {
        "url": "http://192.168.17.36:19001/play",
        "id": 61
      }
    ],
    "result": "success"
  }
}
```

##前端顺序播放指定文字
接口地址: http://192.168.17.187:8080/hqueue/main/station

方法: POST

参数:
```
[
    {"id":"1002","text":"请张三到101诊室就诊"},
    {"id":"1002","text":"请李四到102诊室就诊"},
]
```
返回内容:
```
{
    "speakingMsg":{"id":"1002","text":"请张三到101诊室就诊"}, 	//正在播放的语音
    "speechList":[												//未播放的语音列表
        {"id":"1002","text":"请李四到102诊室就诊"},
        {"id":"1002","text":"请王五到103诊室就诊"}
    ]
}
```
