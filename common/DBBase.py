# -*- coding: utf-8 -*-

import web
import config as cfg

# 排队叫号数据库
DBLocal = web.database(
    dbn='mysql',
    host=cfg.db_host,
    port=int(cfg.db_port),
    user=cfg.db_user,
    pw=cfg.db_pass,
    db=cfg.db_name,
    charset='utf8'
)


# 微信服务器
DBLocal_WX = web.database(
    dbn='mysql',
    host=cfg.wx_db_host,
    port=int(cfg.wx_db_port),
    user=cfg.wx_db_user,
    pw=cfg.wx_db_pass,
    db=cfg.wx_db_name,
    charset='utf8'
)


def hqueue_db():
    return DBLocal


def hqms_cloud_db():
    return DBLocal_WX