#管理工作站的接口

##获取工作站列表

接口地址：http://192.168.17.187/hqueue/manager/station

方法：POST

参数：
```
{
  "token": " safe action",
  "action" : "getList"
}
```
返回内容：
```
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": {
        "stationNum": 3,
        "stationList": [
            {
                "id": 71,
                "name": "本地测试"
            },
            {
                "id": 73,
                "name": "Oracle测试"
            },
            {
                "id": 75,
                "name": "SQL Server测试"
            }
        ]
    }
}
```

##获取工作站信息
接口地址：http://192.168.17.187/hqueue/manager/station

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "getInfo",
  "stationID" : 2
}

```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "aliasDepartment": "department",
    "workerList": null,
    "DBType": "mysql",
    "aliasWorkerName": "workerName",
    "aliasOrderType": "orderType",
    "aliasQueue": "queue",
    "tableName": "visitors",
    "aliasRegistDate": "RegistDate",
    "aliasRegistTime": "registTime",
    "aliasOrderDate": "orderDate",
    "host": "192.168.17.184",
    "aliasName": "name",
    "user": "root",
    "aliasOrderTime": "orderTime",
    "id": 2,
    "aliasDescText": "descText",
    "aliasSnumber": "snumber",
    "name": "分诊台3",
    "renewPeriod": 10,
    "aliasWorkerID": "workerID",
    "charset": "utf8",
    "descText": "Http新建分诊台",
    "aliasVIP": "emergency",
    "port": "3306",
    "passwd": "123456",
    "queueList": null,
    "DBName": "HisQueue",
    "aliasStatus": "status",
    "aliasID": "ID",
    "aliasAge": "age",
    "callerList": null
  }
}
```

##添加一个工作站
接口地址: http://192.168.17.187/hqueue/manager/station

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "add",
  "name": "D exam",
  "descText": "D exam station",
  "DBType" : "mysql",
  "host": "192.168.17.184",
  "port": "3306",
  "charset" : "utf8",
  "user" : "root",
  "passwd" : "123456",
  "DBName" : "HisQueue",
  "tableName" : "visitors",
  "aliasName": "name",
  "aliasAge": "age",
  "aliasQueue": "queue",
  "aliasID" :"ID",
  "aliasOrderDate" : "orderDate",
  "aliasOrderTime" : "orderTime",
  "aliasRegistDate" : "registDate",
  "aliasRegistTime" : "registTime",
  "aliasVIP": "emergency",
  "aliasSnumber" : "snumber",
  "aliasOrderType": "orderType",
  "aliasWorkerID" : "workerID",
  "aliasWorkerName" : "workerName",
  "aliasDepartment" : "department",
  "aliasDescText": "descText",
  "aliasStatus": "status",
  "aliasCardID": "cardID",
  "aliasPersonID:","persionID",
  "aliasPhone","phone",
  "renewPeriod" : "10s"
}
```

必填项目:
```
name
DBType
host
port
charset 若不填默认utf8
user
passwd
DBName
tableName
aliasName
aliasQueue
aliasID
aliasRegistDate
aliasRegistTime
aliasSnumber 
其他alias的项目若不填则提交
```

返回内容:
```
{ 
  "rescode": "202",
  "errInfo" : "none"
  "detail":{
    "stationID": 10
  }
}

```

## 测试工作站数据源
接口地址: http://192.168.17.187/hqueue/manager/station

方法: POST

参数:
```

{
  "token": " safe action",
  "action": "sourceTest",
  "name": "B exam",
  "describe": "B exam station",
  "DBType" : "mysql",
  "host": "192.168.17.184",
  "port": "3306",
  "charset" : "utf8",
  "user" : "root",
  "passwd" : "123456",
  "DBName" : "HisQueue",
  "table" : "visitors"
}
```

返回内容:
```
{ 
  "rescode": "202",
  "errInfo" : "none"
  "detail":{
    "testResult": "success",
  }
}

```
## 测试工作站数据源配置
接口地址: http://192.168.17.187/hqueue/manager/station

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "sourceConfigTest",
  "DBType" : "mysql",
  "host": "192.168.17.184",
  "port": "3306",
  "charset" : "utf8",
  "user" : "root",
  "passwd" : "123456",
  "DBName" : "HisQueue",
  "tableName" : "visitors",
  "aliasName": "name",
  "aliasAge": "age",
  "aliasQueue": "queue",
  "aliasID" :"ID",
  "aliasOrderDate" : "orderDate",
  "aliasOrderTime" : "orderTime",
  "aliasRegistDate" : "registDate",
  "aliasRegistTime" : "registTime",
  "aliasVIP": "emergency",
  "aliasSnumber" : "snumber",
  "aliasOrderType": "orderType",
  "aliasWorkerID" : "workerID",
  "aliasWorkerName" : "workerName",
  "aliasDepartment" : "department",
  "aliasDescText": "descText",
  "aliasStatus": "status",
  "aliasCardID": "cardID",
  "aliasPersonID:","persionID",
  "aliasPhone","phone",
}
```
返回内容:

```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "testResult": "success",
    "testSql": "(SELECT name as name , age as age , queue as queue , ID as ID , orderDate as orderDate , orderTime as orderTime , registDate as registDate , registTime as registTime , snumber as snumber , emergency as VIP , orderType as orderType , workerID as workerID , workerName as workerName , department as department , descText as descText , status as status from visitors) as visitorsView"
  }
}
```

## 删除一个工作站
接口地址: http://192.168.17.187/hqueue/manager/station

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "delete",
  "stationID": 9
}
```

返回内容:
```
{
  "rescode": "202",
  "errInfo": "None",
  "detail":{
  }
}
```

## 修改一个工作站信息
接口地址: http://192.168.17.187/hqueue/manager/station

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "edit",
  "stationID" : 14,
  "name": "E exam",
  "descText": "E exam station",
  "DBType" : "mysql",
  "host": "192.168.17.184",
  "port": "3306",
  "charset" : "utf8",
  "user" : "root",
  "passwd" : "123456",
  "DBName" : "HisQueue",
  "tableName" : "visitors",
  "aliasName": "name",
  "aliasAge": "age",
  "aliasQueue": "queue",
  "aliasID" :"ID",
  "aliasOrderDate" : "orderDate",
  "aliasOrderTime" : "orderTime",
  "aliasRegistDate" : "registDate",
  "aliasRegistTime" : "registTime",
  "aliasVIP": "emergency",
  "aliasSnumber" : "snumber",
  "aliasOrderType": "orderType",
  "aliasWorkerID" : "workerID",
  "aliasWorkerName" : "workerName",
  "aliasDepartment" : "department",
  "aliasDescText": "descText",
  "aliasStatus": "status",
  "aliasCardID": "cardID",
  "aliasPersonID:","persionID",
  "aliasPhone","phone",
  "renewPeriod" : "10s"
}
```

返回内容:
```
{ 
  "rescode": "202",
  "errInfo" : "none",
  "detail":{
  }
}
```