#医生叫号工作页面

测试时每个接口可以不带token 后续使用时需带token

[TOC]

##获得医生登录叫号器信息
接口地址: http://192.168.17.187:8080/hqueue/main/worker

方法: POST

参数:
```json
{
  "token": "safe action",
  "action":"getCallerInfo",
  "stationID":2,
  "id": "D002"
}
```
返回内容:
```json
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "name": "诊室五",
    "ip": "127.0.0.1",
    "priorQueue": "14",
    "pos": "诊室五",
    "stationID": 2,
    "workerLimit": [
      "D002",
      "D003",
      "1"
    ],
    "workerOnline": "D001",
    "type": "soft",
    "id": 10
  }
}
```

##获得医生队列列表
接口地址: http://192.168.17.187:8080/hqueue/main/worker

方法: POST

参数:
```json
{
  "action" : "getQueueList",
  "stationID" : 2,
  "id": "D002"
}
```
返回内容:
```json
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "num": 1,
    "list": [
      {
        "state": "queue not worker",
        "workerOnline": "D002",
        "id": 2,
        "name": "普通门诊"
      }
    ]
  }
}
```
```
参数说明：
  state:
    - "queue and worker": 队列上班，登录的医生也上班
    - "queue not worker": 队列上班，但是登录的医生不上班
    - "not queue": 队列不上班
```

##获取医生队列信息
接口地址: http://192.168.17.187:8080/hqueue/main/worker

方法: POST

参数:
```json
{
  "action" : "getQueueListAll",
  "stationID" : 2,
  "queueID" : 2,
  "id" : "D002"
}
```
返回内容:
```json
{
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "workerOnline": "",
    "name": "队列2",
    "unactiveList" :[],
    "waitingList": [],
    "passedList" : [],
    "finishList": []
  }
}
```

##获取可转移列表
接口地址:  http://192.168.17.187:8080/hqueue/main/worker

方法: POST

参数:
```json
{
  "action" : "getMovetoList",
  "stationID" : 2,
  "id" : "D003"
}
```
返回内容:
```json
{
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "num": 2,
    "list": [
      {
        "id": 1,
        "name": "队列1"
      },
      {
        "id": 2,
        "name": "队列2"
      }
    ]
}
}
```

##移动访客到指定队列
接口地址: http://192.168.17.187:8080/hqueue/main/worker

方法: POST

参数:
```json
{
  "token": " safe action",
  "action" : "visitorMoveto",
  "stationID" : 2,
  "queueID" : 2,
  "vid" : ["221521689552865538"],
  "dest" : {
        "stationID" : 2,
        "queueID" : 46,
        "status" : "waiting",
        "property" : "locked",
        "value" : "1",
        "tag" : "转移患者"
  }
}
```
返回内容:
```json
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "result": "success"
  }
}
```


##呼叫下一位
接口地址:  http://192.168.17.187:8080/hqueue/main/worker

方法: POST

参数:
```json
{
  "action" : "callNext",
  "stationID" : 2,
  "queueID" :2,
  "id" : "D002"  #医生ID
}
```
返回内容:
```json
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "result": "success",
    "list":[
        {
            "soundUrl:" : "http://192.168.17.222:19000/",
            "text": "请 xxx 到 xxx 就诊"
        }
    ]
  }
}
```

##呼叫指定
接口地址:  http://192.168.17.187:8080/hqueue/main/worker

方法: POST

参数:
```json
{
  "action" : "callVisitor",
  "stationID" : 2,
  "queueID" :2,
  "visitorID" : "221521689553942774",
  "id" : "D002"
}
```
返回内容:
```json
{
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "result": "success",
    "list":[
        {
            "soundUrl:" : "http://192.168.17.222:19000/",
            "text": "请 xxx 到 xxx 就诊"
        }
    ]
  }
}
```

##修改访客状态 为 过号/延后/完成
接口地址:  http://192.168.17.187:8080/hqueue/main/worker

方法: POST

参数:
```json
{
  "action" : "visitorPropertySet",
  "stationID" : 2,
  "queueID" : 2,
  "vid" : ["221521689553942774","221521696336602601"],
  "property" : "finish",
  "value" : "1"
}
```
参数说明:
可设置的 poperty 为 passed,delay,finish
设置的value 统一使用字符串形式

返回内容:
```json
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "result": "success"
  }
}
```

##设置医生状态
接口地址:  http://192.168.17.187:8080/hqueue/main/worker

方法: POST

参数:
```json
{
  "action" : "setWorkerStatus",
  "stationID" : 2,
  "id" : "D002",
  "status" : "暂停"
}
```
返回内容:
```json
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "result": "success"
  }
}
```