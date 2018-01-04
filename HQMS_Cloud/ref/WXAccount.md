# 微信账户管理接口


## 用户注册

接口地址：http://192.168.17.187/hqueue_wx/manager/account

请求方法：POST

参数：

```json
{
  "action": "login",
  "name": "张三",
  "phone": "15021801933",
  "cardID": "fan001",
  "personID": "620502199110053637"
}
```

返回内容：

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": {
        "token": "hqms_adv_user_15021801933_50x3spd3",
        "result": "success",
        "userInfo": {
            "uid": 1,
            "personID": "620502199110053637",
            "cardID": "Fan001",
            "phone": "15021801933",
            "registTime": "2017-09-10 00:31:39",
            "name": "范春科"
        }
    }
}
```


## 用户登录

接口地址：http://192.168.17.187/hqueue_wx/manager/account

请求方法：POST

参数：

```json
{
  "action": "login",
  "phone": "15021801933",
  "cardID": "fan001"
}
```

返回内容：

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": {
        "token": "hqms_adv_user_15021801933_50x3spd3",
        "result": "success",
        "userInfo": {
            "uid": 1,
            "personID": "620502199110053637",
            "cardID": "Fan001",
            "phone": "15021801933",
            "registTime": "2017-09-10 00:31:39",
            "name": "范春科"
        }
    }
}
```


## 查询用户信息

接口地址：http://192.168.17.187/hqueue_wx/manager/account

请求方法：POST

参数：

```json
{
  "token": "safe token",
  "action": "getUserInfo",
  "uid":1
}
```

返回内容：

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": {
        "personID": "620502199110053637",
        "phone": "15021801933",
        "cardID": "ZH001",
        "uid": 1,
        "name": "张三"
    }
}
```


## 编辑用户信息

接口地址：http://192.168.17.187/hqueue_wx/manager/account

请求方法：POST

参数：

```json
{
  "token": "safe token",
  "action": "editUserInfo",
  "uid":1,
  "name": "张三",
  "phone": "15021801933",
  "personID": "620502199110053637",
  "cardID": "FAN001"
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

## 获取用户排队情况

接口地址：http://192.168.17.187/hqueue_wx/manager/account

请求方法：POST

参数：

```json
{
  "token": "safe token",
  "action": "getUserQueueInfo",
  "phone": "15021801933"
}
```

返回内容：

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": {
        "queueInfo": {
            "num": 2,
            "list": [
                {
                    "department": null,
                    "status": "waiting",
                    "waitNum": 1,
                    "waitTime": 15,
                    "name": "王宏献队列"
                },
                {
                    "department": "急诊科",
                    "status": "unactive",
                    "waitNum": 0,
                    "waitTime": 0,
                    "name": "急诊队列"
                }
            ]
        },
        "userInfo": {
            "personID": "620502199110053637",
            "phone": "15021801933",
            "cardID": "ZH001",
            "uid": 1,
            "name": "张三"
        }
    }
}
```

```
未登录用户不用传递token

status状态说明：
    - waiting: 正在等待
    - doing: 正在就诊
    - unactive: 未激活
    - unactivewaiting: 激活等待
```
