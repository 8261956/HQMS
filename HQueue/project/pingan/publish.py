# -*- coding: utf-8 -*-

import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

localServer = "127.0.0.1"
localPort = "1883"
localTopic = "station_printer"

def publish_printer(vInfo):
    printInfo = {
        "cmd": "print",
        "val": {
            "print_name": vInfo.get("name",""),
            "print_snumber" : vInfo.get("snumber",""),
            "print_queue": vInfo.get("queue", "")
        }
    }
    publish.single(localTopic, payload=json.dumps(printInfo), qos=0, retain=False, hostname = localServer,
           port=localPort, client_id="", keepalive=60, will=None, auth=None, tls=None,
           protocol=mqtt.MQTTv311)
