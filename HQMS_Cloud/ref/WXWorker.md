# 查询医生信息接口


## 模糊查询医生信息

接口地址: http://192.168.17.187/hqueue_wx/manager/worker

方法: POST

参数:

```json
{
  "token": "safe token",
  "action": "fuzzySearchWorker",
  "keyword": "医生",
  "department": "内科",
  "hospitalName": "义乌中医医院"
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

接口地址: http://192.168.17.187/hqueue_wx/manager/worker

方法: POST

参数:

```json
{
  "token": "safe token",
  "action": "getDepartment",
  "hospitalName": "义乌中医医院"
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