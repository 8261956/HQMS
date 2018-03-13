# -*- coding: utf-8 -*-

import ConfigParser
import json
import os
import random
from functools import wraps
import datetime
import time
import re

from DBIO.DBBase import DBLocal
from common.func import CahedSetValue, CachedGetValue


_config = ConfigParser.ConfigParser()
_config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
stationID = int(_config.get("station", "stationID"))


def memcached_wrapper(key, timeout):
    """memcached装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kw):
            value = CachedGetValue(json.dumps(key))
            if value:
                return value
            result = func(*args, **kw)
            CahedSetValue(json.dumps(key), result, timeout)
            return result
        return wrapper
    return decorator


class VisitorManager(object):

    def __init__(self):
        self.db = DBLocal
        self.counter = 0

    @property
    @memcached_wrapper('test_queue_filter', 3)
    def queue_filter(self):
        what = "DISTINCT queue"
        tmp = self.db.select("visitors", what=what).list()
        queue_filter_list = [item.queue for item in tmp]
        return queue_filter_list

    @property
    @memcached_wrapper('test_department', 3)
    def department(self):
        what = "filter, department"
        queue_info = self.db.select("queueInfo", what=what).list()
        for q in queue_info:
            filter = re.findall(r'queue=\'(.*)\'', q.pop("filter"))
            queue = filter[0]
            q.update({"queue": queue})

        return queue_info

    def create_visitor(self):
        self.counter += 1
        snumber = self.counter
        name = "Test{0}".format(snumber)
        queue = random.choice(self.queue_filter)
        age = random.randrange(10, 80)
        current_time = datetime.datetime.now()
        id = int(time.time() * 1000)
        orderDate = registDate = current_time.strftime("%Y-%m-%d")
        orderTime = registTime = current_time.strftime("%H:%M:%S")
        emergency = random.choice([0, 1])
        orderType = random.choice([0, 1])
        department = None
        for item in self.department:
            for q, d in item.items():
                if q == queue:
                    department = d
                    break

        value = {
            "id": id,
            "name": name,
            "age": age,
            "queue": queue,
            "snumber": snumber,
            "orderDate": orderDate,
            "orderTime": orderTime,
            "registDate": registDate,
            "registTime": registTime,
            "emergency": emergency,
            "orderType": orderType,
            "department": department
        }

        self.db.insert("visitors", **value)
        print "[{0}] add new visitor: {1}".format(current_time, name)

    def run(self):
        while True:
            self.create_visitor()
            time.sleep(30)


if __name__ == '__main__':
    v = VisitorManager()
    v.run()