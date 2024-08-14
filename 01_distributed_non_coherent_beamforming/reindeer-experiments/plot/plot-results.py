import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import glob

# Get the current directory of the script
server_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate one folder back to reach the parent directory
exp_dir = os.path.abspath(os.path.join(server_dir, os.pardir))

# *** Includes continuation ***
sys.path.append(f"{exp_dir}/server")

# *** Local includes ***
from yaml_utils import *

file_path = None

end_name = "0_m5"

x1 = []
x2 = []
y = []

no_meas = 1

for i in range(no_meas):
    # Define the pattern to search for
    pattern = os.path.join(f"{exp_dir}/data/one_tone_phase_duration_1{end_name}", f"phase_{75 + i}_*.csv")

    # Search for the file
    files = glob.glob(pattern)

    # Check if any file is found
    if files:
        # Assuming you want the first match if there are multiple
        file_path = files[0]
        print(file_path)


        # Load the CSV file
        # csv_file = f"./data/one_tone_phase_duration_10/{name}_{meas_number}.csv"  # Replace with your actual CSV file path
        # config_file = f"./data/one_tone_phase_duration_10/{name}_{meas_number}_config.yaml"
        df = pd.read_csv(file_path)
        # [0:1000]


        # #   Read YAML file
        # config = read_yaml_file(f"{config_file}")

        # gain = config.get('client', {}).get('hosts', {}).get('all', {}).get('gain', {})
        # duration = config.get('client', {}).get('hosts', {}).get('all', {}).get('duration', {})

        # Extract 'utc' and 'pwr_nw' columns
        utc = df['utc']
        pwr_nw = df['pwr_nw']
        buffer_voltage_mv = df['buffer_voltage_mv']
        dbm = df['dbm']

        time = df["timestamp"].values - df["timestamp"].values[0]

        dc = np.mean(pwr_nw/1e3)
        rf = np.mean(10**(dbm/10)*1e3)

        print(f"DC mean {np.mean(pwr_nw/1e3)}")
        print(f"RF mean {np.mean(10**(dbm/10)*1e3)}")

        x1.append(dc)
        x2.append(rf)


        # Plot 'utc' against 'pwr_nw'
        plt.figure(figsize=(10, 6))
        plt.plot(time, pwr_nw/1e3, label = 'DC power (EP profiler)')
        plt.plot(time, 10**(dbm/10)*1e3, label = 'RF power (FFT scope)')
        # plt.plot(x, 10*np.log(pwr_nw/1e6), marker='o', label='harvester DC power')
        # plt.plot(x, dbm, marker='o', label='RF power')
        # plt.ylabel('Power (dBm)')
        # plt.plot(time, pwr_nw/1e3, marker='o', label='harvester DC power')
        # plt.plot(time, 10**(dbm/10)*1e3, marker='o', label='harvested RF power')
        # plt.plot(x, buffer_voltage_mv, marker='o', label='harvester DC voltage')dd
        plt.xlabel('Measurements over time [-]')
        # plt.ylim(-5,50)
        plt.ylabel('Power (uW)')
        plt.title(f"Measured harvested and RF power with USRP gain {75 + i} dB and duration {10} seconds")
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)  # Rotate the x-axis labels for better readability
        plt.tight_layout()  # Adjust layout to prevent clipping of labels
        plt.show()