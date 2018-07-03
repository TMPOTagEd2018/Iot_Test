import sqlite3
conn=sqlite3.connect('sensorsData.db')
curs=conn.cursor()

print ("\nLast raw Data logged on database:\n")
for row in curs.execute("SELECT * FROM Door_data ORDER BY timestamp DESC LIMIT 1"):
    print (str(row[0])+" ==> GYRO = "+str(row[1])+"	LUX ="+str(row[2]))
