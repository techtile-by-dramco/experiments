import time  # std module
import pyvisa as visa  # http://github.com/hgrecco/pyvisa
import numpy as np  # http://www.numpy.org/
from scipy.stats import circmean
import zmq

from enum import Enum

ip = "192.108.0.251"

rm = visa.ResourceManager()
scope = rm.open_resource(f'TCPIP::{ip}::4000::SOCKET', write_termination='\n', read_termination='\n')
scope.timeout = None # to ensure no error when waiting for query results
print(scope.query('*IDN?'))


def get_last_meas_name() -> str:
    return scope.query("MEASUrement:LIST?").replace('\n', '').split(',')[-1]

# Add new measurement phase
scope.write("MEASUREMENT:ADDMEAS PHASE")

meas = [None, None, None]


# Define measurement number
meas_name = get_last_meas_name().strip()
print(f"Reading {meas_name}")

meas[0] = meas_name


# Define channels (phase measurment)
channel_1 = "CH3"
channel_2 = "CH4"
channel_3 = "CH1"

# Update sources from last added measurement
scope.write(f"MEASUrement:{meas_name}:SOUrce1 {channel_1}")
scope.write(f"MEASUrement:{meas_name}:SOUrce2 {channel_2}")

# Add new measurement phase
scope.write("MEASUREMENT:ADDMEAS PHASE")


# Define measurement number
meas_name = get_last_meas_name().strip()
print(f"Reading {meas_name}")
meas[1] = meas_name


# Define channels (phase measurment)
channel_1 = "CH1"
channel_2 = "CH2"
channel_3 = "CH3"

# Update sources from last added measurement
scope.write(f"MEASUrement:{meas_name}:SOUrce1 {channel_1}")
scope.write(f"MEASUrement:{meas_name}:SOUrce2 {channel_3}")

# Add new measurement phase
scope.write("MEASUREMENT:ADDMEAS PHASE")


# Define measurement number
meas_name = get_last_meas_name().strip()
print(f"Reading {meas_name}")
meas[2] = meas_name


# Define channels (phase measurment)
channel_1 = "CH1"
channel_2 = "CH2"
channel_3 = "CH3"

# Update sources from last added measurement
scope.write(f"MEASUrement:{meas_name}:SOUrce1 {channel_2}")
scope.write(f"MEASUrement:{meas_name}:SOUrce2 {channel_3}")



meas_ongoing = False

meas_data = []

meas_data1 = []
meas_data2 = []

num_valid_in_meas = 0

context = zmq.Context()
sync_socket = context.socket(zmq.SUB)
sync_socket.connect(f"tcp://10.128.52.53:{5557}")
sync_socket.subscribe("")

# Create a poller
poller = zmq.Poller()
poller.register(sync_socket, zmq.POLLIN)


file_open = False

meas_id = 0

while 1:

    # Poll the socket with a timeout of 1 second (100 ms)
    socks = dict(poller.poll(100))

    if sync_socket in socks and socks[sync_socket] == zmq.POLLIN:
        # Message is available
        meas_id, unique_id = sync_socket.recv_string().split(" ")

        if not file_open:
            file = open(f"data_scope_{unique_id}.txt", "a")
            file_open = True
        print("Received message:", meas_id)

    res = scope.query(f"MEASUrement:{meas[0]}:RESUlts:HISTory:MEAN?")

    res1 = scope.query(f"MEASUrement:{meas[1]}:RESUlts:HISTory:MEAN?")
    res2 = scope.query(f"MEASUrement:{meas[2]}:RESUlts:HISTory:MEAN?")

    res_valid = float(res) < 360.0

    if res_valid and not np.isnan(res_valid):
        print(".", end="", flush=True)
        meas_data.append(float(res))
        meas_data1.append(float(res1))
        meas_data2.append(float(res2))
        num_valid_in_meas += 1
        if not meas_ongoing:
            meas_ongoing = True

    if not res_valid and meas_ongoing:
        # stop previous measurements
        print()
        meas_ongoing = False
        if num_valid_in_meas > 10:
            # skip the last and first 5 meas
            file.write(
                f"{meas_id} {np.rad2deg(circmean(np.deg2rad(meas_data[2:-2])))} {np.rad2deg(circmean(np.deg2rad(meas_data1[2:-2])))} {np.rad2deg(circmean(np.deg2rad(meas_data2[2:-2])))}\n")
            file.flush()
            print(f"{meas_id} {np.rad2deg(circmean(np.deg2rad(meas_data[2:-2])))} {np.rad2deg(circmean(np.deg2rad(meas_data1[2:-2])))} {np.rad2deg(circmean(np.deg2rad(meas_data2[2:-2])))}\n")
        meas_data = []
        meas_data1 = [] 
        meas_data2 = []
        num_valid_in_meas = 0
    
    time.sleep(0.5)

