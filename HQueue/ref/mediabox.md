#语音盒


## 语音盒心跳请求
接口地址: http://192.168.17.187/hqueue/mediaBox/heartBeat

方法: POST

参数:
```
{
    {
        "stationId":"12345",								
        "serverAddress":"http://192.168.17.39:19000",		//终端服务地址
        "isHttpServerAlive":true,							//终端服务是否开启
        "isSpeechManagerInit":true,							//终端语音是否初始化
        "speakerParams":{									//语音参数
            "speed":"50",
            "pitch":"50",
            "volume":"100"
        },
        "speakingMsg":{"id":"1002","text":"请张三到101诊室就诊"}, 	//正在播放的语音
        "speechList":[												//未播放的语音列表
            {"id":"1002","text":"请李四到102诊室就诊"},
            {"id":"1002","text":"请王五到103诊室就诊"}
        ],
        "failedSpeechMsgList":[										//播放失败的列表
                {
                    "msg":{
                        "id":"1002",
                        "text":"请李四到102诊室就诊"
                    },
                    "time":1496720910969,
                    "errorCode":100010,
                    "errorMsg":"错误原因。。。"
                }
        ]

    }
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

语音参数范围:
```
volume:语音音量(0-100) 默认值为100
pitch:音调(0-100)  默认值为50
speed:语速(0-100) 默认值为50
```

## 获取系统中语音盒列表
接口地址： http://192.168.17.187/hqueue/manager/mediabox

方法： POST

参数：
```
{
    "token": " safe action",
    "action" : "getListAll",
}
```
返回内容：
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

## 获取语音盒信息
接口地址： http://192.168.17.187/hqueue/manager/mediabox

方法： POST

参数：
```
{
    "token": " safe action",
    "action" : "getInfo",
    "id":12
}
```
返回内容：
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "id": 12,
    "ip": "192.168.17.184",
    "stationID": 2,
    "stationName": "儿科",
    "status": "online",
    "speed": 50,
    "volume": 50
    "pitch" : 50
  }
}
```

## 修改语音盒信息
接口地址： http://192.168.17.187/hqueue/manager/mediabox

方法：POST

参数：
```
{
    "token": " safe action",
    "action" : "edit",
    "id": 12,
    "speed": 50,
    "volume": 50
    "pitch" : 50
}
```
返回内容：
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
  	"result":"success"
  }
}
```

## 删除离线语音盒

只能删除离线状态的语音盒

接口地址：http://192.168.17.187/hqueue/manager/mediabox

方法： POST

参数：
```
{
    "token": " safe action",
    "action" : "delete",
    "id":2
}
```
返回内容：
```
{
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "result": "success"
  }
}
```