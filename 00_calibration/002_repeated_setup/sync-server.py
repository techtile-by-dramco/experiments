#!/usr/bin/python3
# usage: sync_server.py <delay> <num_subscribers>

# simple_pub.py
import zmq
import time
import sys

if len(sys.argv) > 1:
    delay = int(sys.argv[1])
    num_subscribers = int(sys.argv[2])
else:
    delay = 10
    num_subscribers = 2

host = "*"
sync_port = "5557"
alive_port = "5558"

# Creates a socket instance
context = zmq.Context()

sync_socket = context.socket(zmq.PUB)
# Binds the socket to a predefined port on localhost
sync_socket.bind("tcp://{}:{}".format(host, sync_port))

# Create a SUB socket to listen for subscribers
alive_socket = context.socket(zmq.REP)
alive_socket.bind("tcp://{}:{}".format(host, alive_port))

while True:

    # Wait for specified number of subscribers to send a message
    print(f"Waiting for {num_subscribers} subscribers to send a message...")
    messages_received = 0
    while messages_received < num_subscribers:
        message = alive_socket.recv_string()
        print("Received request:", message)

        # Process the request (for example, you could perform some computation here)
        response = "Response from server"

        # Send the response back to the client
        alive_socket.send_string(response)

        messages_received += 1

    print("Press Enter to send 'SYNC' message...")
    try:
        input()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit()

    time.sleep(delay)

    try:
        sync_socket.send_string("SYNC")
        print("SYNC")
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit()
