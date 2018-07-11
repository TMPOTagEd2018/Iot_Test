import sqlite3
conn=sqlite3.connect('sensorsData.db')
curs=conn.cursor()

print ("\nLast raw Data logged on database:\n")
for row in curs.execute("SELECT * FROM sensor_data ORDER BY timestamp ASC LIMIT 1"):
    print (str(row[0])+ " value : "+str(row[1])+ " node : "+str(row[2])+ " sensor : "+str(row[3]))

