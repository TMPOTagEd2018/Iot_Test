import sqlite3
import sys
conn=sqlite3.connect('sensorsData.db')
curs=conn.cursor()

# function to insert data on a table
def add_data (doorIMU, doorContact, boxAccel, boxContact, roomMic, roomLux, roomPIR):
    curs.execute("INSERT INTO incomingData values(timestamp('now'), (?), (?), (?), (?), (?), (?), (?))", (doorIMU, doorContact, boxAccel, boxContact, roomMic, roomLux, roomPIR))
    conn.commit()

# call the function to insert data
# add_data (40, 10)

# print database content
print ("\nEntire database contents:\n")
for row in curs.execute("SELECT * FROM incomingData"):
    print (row)

# close the database after use
conn.close()
