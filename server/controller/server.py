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

import db
import os.path as path

from typing import Dict

parser = argparse.ArgumentParser()
parser.add_argument("--watch", help="Run the server in watch mode. In this mode, the server will not interact, only recieve.", action="store_true")
args = parser.parse_args()

monitors: Dict[str, monitor.Monitor] = {
    "room/pir": monitor.pir.PirMonitor(0.3),
    "room/lux": monitor.lux.LuxMonitor(0.5),
    "door/accel": monitor.accel.AccelMonitor(2),
    "door/contact": monitor.contact.ContactMonitor(2),
    "box/accel": monitor.accel.AccelMonitor(2),
    "box/contact": monitor.contact.ContactMonitor(3)
}

base_dir = path.dirname(path.dirname(path.abspath(__file__)))

print(f"Base dir: {base_dir}")

db.init(base_dir)

alarm = False


def threat_handler(level: float):
    global alarm

    db.write_threat(level)

    if not args.watch:
        if level > 8 and not alarm:
            alarm = True
            client.publish("server/alarm", 1, qos=1)

        if level < 8 and alarm:
            alarm = False
            client.publish("server/alarm", 0, qos=1)


processor = ThreatProcessor(list(map(lambda m: m.threats, monitors.values())), threat_handler)


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


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
    node_name, sensor_name = path.split(msg.topic)

    if sensor_name == "key" and not args.watch:
        they_pk = msg.payload.decode()

        client.publish("server/key", payload=public_key, qos=1, retain=False)

        sk = dh.gen_shared_key(int(they_pk))

        print(f"Key exchange completed with {node_name} node, shared key {sk}")
        monitors[node_name + "/heartbeat"] = monitor.heartbeat.HeartbeatMonitor(sk)
        authenticated[node_name] = True

        if node_name == "box" and alarm and not args.watch:
            # box node was turned off and is coming back online, hit the alarm!
            client.publish("server/alarm", 1, qos=1)

        return

    if msg.topic in monitors:
        if node_name in authenticated.keys() or args.watch:
            value = float(msg.payload.decode())
            monitors[msg.topic].input(value)

            if sensor_name == "heartbeat":
                db.write_heartbeat(node_name)
            else:
                db.write_cache(node_name, sensor_name, value)
        else:
            print(f"rejected value {msg.payload} from {msg.topic} because {node_name} not in {authenticated.keys()}")


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
