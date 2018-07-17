import sqlite3
import os
from os.path import join, abspath, dirname


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


base_dir = dirname(dirname(abspath(__file__)))
path = join(base_dir, 'data.db')

touch(path)

print(f"Reading data from {path}")
with sqlite3.connect(path) as conn:  # type: sqlite3.Connection
    rows = conn.execute(f"SELECT * FROM threats ORDER BY timestamp DESC LIMIT 10")
    print("Last 10 rows from threat table: ")
    for row in rows:
        print(row)
