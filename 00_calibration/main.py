import zmq
import numpy as np
import sys
from io import BytesIO


context = zmq.Context()
socket = context.socket(zmq.PULL)
#socket.RCVTIMEO = 20*1000  # in milliseconds
socket.connect("tcp://127.0.0.1:5555")

rct_default = socket.RCVTIMEO


phase_socket = context.socket(zmq.REP)
phase_socket.bind("tcp://*:5000")

arr_in = []
arr_out = []

first = True
i = 0


def round_to_nearest_pi_over_4(x):
    # Convert x from radians to degrees
    degrees = np.degrees(x)
    # Calculate the nearest multiple of 45 degrees in degrees
    nearest_degree_multiple = round(degrees / 45) * 45
    # Convert it back to radians
    rounded_x = np.radians(nearest_degree_multiple)
    return rounded_x


while True:
    try:
        i += 1
        buff = BytesIO()
        print(f"[{i}] ----------------------------------")
        print("Listening for IQ samples")
        socket.RCVTIMEO = rct_default
        while True:
            try:
                message = socket.recv()
            except zmq.error.Again as _e:
                break
            buff.write(message)
            print(".", end=" ")
            sys.stdout.flush()
            socket.RCVTIMEO = 1000

        print("Done RX'en")

        dt = np.dtype([('re', np.int16), ('im', np.int16)])

        buff.seek(0)
        a = np.frombuffer(buff.read(), dtype=dt)

        b = np.zeros(len(a), dtype=np.complex64)
        b[:].real = a['re']/(2**15)
        b[:].imag = a['im']/(2**15)

        sample_rate = int(250e3)
        dt = 1/sample_rate

        print(f"{len(b)/sample_rate:0.2f}s recorded")

        # remove 1 sample at the beginning and end
        #b = b[sample_rate//100:-sample_rate//100]

        phase_rad = np.angle(np.mean(b))

        if first:
            arr_in.append(phase_rad)
        else:
            arr_out.append(phase_rad)

        first = not first

        # angles = np.angle(b)
        # phase_rad = np.mod(angles + 2 * np.pi, 2*np.pi)
        phase = np.rad2deg(phase_rad)

        # std = np.std(phase)
        # avg = np.mean(phase)

        # print(f"std: {std:0.2f}°")
        print(f"mean: {phase:0.2f}°")
        print(f"mean amplitude: {np.abs(np.mean(b)):0.2f}")

        print("Listening for incoming messages.")
        msg = phase_socket.recv()
        sys.stdout.flush()
        phase_socket.send_string(str(phase_rad))
        msg = phase_socket.recv()
        phase_socket.send_string(str(round_to_nearest_pi_over_4(phase_rad)))
        print("----------------------------------")
        np.save(f"IQ-{i:2d}.npy", b)
        print("")
        print("")
        print("")
        print("")
    except KeyboardInterrupt:
        sys.exit()
