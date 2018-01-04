#工作站管理工作人员信息的接口

## 获取工作人员列表
接口地址: http://192.168.17.187/hqueue/manager/worker

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "getList",
  "stationID" : 6
}
```
返回内容:

```
{ 
  "errInfo": "none",
  "rescode": "200"
  "detail":{
      "workerNum": 2,
      "workerList": [
        {
          "name": "王医生",
          "title": "主任",
          "headPic": "/headPic/wang",
          "descText": "擅长各种疑难杂症",
          "stationID": 6,
          "user": "wang",
          "department": "超声科",
          "password": "123456",
          "id": "",
          "speciality": "各种疑难杂症"
        },
        {
          "name": "王医生2",
          "title": "主任",
          "headPic": "/headPic/wang",
          "descText": "擅长各种疑难杂症",
          "stationID": 6,
          "user": "wang2",
          "department": "超声科",
          "password": "123456",
          "id": "D001",
          "speciality": "各种疑难杂症"
        }
      ],
  }
}
```

##获取工作者信息
接口地址: http://192.168.17.187/hqueue/manager/worker

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "getInfo",
  "id" : "D001"
}
```
返回内容:

```
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
      "name": "王医生2",
      "title": "主任",
      "headPic": "/headPic/wang",
      "descText": "擅长各种疑难杂症",
      "stationID": 6,
      "user": "wang2",
      "department": "超声科",
      "password": "123456",
      "id": "D001",
      "callerList": "[{},{}]",
      "speciality": "各种疑难杂症"
  }
}
```

##从数据源导入工作者信息
接口地址: http://192.168.17.187/hqueue/manager/worker

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "import",
  "DBType" : "mysql",
  "host": "192.168.17.184",
  "port": "3306",
  "charset" : "utf8",
  "user" : "root",
  "passwd" : "123456",
  "DBName" : "HisQueue",
  "tableName" : "workers_import",
  "id" : "id",
  "name":"name",
  "title":"title",
  "department":"department",
  "descText":"descText",
  "headPic" : "headPic",
  "speciality": "speciality"
}
```
必填项目： id, name 用户不填的传递""
返回内容:
```
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": {
        "successCount": 1,
        "totalImport": 3,
        "failedCount": 2
    }
}
```

##手动添加工作者信息
接口地址: http://192.168.17.187/hqueue/manager/worker

方法: POST

参数:

```
{
  "token": " safe action",
  "action": "addWorker",
  "id" : "D001",
  "name" : "王医生2",
  "user" : "wang2",
  "password" : "123456",
  "title" : "主任",
  "department" : "超声科",
  "descText" : "擅长各种疑难杂症",
  "headPic" : "/headPic/wang",
  "speciality": "各种疑难杂症"
}
```

默认的用户名为工作者ID_工作站ID，默认密码123456  
例如 工作站4的工作者ID D003  用户名默认为D003_4


返回内容:
```
{
   "errInfo": "none",
   "rescode": "200",
   "detail":{
   }
}
```

## 删除一个工作者信息
接口地址: http://192.168.17.187/hqueue/manager/worker/

方法: POST

参数:

```
{
  "token": " safe action",
  "action" : "delWorker",
  "id" : "D003"
}
```
返回内容:
```
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
        "result": "success"
   }
}
```
##修改一个工作者信息
接口地址: http://192.168.17.187/hqueue/manager/worker/

方法: POST

参数:

```
{
  "token": " safe action",
  "action" : "editWorker",
  "id" : "D001",
  "name": "王医生3",
  "title": "主任",
  "headPic": "/headPic/wang",
  "descText": "擅长各种疑难杂症",
  "user": "wang2",
  "department": "超声科",
  "speciality": "各种疑难杂症",
  "password": "123456"
}
```
返回内容:
```
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
     "result": "success/failed"
   }
}

```

## 获取导入医生的配置信息

接口地址: http://192.168.17.187/hqueue/manager/worker/

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
        "passwd": "clear!@#",
        "tableName": "workers",
        "host": "192.168.17.58",
        "user": "root",
        "id": "id",
        "name": "name",
        "title": "title",
        "headPic": "",
        "charset": "utf8",
        "descText": "descText",
        "port": 3306,
        "DBType": "mysql",
        "department": "department",
        "DBName": "HisQueue",
        "speciality": ""
    }
}
```

## 测试工作者数据源
接口地址: http://192.168.17.187/hqueue/manager/worker

方法: POST

参数:

```
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
  "tableName" : "workers_import"
}
```
返回内容:

```
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
    "result": "success/failed"
   }
}
```

##测试工作数据源配置
接口地址: http://192.168.17.187/hqueue/manager/worker

方法: POST

参数:

```
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
  "id" : "id",
  "name":"name",
  "title":"title",
  "department":"department",
  "descText":"descText",
  "headPic" : "",
  "speciality": ""
}
```
返回内容:

```
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
     "sql": "(SELECT id as id , name as name , title as title , department as department , descText as descText from workers_import) as workerView",
     "result": "success/failed"
   }
}
```
## 验证一个工作者ID是否可用
接口地址: http://192.168.17.187/hqueue/manager/worker/

方法: POST

参数:

```
{
  "token": " safe action",
  "action" : "checkID",
  "id" : "D003"
}
```
返回内容:
```
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
        "conflict": 0
   }
}
```
##上传工作者头像接口
nginx方法接口地址
http://192.168.17.187/headpicUpload
web.py方法接口地址
http://192.168.17.187/hqueue/manager/upload

方法: POST

参数:
```
upload filename stationID_workerID.jpg
```
返回内容:

```
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
     "result": "success",
     "upload_path" :"headpic/stationID2/D001.jpg",
     "size" : 100K,
   }
}

```

## 模糊查询医生信息

接口地址: http://192.168.17.187/hqueue/manager/worker/

方法: POST

参数:

```json
{
  "token": "safe token",
  "action": "fuzzySearchWorker",
  "keyword": "医生",
  "department": "内科"
}
```

返回内容：

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": [
        {
            "status": null,
            "name": "王医生",
            "title": "副主任",
            "department": "内科",
            "id": "D001",
            "descText": "",
            "source": "import",
            "speciality": "各种疑难杂症"
        },
        {
            "status": "离开",
            "name": "李医生",
            "title": "主任",
            "department": "内科",
            "id": "D002",
            "descText": "",
            "source": "manual_add",
            "speciality": "各种疑难杂症"
        }
    ]
}
```

参数说明：

```
来源：
    - import: 导入
    - manual_add: 手动添加
    - department: 
        - 传入此参数，可以获取此科室符合条件的医生
        - 不传入此参数或者此参数为空，则获取所有科室中符合条件的医生
```

## 获取所有科室

接口地址: http://192.168.17.187/hqueue/manager/worker/

方法: POST

参数:

```json
{
  "token": "safe token",
  "action": "getDepartment"
}
```

返回内容：

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": [
        "内科",
        "普通内科",
        "呼吸内科"
    ]
}
```

## 获取所有职称

接口地址: http://192.168.17.187/hqueue/manager/worker/

方法: POST

参数:

```json
{
  "token": "safe token",
  "action": "getTitle"
}
```

返回内容：

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": [
        "主任",
        "副主任",
        "医师"
    ]
}
```

## 根据条件查询医生信息

接口地址: http://192.168.17.187/hqueue/manager/worker/

方法: POST

参数:

```json
{
  "token": "safe token",
  "action": "getWorker",
  "department": "内科",
  "title": "主任",
  "source": "import",
  "name": "",
  "pageNum": 1,
  "pageSize": 2
}
```

返回内容：

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": {
        "count": 1,
        "list": [
            {
                "status": "离开",
                "source": "import",
                "name": "李医生",
                "title": "主任",
                "department": "内科",
                "id": "D002",
                "descText": "",
                "speciality": "各种疑难杂症"
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
    
查询参数：
    - department: 科室，如果不传入此参数，获取所有科室下的符合条件的医生
    - title: 职称，如果不传入此参数，获取符合条件的所有职称的医生
    - source: 来源，
        - import: 导入
        - manual_add: 手动添加
        - 如果不传入source参数，获取符合条件的所有来源的医生
    - name: 名字，如果不传入此参数，获取符合条件和名字的医生
```