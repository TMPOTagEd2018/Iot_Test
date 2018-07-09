import sqlite3
import os
import time
import random
from os.path import join, realpath, dirname, isfile

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

path = join(dirname(realpath(__file__)), '..\\sensor-data.db')

touch(path)

print(f"Writing data to {path}")
with sqlite3.connect(path) as conn:
    try:
        conn.execute(r"""
        CREATE TABLE sensor_data (
            timestamp TIME    NOT NULL,
            value     INTEGER NOT NULL
                            DEFAULT (0) 
                            CHECK (128 > value AND 
                                    value > -128),
            node      TEXT    NOT NULL,
            sensor    TEXT    NOT NULL
        );""")
    except:
        # error means that the table already exists
        pass
    
    if input("Fill DB with fake data? (yes/NO): ").lower() == "yes":
        cur = conn.cursor()

        nodes = ["door", "box", "room"]
        sensors = ["imu", "lux", "contact"]

        for i in range(500):
            cur.execute(f"INSERT INTO sensor_data VALUES ({int(time.time()) - i * 1000}, {random.randint(-127, 127)}, '{random.choice(nodes)}', '{random.choice(sensors)}')")