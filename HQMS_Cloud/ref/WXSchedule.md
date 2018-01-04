# 微信排班查询接口


## 根据专家ID查询排班信息

接口地址：http://192.168.17.187/hqueue_wx/manager/schedule

请求方法：POST

参数：

```json
{
  "token": "safe token",
  "action": "getScheduleByName",
  "workerID": "D001",
  "hospitalName": "义乌中医医院"
}
```

返回内容：

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": {
        "list": [
            {
                "queueID": 75,
                "name": "测试队列TM_CH",
                "schedule": [
                    {
                        "onDuty": 1,
                        "workDate": "2017-09-12",
                        "workTime": 1,
                        "weekday": 2
                    },
                    {
                        "onDuty": 1,
                        "workDate": "2017-09-12",
                        "workTime": 2,
                        "weekday": 2
                    },
                    {
                        "onDuty": 1,
                        "workDate": "2017-09-14",
                        "workTime": 1,
                        "weekday": 4
                    },
                    {
                        "onDuty": 1,
                        "workDate": "2017-09-14",
                        "workTime": 2,
                        "weekday": 4
                    }
                ],
                "workerInfo": {
                    "name": "王医生",
                    "title": "主任",
                    "headPic": "http://192.168.17.187/upload_resource/c81e728d9d4c2f636f067f89cc14862c.jpg",
                    "descText": "擅长耳鼻眼候",
                    "department": "五官科",
                    "speciality": "各种疑难杂症"
                },
                "stationID": 71,
                "filter": "TM_CH",
                "isExpert": 1
            }
        ]
    }
}
```


## 根据科室名称查询排班信息

接口地址：http://192.168.17.187/hqueue_wx/manager/schedule

请求方法：POST

参数：

```json
{
  "token": "safe token",
  "action": "getScheduleByDepartment",
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
        "list": [
            {
                "queueID": 75,
                "name": "测试队列TM_CH",
                "schedule": [
                    {
                        "onDuty": 1,
                        "workDate": "2017-09-12",
                        "workTime": 1,
                        "weekday": 2
                    },
                    {
                        "onDuty": 1,
                        "workDate": "2017-09-12",
                        "workTime": 2,
                        "weekday": 2
                    },
                    {
                        "onDuty": 1,
                        "workDate": "2017-09-14",
                        "workTime": 1,
                        "weekday": 4
                    },
                    {
                        "onDuty": 1,
                        "workDate": "2017-09-14",
                        "workTime": 2,
                        "weekday": 4
                    }
                ],
                "workerInfo": {
                    "name": "王医生",
                    "title": "主任",
                    "headPic": "http://192.168.17.187/upload_resource/c81e728d9d4c2f636f067f89cc14862c.jpg",
                    "descText": "擅长耳鼻眼候",
                    "department": "五官科",
                    "speciality": "各种疑难杂症"
                },
                "stationID": 71,
                "filter": "TM_CH",
                "isExpert": 1
            }
        ]
    }
}
```