import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://192.108.0.15:5555")
socket.setsockopt_string(zmq.SUBSCRIBE, "")

while True:
    # Receive the reply from the server for the first request
    message = socket.recv_string()
    print(f"Received reply from server: {message}")
