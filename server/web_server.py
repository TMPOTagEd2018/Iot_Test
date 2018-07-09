from flask import Flask, render_template, request
from flask_restful import Resource, Api

import sqlite3



'''
# Retrieve data from database
def getData():
	curs = conn.cursor()
	data = []
	names = ["door_imu", "door_contact", "box_accel",
		"box_contact", "room_mic", "room_lux", "room_pir"]

	for name in names:
		for row in curs.execute("SELECT * FROM " + name + " ORDER BY timestamp ASC LIMIT 1"):
			timestamp = str(row[0])
			data.append(row[1])


	conn.close()
	return timestamp, doorIMU, doorContact, boxAccel, boxContact, roomMic, roomLux, roomPIR
'''


def get_latest_data(node, sensor):
	with sqlite3.connect('sensors-data.db') as conn:
		cur = conn.cursor()
		table = node + "_" + sensor
		for row in cur.execute("SELECT * FROM " + table + " ORDER BY timestamp ASC LIMIT 1"):
			return str(row[0]), str(row[1])


class Node(Resource):
	def get(self, node, sensor):
		get_latest_data(node, sensor)

# main route

def create_app():
	app = Flask(__name__)
	api = Api(app)
	api.add_resource(Node, "/<string:node>/<string:sensor>/")

	return app

app = create_app()

@app.route("/")
def index():
	return render_template("../client/dist/index.html")

if __name__ == "__main__":
	app.run(debug=True)

#    host='0.0.0.0', port=80, debug=False
