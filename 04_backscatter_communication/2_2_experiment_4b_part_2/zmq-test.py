import zmq
import json
import time



# Create a ZeroMQ context
context = zmq.Context()

# Create a ZeroMQ PUSH socket
socket = context.socket(zmq.PUB)
socket.bind("tcp://0.0.0.0:5555")  # Bind to local address and port

status_now = 'capture_bs_start'

while 1:

    file_timestamp = round(time.time())

    if status_now == 'capture_bs_start':
        status_now = 'capture_bs_stop'
    else:
        status_now = 'capture_bs_start'

    data = dict(name=file_timestamp,
                status=status_now,
                )

    print(data)

    # Send JSON data over the socket
    socket.send_string(json.dumps(data))

    time.sleep(1)


# Close the socket and ZeroMQ context
socket.close()
context.term()