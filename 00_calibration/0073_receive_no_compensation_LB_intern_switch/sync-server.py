#!/usr/bin/python3
# usage: sync_server.py <delay> <num_subscribers>

# simple_pub.py
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

MEAS_TYPE_LOOPBACK = "LB"
MEAS_TYPE_PLL = "PLL"
MEAS_TYPE_LOOPBACK_CHECK = "LBCK"
MEAS_TYPE_PLL_CHECK = "PLLCK"
MEAS_TYPE_PHASE_DIFF = "PDIFF"

SCOPE = "SCOPE"

NUM_VALUES = 5


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


def parse_data(data_str):
    print(data_str)
    # format
    # TILE ; MEAS_TYPE ; TX_ANGLE_CH0 ; TX_ANGLE_CH1 ; RX_ANGLE_CH0 ; RX_ANGLE_CH1 ; RX_AMPL_CH0 ; RX_AMPL_CH1 ; PHASE_DIFF
    vals = data_str.split(";")

    if vals[0] == SCOPE:
        # only transmits the phase difference
        return [SCOPE, MEAS_TYPE_PHASE_DIFF, -1, -1, -1, -1, -1, -1, float(vals[1])]
    else:
        return vals + [-1] # append the pase diff value


meas_id = 0
unique_id = str(datetime.utcnow().strftime("%Y%m%d%H%M%S"))

script_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))


# Get current UTC timestamp
# timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")

# file_path = os.path.join(script_dir, f"data_{timestamp}.csv")

# print(f"Saving to {file_path}")


# TILE ; MEAS_TYPE ; TX_ANGLE_CH0 ; TX_ANGLE_CH1 ; RX_ANGLE_CH0 ; RX_ANGLE_CH1 ; RX_AMPL_CH0 ; RX_AMPL_CH1
fields = ["meas_id", "tile", "meas_type", "tx_angle_ch0"
          "tx_angle_ch1",
          "rx_angle_ch0",
          "rx_angle_ch1",
          "rx_ampl_ch0",
          "rx_ampl_ch1", "phase_diff"]

poller = zmq.Poller()
poller.register(alive_socket, zmq.POLLIN)

# # with open(file_path, 'w') as file:
#     csvwriter = csv.writer(file)

#     csvwriter.writerow(fields)
# try:
print(f"Starting experiment: {unique_id}")
while True:
        # Wait for specified number of subscribers to send a message
        print(
            f"Waiting for {num_subscribers} subscribers to send a message...")
        messages_received = 0
        while messages_received < num_subscribers:
            socks = dict(poller.poll(1000))  # Poll with a timeout of 100 ms
            if alive_socket in socks and socks[alive_socket] == zmq.POLLIN:
                message = alive_socket.recv_string()
                print("Received message:", message)
                messages_received += 1
                # Process the request (for example, you could perform some computation here)
                response = "Response from server"

                # Send the response back to the client
                alive_socket.send_string(response)
          
        print(f"sending 'SYNC' message in {delay}s...")
        time.sleep(delay)

        meas_id = meas_id+1
        sync_socket.send_string(f"{meas_id} {unique_id}")  # str(meas_id)
        print(f"SYNC {meas_id}")
            
                # collect the data from the subscribers and the scope
                # each rpi transmits 4 measurements per meas
                # for _ in range(num_subscribers*4):
                #     print("waiting for data...",end="")
                #     data_str = data_socket.recv_string()
                #     print("done.")
                #     data = parse_data(data_str)

                #     row = [meas_id] + data

                #     print(row)

                #     csvwriter.writerow(row)
                # file.flush()
# except KeyboardInterrupt:
#     print("Exiting...")
#     sys.exit()
# finally:
#     context.term()
#     data_socket.close()
#     alive_socket.close()
#     sync_socket.close()
