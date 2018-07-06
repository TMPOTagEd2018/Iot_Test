from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
app = Flask(__name__)
import sqlite3

# Retrieve data from database
def getData():
	conn=sqlite3.connect('../sensorsData.db')
	curs=conn.cursor()

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

# main route 
@app.route("/")
def index():	
	timestamp, doorIMU, doorContact, boxAccel, boxContact, roomMic, roomLux, roomPIR = getData()
	templateData = {
		'timestamp': timestamp,
		'doorIMU': doorIMU,
		'doorContact': doorContact,
		'boxAccel': boxAccel,
		'boxContact': boxContact,
		'roomMic': roomMic,
		'roomLux': roomLux,
		'roomPIR': roomPIR,
	}
	return render_template('index.html', **templateData)
def create_app():
  app = Flask(__name__)
  Bootstrap(app)

  return app
if __name__ == "__main__":
   app.run()
#    host='0.0.0.0', port=80, debug=False