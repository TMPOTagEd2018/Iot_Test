from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_restful import Resource, Api

import sqlite3

conn = sqlite3.connect('../sensors-data.db')

# Retrieve data from database
def getData():
    curs = conn.cursor()

    for row in curs.execute("SELECT * FROM door_imu ORDER BY timestamp ASC LIMIT 1"):
        timestamp = str(row[0])
        doorIMU = row[1]
        
	for row in curs.execute("SELECT * FROM door_contact ORDER BY timestamp ASC LIMIT 1"):
        timestamp = str(row[0])	
		doorContact = row[1]

	for row in curs.execute("SELECT * FROM box_accel ORDER BY timestamp ASC LIMIT 1"):
        timestamp = str(row[0])
        boxAccel = row[1]
    for row in curs.execute("SELECT * FROM box_contact ORDER BY timestamp ASC LIMIT 1"):
        timestamp = str(row[0])
		boxContact = row[1]
	for row in curs.execute("SELECT * FROM room_mic ORDER BY timestamp ASC LIMIT 1"):
        timestamp = str(row[0])
        roomMic = row[1]
	for row in curs.execute("SELECT * FROM room_lux ORDER BY timestamp ASC LIMIT 1"):
        timestamp = str(row[0])	
        roomLux = row[1]
	for row in curs.execute("SELECT * FROM room_pir ORDER BY timestamp ASC LIMIT 1"):
        timestamp = str(row[0])
        roomPIR = row[1]
    conn.close()
    return timestamp, doorIMU, doorContact, boxAccel, boxContact, roomMic, roomLux, roomPIR

def get_latest_data(node, sensor):
	table = node + "_" * sensor
	for row in curs.execute("SELECT * FROM table ORDER BY timestamp ASC LIMIT 1"):
		print (str(row[0])+ str(row[1])) 

class Node(Resource):
	def __init__(self, node):
		super().__init__()
		self.node = node

	def get(self, sensor):
		get_latest_data(self.node, sensor)

# main route

@app.route("/")
def index():
    return render_template("../client/dist/index.html")


def create_app():
    app = Flask(__name__)
	api = Api(app)
	api.add_resource(Node("door"))
	api.add_resource(Node("box"))
	api.add_resource(Node("room"))

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

#    host='0.0.0.0', port=80, debug=False
