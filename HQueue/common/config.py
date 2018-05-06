
# -*- coding: UTF-8 -*-

import ConfigParser
import os

_config = ConfigParser.ConfigParser()
_config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

db_host = _config.get('database', 'host')
db_port = _config.get('database', 'port')
db_name = _config.get('database', 'name')
db_user = _config.get('database', 'user')
db_pass = _config.get('database', 'pass')

headPicPath = _config.get('global','HeadPicPath')
upload_http_base = _config.get('global','upload_http_base')
integrateType = _config.get("global","integrateType")
projectMark = _config.get("global","projectMark")

memcached_host = _config.get('memcached', 'host')
memcached_timeout = int(_config.get('memcached', 'timeout'))

mqServer = _config.get('MQ', 'mqServer')
mqPort = _config.get('MQ', 'mqPort')
mqKey = _config.get('MQ', 'mqKey')