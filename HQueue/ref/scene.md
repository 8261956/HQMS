# 策略管理接口

[TOC]

##策略字段和说明
| name        | 说明           |           
| ------------- |:-------------:|      
| name      | 名字       | 
| descText      | 预留描述       | 
| activeLocal      | 本地激活       | 
| rankWay      | 排序方式      |
| output      | 叫号输出      |
| prepareOutput     | 候者叫号输出      | 
| soundDoingTimes      | 叫号播报次数      |
| soundPrepareTimes      | 候诊播报次数      |
| autoPrepare      | 自动分诊      |
| defaultPrepareNum      | 默认候诊人数      |  
| delayTime      | 预留激活延迟时间      |  
| InsertPassedSeries      | 过号连续插入个数      | 
| InsertPassedInterval      | 过号插入间隔      | 
| InsertReviewSeries      | 复诊连续插入个数      |
| InsertReviewInterval      | 复诊连续插入间隔      |
| InsertPriorSeries      | 优先连续插入个数      | 
| InsertPriorInterval      | 优先连续插入间隔      |  
| priorOlderAge      | 老人优先年龄      | 
| priorCldAge      | 儿童优先年龄      | 
| workDays      | 队列数据有效天数      | 
| autoSyncFinish      | 自动识别完成状态      |  
| property      | 预留 特性保存区 字典转字符串      | 

## 添加自定义场景

接口地址： http://192.168.17.187/hqueue/manager/scene

方法： POST

参数：

```json
{
    "action": "addScene",

    "name": "新策略",
    "descText": "",
    "activeLocal": 1,
    "rankWay": "snumber",
    "output": "请$name到$pos就诊",
    "prepareOutput": "请$name等候",

    "soundDoingTimes": 2,
    "soundPrepareTimes": 1,
    "autoPrepare": 0,
    "defaultPrepareNum": 1,
    "delayTime": 0,
    "InsertPassedSeries": 2,
    "InsertPassedInterval": 3,
    "InsertReviewSeries": 2,
    "InsertReviewInterval": 3,
    "InsertPriorSeries": 2,
    "InsertPriorInterval": 3,

    "priorOlderAge": 65,
    "priorCldAge": 8,
    "workDays": 1,
    "autoSyncFinish": null,
    "property": {}
}
```

返回内容：

```json
{
  "errInfo": "none",
  "rescode": "200",
  "detail": {
    "result": "success",
    "sceneID": 33
  }
}
```

参数说明：
```
  InsertPassedSeries: 过号插入数量，可以连续插入过号患者的数量;
  InsertPassedInterval: 过号插入间隔，每隔一定间隔可插入过号患者;
  InsertReviewSeries: 复诊插入数量，可以连续插入复诊患者的数量;
  InsertReviewInterval: 复诊插入间隔, 每隔一定间隔可插入复诊患者;
  InsertPriorSeries: 优先插入数量，可以连续插入优先患者的数量;
  InsertPriorInterval: 优先插入间隔, 每隔一定间隔可插入优先患者;
  
  output、prepareOutput中的表达式需由前端根据用户输入选项生成
  
  autoSyncFinish: 视图删除数据后是否设置患者状态为已完成，值为0或者1;
  property 中可添加若干其他熟悉 例如：orderNoPrior:1 患者预约是否优先，值为0或者1;
```


## 修改某一个场景

接口地址： http://192.168.17.187/hqueue/manager/scene

方法： POST

参数：

```json
{
    "action": "editScene",
    "sceneID" : 33,

    "name": "新策略修改",
    "descText": "",
    "activeLocal": 1,
    "rankWay": "snumber",
    "output": "请$name到$pos就诊",
    "prepareOutput": "请$name等候",

    "soundDoingTimes": 2,
    "soundPrepareTimes": 1,
    "autoPrepare": 0,
    "defaultPrepareNum": 1,
    "delayTime": 0,
    "InsertPassedSeries": 2,
    "InsertPassedInterval": 3,
    "InsertReviewSeries": 2,
    "InsertReviewInterval": 3,
    "InsertPriorSeries": 2,
    "InsertPriorInterval": 3,

    "priorOlderAge": 65,
    "priorCldAge": 8,
    "workDays": 1,
    "autoSyncFinish": null,
    "property": {}
}
```

返回内容：

```json
{
  "errInfo": "none",
  "rescode": "200",
  "detail": {
    "result": "success"
  }
}
```

## 获取某一个场景的信息

接口地址： http://192.168.17.187/hqueue/manager/scene

方法： POST

参数：

```json
{
    "token": " safe action",
	"action": "getSceneInfo",
	"sceneID": 9
}
```

返回内容：

```json
{
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
  	"id": 9,
    "name": "测试",
    "descText": "",
    "activeLocal": 1,
    "rankWay": "snumber",
    "output": "请$name到$pos就诊",
    "prepareOutput": "请$name等候",
    
    "soundDoingTimes": 2,
    "soundPrepareTimes": 1,
    "autoPrepare": 0,
    "defaultPrepareNum": 1,
    "delayTime": 0,
    "InsertPassedSeries": 2,
    "InsertPassedInterval": 3,
    "InsertReviewSeries": 2,
    "InsertReviewInterval": 3,
    "InsertPriorSeries": 2,
    "InsertPriorInterval": 3,
    
    "priorOlderAge": null,
    "priorCldAge": null,
    "workDays": 1
    "autoSyncFinish": null,
    "property": {},
  }
}
```