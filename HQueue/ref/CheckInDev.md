#报到机

### 报到机心跳请求
接口地址: http://192.168.17.187/hqueue/manager/CheckInDev

方法: POST

参数:
```
{
    "action" : "heartbeat",
    "stationID" : "2"
}
```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
	 "Date":"20170331",
     "time":"101010"
  }
}
```

### 获取系统中报到机列表
接口地址: http://192.168.17.187/hqueue/manager/CheckInDev

方法: POST

参数:
```
{
    "token": " safe action",
    "action" : "getListAll",
}
```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "num": 1,
    "list": [
      {
        "id": 12,
        "ip": "192.168.17.184",
        "status": "online",
        "stationID" : 2,
        "stationName" : "儿科"
      }
    ]
  }
}
```
