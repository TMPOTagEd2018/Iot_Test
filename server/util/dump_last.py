import sqlite3
conn=sqlite3.connect('sensorsData.db')
curs=conn.cursor()

print ("\nLast raw Data logged on database:\n")
for row in curs.execute("SELECT * FROM incomingData ORDER BY timestamp ASC LIMIT 1"):
    print (str(row[0])+ " doorIMU ==> "+str(row[1])+" doorContact ==>"+str(row[2])+"boxAccel ==>"+str(row[3])+" boxContact ==>"+str(row[4])+" roomMic ==>"+str(row[5])+" roomLux ==>"+str(row[6])+" roomPIR ==>"+str(row[7]))