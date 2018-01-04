# -*- coding: utf-8 -*-

import ConfigParser
import os

_config = ConfigParser.ConfigParser()
_config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

# 医院排队叫号系统的数据库参数
db_host = _config.get('database', 'host')
db_port = _config.get('database', 'port')
db_name = _config.get('database', 'name')
db_user = _config.get('database', 'user')
db_pass = _config.get('database', 'pass')

# 微信云服务器的数据库参数
wx_db_host = _config.get("database_wx", "host")
wx_db_port = _config.get("database_wx", "port")
wx_db_name = _config.get("database_wx", "name")
wx_db_user = _config.get("database_wx", "user")
wx_db_pass = _config.get("database_wx", "pass")

# 访问医院内网数据的API接口地址
wx_api_url = _config.get('global','wx_api_url')

# 向微信云服务器同步数据的API接口地址
sync_api_url = _config.get('global', 'sync_api_url')
headPicPath = _config.get('global','HeadPicPath')

# 从医院内网访问医生头像的URL基础地址
upload_http_base = _config.get('global','upload_http_base')

# 从微信云端访问医生头像的URL基础地址
wx_upload_http_base = _config.get('global','wx_upload_http_base')

backupTime = _config.get("global","backupTime")
deadTime = _config.get("global","deadTime")
currentDayOnly = _config.get("global","currentDayOnly")
AutoSyncFinish = _config.get("global","AutoSyncFinish")

memcached_host = _config.get('memcached', 'host')
memcached_timeout = int(_config.get('memcached', 'timeout'))

displayFormateDefault = _config.get('voice','displayFormateDefault')
voiceFormateDefault = _config.get('voice','voiceFormateDefault')