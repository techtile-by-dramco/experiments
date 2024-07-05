import zmq

def subscriber():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://192.108.0.204:5558")
    
    topic_filter = "phase"
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    
    while True:
        message = socket.recv_string()
        print(f"Received: {message}")

if __name__ == "__main__":
    subscriber()