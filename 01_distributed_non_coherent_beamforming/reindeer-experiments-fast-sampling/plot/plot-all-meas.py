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

# path_name = 'multi_tone_m1'
# path_name = "one_tone_phase_duration_5_m1"

path_name = ['multi_tone_m1', 'one_tone_phase_duration_5_m1']

def meas(path_n):

    avg_pwr_dc = {}
    avg_pwr_rf = {}

    begin_no_meas = 0
    no_meas = 11

    saved_data_names = ["ep", "scope"]

    for i in range(begin_no_meas, no_meas):

        files = [None]*2

        for index, name in enumerate(saved_data_names):
            # Define the pattern to search for
            pattern = os.path.join(f"{exp_dir}/data/{path_n}", f"phase_{75 + i}_*_{name}.csv")

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
            #plt.plot(df[0]["timestamp"], pwr_pw/1e6 - buffer_voltage_mv**2/res)

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

            print(f"DC mean {np.mean(pwr_pw/1e6)} uW")
            print(f"DC std {np.std(pwr_pw/1e6)} uW")
            print(f"RF mean {np.mean(10**(pwr_dbm/10)*1e3)} uW")
            print(f"RF std {np.std(10**(pwr_dbm/10)*1e3)} uW")
            print(f"RF mean {np.mean(pwr_dbm)} dBm")

            avg_pwr_dc.setdefault('mean', []).append(np.mean(pwr_pw/1e6))
            avg_pwr_rf.setdefault('mean', []).append(np.mean(10**(pwr_dbm/10)*1e3))
            avg_pwr_dc.setdefault('std', []).append(np.std(pwr_pw/1e6))
            avg_pwr_rf.setdefault('std', []).append(np.std(10**(pwr_dbm/10)*1e3))

    avg_pwr_dc['mean'] = np.asarray(avg_pwr_dc['mean'])
    avg_pwr_rf['mean'] = np.asarray(avg_pwr_rf['mean'])
    avg_pwr_dc['std'] = np.asarray(avg_pwr_dc['std'])
    avg_pwr_rf['std'] = np.asarray(avg_pwr_rf['std'])

    return avg_pwr_dc, avg_pwr_rf


avg_pwr_dc_m, avg_pwr_rf_m = meas(path_name[0])
avg_pwr_dc_s, avg_pwr_rf_s = meas(path_name[1])

# # Main plot
# fig, ax1 = plt.subplots()

# # X-axis values
# x_values = np.linspace(1, len(avg_pwr_dc_m['mean']), len(avg_pwr_dc_m['mean'])) + 74

# ax1.plot(x_values, avg_pwr_dc_m['mean'], '#1f77b4', linestyle='-', label='Multitone Mean DC power')
# ax1.plot(x_values, avg_pwr_rf_m['mean'], '#1f77b4', linestyle='--', label='Multitone Mean RF power')
# ax1.plot(x_values, avg_pwr_dc_s['mean'], '#1f77b4', linestyle='-.', label='Single tone Mean DC power')
# ax1.plot(x_values, avg_pwr_rf_s['mean'], '#1f77b4', linestyle=':', label='Single tone Mean RF power')

# # ax1.fill_between(x_values, avg_pwr_dc_m['mean'] - avg_pwr_dc_m['std'], avg_pwr_dc_m['mean'] + avg_pwr_dc_m['std'], color='#1f77b4', alpha=0.2)
# # ax1.fill_between(x_values, avg_pwr_dc_s['mean'] - avg_pwr_dc_s['std'], avg_pwr_dc_s['mean'] + avg_pwr_dc_s['std'], color='#1f77b4', alpha=0.2)

# ax1.set_xlabel('USRP gain [dB]')
# ax1.set_ylabel('Power [uW]', color='#1f77b4')
# ax1.tick_params(axis='y', labelcolor='#1f77b4')

# ax2 = ax1.twinx()

# ax2.plot(x_values, avg_pwr_dc_m['mean']/avg_pwr_rf_m['mean']*100, '#ff7f0e', linestyle='-', label='Multitone Efficiency')
# ax2.plot(x_values, avg_pwr_dc_s['mean']/avg_pwr_rf_s['mean']*100, '#ff7f0e', linestyle='--', label='Single tone Efficiency')
# ax2.set_ylabel('Efficiency [%]', color='#ff7f0e')
# ax2.tick_params(axis='y', labelcolor='#ff7f0e')

# # Add legends
# # ax1.legend(loc='upper left')
# # ax2.legend(loc='upper right')

# plt.grid()
# plt.show()


# Main plot
fig, ax1 = plt.subplots()

# X-axis values
x_values = np.linspace(1, len(avg_pwr_dc_m['mean']), len(avg_pwr_dc_m['mean'])) + 74

ax1.plot(x_values, avg_pwr_dc_m['mean'], '#1f77b4', label='Multitone Mean DC power')
ax1.plot(x_values, avg_pwr_rf_m['mean'], '#1f77b4', label='Multitone Mean RF power')
ax1.plot(x_values, avg_pwr_dc_s['mean'], '#1f77b4', label='Single tone Mean DC power')
ax1.plot(x_values, avg_pwr_rf_s['mean'], '#1f77b4', label='Single tone Mean RF power')

# ax1.fill_between(x_values, avg_pwr_dc_m['mean'] - avg_pwr_dc_m['std'], avg_pwr_dc_m['mean'] + avg_pwr_dc_m['std'], color='#1f77b4', alpha=0.2)
# ax1.fill_between(x_values, avg_pwr_dc_s['mean'] - avg_pwr_dc_s['std'], avg_pwr_dc_s['mean'] + avg_pwr_dc_s['std'], color='#1f77b4', alpha=0.2)

ax1.set_xlabel('USRP gain [dB]')
ax1.set_ylabel('Power [uW]', color='#1f77b4')
ax1.tick_params(axis='y', labelcolor='#1f77b4')

ax2 = ax1.twinx()

ax2.plot(x_values, avg_pwr_dc_m['mean']/avg_pwr_rf_m['mean']*100, '#ff7f0e', label='Multitone Efficiency')
ax2.plot(x_values, avg_pwr_dc_s['mean']/avg_pwr_rf_s['mean']*100, '#ff7f0e', label='Single tone Efficiency')

ax2.set_ylabel('Efficiency [%]', color='#ff7f0e')
ax2.tick_params(axis='y', labelcolor='#ff7f0e')
# Add legends
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

plt.grid()

# plt.show()
# exit()

import tikzplotlib

def tikzplotlib_fix_ncols(obj):
    """
    workaround for matplotlib 3.6 renamed legend's _ncol to _ncols, which breaks tikzplotlib
    """
    if hasattr(obj, "_ncols"):
        obj._ncol = obj._ncols
    for child in obj.get_children():
        tikzplotlib_fix_ncols(child)

tikzplotlib_fix_ncols(fig)

tikzplotlib.save(f"{exp_dir}/plot/efficiency.tex")