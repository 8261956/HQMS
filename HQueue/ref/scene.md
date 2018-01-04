# 策略管理接口
## 添加自定义场景

接口地址： http://192.168.17.187/hqueue/manager/scene

方法： POST

参数：

```json
{
  "token": " safe action",
  "action": "addScene",
  "name": "测试",
  "activeLocal": "1",
  "rankWay": "registTime",
  "delayTime": "30",
  "waitNum": "5",
  "outputText": "就诊",
  "passedWaitNum": "5",
  "reviewWaitNum": "5",
  "priorNum": "3",
  "workDays": 1,
  "InsertPassedSeries": 2,
  "InsertPassedInterval": 3,
  "InsertReviewSeries": 2,
  "InsertReviewInterval": 3,
  "InsertPriorSeries": 2,
  "InsertPriorInterval": 3,
  "property": {
      "morningPrior": 1,
      "noPrepare": 1,
      "callMode": "callByCardID",
      "autoSyncFinish": 1,
      "orderNoPrior": 0
  }
}
```

返回内容：

```json
{
  "errInfo": "none",
  "rescode": "200",
  "detail": {
    "result": "success",
    "sceneID": "6"
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
  
  morningPrior: 早上患者优先，值为0或者1;
  noPrepare: 是否播报"请***准备"，值为0或者1;
  callMode: 播报方式，值为callByName, callBySnumber, callByCardID;
  autoSyncFinish: 视图删除数据后是否设置患者状态为已完成，值为0或者1;
  orderNoPrior: 患者预约是否优先，值为0或者1;
```


## 修改某一个场景

接口地址： http://192.168.17.187/hqueue/manager/scene

方法： POST

参数：

```json
{
  "token": " safe action",
  "action": "editScene",
  "sceneID": "9",
  "name": "测试",
  "activeLocal": "1",
  "rankWay": "registTime",
  "delayTime": "30",
  "waitNum": "5",
  "outputText": "取药",
  "passedWaitNum": "5",
  "reviewWaitNum": "5",
  "priorNum": "3",
  "workDays": 1,
  "InsertPassedSeries": 2,
  "InsertPassedInterval": 3,
  "InsertReviewSeries": 2,
  "InsertReviewInterval": 3,
  "InsertPriorSeries": 2,
  "InsertPriorInterval": 3,
  "property": {
      "morningPrior": 1,
      "noPrepare": 1,
      "callMode": "callByCardID",
      "autoSyncFinish": 1,
      "orderNoPrior": 0
  }
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
        "activeLocal": 1,
        "rankWay": "registTime",
        "waitNum": 5,
        "delayTime": 30,
        "name": "测试",
        "outputText": "就诊",
        "id": 9,
        "passedWaitNum": "5",
        "reviewWaitNum": "5",
        "priorNum": "3",
        "workDays": 1,
        "descText": "测试场景, 需要本地激活, 使用挂号时间进行排序, 播报请**到**就诊",
        "InsertPassedSeries": 2,
        "InsertPassedInterval": 3,
        "InsertReviewSeries": 2,
        "InsertReviewInterval": 3,
        "InsertPriorSeries": 2,
        "InsertPriorInterval": 3,
        "property": {
            "morningPrior": 1,
            "noPrepare": 1,
            "callMode": "callByCardID",
            "autoSyncFinish": 1,
            "orderNoPrior": 0
        }
    }
}
```