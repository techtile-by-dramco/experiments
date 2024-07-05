import zmq

# Create a ZeroMQ context
context = zmq.Context()

# Create a SUB (subscribe) socket
sub_socket = context.socket(zmq.SUB)
sub_socket.connect("tcp://192.108.0.204:5555")

# Subscribe to all topics
sub_socket.subscribe(b'')

# Create a poller object
poller = zmq.Poller()
poller.register(sub_socket, zmq.POLLIN)

try:
    while True:
        # Wait for events on the socket(s) for up to 1000 milliseconds (1 second)
        events = dict(poller.poll(1000))  # Timeout set to 1000 milliseconds

        if sub_socket in events:
            # Receive message
            message = sub_socket.recv_string()
            print(f"Received message: {message}")
        
        # Add more sockets to poll here if needed

except KeyboardInterrupt:
    print("Polling interrupted. Exiting...")
finally:
    sub_socket.close()
    context.term()