#!/usr/bin/python3

# MQTT
import paho.mqtt.client as mqtt

# Monitors
import monitor
import monitor.imu
import monitor.contact
import monitor.heartbeat

from processor import ThreatProcessor

# Key exchange and verification
import keyex
import random

# Data
import sqlite3
import time

import os.path as path

from rx import Observable

from typing import Dict

monitors: Dict[str, monitor.Monitor] = {
    "door/imu": monitor.imu.ImuMonitor(1),
    "door/contact": monitor.contact.ContactMonitor(1),
    "door/heartbeat": monitor.heartbeat.HeartbeatMonitor(1),
    "box/imu": monitor.imu.ImuMonitor(1),
    "box/contact": monitor.contact.ContactMonitor(1),
    "box/heartbeat": monitor.heartbeat.HeartbeatMonitor(1)
}

processor = ThreatProcessor(list(map(lambda m: m.threats, monitors.values())), 5)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

    client.subscribe("door/imu")
    client.subscribe("door/contact")
    client.subscribe("door/heartbeat")
    client.subscribe("door/key")

    client.subscribe("room/lux")
    client.subscribe("room/pir")
    client.subscribe("room/range")
    client.subscribe("room/heartbeat")
    client.subscribe("room/key")

    client.subscribe("box/imu")
    client.subscribe("box/contact")
    client.subscribe("box/range")
    client.subscribe("box/heartbeat")
    client.subscribe("box/key")


rngs = {}
dh = keyex.DiffieHellman()

# The callback for when a PUBLISH message is received from the server.

conn = sqlite3.connect("..\\data.db") # type: sqlite3.Connection


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
    node_name, sensor_name = path.split(msg.topic)

    if sensor_name == "key":
        they_pk = msg.payload

        client.publish(msg.topic, qos=1)

        sk = dh.gen_shared_key(they_pk)
        seed = int(sk, 16)

        random.seed(seed)

        rngs[node_name] = random.getstate()
        montiors[node_name] = monitor.heartbeat.HeartbeatMonitor()
        return

    if node_name not in rngs:
        return

    if sensor_name == "heartbeat":
        random.setstate(rngs[node_name])

        check = random.getrandbits(32)
        heartbeat = int(msg.payload.decode())

        if check != heartbeat:
            continue

        monitors[msg.topic].input(heartbeat)

    else if msg.topic in monitors:
        value = msg.payload.decode()
        monitors[msg.topic].input(value)

        conn.execute("INSERT INTO sensor_data VALUES (?, ?, ?, ?)", (round(time.time(), 3), value, node_name, sensor_name))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("10.90.12.213", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
