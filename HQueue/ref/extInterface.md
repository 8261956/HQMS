
#内网排队信息查询接口

目前考虑主要通过 Http/Https Post请求 访问服务器获取排队信息
projectToken 由我方提供

[TOC]
##获取查询权限
接口地址: http://server_ip/hqueue/main/extUser

方法: POST

参数:
```
{
  "action" : "GetToken",
  "type" : "extUser",
  "projectToken" : "xxxxxxxx"
}
```
返回内容:
```
{ 
  "errInfo": "none",
  "rescode": "200",
  "detail":{
     "userType" : "extUser",
     "token": "HQMS_extUser_eseach29x1",
  }
}
```

##模糊查询患者信息
接口地址: http://server_ip/hqueue/main/extInterface
依据卡号 cardID 、手机号 phone、身份证号 personID 进行查询

方法: POST

参数:
```
{
  "token": " HQMS_extUser_eseach29x1",
  "action" : "FuzzySearch",
  "paraName" : "phone",
  "paraVal" : "15821432783"
}
```
返回内容:
```
{
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
  	"vList" : [
    	{
        	"id": "D0022",
        	"name": "刘武",
            "snumber": 4,			#序号
            "status": "已预约",
            "queueName": "儿科王岚",
            "localStatus": "排队中",
            "registDate": 2018-02-07,
            "age": 14,
            "department": "儿科",
            "waitingTime": 75,             #预估等候时间  分钟
            "waitingNum": 5				   #预估等候人数
        },
        {
        	"id": "D0023",
        	"name": "刘武",
            "snumber": 32,			#序号
            "status": "普通",
            "queueName": "眼科刘伟",
            "localStatus": "排队中",
            "registDate": 2018-02-07,
            "age": 14,
            "department": "眼科",
            "waitingTime": 35,             #预估等候时间  分钟
            "waitingNum": 2				   #预估等候人数
        }
    ]
  }
}
```

##精确查询患者信息
接口地址: http://server_ip/hqueue/main/extInterface
已知挂号ID情况下快速查询

方法: POST

参数:
```
{
  "token": " HQMS_extUser_eseach29x1",
  "action" : "visitorSearch",
  "id" : "D0022"
}
```
返回内容:
```
{
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
  	"vList" : [
    	{
        	"id": "D0022",
        	"name": "刘武",
            "snumber": 4,			#序号
            "status": "已预约",
            "queueName": "儿科王岚",
            "localStatus": "排队中",
            "registDate": 2018-02-07,
            "age": 14,
            "department": "儿科",
            "waitingTime": 75,             #预估等候时间  分钟
            "waitingNum": 5				   #预估等候人数
        }
    ]
  }
}
```