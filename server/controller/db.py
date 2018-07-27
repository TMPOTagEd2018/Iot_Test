# Data
import sqlite3
import struct

# I/O
import os.path as path
import os

# Async
import queue
import threading

import time

base_path = None
threat_level_queue = queue.Queue()


def threat_level_writer(q: queue.Queue):
    conn: sqlite3.Connection = sqlite3.connect(db_path)

    last_write = time.time()
    records = []
    last_record = None
    while True:
        try:
            timestamp, level = q.get(timeout=10)

            record = (timestamp, 0 if last_record is None else last_record[2], level)
            records.append(record)
            last_record = record
        except queue.Empty:
            pass

        if time.time() - last_write > 10:
            conn.executemany("INSERT INTO threats(timestamp, old_level, new_level) VALUES (?, ?, ?)", records)
            conn.commit()
            records.clear()
            last_write = time.time()


def init(base_dir: str):
    global conn
    global base_path
    global db_path

    base_path = base_dir
    db_path = path.join(base_path, "data.db")

    print(f"DB path: {db_path}")

    threat_level_daemon = threading.Thread(target=threat_level_writer, args=(threat_level_queue, ))
    threat_level_daemon.daemon = True
    threat_level_daemon.start()


def write_threat(level: float):
    timestamp = time.time()
    threat_level_queue.put((timestamp, level))
    cache_file_name = path.join(base_path, "cache/threat")

    POINTER_SIZE = 4
    RECORD_SIZE = 12
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

        file_position = POINTER_SIZE + position * RECORD_SIZE

        cache_file.seek(file_position, 0)
        cache_file.write(struct.pack("<df", timestamp, level))

        position = (position + 1) % RECORD_COUNT
        position_bytes = struct.pack("<L", position)

        cache_file.seek(0, 0)
        cache_file.write(position_bytes)
        cache_file.flush()


def write_heartbeat(node_name: str):
    cache_folder = path.join(base_path, f"cache/{node_name}")

    if not path.exists(cache_folder):
        os.makedirs(cache_folder)

    cache_file_name = path.join(cache_folder, "heartbeat")

    with open(cache_file_name, "w+") as cache_file:
        cache_file.write(str(time.time()))


def write_cache(node_name: str, sensor_name: str, value: float):
    cache_folder = path.join(base_path, f"cache/{node_name}")

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
