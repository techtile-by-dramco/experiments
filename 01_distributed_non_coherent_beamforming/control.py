import sys
import zmq

context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.bind("tcp://0.0.0.0:5555")

while True:
    user_input = input("Enter a string: ")
    print(user_input)
    pub_socket.send_string(user_input)