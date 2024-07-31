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

end_name = "5_m1"

x1 = []
x2 = []
y = []

begin_no_meas = 10
no_meas = 11

saved_data_names = ["ep", "scope"]

for i in range(begin_no_meas, no_meas):

    files = [None]*2

    for index, name in enumerate(saved_data_names):
        # Define the pattern to search for
        pattern = os.path.join(f"{exp_dir}/data/one_tone_phase_duration_{end_name}", f"phase_{75 + i}_*_{name}.csv")
        print(pattern)

        # Search for the file
        files[index] = glob.glob(pattern)
    
    df = [None]*2

    # Check if any file is found
    if files:

        # Load the CSV file
        # csv_file = f"./data/one_tone_phase_duration_10/{name}_{meas_number}.csv"  # Replace with your actual CSV file path
        # config_file = f"./data/one_tone_phase_duration_10/{name}_{meas_number}_config.yaml"
        for name in saved_data_names:
            df[saved_data_names.index(name)] = pd.read_csv(files[saved_data_names.index(name)][0])
        # [0:1000]


        # #   Read YAML file
        # config = read_yaml_file(f"{config_file}")

        # gain = config.get('client', {}).get('hosts', {}).get('all', {}).get('gain', {})
        # duration = config.get('client', {}).get('hosts', {}).get('all', {}).get('duration', {})

        # Extract 'utc' and 'pwr_nw' columns
        #utc = df['utc']
        pwr_nw = df[0]['pwr_nw']
        buffer_voltage_mv = df[0]['buffer_voltage_mv']
        res = df[0]['resistance']
        #dbm = df['dbm']

        # Check race condition faults
        plt.plot(df[0]["timestamp"], pwr_nw/1e3 - buffer_voltage_mv**2/res)

        print(f"Max voltage: {max(buffer_voltage_mv)}")

        time = df[0]["timestamp"].values - df[0]["timestamp"].values[0]

        pwr_dbm = df[1]['dbm'] + 10
        time2 = df[1]["timestamp"].values - df[1]["timestamp"].values[0]

        dc = np.mean(pwr_nw/1e3)
        #rf = np.mean(10**(dbm/10)*1e3)


        print(f"DC mean {np.mean(pwr_nw/1e3)}")
        print(f"RF mean {np.mean(10**(pwr_dbm/10)*1e3)}")
        print(f"RF mean {np.max(pwr_dbm)}")

        x1.append(dc)
        #x2.append(rf)


        # Plot 'utc' against 'pwr_nw'
        plt.figure(figsize=(10, 6))
        plt.plot(df[0]["timestamp"], pwr_nw/1e3, label = 'DC power (EP profiler)')
        plt.plot(df[0]["timestamp"], buffer_voltage_mv/1e3, label = 'Harv. voltage')
        plt.plot(df[0]["timestamp"], res/1e6, label = 'EP resistance')
        plt.plot(df[1]["timestamp"], 10**(pwr_dbm/10)*1e3, label = 'RF power (FFT scope)')
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