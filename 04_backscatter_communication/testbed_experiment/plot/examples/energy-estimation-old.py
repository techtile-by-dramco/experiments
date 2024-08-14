#!/usr/local/bin/env python3.12

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import glob
from scipy.interpolate import interp1d
# import tikzplotlib

# Get the current directory of the script
server_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate one folder back to reach the parent directory
exp_dir = os.path.abspath(os.path.join(server_dir, os.pardir))

# *** Includes continuation ***
sys.path.append(f"{exp_dir}/server")

# *** Local includes ***
from yaml_utils import *

file_path = None

path_name = "one_tone_phase_duration_5_m1"

x1 = []
x2 = []
y = []

no_meas = 11

# Data - full
mcu_voltage = np.array([0, 0.5, 0.75, 1, 1.25, 1.5, 1.7, 1.75, 1.8, 2])
mcu_current = np.array([0, 7e-9, 94e-9, 546e-9, 2.39e-6, 2.88e-6, 2.97e-6, 205e-6, 212e-6, 228e-6])

# Data - mcu not running
# mcu_voltage = np.array([0.5, 0.75, 1, 1.25, 1.5, 1.7])
# mcu_current = np.array([7e-9, 94e-9, 546e-9, 2.39e-6, 2.88e-6, 2.97e-6])

# Create an interpolating function
linear_interpolant = interp1d(mcu_voltage, mcu_current, kind='linear')

# Generate voltage values for interpolation
x_inter = np.linspace(min(mcu_voltage), max(mcu_voltage), 100)
# y_inter = linear_interpolant(x_new)

def get_mcu_consumption_power(voltage):
    current = linear_interpolant(voltage)
    # if current < 0: 
    #     current = 0
    
    return current*voltage

print(get_mcu_consumption_power(1.2))

#  *** MCU power consumption *** #

# # Plot the data and the interpolated curve
# plt.scatter(mcu_voltage, mcu_current*mcu_voltage, label='Data')
# plt.plot(x_inter, get_mcu_consumption_power(x_inter), color='red', label='Polynomial fit')
# plt.xlabel('MCU supply voltage (V)')
# plt.ylabel('MCU power consumption (W)')
# plt.yscale('log')
# plt.grid()
# # plt.legend()

# # plt.show()

# tikzplotlib.save("plot/output/mcu_power_consumption_interpolation.tex")


# exit()

target_voltage = 1.75


for i in range(no_meas):
    # Print experiment number
    print(f"*******************************************************")
    print(f"    *** USRP gain equals {75 + i} -- Duration {path_name} ***     ")

    # Define the pattern to search for
    pattern = os.path.join(f"{exp_dir}/data/{path_name}", f"phase_{75 + i}_*.csv")

    # Search for the file
    files = glob.glob(pattern)

    # Check if any file is found
    if files:
        # Assuming you want the first match if there are multiple
        file_path = files[0]
        # print(file_path)

        # Load the CSV file
        df = pd.read_csv(file_path)

        # Extract 'utc' and 'pwr_nw' columns
        utc = df['utc']
        pwr_nw = df['pwr_nw']
        buffer_voltage_mv = df['buffer_voltage_mv']
        dbm = df['dbm']

        capacitor = 100e-6#22e-6 #22uF
        # print(capacitor)

        buffer_voltage = buffer_voltage_mv/1000

        vbuffer = [0]
        timestamp_buffer_charge = []

        time_above_target_voltage = 0

        time = df["timestamp"].values - df["timestamp"].values[0]

        dc = np.mean(pwr_nw/1e3)
        rf = np.mean(10**(dbm/10)*1e3)

        # print(f"DC mean {np.mean(pwr_nw/1e3)}")
        # print(f"RF mean {np.mean(10**(dbm/10)*1e3)}")

        # x1.append(dc)
        # x2.append(rf)

        delta_time = time[1:] - time[:-1]

        # print(delta_time)

        # charge_time = 0

        dc_power_w = (pwr_nw/1e9)[:-1]

        # Initialize flag
        executed_once = False

        for index, harv_voltage in enumerate(buffer_voltage[:-1]):
            
            # vbuffer.append(np.sqrt(vbuffer[-1]**2 + (2 * delta_time[index] * dc_power_w[index] - get_mcu_consumption_power(vbuffer[-1]))/capacitor))

            # If harvester voltage is higher than buffer voltage
            if harv_voltage > vbuffer[-1]:
                # print(harv_voltage, vbuffer[-1], delta_time[index], dc_power_w[index], capacitor)
                new_volt = np.sqrt(vbuffer[-1]**2 + (2 * delta_time[index] * (dc_power_w[index] - get_mcu_consumption_power(vbuffer[-1])))/capacitor)
                
                # If new voltage is lower than harvester harv_voltage --> it is OK
                if new_volt < harv_voltage:
                    vbuffer.append(new_volt)
                else:
                    # vbuffer.append(harv_voltage)
                    drained_power = dc_power_w[index] - get_mcu_consumption_power(vbuffer[-1])
                    if drained_power < 0:
                        vbuffer.append(np.sqrt(vbuffer[-1]**2 + (2 * delta_time[index] * drained_power)/capacitor))
                    else:
                        vbuffer.append(vbuffer[-1])
            # If harvester voltage is lower than buffer harv_voltage
            else:
                drained_power = dc_power_w[index] - get_mcu_consumption_power(vbuffer[-1])
                new_sqrt = vbuffer[-1]**2 + (2 * delta_time[index] * drained_power)/capacitor
                # print(new_sqrt)
                # print((2 * delta_time[index] * drained_power)/capacitor)
                if drained_power < 0:
                    if new_sqrt > 0:
                        vbuffer.append(np.sqrt(new_sqrt))
                    else:
                        vbuffer.append(0)
                else:
                    vbuffer.append(vbuffer[-1])

            # if vbuffer[-1] > target_voltage and not executed_once:
            #     charge_time = time[index]
            #     executed_once = True

        vbuffer = vbuffer[1:]

        # print(vbuffer)

        # print([voltage for voltage in buffer_voltage_mv if voltage > 1400])

        # for index, volt in enumerate(vbuffer):
        #     if volt > target_voltage:
        #         time_above_target_voltage = time_above_target_voltage + delta_time[index]
        
        
        print(f"Time above target voltage: {round(time_above_target_voltage)} s")
        print(f"Total meas time: {round(time[-1])} s")
        print(f"Percentage above target voltage;: {round(time_above_target_voltage/time[-1]*1E4)/1E2} %")


        # plt.plot(np.linspace(1, len(vbuffer), len(vbuffer)), vbuffer)
        plt.title(f"Charging {round(capacitor*1e6)}uF buffer (gain {75 + i})")
        plt.plot(time[1:], vbuffer, label = 'cap buffer voltage')
        plt.plot(time, buffer_voltage, label = 'harvester voltage')
        # plt.plot(time[:-1], (2 * delta_time * dc_power_w)/capacitor)
        plt.grid()
        plt.legend(loc='lower right')
        plt.show()