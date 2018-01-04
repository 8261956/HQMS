# 微信队列查询接口


## 根据科室查询队列概览

接口地址：http://192.168.17.187/hqueue_wx/manager/queue

请求方法：POST

参数：

```json
{
  "token": "safe token",
  "action": "getWXQueueInfo",
  "department": "内科",
  "hospitalName": "义乌中医医院"
}
```

返回内容：

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": {
        "num": 17,
        "list": [
            {
                "isExpert": 1,
                "stationID": 73,
                "waitNum": 0,
                "name": "测试队列-张华清",
                "finishNum": 0,
                "department": "内科",
                "id": 73,
                "currentVisitor": null
            },
            {
                "isExpert": 1,
                "stationID": 71,
                "waitNum": 0,
                "name": "测试队列TM_CH",
                "finishNum": 0,
                "department": "内科",
                "id": 75,
                "currentVisitor": null
            }
        ]
    }
}
```