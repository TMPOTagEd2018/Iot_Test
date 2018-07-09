import sqlite3
from os.path import join, realpath, dirname

path = join(dirname(realpath(__file__)), '..\\sensor-data.db')
print(f"Writing data to {path}")
conn = sqlite3.connect(path)
cur = conn.cursor()
