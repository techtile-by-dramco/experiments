#!/usr/bin/python3
# usage: sync_server.py <delay> <num_subscribers>

import zmq
import time
import sys
import numpy as np
import os
from datetime import datetime

import csv


if len(sys.argv) > 1:
    delay = int(sys.argv[1])
    num_subscribers = int(sys.argv[2])
else:
    delay = 10
    num_subscribers = 2

host = "*"
sync_port = "5557"
alive_port = "5558"
data_port = "5559"


# Creates a socket instance
context = zmq.Context()

sync_socket = context.socket(zmq.PUB)
# Binds the socket to a predefined port on localhost
sync_socket.bind("tcp://{}:{}".format(host, sync_port))

# Create a SUB socket to listen for subscribers
alive_socket = context.socket(zmq.REP)
alive_socket.bind("tcp://{}:{}".format(host, alive_port))


# Create a SUB socket to listen for subscribers
data_socket = context.socket(zmq.REP)
data_socket.bind("tcp://{}:{}".format(host, data_port))


meas_id = 0
unique_id = str(datetime.utcnow().strftime("%Y%m%d%H%M%S"))

script_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))


poller = zmq.Poller()
poller.register(alive_socket, zmq.POLLIN)

new_msg_received = 0
WAIT_TIMEOUT = 60.0*10.0

print(f"Starting experiment: {unique_id}")
output_path = f"../data/exp-{unique_id}.yml"
with open(output_path, "w") as f:
    f.write(f"experiment: {unique_id}\n")
    f.write(f"num_subscribers: {num_subscribers}\n")
    f.write(f"measurments:\n")

    while True:
        # Wait for specified number of subscribers to send a message
        print(f"Waiting for {num_subscribers} subscribers to send a message...")
        f.write(f"  - meas_id: {meas_id}\n")
        f.write("    active_tiles:\n")
        messages_received = 0
        start_processing = None
        while messages_received < num_subscribers:
            socks = dict(poller.poll(1000))  # Poll with a timeout of 100 ms
            if messages_received > 2 and time.time() - new_msg_received > WAIT_TIMEOUT:
                break

            if alive_socket in socks and socks[alive_socket] == zmq.POLLIN:
                new_msg_received = time.time()
                message = alive_socket.recv_string()
                messages_received += 1
                print(f"{message} ({messages_received}/{num_subscribers})")
                f.write(f"     - {message}\n")
                # Process the request (for example, you could perform some computation here)
                response = "Response from server"

                # Send the response back to the client
                alive_socket.send_string(response)

        print(f"sending 'SYNC' message in {delay}s...")
        f.flush()
        time.sleep(delay)

        meas_id = meas_id + 1
        sync_socket.send_string(f"{meas_id} {unique_id}")  # str(meas_id)
        print(f"SYNC {meas_id}")
        # storing this
