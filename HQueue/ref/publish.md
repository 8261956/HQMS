#发布器接口

##说明
前端在网页Url中得到分诊台ID和叫号器ID

示例:  
http://172.16.3.131/HQMS/index_caller_720.html?station=60&caller=8
http://172.16.3.131/HQMS/index_station_720.html?station=60

## 叫号器获取内容发布
接口地址: http://192.168.17.187/hqueue/main/publish

方法: POST

参数:
```
{
	"action":"getCallerList",
	"stationID" : 2,
	"callerID" : [8]
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
        "workerInfo": {
          "department": "内科",
          "headpic": "www.baidu.com",
          "title": "主任",
          "name": "张医生2",
          "descText": "",
          "id": "1",
          "status": "",
          "speciality": "各种疑难杂症"
        },
        "queueInfo": {
          "department": "内科",
          "pos": "诊室二",
          "listNum": 8
        },
        "listInfo": {
          "seeing": {
            "show": 0,
            "name": "刘武3",
            "id": null,
            "status": "locked",
            "outputText": "检查"
          },
          "waiting": [
            {
              "name": "李四",
              "id": "V0020",
              "status": "VIP"
            },
            {
              "name": "张武1",
              "id": "V0022",
              "status": "order"
            },
            {
              "name": "张武4",
              "id": "V0025",
              "status": "normal"
            }
          ]
        }
      }
    ]
  }
}
```

**医生信息中的status说明**:
```
status为""，表示医生在线
status为"暂停"，表示医生暂停工作
```

**等待队列中status说明**：
```
locked: 锁定
VIP: 优先
order: 预约
normal: 普通
emergency: 急诊
review: 复诊
pass: 过号
delay: 延后

```

## 工作站获取内容发布
接口地址: http://192.168.17.187/hqueue/main/publish

方法: POST

参数:
```
{
	"action":"getStationList",
	"stationID" : 2
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
        "workerInfo": {
          "department": "内科",
          "headpic": "www.baidu.com",
          "title": "主任",
          "name": "张医生2",
          "descText": "",
          "id": "1",
          "status": "暂停",
          "speciality": "各种疑难杂症"
        },
        "queueInfo": {
          "department": "内科",
          "pos": "诊室二",
          "listNum": 8
        },
        "listInfo": {
          "seeing": {
            "show": 0,
            "name": "刘武3",
            "id": null,
            "status": "locked"，
            "outputText": "检查"
          },
          "waiting": [
            {
              "name": "李四",
              "id": "V0020",
              "status": "VIP"
            },
            {
              "name": "张武1",
              "id": "V0022",
              "status": "order"
            },
            {
              "name": "张武4",
              "id": "V0025",
              "status": "normal"
            }
          ]
        }
      }
    ]
  }
}
```

## 药房获取内容发布
接口地址: http://192.168.17.187/hqueue/main/publish

方法: POST

参数:
```
{
	"action":"getWinList",
	"stationID" : 2,
	"callerID" : [8]
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
        "seeingList": [
          {
            "name": "张武2",
            "id": "V0023"
          }
        ],
        "watingList": [
          {
            "name": "张武5",
            "id": "V0026"
          },
          {
            "name": "张武6",
            "id": "V0027"
          }
        ],
        "calling": {
          "name": "王武14",
          "id": "W0035",
          "pos": "诊室一"
        }
      }
    ]
  }
}

```