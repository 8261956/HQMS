#账户管理

###获取工作站账户列表
接口地址: http://192.168.17.187/manager/stationAccount

方法: POST

参数:
```
{
  "token" : "safeAction",
  "action":"getList"
}
```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "accountList": [
      {
        "stationID": 13,
        "user": "station13",
        "password": "233332",
        "type": "station",
        "id": 2,
        "descText": "d exam"
      }
    ]
  }
}
```

###获取工作站账户详情
接口地址: http://192.168.17.187/manager/stationAccount

方法: POST

参数:
```
{
  "token" : "safeAction",
  "action":"getInfo",
  "stationID" :13
}
```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "stationID": 13,
    "user": "station13",
    "password": "233332",
    "type": "station",
    "id": 2,
    "descText": "d exam"
  }
}
```

###编辑工作站账户
接口地址: http://192.168.17.187/manager/stationAccount

方法: POST

参数:
```
{
    "token": " safe action",
    "action" : "edit",
    "stationID": 13,
    "user": "station13",
    "password": "233332",
    "type": "station",
    "id": 2,
    "descText": "d exam"
}
```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {}
}```
