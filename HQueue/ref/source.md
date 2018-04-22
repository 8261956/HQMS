#患者登记接口



[TOC]

##患者登记
接口地址: http://192.168.17.187/hqueue/manager/source

方法: POST

参数:
```json
{
  "token": "safe action",
  "action":"regist",
  "vInfo" : {
  	"id" : "2018042201",
    "name" : "测试号",
    "queue" : "王宏献"
  }
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

##亚心查询患者信息 （同时登记）
接口地址: http://192.168.17.187/hqueue/yaxin/source

方法: POST

参数:
```json
{
  "action":"reqInfo",
  "trmtno" : "",
  "regist" : 1,
  "ywlx" : ""
}
```
返回内容:
```json
{

}
