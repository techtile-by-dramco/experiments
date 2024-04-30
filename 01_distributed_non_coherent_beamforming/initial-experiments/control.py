import sys
import zmq

context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.bind("tcp://0.0.0.0:5555")

commands = ["START", "STOP", "change gain <int>"]

while True:
    print("-----------------------------------")
    print("List of commands:")
    for command in commands:
        print(command)
    print("-----------------------------------")
    user_input = input("Enter a command: ")
    print(user_input)
    pub_socket.send_string(user_input)