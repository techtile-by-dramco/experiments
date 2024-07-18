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

name = "phase_75"
meas_number = 1718783696

# Load the CSV file
csv_file = f"./data/{name}_{meas_number}.csv"  # Replace with your actual CSV file path
config_file = f"./data/{name}_{meas_number}_config.yaml"
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

# Plot 'utc' against 'pwr_nw'
plt.figure(figsize=(10, 6))
# plt.plot(x, 10*np.log(pwr_nw/1e6), marker='o', label='harvester DC power')
# plt.plot(x, dbm, marker='o', label='RF power')
# plt.ylabel('Power (dBm)')
plt.plot(time, pwr_nw/1e3, marker='o', label='harvester DC power')
plt.plot(time, 10**(dbm/10)*1e3, marker='o', label='harvested RF power')
# plt.plot(x, buffer_voltage_mv, marker='o', label='harvester DC voltage')dd
plt.xlabel('Time [-]')
plt.ylabel('Power (uW)')
plt.title(f"Measured harvested and RF power with USRP gain {gain} dB and duration {duration} seconds")
plt.grid(True)
plt.legend()
plt.xticks(rotation=45)  # Rotate the x-axis labels for better readability
plt.tight_layout()  # Adjust layout to prevent clipping of labels
plt.show()