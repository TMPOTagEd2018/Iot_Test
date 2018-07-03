from flask import Flask, render_template, request
app = Flask(__name__)

import sqlite3

# Retrieve data from database
def getData():
	conn=sqlite3.connect('../sensorsData.db')
	curs=conn.cursor()

	for row in curs.execute("SELECT * FROM Door_data ORDER BY timestamp DESC LIMIT 1"):
		time = str(row[0])
		angv = row[1]
		lux = row[2]
	conn.close()
	return time, angv, lux

# main route 
@app.route("/")
def index():	
	time, angv, lux = getData()
	templateData = {
		'time': time,
		'angv': angv,
		'lux': lux
	}
	return render_template('index.html', **templateData)

if __name__ == "__main__":
   app.run()

#    host='0.0.0.0', port=80, debug=False