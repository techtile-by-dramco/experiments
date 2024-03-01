#!/usr/bin/python3

# simple_pub.py
import zmq
import time
from datetime import datetime, timezone


host = "*"
port = "5557"

# Creates a socket instance
context = zmq.Context()


start_socket = context.socket(zmq.PUB)
# Binds the socket to a predefined port on localhost
start_socket.bind("tcp://{}:{}".format(host, port))

time.sleep(10)

start_socket.send_string("SYNC")
print("SYNC")

