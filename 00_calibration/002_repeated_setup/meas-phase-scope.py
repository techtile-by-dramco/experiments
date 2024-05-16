import time  # std module
import pyvisa as visa  # http://github.com/hgrecco/pyvisa
import numpy as np  # http://www.numpy.org/
from scipy.signal import find_peaks

from enum import Enum

ip = "192.108.0.251"

rm = visa.ResourceManager()
scope = rm.open_resource(f'TCPIP::{ip}::INSTR')

# Add new measurement phase
scope.write("MEASUREMENT:ADDMEAS PHASE")

# Query list of measurements
meas_list = scope.query("MEASUrement:LIST?")
meas_list = meas_list.replace('\n', '').split(',')

# Define channels (phase measurment)
channel_1 = "CH1"
channel_2 = "CH2"

# Update sources from last added measurement
scope.write(f"MEASUrement:{meas_list[-1]}:SOUrce1 {channel_1}")
scope.write(f"MEASUrement:{meas_list[-1]}:SOUrce2 {channel_2}")


def get_last_meas_name():
  return scope.query("MEASUrement:LIST?").replace('\n', '').split(',')[-1]


while 1:

  # Define measurement number
  # meas_name = 'MEAS2'
  meas_name = get_last_meas_name()

  res = scope.query(f"MEASUrement:{meas_name}:RESUlts:HISTory:MEAN?")
  print(f"{meas_name}: {res}")

  time.sleep(1)
