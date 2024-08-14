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

path_name = ['multi_tone_m1', 'one_tone_phase_duration_5_m1']

usrp_gain = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5, 0]
output_power = [18.2, 18.0, 18.4, 17.4, 13.4, 9.1, 4.6, -0.4, -5.6, -10.8, -15.7, -20.8, -26.4, -30.4, -37.0, -42.5, -46.5, -51.3, -56.3, -61.1, -67.4]

def get_usrp_output_power(usrp_gain_query):

    # Create an interpolation function
    interpolation_function = np.interp(usrp_gain_query, usrp_gain[::-1], output_power[::-1])
    return round(interpolation_function*100)/100

def get_total_tx_power(usrp_gain_query):
    return round((get_usrp_output_power(usrp_gain_query) + 10*np.log10(84))*100)/100

def meas(path_n):

    pwr_dc = {}
    pwr_rf = {}

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

            pwr_dc.setdefault('mean', []).append(round(np.mean(pwr_pw/1e6)*100)/100)
            pwr_rf.setdefault('mean', []).append(round(np.mean(10**(pwr_dbm/10)*1e3)*100)/100)
            pwr_dc.setdefault('std', []).append(round(np.std(pwr_pw/1e6)*100)/100)
            pwr_rf.setdefault('std', []).append(round(np.std(10**(pwr_dbm/10)*1e3)*100)/100)

            vc = 0
            usable_energy = 0

            for voltage in buffer_voltage_mv:
                if voltage > 1750:
                    vc = vc + 1

            print(vc/len(buffer_voltage_mv)*100)

            pwr_dc.setdefault('tar_v_percentage', []).append(round(vc/len(buffer_voltage_mv)*100*100)/100)

            pwr_dc.setdefault('harv_eff', []).append(round(pwr_dc['mean'][-1]/pwr_rf['mean'][-1]*1e4)/100)
            pwr_dc.setdefault('tot_eff', []).append(round(round(pwr_dc['mean'][-1]/(10**(get_total_tx_power(75+i)/10)*1e3)*1e8)/1e6*1e3*1e2)/100)
            
    pwr_dc['mean'] = np.asarray(pwr_dc['mean'])
    pwr_rf['mean'] = np.asarray(pwr_rf['mean'])
    pwr_dc['std'] = np.asarray(pwr_dc['std'])
    pwr_rf['std'] = np.asarray(pwr_rf['std'])

    pwr_dc['tar_v_percentage'] = np.asarray(pwr_dc['tar_v_percentage'])

    pwr_dc['harv_eff'] = np.asarray(pwr_dc['harv_eff'])
    pwr_dc['tot_eff'] = np.asarray(pwr_dc['tot_eff'])

    pwr_dc

    return pwr_dc, pwr_rf


pwr_dc_m, pwr_rf_m = meas(path_name[0])
pwr_dc_s, pwr_rf_s = meas(path_name[1])

print(pwr_dc_m['mean'])

print("*** multi ***")

for i in range(len(pwr_dc_m['mean'])):
    print(f"{75+i} & {get_usrp_output_power(75+i)} & {get_total_tx_power(75+i)} & "
          f"{pwr_rf_m['mean'][i]} & {pwr_dc_m['mean'][i]} & "
          f"{pwr_dc_m['harv_eff'][i]} & {pwr_dc_m['tot_eff'][i]} & {pwr_dc_m['tar_v_percentage'][i]}")
    

print("*** single ***")

for i in range(len(pwr_dc_s['mean'])):
    print(f"{75+i} & {get_usrp_output_power(75+i)} & {get_total_tx_power(75+i)} & "
          f"{pwr_rf_s['mean'][i]} & {pwr_dc_s['mean'][i]} & "
          f"{pwr_dc_s['harv_eff'][i]} & {pwr_dc_s['tot_eff'][i]} & {pwr_dc_s['tar_v_percentage'][i]}")
    
