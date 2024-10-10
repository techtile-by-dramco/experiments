import numpy as np
import serial
import time


class ACRO():
    def __init__(self, COMport):
        # Establish serial connection
        self.ser = serial.Serial(COMport, baudrate=115200, timeout=1)  # Replace with the appropriate serial port

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
        self.wait_till_idle()        # Wait until controller reports idle state

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

if __name__ == '__main__':
    ACRO = ACRO(COMport='COM6')
    ACRO.home_ACRO()

    ACRO.move_ACRO(600, 600, wait_idle=True)

    input('Press to start moving')

    x = np.arange(25, 1200, 300/100) + 25
    y = np.arange(25, 1200, 300/100) + 25

    xx, yy = np.meshgrid(x, y)
    xx[1::2] = xx[1::2,::-1] # flip the coordinates of x every other y to create a zig zag
    xx, yy = xx.ravel(), yy.ravel()

    for x, y in zip(xx, yy):
        ACRO.move_ACRO(x, y, wait_idle=True)
        time.sleep(0.2)
        #TODO: Perform measurement

    # Return to origin
    ACRO.move_ACRO_to_origin()

    print("Done")