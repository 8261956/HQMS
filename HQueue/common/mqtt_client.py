# -*- coding: utf-8 -*-

import json
import threading
import paho.mqtt.client as mqtt
import copy
import config
from controller.visitor import VisitorManager

mqttclient = mqtt.Client()

class mqtt_task(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        mqttclient.on_connect = on_connect
        mqttclient.on_message = on_message
        mqttclient.on_disconnect = on_disconnect

    def run(self):
        print "mqtt start work"
        mqttclient.connect(config.mqServer, config.mqPort, 60)
        mqttclient.loop_forever()

def on_connect(client, userdata, flags, rc):
    print("connected :" + str(rc))
    client.subscribe(config.mqKey)

def on_message(client, userdata, msg):
    print client
    topic = msg.topic
    data = msg.payload.decode('gbk')
    print topic, data
    handle_message(topic, data)

def on_disconnect(client, userdata, rc):
    print "disconnect:", rc
    client.reconnect()

def publish_message(topic, payload):
    print "topic:",topic,"msg:",payload
    mqttclient.publish(topic, payload)

def stop_client():
    mqttclient.loop_stop(True)

def handle_message(topic, data):
    """
    MQTT 患者消息处理
    :param topic: 订阅关键字
    :param data: 数据包
    :return:
    """

    print "handle_message"
    try:
        sourceItem = json.loads(data)
        VisitorManager().visitor_quick_add(sourceItem)
        if config.projectMark == "PINGAN" :
            from project.pingan.publish import publish_printer
            publish_printer(sourceItem)

    except Exception as e:
        print e.message

if __name__ == "__main__":
    m = mqtt_task()
    m.start()