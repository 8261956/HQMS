# 取号机管理接口

## 获取某一个队列排队小票信息

接口地址：http://192.168.17.187/hqueue/manager/queueMachine

方法：POST

参数：

```json
{
  "action" : "getReceipt",
  "stationID": 71,
  "queueID": 80,
  "taskType": "RegistNew",
  "cardID": "D00001"
}
```
返回内容：

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": {
        "queueInfo": {
            "queueID": 80,
            "stationID": 71,
            "queueName": "测试队列AM_US",
            "stationName": "本地测试"
        },
        "visitorInfo": {
            "waitNum": 9,
            "snumber": 23,
            "id": "71801504259408071781",
            "cardID": "1504259408071781"
        },
        "styleInfo": {
            "subtitle": "义乌",
            "name": "样式一",
            "title": "自助取号",
            "styleURL": "/static/html/style1.html",
            "previewURL": "/static/img/style1.png",
            "footer2": "祝您早日康复",
            "id": 1,
            "footer1": "请关注您的排队号码"
        }
    }
}
```

参数说明:

```
taskType：
    - RegistNew: 无卡取号
    - RegistOrder: 预约取号
    - RegistByCard: 刷卡取号
    - 如果是刷卡取号，必须传入cardID；其他两种方式不用传入cardID，系统自动生成
```

## 取号机心跳请求

接口地址: http://192.168.17.187/hqueue/manager/queueMachine

方法: POST

参数:

```json
{
    "action" : "heartBeat",
    "stationID" : 2
}
```

返回内容:

```json
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
	 "Date":"20170331",
     "time":"101010"
  }
}
```

## 获取取号机列表

接口地址: http://192.168.17.187/hqueue/manager/queueMachine

方法: POST

参数:

```json
{
    "token": "safe token",
    "action": "getListAll"
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
                "status": "offline",
                "stationID": 71,
                "queueLimit": [
                    "80",
                    "75"
                ],
                "stationName": "本地测试",
                "ip": "127.0.0.1",
                "id": 1
            }
        ]
    }
}
```

## 获取某个取号机详情

接口地址: http://192.168.17.187/hqueue/manager/queueMachine

方法: POST

参数:

```json
{
    "token": "safe token",
    "action": "getInfo",
    "stationID": 71,
    "id": 1
}
```

返回内容:

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": {
        "status": "offline",
        "deviceIP": "127.0.0.1",
        "printSettings": {
            "styleInfo": {
                "styleURL": "/static/html/style.html",
                "previewURL": "/static/img/style1.png",
                "name": "样式一",
                "id": 1
            },
            "subtitle": "义乌市中医医院",
            "footer1": "请注意你的就诊号码",
            "footer2": "祝您早日康复",
            "title": "票号单"
        },
        "queueLimit": [
            {
                "queueID": 80,
                "name": "测试队列AM_US"
            },
            {
                "queueID": 75,
                "name": "测试队列TM_CH"
            },
            {
                "queueID": 76,
                "name": "测试队列PM_US"
            }
        ],
        "supportFeature": {
            "allowOrder": 1,
            "allowSwipe": 1,
            "showHomePage": 1,
            "allowNoCard": 1
        },
        "stationID": 71,
        "queueNum": 3,
        "id": 1
    }
}
```

参数说明：

```
- token: 在后台页面中访问时需要传入此参数，取号机上不传
- id: 在后台页面中访问时需要传入此参数，取号机访问时不传，取号机会根据IP地址进行查询
- showHomePage: 是否在取号机上显示首页
- allowNoCard: 取号机是否允许无卡取号
- allowOrder: 取号机是否允许预约取号
- allowSwipe: 取号机是否允许刷卡取号
```

## 编辑某个取号机

接口地址: http://192.168.17.187/hqueue/manager/queueMachine

方法: POST

参数:

```json
{
  "token": "safe token",
  "action": "editQueueMachine",
  "stationID": 71,
  "id": 2,
  "queueLimit": [80],
  "showHomePage": 1,
  "allowNoCard": 1,
  "allowOrder": 1,
  "allowSwipe": 1,
  "title": "票号单",
  "subtitle": "义乌中医医院",
  "footer1": "请关注您的排队号码",
  "footer2": "祝您早日康复",
  "styleID": 1
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

## 删除某个取号机

接口地址: http://192.168.17.187/hqueue/manager/queueMachine

方法: POST

参数:

```json
{
    "token": "safe token",
    "action": "delQueueMachine",
    "stationID": 71,
    "id": 2
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

## 获取样式表

接口地址: http://192.168.17.187/hqueue/manager/queueMachine

方法: POST

参数:

```json
{
    "token": "safe token",
    "action": "getStyleList"
}
```

返回内容:

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": [
        {
            "styleURL": "/static/html/style1.html",
            "previewURL": "/static/img/style1.png",
            "name": "样式一",
            "id": 1
        },
        {
            "styleURL": "/static/html/style2.html",
            "previewURL": "/static/img/style2.png",
            "name": "样式二",
            "id": 2
        }
    ]
}
```