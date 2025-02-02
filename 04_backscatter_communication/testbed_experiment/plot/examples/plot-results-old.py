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

path_name = 'multi_tone_m1'
# path_name = "one_tone_phase_duration_5_m1"

x1 = []
x2 = []
y = []

begin_no_meas = 0
no_meas = 2

saved_data_names = ["ep", "scope"]

for i in range(begin_no_meas, no_meas):

    files = [None]*2

    for index, name in enumerate(saved_data_names):
        # Define the pattern to search for
        pattern = os.path.join(f"{exp_dir}/data/{path_name}", f"phase_{75 + i}_*_{name}.csv")
        print(pattern)

        # Search for the file
        files[index] = glob.glob(pattern)

    print(files)
    
    df = [None]*2

    # Check if any file is found
    if files:

        # Load the CSV file
        # csv_file = f"./data/one_tone_phase_duration_10/{name}_{meas_number}.csv"  # Replace with your actual CSV file path
        # config_file = f"./data/one_tone_phase_duration_10/{name}_{meas_number}_config.yaml"
        for name in saved_data_names:
            df[saved_data_names.index(name)] = pd.read_csv(files[saved_data_names.index(name)][0])
        # [0:1000]


        # Define min start time
        start_time = np.min([df[0]["timestamp"][0], df[1]["timestamp"][0]])

        # #   Read YAML file
        # config = read_yaml_file(f"{config_file}")

        # gain = config.get('client', {}).get('hosts', {}).get('all', {}).get('gain', {})
        # duration = config.get('client', {}).get('hosts', {}).get('all', {}).get('duration', {})

        # Extract 'utc' and 'pwr_pw' columns
        #utc = df['utc']
        pwr_pw = df[0]['pwr_pw']
        buffer_voltage_mv = df[0]['buffer_voltage_mv']
        res = df[0]['resistance']
        #dbm = df['dbm']

        # Check race condition faults
        # plt.plot(df[0]["timestamp"], pwr_pw/1e6 - buffer_voltage_mv**2/res)

        print(f"Max voltage: {max(buffer_voltage_mv)}")

        pwr_dbm = df[1]['dbm'] + 10

        # Define list of timestamps
        time_ep = (df[0]["timestamp"].values - start_time)/1e3
        time_scope = (df[1]["timestamp"].values - start_time)/1e3

        # Find out time when USRP transmitters became active
        usrp_active_index = np.where(pwr_dbm > -70)[0][0]
        usrp_active_time = time_scope[usrp_active_index]

        # Update lists of data scope
        time_scope = (time_scope - usrp_active_time)[usrp_active_index:]
        pwr_dbm = pwr_dbm[usrp_active_index:]
        
        # Update EP time data
        time_ep = (time_ep - usrp_active_time)

        # Find similarly index for ep
        usrp_active_index_ep = np.where(time_ep > time_scope[0])[0][0]
        print(usrp_active_index_ep)

        # Update lists of ep data
        time_ep = time_ep[usrp_active_index_ep:]
        pwr_pw = pwr_pw[usrp_active_index_ep:]
        buffer_voltage_mv = buffer_voltage_mv[usrp_active_index_ep:]
        res = res[usrp_active_index_ep:]

        dc = np.mean(pwr_pw/1e6)
        #rf = np.mean(10**(dbm/10)*1e3)

        print(f"DC mean {np.mean(pwr_pw/1e6)}")
        print(f"RF mean {np.mean(10**(pwr_dbm/10)*1e3)}")
        print(f"RF mean {np.max(pwr_dbm)}")

        x1.append(dc)
        #x2.append(rf)


        # Plot 'utc' against 'pwr_pw'
        plt.figure(figsize=(10, 6))
        plt.plot(time_ep, pwr_pw/1e6, label = 'DC power (EP profiler)')
        plt.plot(time_ep, buffer_voltage_mv/1e3, label = 'Voltage (EP profiler)')
        plt.plot(time_ep, res/1e6, label = 'Resistance (EP profiler)')
        plt.plot(time_scope, 10**(pwr_dbm/10)*1e3, label = 'RF power (FFT scope)')
        # plt.plot(x, 10*np.log(pwr_pw/1e6), marker='o', label='harvester DC power')
        # plt.plot(x, dbm, marker='o', label='RF power')
        # plt.ylabel('Power (dBm)')
        # plt.plot(time, pwr_pw/1e3, marker='o', label='harvester DC power')
        # plt.plot(time, 10**(dbm/10)*1e3, marker='o', label='harvested RF power')
        # plt.plot(x, buffer_voltage_mv, marker='o', label='harvester DC voltage')dd
        plt.xlabel('Measurement time [s]')
        # plt.ylim(-5,50)
        plt.ylabel('Power (uW)')
        plt.title(f"Measured harvested and RF power with USRP gain {75 + i} dB")
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)  # Rotate the x-axis labels for better readability
        plt.tight_layout()  # Adjust layout to prevent clipping of labels
        plt.show()