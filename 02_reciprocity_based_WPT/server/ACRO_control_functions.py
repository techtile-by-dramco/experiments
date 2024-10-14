import numpy as np
import serial
import time
import zmq


context = zmq.Context()

iq_socket = context.socket(zmq.PUB)

iq_socket.bind(f"tcp://*:{50001}")


class ACRO:
    def __init__(self, COMport):
        # Establish serial connection
        self.ser = serial.Serial(
            COMport, baudrate=115200, timeout=1
        )  # Replace with the appropriate serial port

        # Wake up grbl
        self.ser.write(b"\r\n\r\n")
        time.sleep(2)  # Wait for grbl to initialize
        self.ser.flushInput()  # Flush startup text in serial input

    def wait_till_idle(self):
        response = ""
        while True:
            time.sleep(0.1)

            self.ser.flushInput()
            self.ser.write(b"?\n")
            response = self.ser.readline().decode().strip()
            print(response)

            if "Idle" in response:
                break

    def home_ACRO(self):
        # Send the query command
        self.ser.write(b"G54\n")
        self.ser.write(b"?\n")

        self.wait_till_idle()

        # Read and decode the response
        response = self.ser.readline().decode().strip()
        print("Controller response:", response)

        # Send homing command
        command = f"$H\n"  # Command to start homing
        self.ser.write(command.encode())
        self.wait_till_idle()  # Wait until controller reports idle state

        self.ser.write("G10 P0 L20 X0 Y0 Z0\n".encode())
        self.wait_till_idle()

        self.ser.write(b"G54\n")
        self.ser.write(b"?\n")

        self.wait_till_idle()

        print("Machine is homed")

    def move_ACRO(self, x, y, wait_idle=True):
        command = f"G0 X{x} Y{y}\n"  # Command to move to specific location
        self.ser.write(command.encode())  # Send command to move to a specific position
        if wait_idle:
            self.wait_till_idle()  # Wait until controller reports idle state

    def move_ACRO_to_origin(self):
        command = f"G0 X0 Y0\n"  # Command to move to specific location
        self.ser.write(command.encode())
        self.wait_till_idle()  # Wait until controller reports idle state

    def close_ACRO(self):
        self.ser.close()


def wait_till_go_from_server():

    global meas_id, file_open, data_file, file_name
    # Connect to the publisher's address
    print("Connecting to server %s.", "10.128.52.53")
    sync_socket = context.socket(zmq.SUB)

    alive_socket = context.socket(zmq.REQ)

    sync_socket.connect(f"tcp://10.128.52.53:{5557}")
    alive_socket.connect(f"tcp://10.128.52.53:{5558}")
    # Subscribe to topics
    sync_socket.subscribe("")

    print("Sending ALIVE")
    alive_socket.send_string("ROVER")
    # Receives a string format message
    print("Waiting on SYNC from server %s.", "10.128.52.53")

    meas_id, unique_id = sync_socket.recv_string().split(" ")

    print(meas_id)

    alive_socket.close()
    sync_socket.close()


if __name__ == "__main__":
    ACRO = ACRO(COMport="COM7")
    ACRO.home_ACRO()

    ACRO.move_ACRO(600 + 80, 600 - 40, wait_idle=True)

    x = np.arange(0, 1250, 300 / 4) + 10  # np.arange(25, 1200, 300/100) + 25
    y = np.arange(0, 1250, 300 / 4) + 10

    xx, yy = np.meshgrid(x, y)
    xx[1::2] = xx[
        1::2, ::-1
    ]  # flip the coordinates of x every other y to create a zig zag
    xx, yy = xx.ravel(), yy.ravel()

    while True:

        ACRO.move_ACRO(600 + 80, 600 - 40, wait_idle=True)
        wait_till_go_from_server()
        time.sleep(60)  # be sure that calibration is done

        for x, y in zip(xx, yy):
            ACRO.move_ACRO(x, y, wait_idle=True)
            time.sleep(0.1)

        xx = xx[::-1]  # alternate between starting at the beginning and end
        yy = yy[::-1]  # alternate between starting at the beginning and end

    # Return to origin
    ACRO.move_ACRO_to_origin()

    print("Done")
