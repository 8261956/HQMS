# -*- coding:utf-8 -*-

import ConfigParser
import os
import json
import time

import datetime

from common.func import CachedGetValue, CahedSetValue

_config = ConfigParser.ConfigParser()
_config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
stationID = int(_config.get("station", "stationID"))
server = _config.get("station", "server")


class StationPrinter(object):

    def __init__(self):
        self.stationID = stationID

    def run(self):
        key = "print_stationID_{0}".format(self.stationID)

        while True:
            queue = CachedGetValue(json.dumps(key))
            while len(queue):
                result = queue.popleft()
                CahedSetValue(json.dumps(key), queue, timeout=0)
                current_time = datetime.datetime.now()
                print "[{0}] new visitor: {1}".format(current_time, result)
            time.sleep(2)


if __name__ == '__main__':
    station_printer = StationPrinter()
    station_printer.run()
