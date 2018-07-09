from flask import Flask, render_template, request
from flask_restful import Resource, Api

import sqlite3

def get_data_since(node, sensor, time, limit = 500):
	with sqlite3.connect('sensor-data.db') as conn:
		cur = conn.cursor()
		limit = min(500, limit)
		rows = list(cur.execute( \
			f"SELECT * FROM sensor_data WHERE " + \
			f"timestamp > {time} and node = '{node}' and sensor = '{sensor}' " + \
			f"ORDER BY timestamp DESC LIMIT {limit}"))
		return rows

def get_data(node, sensor, limit = 500):
	with sqlite3.connect('sensor-data.db') as conn:
		cur = conn.cursor()
		limit = min(500, limit)
		rows = list(cur.execute( \
			f"SELECT * FROM sensor_data WHERE " + \
			f"node = '{node}' and sensor = '{sensor}' " + \
			f"ORDER BY timestamp DESC LIMIT {limit}"))
		return rows

class Node(Resource):
	def get(self, node, sensor, time = None, limit = 1):
		if time:
			data = get_data_since(node, sensor, time, limit)
		else:
			data = get_data(node, sensor, limit)
		return list(map(lambda row: { "timestamp": row[0], "value": row[1] }, data))

# main route

def create_app():
	app = Flask(__name__)
	api = Api(app)
	api.add_resource(Node,
		"/api/<string:node>/<string:sensor>/",
		"/api/<string:node>/<string:sensor>/limit:<int:limit>",
		"/api/<string:node>/<string:sensor>/since:<int:time>")

	return app

app = create_app()

@app.route("/")
def index():
	return render_template("../client/dist/index.html")

if __name__ == "__main__":
	app.run(debug=True)

#    host='0.0.0.0', port=80, debug=False
