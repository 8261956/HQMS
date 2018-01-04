# 数据库接口

## 获取不同数据库默认设置

接口地址: http://192.168.17.187/hqueue/manager/database

方法: POST

参数:

```json
{
  "token": "safe token",
  "action": "getDefaultSetting"
}
```

返回内容:

```json
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": {
        "oracle": {
            "passwd": "",
            "charset": "",
            "tableName": "",
            "DBName": "",
            "DBType": "oracle",
            "host": "",
            "user": "system",
            "port": 1521
        },
        "mssql": {
            "passwd": "",
            "charset": "utf8",
            "tableName": "",
            "DBName": "",
            "DBType": "mssql",
            "host": "",
            "user": "sa",
            "port": 1433
        },
        "mysql": {
            "passwd": "",
            "charset": "utf8",
            "tableName": "",
            "DBName": "",
            "DBType": "mysql",
            "host": "",
            "user": "root",
            "port": 3306
        }
    }
}
```

    注意:

    - 当数据库类型为mysql和mssql时，返回的字段都为必填项；
    - 当数据库类型为oracle时，返回的字段中以下字段不是必填项：
        - DBName
        - charset