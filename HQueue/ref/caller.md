#叫号器


###获取工作站中叫号器列表
接口地址: http://192.168.17.187/hqueue/manager/caller

方法: POST

参数:
```
{
    "token": " safe action",
    "action" : "getList",
    "stationID":2,
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
        "name": "诊室一",
        "ip": "192.168.17.184",
        "priorQueue": null,
        "pos": "诊室一",
        "stationID": 2,
        "workerLimit": ["D002", "1"],
        "type": "soft",
        "id": 1
      }
    ]
  }
}
```

###获取工作站中叫号器信息
接口地址: http://192.168.17.187/hqueue/manager/caller

方法: POST

参数:
```
{
    "token": " safe action",
    "action" : "getInfo",
    "stationID":2,
    "id":1
}
```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "name": "诊室一",
    "ip": "192.168.17.184",
    "priorQueue": null,
    "pos": "诊室一",
    "stationID": 2,
    "workerLimit": ["D002", "1"],
    "type": "soft",
    "id": 1
  }
}
```

###向工作站中添加叫号器
接口地址: http://192.168.17.187/hqueue/manager/caller

方法: POST

参数:
```
{
    "token": " safe action",
    "action" : "add",
    "stationID":2,
    "name": "诊室二",
    "ip": "192.168.17.184",
    "priorQueue": null,
    "pos": "诊室一",
    "workerLimit": ["D002", "1"],
    "type": "soft",
}
```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {}
}
```

###向工作站中修改叫号器
接口地址: http://192.168.17.187/hqueue/manager/caller

方法: POST

参数:
```
{
    "token": " safe action",
    "action" : "edit",
    "stationID":2,
    "id":2,
    "name": "诊室三",
    "ip": "192.168.17.184",
    "priorQueue": null,
    "pos": "诊室一",
    "workerLimit": ["D002", "1"],
    "type": "soft"
}
```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {}
}
```

###向工作站中删除叫号器
接口地址: http://192.168.17.187/hqueue/manager/caller

方法: POST

参数:
```
{
    "token": " safe action",
    "action" : "delete",
    "stationID":2,
    "id":2
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

## 检查一个IP是否可用

接口地址: http://192.168.17.187/hqueue/manager/caller

方法: POST

参数:

```json
{
  "token": "safe token",
  "action" : "checkIP",
  "ip" : "192.168.17.71"
}
```

返回内容:

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": {
        "conflict": 1
    }
}
```

参数说明:

```
conflict:
    - 0: 没有冲突
    - 1: 已经有相同IP
```

##呼叫下一个

##呼叫指定访客