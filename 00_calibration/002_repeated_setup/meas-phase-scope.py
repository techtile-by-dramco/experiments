import time  # std module
import pyvisa as visa  # http://github.com/hgrecco/pyvisa
import numpy as np  # http://www.numpy.org/
from scipy.stats import circmean

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


# Define measurement number
meas_name = get_last_meas_name().strip()
print(f"Reading {meas_name}")


# Define channels (phase measurment)
channel_1 = "CH1"
channel_2 = "CH2"

# Update sources from last added measurement
scope.write(f"MEASUrement:{meas_name}:SOUrce1 {channel_1}")
scope.write(f"MEASUrement:{meas_name}:SOUrce2 {channel_2}")



meas_ongoing = False

meas_data = []

num_valid_in_meas = 0



while 1:

    res = scope.query(f"MEASUrement:{meas_name}:RESUlts:HISTory:MEAN?")

    res_valid = float(res) < 360.0

    # TODO ignore 1 shots

    if res_valid and not np.isnan(res_valid):
        print(".", end="", flush=True)
        meas_data.append(float(res))
        num_valid_in_meas += 1
        if not meas_ongoing:
            meas_ongoing = True

    if not res_valid and meas_ongoing:
        # stop previous measurements
        print()
        meas_ongoing = False
        if num_valid_in_meas > 10:
            # skip the last and first 5 meas
            print(np.rad2deg(circmean(np.deg2rad(meas_data[2:-2]))))
        meas_data = []
        num_valid_in_meas = 0
    
    time.sleep(0.5)

