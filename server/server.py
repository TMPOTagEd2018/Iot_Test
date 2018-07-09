import socket
import _thread
import sqlite3
import sys

conn=sqlite3.connect('sensorsData.db')
curs=conn.cursor()

HOST = '192.168.4.1'
PORT = 8000

def add_data (doorIMU, doorContact, boxAccel, boxContact, roomMic, roomLux, roomPIR):
    curs.execute("INSERT INTO incomingData values(timestamp('now'), (?), (?), (?), (?), (?), (?), (?))", (doorIMU, doorContact, boxAccel, boxContact, roomMic, roomLux, roomPIR))
    conn.commit()

def connectionHandler(client, addr):
    while True:
        msg = client.recv(1024).decode()
        if not msg:
            break
        print(msg)
        add_data(int(msg), 10, 10, 10, 10, 10, 10)
        client.send(msg.encode())
    client.close()


s = socket.socket()

print("Starting server...")
print("Waiting for clients")

s.bind((HOST, PORT))
s.listen(1)

while True:
    c, addr = s.accept()
    connectionHandler(c, addr)
s.close()