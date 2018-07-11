import socket
import _thread
import sqlite3
import sys

conn=sqlite3.connect('sensorsData.db')
curs=conn.cursor()

HOST = '192.168.4.1'
PORT = 8000

def add_data_door_imu (door_imu):
    curs.execute("INSERT INTO door_imu values(timestamp('now'), (?))", (door_imu))
    conn.commit()

def add_data_door_contact (door_contact):
    curs.execute("INSERT INTO door_contact values(timestamp('now'), (?))", (door_contact))
    conn.commit()

def add_data_box_accel (box_accel):
    curs.execute("INSERT INTO box_accel values(timestamp('now'), (?))", (box_accel))
    conn.commit()

def add_data_room_lux (room_lux):
    curs.execute("INSERT INTO room_lux values(timestamp('now'), (?))", (room_lux))
    conn.commit()

def add_data_room_pir (room_pir):
    curs.execute("INSERT INTO room_pir values(timestamp('now'), (?))", (room_pir))
    conn.commit()

# def connectionHandler(client, addr):
#     while True:
#         msg = client.recv(1024).decode()
#         if not msg:
#             break
#         print(msg)
#         add_data_door_imu(int(msg))
#         client.send(msg.encode())
#     client.close()


# s = socket.socket()

# print("Starting server...")
# print("Waiting for clients")

# s.bind((HOST, PORT))
# s.listen(1)

# while True:
#     c, addr = s.accept()
#     connectionHandler(c, addr)
# s.close()
