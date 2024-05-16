#!/usr/bin/python3

import zmq
import time
import sys

if len(sys.argv) > 1:
    delay = int(sys.argv[1])
else:
    delay = 10

host = "*"
port = "5557"

# Creates a socket instance
context = zmq.Context()

start_socket = context.socket(zmq.PUB)
# Binds the socket to a predefined port on localhost
start_socket.bind("tcp://{}:{}".format(host, port))

while 1:

    try:
        input(f"Press Enter to send 'SYNC' message with delay {delay}s...")
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit()

    time.sleep(delay)

    try:
        start_socket.send_string("SYNC")
        print("SYNC")
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit()
