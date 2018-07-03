import sqlite3
import sys
conn=sqlite3.connect('sensorsData.db')
curs=conn.cursor()

# function to insert data on a table
def add_data (angv, lux):
    curs.execute("INSERT INTO Door_data values(datetime('now'), (?), (?))", (angv,lux))
    conn.commit()

# call the function to insert data
# add_data (40, 10)

# print database content
print ("\nEntire database contents:\n")
for row in curs.execute("SELECT * FROM Door_data"):
    print (row)

# close the database after use
conn.close()
