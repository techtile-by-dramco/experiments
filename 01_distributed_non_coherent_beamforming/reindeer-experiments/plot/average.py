import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Get the current directory of the script
server_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate one folder back to reach the parent directory
exp_dir = os.path.abspath(os.path.join(server_dir, os.pardir))

# *** Includes continuation ***
sys.path.append(f"{exp_dir}/server")

# *** Local includes ***
from yaml_utils import *

name = "phase_79"
meas_number = 1719407906

# Load the CSV file
csv_file = f"./data/one_tone_phase_duration_10/{name}_{meas_number}.csv"  # Replace with your actual CSV file path
config_file = f"./data/one_tone_phase_duration_10/{name}_{meas_number}_config.yaml"
df = pd.read_csv(csv_file)

#   Read YAML file
config = read_yaml_file(f"{config_file}")

gain = config.get('client', {}).get('hosts', {}).get('all', {}).get('gain', {})
duration = config.get('client', {}).get('hosts', {}).get('all', {}).get('duration', {})

# Extract 'utc' and 'pwr_nw' columns
utc = df['utc']
pwr_nw = df['pwr_nw']
buffer_voltage_mv = df['buffer_voltage_mv']
dbm = df['dbm']

time = df["timestamp"].values - df["timestamp"].values[0]

print(f"DC mean {np.mean(pwr_nw/1e3)}")
print(f"RF mean {np.mean(10**(dbm/10)*1e3)}")

