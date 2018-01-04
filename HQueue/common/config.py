
# -*- coding: UTF-8 -*-

import ConfigParser
import os

_config = ConfigParser.ConfigParser()
_config.read(os.path.join(os.path.dirname(__file__), '../static/config.ini'))

db_host = _config.get('database', 'host')
db_port = _config.get('database', 'port')
db_name = _config.get('database', 'name')
db_user = _config.get('database', 'user')
db_pass = _config.get('database', 'pass')

headPicPath = _config.get('global','HeadPicPath')
upload_http_base = _config.get('global','upload_http_base')
backupTime = _config.get("global","backupTime")
deadTime = _config.get("global","deadTime")
currentDayOnly = _config.get("global","currentDayOnly")
AutoSyncFinish = _config.get("global","AutoSyncFinish")

memcached_host = _config.get('memcached', 'host')
memcached_timeout = int(_config.get('memcached', 'timeout'))

displayFormateDefault = _config.get('voice','displayFormateDefault')
voiceFormateDefault = _config.get('voice','voiceFormateDefault')
