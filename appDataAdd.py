import sqlite3
import sys
conn=sqlite3.connect('sensorsData.db')
curs=conn.cursor()

# function to insert data on a table
def add_data (doorIMU, doorContact, boxAccel, boxContact, roomMic, roomLux, roomPIR):
    curs.execute("INSERT INTO incomingData values(datetime('now'), (?), (?), (?), (?), (?), (?), (?))", (doorIMU, doorContact, boxAccel, boxContact, roomMic, roomLux, roomPIR))
    conn.commit()

# call the function to insert data
add_data (20.5, 30, 10, 10, 10, 10, 10)
add_data (25.8, 40, 10, 10, 10, 10, 10)
add_data (30.3, 50, 10, 10, 10, 10, 10)

# print database content
print ("\nEntire database contents:\n")
for row in curs.execute("SELECT * FROM incomingData"):
    print (row)

# close the database after use
conn.close()
