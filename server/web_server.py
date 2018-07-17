#!/usr/local/bin/python3.6

from flask import Flask
import flask_restful as rest

import struct
import os.path as path
import sqlite3

base_dir = path.dirname(__file__)

app = Flask(__name__, static_folder="../client/dist", static_url_path="")


@app.route('/')
def index():
    return app.send_static_file('index.html')


def get_sensor_data(node, sensor, since_time=None, limit=500):
    cache_folder = path.join(base_dir, f"cache/{node}")
    cache_file_name = path.join(cache_folder, sensor)

    if not path.exists(cache_file_name):
        return []

    POINTER_SIZE = 4
    RECORD_SIZE = 9
    RECORD_COUNT = 2400

    limit = min(RECORD_COUNT, limit)

    with open(cache_file_name, "rb") as cache_file:
        def read_records():
            # read position of ring buffer
            position = struct.unpack("L", cache_file.read(POINTER_SIZE))[0]

            start_position = (position - limit) % RECORD_COUNT
            cache_file.seek(POINTER_SIZE + start_position * RECORD_SIZE, 0)

            current_position = start_position
            while current_position != position:
                record_bytes = cache_file.read(RECORD_SIZE)
                if len(record_bytes) < RECORD_SIZE:
                    app.logger.warning(f"not enough bytes ({len(record_bytes)}) at {current_position}")
                    break

                current_position = current_position + 1
                if current_position >= RECORD_COUNT:
                    current_position = 0
                    cache_file.seek(POINTER_SIZE, 0)

                timestamp, value = struct.unpack("db", record_bytes)
                if timestamp == 0:
                    continue
                    
                yield {"timestamp": timestamp, "value": value}

        return list(reversed(list(read_records())))


def get_threat_data(node, threat, min_level=None, since_time=None, limit=500):
    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        limit = min(500, limit)

        conditions = []

        if node is not None and threat is not None:
            conditions.append(f"node = '{node}' and threat = '{threat}'")

        if since_time is not None:
            conditions.append(f"timestamp >= {since_time}")

        if min_level is not None:
            conditions.append(f"new_level >= {min_level}")

        where = ""

        if len(conditions) > 0:
            where = "WHERE " + " and ".join(conditions)

        query = f"SELECT * FROM threats {where} ORDER BY timestamp DESC LIMIT {limit}"

        rows = list(cur.execute(query))

        return rows


class Node(rest.Resource):
    def get(self, node, sensor, time=None, limit=1):
        return get_sensor_data(node, sensor, since_time=time, limit=limit)


class Threat(rest.Resource):
    def get(self, node=None, threat=None, min_level=None, time=None, limit=1):
        return list(
            map(lambda row: {
                "timestamp": row[0],
                "node": row[1],
                "threat": row[2],
                "old_level": row[3],
                "new_level": row[4]
            }, get_threat_data(node, threat, min_level=min_level, since_time=time, limit=limit)))


api = rest.Api(app)

api.add_resource(Node,
                    "/api/sensor/<string:node>/<string:sensor>/",
                    "/api/sensor/<string:node>/<string:sensor>/limit:<int:limit>",
                    "/api/sensor/<string:node>/<string:sensor>/since:<int:time>",
                    "/api/sensor/<string:node>/<string:sensor>/since:<int:time>/limit:<int:limit>")

api.add_resource(Threat,
                    "/api/threat/",
                    "/api/threat/limit:<int:limit>",
                    "/api/threat/since:<int:time>",
                    "/api/threat/since:<int:time>/limit:<int:limit>",
                    "/api/threat/minlevel:<int:min_level>/limit:<int:limit>",
                    "/api/threat/<string:node>/<string:threat>/",
                    "/api/threat/<string:node>/<string:threat>/limit:<int:limit>",
                    "/api/threat/<string:node>/<string:threat>/minlevel:<int:min_level>/",
                    "/api/threat/<string:node>/<string:threat>/minlevel:<int:min_level>/limit:<int:limit>",
                    "/api/threat/<string:node>/<string:threat>/since:<int:time>",
                    "/api/threat/<string:node>/<string:threat>/since:<int:time>/limit:<int:limit>",
                    "/api/threat/<string:node>/<string:threat>/since:<int:time>/minlevel:<int:min_level>/",
                    "/api/threat/<string:node>/<string:threat>/since:<int:time>/minlevel:<int:min_level>/limit:<int:limit>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context=("certs/http/cert.pem", "certs/http/key.pem"))

#    host='0.0.0.0', port=80, debug=False
