#工作站工作主页的接口

##获取工作站的队列列表

接口地址

http://192.168.17.187/hqueue/main/station

方法: POST

参数:
```

{
  "token": " safe action",
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
        "workerOnline": "None",
        "id": 1,
        "tab": [
          "waiting",
          "finish"
        ],
        "name": "队列1"
      },
      {
        "workerOnline": "None",
        "id": 2,
        "tab": [
          "waiting",
          "finish"
        ],
        "name": "队列2"
      }
    ]
  }
}
```

##获取队列信息

接口地址: http://192.168.17.187/hqueue/main/station

方法: POST

参数:
```
{
  "token": " safe action",
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
    "workerOnline": "None",
    "name": "队列2",
    "waitingList": [
      {
        "status": "doing",
        "queueID": 2,
        "orderTime": "0:10:22",
        "activeLocalTime": "0:0:0",
        "activeLocal": 0,
        "workerID": "D001",
        "registTime": "23:10:55",
        "snumber": 1,
        "id": "V0011",
        "registDate": "2017-03-31",
        "name": "张三",
        "orderType": 1,
        "age": 14,
        "stationID": 2,
        "descText": "肠胃不适",
        "queue": "PM_US",
        "VIP": 0,
        "workerName": "李医生",
        "department": "内科",
        "orderDate": "2017-03-31",
        "originScore": 999999,
        "finalScore": 999999
      }
    ],
    "finishList": [
      {
        "status": "finish",
        "queueID": 2,
        "orderTime": "0:10:22",
        "activeLocalTime": "0:0:0",
        "activeLocal": 0,
        "workerID": "D001",
        "registTime": "9:9:2",
        "snumber": 7,
        "id": "V0025",
        "registDate": null,
        "name": "张武4",
        "orderType": 0,
        "age": 37,
        "stationID": 2,
        "descText": "胃痛",
        "queue": "PM_US",
        "VIP": 0,
        "workerName": "李医生",
        "department": "内科",
        "orderDate": null,
        "originScore": 999999,
        "finalScore": 999999
      }
    ]
  }
}
```

##获取访客信息

接口地址: http://192.168.17.187/hqueue/main/station

方法: POST

参数:
```
{
  "token": " safe action",
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
    "status": "已预约",
    "queueID": 2,
    "orderTime": "0:10:22",
    "activeLocalTime": "0:0:0",
    "activeLocal": 0,
    "workerID": "D001",
    "registTime": "23:9:0",
    "localStatus": "waiting",
    "snumber": 3,
    "id": "V0021",
    "registDate": "2017-03-31",
    "name": "张武",
    "orderType": 0,
    "age": 33,
    "stationID": 2,
    "descText": "胃痛",
    "queue": "PM_US",
    "VIP": 0,
    "workerName": "李医生",
    "department": "内科",
    "orderDate": "2017-03-31"
  }
}
```

##移动访客到指定位置

接口地址: http://192.168.17.187/hqueue/main/station

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "visitorMoveto",
  "stationID" : 2,
  "queueID" : 1,
  "id" : "V0022",
  "dest" : {
  	"queueID" : 2,
    "id" : "D0024",
    "status" : "waiting"
  }
}
```
第一个ID为访客自身ID, dest中的ID是目标位置的访客ID, 移动后将排在这个ID之前。若目标队列无访客, ID填写""。status是目标队列状态，有unactive,waiting,finsh三种。 

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
接口地址: http://192.168.17.187/hqueue/main/station

方法: POST

参数:
```
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
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "result": "success"
  }
}
```

##设置访客优先

接口地址: http://192.168.17.187/hqueue/main/station

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "visitorProirSet",
  "stationID" : 2,
  "queueID" : 2,
  "id" : "V0022",
  "prior" : 1
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

##设置访客锁定
接口地址: http://192.168.17.187/hqueue/main/station

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "visitorLockSet",
  "stationID" : 2,
  "queueID" : 2,
  "id" : "V0022",
  "locked" : 1
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

##设置访客完成
接口地址: http://192.168.17.187/hqueue/main/station

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "visitorFinishSet",
  "stationID" : 2,
  "queueID" : 2,
  "id" : "V0022",
  "finish" : 1
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

##查询访客
接口地址: http://192.168.17.187/hqueue/main/station

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "visitorSearch",
  "stationID" : 2,
  "id" : "D0022"
}
```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "status": "已预约",
    "queueID": 1,
    "orderTime": "0:10:22",
    "activeLocalTime": "0:0:0",
    "activeLocal": 0,
    "workerID": "D001",
    "registTime": "22:11:1",
    "localStatus": "waiting",
    "snumber": 4,
    "id": "D0022",
    "registDate": null,
    "name": "刘武1",
    "orderType": 1,
    "age": 34,
    "stationID": 2,
    "descText": "胃痛",
    "queue": "AM_US",
    "VIP": 0,
    "workerName": "李医生",
    "department": "内科",
    "orderDate": null,
    "waitingTime": 75,
    "waitingNum": 5
  }
}
```

##激活访客
接口地址: http://192.168.17.187/hqueue/main/station

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "visitorActiveSet",
  "stationID" : 2,
  "queueID" : 2,
  "id" : "V0022",
  "active" : 1
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
接口地址：http://192.168.17.187/hqueue/main/station

方法：POST

参数：
```
{
  "token": "safe token",
  "action": "addVisitor",
  "stationID": 2,
  "queueID": 1,
  "name": "fan",
  "age": 50,
  "snumber": 1,
  "VIP": 0,
  "orderType": 0,
  "descText": "头疼",
  "cardID": "222222",
  "personID": "111111",
  "phone": "12345678"
}
```
参数说明：
```
选填：
  - age
  - orderType: 默认为0
  - personID
  - phone
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


##前端查询是否有音频要播放
接口地址: http://192.168.17.187/hqueue/main/worker

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "AnnounceAsk",
  "stationID" : 2,
  "clear" : 0
}
```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "result" : 1,
    "url": "http://192.168.17.3:19000/media/T001.wav"
  }
}
```
