#医生叫号工作页面

##获得医生登录叫号器信息
接口地址: http://192.168.17.187/hqueue/main/worker

方法: POST

参数:
```json
{
  "token": "safe action",
  "action":"getCallerInfo",
  "stationID":2,
  "id": "D0001"
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
      "D003"
    ],
    "type": "soft",
    "id": 10
  }
}
```

##获得医生队列列表
接口地址: http://192.168.17.187/hqueue/main/worker

方法: POST

参数:
```json
{
  "token": " safe action",
  "action" : "getQueueList",
  "stationID" : 2,
  "id": "D0001"
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
        "workerOnline": "",
        "id": 4,
        "tab": [
          "waiting",
          "finish"
        ],
        "name": "队列2",
        "state": "queue and worker"
      },
      {
        "workerOnline": null,
        "id": 25,
        "tab": [
          "waiting",
          "finish"
        ],
        "name": "队列4",
        "state": "queue not worker"
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
接口地址: http://192.168.17.187/hqueue/main/worker

方法: POST

参数:
```json
{
  "token": " safe action",
  "action" : "getQueueListAll",
  "stationID" : 2,
  "queueID" : 1,
  "id" : "D001"
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
    "waitingList": [],
    "finishList": []
  }
}
```

##获取可转移列表
接口地址: http://192.168.17.187/hqueue/main/worker

方法: POST

参数:
```json
{
  "token": " safe action",
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
接口地址: http://192.168.17.187/hqueue/main/worker

方法: POST

参数:
```json
{
  "token": " safe action",
  "action" : "visitorAppendQueue",
  "stationID" : 2,
  "queueID" : 1,
  "id" : "V0022",
  "dest" : {
  	"queueID" : 2,
    "status" : "waiting"
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

##访客顺序 前进或后退
接口地址: http://192.168.17.187/hqueue/main/worker

方法: POST

参数:
```json
{
  "token": " safe action",
  "action" : "visitorMoveby",
  "stationID" : 2,
  "queueID" : 2,
  "id" : "V0022",
  "value" : -1
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
接口地址: http://192.168.17.187/hqueue/main/worker

方法: POST

参数:
```json
{
  "token": " safe action",
  "action" : "callNext",
  "stationID" : 2,
  "queueID" :2,
  "id" : 1
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

## 设置访客延后

接口地址: http://192.168.17.187/hqueue/main/worker

方法: POST

参数:
```json
{
  "token": " safe action",
  "action": "setDelay",
  "stationID": 71,
  "queueID": 75,
  "id": "D001"
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

## 设置访客过号

接口地址: http://192.168.17.187/hqueue/main/worker

方法: POST

参数:
```json
{
  "token": " safe action",
  "action": "callPass",
  "stationID": 71,
  "queueID": 75,
  "id": "D001"
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

##呼叫指定
接口地址: http://192.168.17.187/hqueue/main/worker

方法: POST

参数:
```json
{
  "token": " safe action",
  "action" : "callVisitor",
  "stationID" : 2,
  "queueID" :2,
  "visitorID" : "V0021",
  "id" : "D002"
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

##修改访客状态为完成
接口地址: http://192.168.17.187/hqueue/main/worker

方法: POST

参数:
```json
{
  "token": " safe action",
  "action" : "visitorFinishSet",
  "stationID" : 2,
  "queueID" : 2,
  "visitorID" : "V0022",
  "id" : "D002",
  "finish" : 1
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

##设置医生状态
接口地址: http://192.168.17.187/hqueue/main/worker

方法: POST

参数:
```json
{
  "token": " safe action",
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