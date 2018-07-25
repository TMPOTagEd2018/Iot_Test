#!/usr/bin/python3

import argparse

# MQTT
import paho.mqtt.client as mqtt

# Monitors
import monitor
import monitor.pir
import monitor.lux
import monitor.accel
import monitor.contact
import monitor.heartbeat

from processor import ThreatProcessor

# Key exchange and verification
import keyex

# Data
import sqlite3
import struct

import os.path as path
import os

import time

from typing import Dict

parser = argparse.ArgumentParser()
parser.add_argument("--watch", help="Run the server in watch mode. In this mode, the server will not interact, only recieve.", action="store_true")
args = parser.parse_args()

monitors: Dict[str, monitor.Monitor] = {
    "room/pir": monitor.pir.PirMonitor(1),
    "room/lux": monitor.lux.LuxMonitor(1),
    "door/accel": monitor.accel.AccelMonitor(1),
    "door/contact": monitor.contact.ContactMonitor(1),
    "box/accel": monitor.accel.AccelMonitor(2),
    "box/contact": monitor.contact.ContactMonitor(3)
}

base_dir = path.dirname(path.dirname(path.abspath(__file__)))

print(f"Base dir: {base_dir}")

db_path = path.join(base_dir, "data.db")

print(f"DB path: {db_path}")

conn = sqlite3.connect(db_path)  # type: sqlite3.Connection

processor = ThreatProcessor(list(map(lambda m: m.threats, monitors.values())), conn, 5)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

    client.subscribe("door/accel")
    client.subscribe("door/contact")
    client.subscribe("door/heartbeat")
    client.subscribe("door/key")

    client.subscribe("room/lux")
    client.subscribe("room/pir")
    client.subscribe("room/heartbeat")
    client.subscribe("room/key")

    client.subscribe("box/accel")
    client.subscribe("box/contact")
    client.subscribe("box/heartbeat")
    client.subscribe("box/key")


authenticated = {}
dh = keyex.DiffieHellman()
private_key, public_key = dh.get_private_key(), dh.gen_public_key()


print(f"Server initialising, public key {hex(public_key)[:16] + hex(public_key)[-16:]}")

if args.watch:
    print("Watch mode enabled.")


def write_heartbeat(node_name: str):
    cache_folder = path.join(base_dir, f"cache/{node_name}")

    if not path.exists(cache_folder):
        os.makedirs(cache_folder)

    cache_file_name = path.join(cache_folder, "heartbeat")

    with open(cache_file_name, "w+") as cache_file:
        cache_file.write(str(time.time()))


def write_cache(node_name: str, sensor_name: str, value: float):
    cache_folder = path.join(base_dir, f"cache/{node_name}")

    if not path.exists(cache_folder):
        os.makedirs(cache_folder)

    cache_file_name = path.join(cache_folder, sensor_name)

    POINTER_SIZE = 4
    RECORD_SIZE = 13
    RECORD_COUNT = 2400
    with open(cache_file_name, "r+b" if os.path.exists(cache_file_name) else "w+b") as cache_file:
        current_size = os.stat(cache_file_name).st_size
        target_size = POINTER_SIZE + RECORD_SIZE * RECORD_COUNT

        if current_size < target_size:
            cache_file.seek(0, 2)
            bloc = bytearray(target_size - current_size)
            cache_file.write(bloc)

        cache_file.seek(0, 0)

        # read position of ring buffer
        position_bytes = cache_file.read(POINTER_SIZE)
        position = struct.unpack("<L", position_bytes)[0]

        timestamp = time.time()
        file_position = POINTER_SIZE + position * RECORD_SIZE
        cache_file.seek(file_position, 0)

        if int(value) == value:
            cache_file.write(struct.pack("<d?i", timestamp, False, int(value)))
        else:
            cache_file.write(struct.pack("<d?f", timestamp, True, float(value)))

        position = (position + 1) % RECORD_COUNT
        position_bytes = struct.pack("<L", position)

        cache_file.seek(0, 0)
        cache_file.write(position_bytes)
        cache_file.flush()


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
    node_name, sensor_name = path.split(msg.topic)

    if sensor_name == "key" and not args.watch:
        they_pk = msg.payload.decode()

        client.publish("server/key", payload=public_key, qos=1, retain=False)

        sk = dh.gen_shared_key(int(they_pk))

        abbrev_sk = hex(sk)[:16] + hex(sk)[-16:]

        print(f"Key exchange completed with {node_name} node, shared key {abbrev_sk}")
        monitors[node_name + "/heartbeat"] = monitor.heartbeat.HeartbeatMonitor(sk)
        authenticated[node_name] = True
        return

    if msg.topic in monitors and (node_name in authenticated.keys() or args.watch):
        value = float(msg.payload.decode())
        monitors[msg.topic].input(value)

        if sensor_name == "heartbeat":
            write_heartbeat(node_name)
        else:
            write_cache(node_name, sensor_name, value)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.tls_set(path.join(base_dir, "certs/mqtt/ca.crt"))

client.connect("10.90.12.213", 8883, 60)

if not args.watch:
    client.publish("server/init", True, qos=2)
    print("init signal broadcasted")

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
