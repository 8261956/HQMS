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

}