# -*- coding: utf-8 -*-

import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

localServer = "127.0.0.1"
localPort = "1883"
localTopic = "station_printer"

def publish_printer(vInfo):
    publish.single(localTopic, payload=vInfo, qos=0, retain=False, hostname="localhost",
           port=1883, client_id="", keepalive=60, will=None, auth=None, tls=None,
           protocol=mqtt.MQTTv311)
