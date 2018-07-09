from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_restful import Resource, Api

import sqlite3

conn = sqlite3.connect('../sensorsData.db')

# Retrieve data from database
def getData():
    curs = conn.cursor()

    for row in curs.execute("SELECT * FROM incomingData ORDER BY timestamp ASC LIMIT 1"):
        timestamp = str(row[0])
        doorIMU = row[1]
        doorContact = row[2]
        boxAccel = row[3]
        boxContact = row[4]
        roomMic = row[5]
        roomLux = row[6]
        roomPIR = row[7]
    conn.close()
    return timestamp, doorIMU, doorContact, boxAccel, boxContact, roomMic, roomLux, roomPIR

def get_latest_data(node, sensor):
	# TODO: Grace please make this function query the db for a given node and sensor

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
