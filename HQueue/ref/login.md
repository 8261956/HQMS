#登入

###管理员/工作者登入
接口地址: http://192.168.17.187/hqueue/login

方法: POST

参数:
```
{
  "action": "GetToken",
  "user" : "root",
  "passwd" : "123456",
  "type": "manager"
}
```

参数说明:

```
type:
    - 旧的登录方式中不传入type参数；
    - 新的登录方式中传入type参数
        - manager: 后台登录
        - station: 分诊台登录
        - worker: 叫号器登录
```

```
管理员帐号 root/123456  
分诊台帐号 station2/123456  station6/123456  
医生帐号 D002_2/123456
```

返回内容:

Manager类型用户返回参数
```
{ 
  "errInfo": "none",
  "rescode": "200"
  "detail":{
     "userType" : "Manager",
     "token": "HQMS_manager_evod29x1",
  }
}
```
Station类型用户返回参数
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "userType": "station",
    "stationID": 2,
    "token": "HQMS_station_edotor29x1"
  }
}
```
Worker类型用户返回参数
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "userType": "worker",
    "stationID": 2,
    "token": "HQMS_worker_edotor29x1",
    "callerID": 10
  }
}```
