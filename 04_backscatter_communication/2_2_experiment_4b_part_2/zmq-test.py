import zmq
import json
import time



# Create a ZeroMQ context
context = zmq.Context()

# Create a ZeroMQ PUSH socket
socket = context.socket(zmq.PUB)
socket.bind("tcp://0.0.0.0:5555")  # Bind to local address and port

while 1:

    file_timestamp = round(time.time())

    data = dict(name=file_timestamp)

    print(file_timestamp)

    # Send JSON data over the socket
    socket.send_string(json.dumps(data))

    time.sleep(1)


# Close the socket and ZeroMQ context
socket.close()
context.term()