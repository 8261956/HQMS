# -*- coding: utf-8 -*-

import datetime
import json
import web
from HQueue.common.func import checkPostAction
from HQueue.DBIO import DBBase as DB
from HQueue.modules.publish import PublishTVInterface


def collectLevel(cls,scene,sourceData,localData):  #收集访客的优先信息
        level = int(sourceData["snumber"])/1000 * 2
        order = sourceData["orderType"]
        level = level + 1 - order
        return level
