import sqlite3
import os
import time
import random
from os.path import join, realpath, dirname, isfile


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


path = join(dirname(realpath(__file__)), '..\\data.db')

touch(path)

print(f"Writing data to {path}")
with sqlite3.connect(path) as conn:  # type: sqlite3.Connection
    try:
        if input("Delete existing sensor data table? (yes/NO): ").lower() == "yes":
            conn.execute("DROP TABLE sensor_data")

        conn.execute(r"""
        CREATE TABLE sensor_data (
            timestamp TIME      NOT NULL,
            value     INTEGER   NOT NULL
                                DEFAULT (0) 
                                CHECK (128 > value AND value > -128),
            node      TEXT      NOT NULL,
            sensor    TEXT      NOT NULL
        );""")
    except:
        # error means that the table already exists
        pass

    if input("Generate fake sensor data? (yes/NO): ").lower() == "yes":
        cur = conn.cursor()

        nodes = ["door", "box", "room"]
        sensors = ["imu", "lux", "contact", "pir"]

        for i in range(500):
            cur.execute(
                f"INSERT INTO sensor_data VALUES ({int(time.time()) - i * 1000}, {random.randint(-127, 127)}, '{random.choice(nodes)}', '{random.choice(sensors)}')")

    try:
        if input("Delete existing user table? (yes/NO): ").lower() == "yes":
            conn.execute("DROP TABLE users")

        conn.execute(r"""
        CREATE TABLE users (
            name     TEXT       NOT NULL
                                UNIQUE
                                PRIMARY KEY ASC,
            password BLOB (60)  NOT NULL
        );
        """)
    except:
        # error means that the table already exists
        pass

    if input("Generate fake user data? (yes/NO): ").lower() == "yes":
        import random
        import bcrypt

        pw = input("Password?: ").encode()

        for i in range(15):
            un = "".join(map(
                lambda _: random.choice("abcdefghijklmnopqrstuvwxyz0123456789"), 
                range(random.randint(7, 17))))
            conn.execute(f"INSERT INTO users VALUES ('{un}', ?)", [
                         bcrypt.hashpw(pw, bcrypt.gensalt())])
    
    try:
        if input("Delete existing threats table? (yes/NO): ").lower() == "yes":
            conn.execute("DROP TABLE threats")

        conn.execute(r"""
        CREATE TABLE threats (
            timestamp TIME    NOT NULL,
            node      TEXT,
            threat    TEXT,
            old_level INTEGER NOT NULL,
            new_level INTEGER NOT NULL
        );
        """)
    except:
        # error means that the table already exists
        pass
