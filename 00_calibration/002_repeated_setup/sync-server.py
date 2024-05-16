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
port = "5557"

# Creates a socket instance
context = zmq.Context()

start_socket = context.socket(zmq.PUB)
# Binds the socket to a predefined port on localhost
start_socket.bind("tcp://{}:{}".format(host, port))

# Create a SUB socket to listen for subscribers
subscriber_socket = context.socket(zmq.SUB)
subscriber_socket.bind("tcp://{}:{}".format(host, port + "1"))

# Set socket options to subscribe to all topics
subscriber_socket.setsockopt_string(zmq.SUBSCRIBE, '')

# Create a poller to listen for incoming messages from subscribers
poller = zmq.Poller()
poller.register(subscriber_socket, zmq.POLLIN)

while True:

    # Wait for specified number of subscribers to send a message
    print(f"Waiting for {num_subscribers} subscribers to send a message...")
    messages_received = 0
    while messages_received < num_subscribers:
        socks = dict(poller.poll())
        if subscriber_socket in socks and socks[subscriber_socket] == zmq.POLLIN:
            subscriber_socket.recv()
            print("Subscriber sent a message.")
            messages_received += 1

    print("Press Enter to send 'SYNC' message...")
    try:
        input()
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
