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

# Data
import sqlite3

import os.path as path

from typing import Dict

monitors: Dict[str, monitor.Monitor] = {
    "door/imu": monitor.imu.ImuMonitor(1),
    "door/contact": monitor.contact.ContactMonitor(1),
    "box/imu": monitor.imu.ImuMonitor(1),
    "box/contact": monitor.contact.ContactMonitor(1)
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
private_key, public_key = dh.get_private_key(), dh.gen_public_key()


# The callback for when a PUBLISH message is received from the server.

base_dir = path.join(path.dirname(__file__), "..")

conn = sqlite3.connect(path.join(base_dir, "data.db"))  # type: sqlite3.Connection

print(f"Server initialising, public key {public_key}")


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
    node_name, sensor_name = path.split(msg.topic)

    if sensor_name == "key":
        they_pk = msg.payload.decode()

        client.publish("server/key", payload=public_key, qos=1, retain=False)

        sk = dh.gen_shared_key(int(they_pk))

        print(f"Key exchange completed with {node_name} node, shared key {sk}")
        monitors[node_name + "/heartbeat"] = monitor.heartbeat.HeartbeatMonitor(sk)
        return

    if msg.topic in monitors:
        value = msg.payload.decode()
        monitors[msg.topic].input(value)

        # conn.execute("INSERT INTO sensor_data VALUES (?, ?, ?, ?)", (round(time.time(), 3), value, node_name, sensor_name))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.tls_set(path.join(base_dir, "certs/ca.crt"))

client.connect("10.90.12.213", 8883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
