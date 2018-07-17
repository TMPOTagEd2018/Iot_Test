import sqlite3
import os
import time
import random
from os.path import join, realpath, dirname


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


path = join(dirname(realpath(__file__)), '..\\data.db')

touch(path)

print(f"Writing data to {path}")
with sqlite3.connect(path) as conn:  # type: sqlite3.Connection

    if input("Generate fake user data? (yes/NO): ").lower() == "yes":
        import bcrypt

        pw = input("Password?: ").encode()

        for i in range(15):
            un = "".join(map(
                lambda _: random.choice(
                    "abcdefghijklmnopqrstuvwxyz0123456789"),
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
            old_level NUMERIC NOT NULL,
            new_level NUMERIC NOT NULL
        );
        """)
        print("Threats table created.")

    except sqlite3.OperationalError:
        print("Threats table already existed.")
        # error means that the table already exists
        pass

    if input("Generate fake threat data? (yes/NO): ").lower() == "yes":
        for i in range(20):
            conn.execute(
                f"INSERT INTO threats VALUES ({time.time()}, null, null, {random.randint(0, 10)}, {random.randint(0, 10)})")
