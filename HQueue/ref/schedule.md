# 排班管理接口

## 获取某个队列的排班信息

请求地址：http://192.168.17.187/hqueue/manager/schedule

方法：POST
 
参数：

```json
{
  "token": "safe token",
  "action": "getQueueSchedule",
  "stationID": 2,
  "queueID": 1,
  "startTime": "2017-08-07",
  "endTime": "2017-08-13"
}
```

返回值：

```json
{
  "errorInfo": "none",
  "rescode": "200",
  "detail": {
    "stationID": 2,
    "queueID": 1,
    "name": "测试队列",
    "filter": "AM_US",
    "isExpert": 1,
    "schedule": [
      {
        "workDate": "2017-08-07",
        "onDuty": 0,
        "weekday": 1,
        "workerID": [
            "D001",
            "D002"
        ],
        "workTime": 1
      },
      {
        "workDate": "2017-08-07",
        "onDuty": 0,
        "weekday": 1,
        "workerID": [
            "D001",
            "D002"
        ],
        "workTime": 2
      }
    ]
  }
}
```

参数说明：
```
onDuty状态
    - 0: 不上班
    - 1: 上班
    - 2: 请假
    - 3: 加班
    
date: 日期

time: 
    - 1: 上午
    - 2: 下午

weekday: 星期几
```

## 获取分诊台下所有队列的排班信息

请求地址：http://192.168.17.187/hqueue/manager/schedule

方法：POST

参数：

```json
{
  "token": "safe token",
  "action": "getStationSchedule",
  "stationID": 2,
  "startTime": "2017-08-07",
  "endTime": "2017-08-13",
  "pageNum": 1,
  "pageSize": 5
}
```

返回值：

```json
{
  "errorInfo": "none",
  "rescode": "200",
  "detail": {
    "count": 9,
    "list": [
      {
        "stationID": 2,
        "queueID": 1,
        "name": "测试队列",
        "filter": "AM_US",
        "isExpert": 1,
        "schedule": [
          {
            "workDate": "2017-08-07",
            "onDuty": 0,
            "weekday": 1,
            "workerID": [
                "D001",
                "D002"
            ],
            "workTime": 1
          },
          {
            "workDate": "2017-08-07",
            "onDuty": 0,
            "weekday": 1,
            "workerID": [
                "D001",
                "D002"
            ],
            "workTime": 2
          }
        ]
      },
      {
        "stationID": 2,
        "queueID": 2,
        "name": "测试队列二",
        "filter": "TM_CH",
        "isExpert": 0,
        "schedule": [
          {
            "workDate": "2017-08-07",
            "onDuty": 0,
            "weekday": 1,
            "workerID": [
                "D001",
                "D002"
            ],
            "workTime": 1
          },
          {
            "workDate": "2017-08-07",
            "onDuty": 0,
            "weekday": 1,
            "workerID": [
                "D001",
                "D002"
            ],
            "workTime": 2
          }
        ]
      }
    ]
  }
}
```

参数说明：

```
数据分页：
    - pageNum: 页数，从第 1 页开始
    - pageSize: 每页的数据量
    - 传入的参数中存在以上两个参数，则返回分页数据；否则返回所有数据
    
分诊台：
    - 传入的参数中有stationID，返回对应的分诊台下的数据
    - 传入的参数中stationID=""，返回所有分诊台下的数据
```

## 模糊搜索队列的排班信息

请求地址：http://192.168.17.187/hqueue/manager/schedule

方法：POST
 
参数：

```json
{
  "token": "safe token",
  "action": "fuzzySearchSchedule",
  "keyword": "测试队列",
  "startTime": "2017-08-07",
  "endTime": "2017-08-13"
}
```

返回值：

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": [
        {
            "isExpert": 1,
            "queueID": 75,
            "name": "测试队列二", 
            "filter": "TM_CH",
            "schedule": [
                {

                    "workDate": "2017-08-07",
                    "onDuty": 0,
                    "weekday": 1,
                    "workerID": [
                        "D001",
                        "D002"
                    ],
                    "workTime": 1
                }
            ]
        }
    ]
}
```

## 添加某个队列的排班信息

请求地址：http://192.168.17.187/hqueue/manager/schedule

方法：POST

参数：

```json
{
  "token": "safe token",
  "action": "addSchedule",
  "scheduleList": [
    {
      "stationID": 2,
      "queueID": 1,
      "isExpert": 1,
      "schedule": [
        {
            "workDate": "2017-08-14",
            "onDuty": 1,
            "weekday": 1,
            "workerID": [
                "D001",
                "D002"
            ],
            "workTime": 1,
            "isTemporary": 1
        },
        {
            "workDate": "2017-08-14",
            "onDuty": 1,
            "weekday": 1,
            "workerID": [
                "D001",
                "D002"
            ],
            "workTime": 2,
            "isTemporary": 1
        }
      ]
    }
  ]
}
```

返回值：

```json
{
  "errorInfo": "none",
  "rescode": "200",
  "detail": {
    "result": "success/failed"
  }
}
```

## 编辑某个队列的排班信息

请求地址：http://192.168.17.187/hqueue/manager/schedule

方法：POST

参数：

```json
{
  "token": "safe token",
  "action": "editSchedule",
  "scheduleList": [
    {
      "stationID": 2,
      "queueID": 1,
      "isExpert": 1,
      "schedule": [
        {
            "workDate": "2017-08-14",
            "onDuty": 1,
            "weekday": 1,
            "workerID": [
                "D001",
                "D002"
            ],
            "workTime": 1,
            "isTemporary": 1
        },
        {
            "workDate": "2017-08-14",
            "onDuty": 1,
            "weekday": 1,
            "workerID": [
                "D001",
                "D002"
            ],
            "workTime": 2,
            "isTemporary": 1
        }
      ]
    }
  ]
}
```

返回值：

```json
{
  "errorInfo": "none",
  "rescode": "200",
  "detail": {
    "result": "success/failed"
  }
}
```

## 删除某一个队列的排班信息

请求地址：http://192.168.17.187/hqueue/manager/schedule

方法：POST

参数：

```json
{
  "token": "safe token",
  "action": "deleteSchedule",
  "stationID": 2,
  "queueID": 1,
  "workDate": "2017-08-07",
  "weekday": 1,
  "isTemporary": 0
}
```

返回值：

```json
{
  "errorInfo": "none",
  "rescode": "200",
  "detail": {
    "result": "success/failed"
  }
}
```

## 获取导入排班的配置信息

接口地址: http://192.168.17.187/hqueue/manager/schedule/

方法: POST

参数:

```json
{
  "token": " safe action",
  "action" : "getConfig"
}
```

返回内容：

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": {
        "passwd": "123456",
        "workerID": "workerID",
        "tableName": "schedule_import",
        "host": "127.0.0.1",
        "user": "root",
        "workDate": "workDate",
        "onDuty": "onDuty",
        "port": 3306,
        "isExpert": "isExpert",
        "charset": "utf8",
        "queue": "queue",
        "DBType": "mysql",
        "weekday": "weekday",
        "workTime": "workTime",
        "DBName": "HisQueue",
        "importWeeks": 1
    }
}
```

## 测试排班信息数据源

接口地址: http://192.168.17.187/hqueue/manager/schedule

方法: POST

参数:

```json
{
  "token": " safe action",
  "action" : "testSource",
  "DBType" : "mysql",
  "host": "192.168.17.184",
  "port": "3306",
  "charset" : "utf8",
  "user" : "root",
  "passwd" : "123456",
  "DBName" : "HisQueue",
  "tableName" : "schdule_import"
}
```
返回内容:

```json
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
    "result": "success/failed"
   }
}
```

##测试排班信息数据源配置

接口地址: http://192.168.17.187/hqueue/manager/schedule

方法: POST

参数:

```json
{
  "token": " safe action",
  "action" : "testSourceConfig",
  "DBType" : "mysql",
  "host": "192.168.17.184",
  "port": "3306",
  "charset" : "utf8",
  "user" : "root",
  "passwd" : "123456",
  "DBName" : "HisQueue",
  "tableName" : "workers_import",
  "queue": "queue",
  "isExpert": "isExpert",
  "workDate": "workDate",
  "weekday": "weekday",
  "workTime": "workTime",
  "onDuty": "onDuty",
  "workerID": "workerID"
}
```
返回内容:

```json
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
     "sql": "(SELECT isExpert AS isExpert, date AS date, workerID AS workerID, queue AS queue, time AS time, onDuty AS onDuty, weekday AS weekday FROM schedule_import) AS scheduleView",
     "result": "success/failed"
   }
}
```

## 导入排班信息

接口地址: http://192.168.17.187/hqueue/manager/schedule

方法: POST

参数:

```json
{
  "token": " safe action",
  "action" : "importSchedule",
  "DBType" : "mysql",
  "host": "127.0.0.1",
  "port": "3306",
  "charset" : "utf8",
  "user" : "root",
  "passwd" : "123456",
  "DBName" : "HisQueue",
  "tableName" : "schedule_import",
  "queue": "queue",
  "isExpert": "isExpert",
  "workDate": "workDate",
  "weekday": "weekday",
  "workTime": "workTime",
  "onDuty": "onDuty_AM",
  "workerID": "workerID",
  "importWeeks": 2
}
```

返回内容：

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": {
        "result": "success"
    }
}
```

参数说明：

```
importWeeks:
    - 导入几周的排班信息。
    - 目前支持导入1周、2周、4周的数据。如果不传入该参数，默认导入1周的数据
    - 导入前需要先确认好数据源中有几周需要导入的数据
```

## 获取专家队列的上班情况

接口地址: http://192.168.17.187/hqueue/manager/schedule

方法: POST

参数:

```json
{
  "token": "safe token",
  "action": "getExpertSchedule",
  "stationID": 71,
  "startTime": "2017-08-21",
  "endTime": "2017-08-27",
  "queueID": [80]
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
                "queueID": 76,
                "name": "测试队列PM_US",
                "schedule": [
                    {
                        "workDate": "2017-08-21",
                        "onDuty": 1,
                        "weekday": 1,
                        "workTime": 1
                    },
                    {
                        "workDate": "2017-08-21",
                        "onDuty": 1,
                        "weekday": 1,
                        "workTime": 2
                    }
                ],
                "workerInfo": {
                    "name": "王医生3",
                    "title": "主任",
                    "department": "超声科",
                    "headPic": "",
                    "descText": "擅长各种疑难杂症"
                },
                "filter": "PM_US",
                "stationID": 71,
                "isExpert": 1
            }
        ]
    }
}
```

参数说明：

```
queueID:
    - 可以传递这个参数，也可以不传递这个参数；
    - 当不传递queueID或者queueID=[],返回整个分诊台下所有专家队列上班的情况；
    - 可以传递多个queueID，例如queueID=[80, 81]，这样可以获取指定队列的上班情况
    - 如果传递的queueID不是专家队列，或者是专家队列但是指定日期范围内不上班，则不返回数据
startTime、endTime:
    - 可以传递，也可以不传递
    - 如果不指定，则默认返回当前周的数据（周一到周日）
    
stationID:
    - 可以传递，也可以不传递
    - 如果不传递，返回所有分诊台下的专家队列的上班信息
```