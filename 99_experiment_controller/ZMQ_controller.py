import zmq

def main():
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind("tcp://*:5558")

    while True:
        # Read user input
        user_input = input("Enter 'init', 'start', 'stop', or 'close' to stop the server: ").strip().lower()

        # Check if input is valid
        if user_input not in ["init", "start", "stop", "close"]:
            print("Invalid input. Please enter 'start', 'stop', or 'close'.")
            continue

        # Publish the input on the "phase" topic
        publisher.send_multipart([b"phase", user_input.encode()])
        print(user_input.encode())

        # If user input is 'close', break out of the loop and stop the server
        if user_input == "close":
            break

    # Close the socket and context when done
    publisher.close()
    context.term()

if __name__ == "__main__":
    main()
