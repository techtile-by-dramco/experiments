import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import glob
from scipy.interpolate import interp1d
import random

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

usrp_gain = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5, 0]
output_power = [18.2, 18.0, 18.4, 17.4, 13.4, 9.1, 4.6, -0.4, -5.6, -10.8, -15.7, -20.8, -26.4, -30.4, -37.0, -42.5, -46.5, -51.3, -56.3, -61.1, -67.4]

def get_usrp_output_power(usrp_gain_query):

    # Create an interpolation function
    interpolation_function = np.interp(usrp_gain_query, usrp_gain[::-1], output_power[::-1])
    return round(interpolation_function*100)/100

def get_total_tx_power(usrp_gain_query):
    return round((get_usrp_output_power(usrp_gain_query) + 10*np.log10(84))*100)/100

# Data - full
mcu_voltage = np.array([0, 0.5, 0.75, 1, 1.25, 1.5, 1.7, 1.74, 1.75, 1.8, 2])
# mcu_current = np.array([0, 7e-9, 94e-9, 546e-9, 2.39e-6, 2.88e-6, 2.97e-6, 2.99e-6, 205e-6, 212e-6, 228e-6])
mcu_current = np.array([0, 0, 0, 0, 0, 0, 0, 0, 205e-6, 212e-6, 228e-6])

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

def tikzplotlib_fix_ncols(obj):
    """
    workaround for matplotlib 3.6 renamed legend's _ncol to _ncols, which breaks tikzplotlib
    """
    if hasattr(obj, "_ncols"):
        obj._ncol = obj._ncols
    for child in obj.get_children():
        tikzplotlib_fix_ncols(child)

def calc_vbuffer(time_ep, buffer_voltage_mv, pwr_pw):
    capacitor = 100e-6

    # Adapt voltage buffer
    buffer_voltage = buffer_voltage_mv/1000

    # Create new result buffer
    vbuffer = [0]

    # Define delta time
    delta_time = np.asarray(time_ep[1:] - time_ep[:-1])

    # dc power buffer in watt
    dc_power_w = np.asarray((pwr_pw/1e12)[:-1])

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

    return vbuffer[1:]


def meas(path_n):

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

            # print(f"Max voltage: {max(buffer_voltage_mv)}")

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
            # print(usrp_active_index_ep)

            # Update lists of ep data
            time_ep = time_ep[usrp_active_index_ep:]
            pwr_pw = pwr_pw[usrp_active_index_ep:]
            buffer_voltage_mv = buffer_voltage_mv[usrp_active_index_ep:]
            res = res[usrp_active_index_ep:]

            # Find similarly index for ep
            usrp_active_index_ep = np.where(time_ep > time_scope[0])[0][0]
            # print(usrp_active_index_ep)

            samples = 500

            # Restrict plot size and find index
            # for index, t in enumerate(time_ep):
            #     if t > time_ep[0]+100:
            #         ep_index_lim = index
            #         break

            # print(time_ep)

            # for index, t in enumerate(time_scope):
            #     if t > time_scope[0]+5:
            #         scope_index_lim = index
            #         break
            
            time_ep = time_ep[::1]
            pwr_pw = pwr_pw[::1]
            buffer_voltage_mv = buffer_voltage_mv[::1]

            # time_scope = time_scope[:scope_index_lim][::1]
            # pwr_dbm = pwr_dbm[:scope_index_lim][::1]


            ######################################

            vbuffer = calc_vbuffer(time_ep, buffer_voltage_mv, pwr_pw)

            target = None
            if any(value > 1.74 for value in vbuffer):
                target = 'yes'
            else:
                target = 'no'

            tg_count = 0
            for volt in vbuffer:
                if volt > 1.74:
                    tg_count +=1

            tg_count_perc = round(tg_count/len(vbuffer)*1e4)/100


            # ######################################## Define average response time ########################################
            # vbuffer_rp = vbuffer + vbuffer
            # time_ep_rp = np.concatenate((np.asarray(time_ep), np.asarray(time_ep + time_ep[-1])))

            # no_iterations = 10000

            # avg_rsp_time_buffer = [0]*no_iterations

            # for j in range(no_iterations):
                
            #     random_integer = random.randint(1, len(vbuffer))

            #     # print(len(vbuffer))
            #     # print(random_integer)
            #     # print(len(vbuffer_rp))
            #     # print(len(vbuffer_rp[random_integer:]))
            #     # print(len(time_ep_rp))

            #     rt_count = 0
            #     for index, volt in enumerate(vbuffer_rp[random_integer:]):
            #         if volt > 1.74:
            #             rt_count = index
            #             break
                
            #     # print(f"rt_count {rt_count}")
            #     # print(f"start {time_ep_rp[random_integer]}")
            #     # print(f"response {time_ep_rp[random_integer + rt_count] - time_ep_rp[random_integer]}")

            #     avg_rsp_time_buffer [j] = time_ep_rp[random_integer + rt_count] - time_ep_rp[random_integer]

            # avg_rsp_time = np.mean(avg_rsp_time_buffer)


            # ######################################## Define average response time ########################################
            
            ######################################## Define average response time ########################################
            # vbuffer_rp = vbuffer + vbuffer
            # time_ep_rp = np.concatenate((np.asarray(time_ep), np.asarray(time_ep + time_ep[-1])))

            no_iterations = 10

            avg_rsp_time_buffer = [0]*no_iterations

            for j in range(no_iterations):
                
                random_integer = random.randint(1, len(vbuffer))

                buffer_voltage_mv = np.concatenate((np.asarray(buffer_voltage_mv[random_integer:]), np.asarray(buffer_voltage_mv[:random_integer])))
                pwr_pw = np.concatenate((np.asarray(pwr_pw[random_integer:]), np.asarray(pwr_pw[:random_integer])))

                vbuffer_rp = calc_vbuffer(time_ep, buffer_voltage_mv, pwr_pw)

                # print(len(vbuffer))
                # print(random_integer)
                # print(len(vbuffer_rp))
                # print(len(vbuffer_rp[random_integer:]))
                # print(len(time_ep_rp))

                rt_count = 0
                for index, volt in enumerate(vbuffer_rp):
                    if volt > 1.74:
                        rt_count = index
                        break
                
                # print(f"rt_count {rt_count}")
                # print(f"start {time_ep_rp[random_integer]}")
                # print(f"response {time_ep_rp[random_integer + rt_count] - time_ep_rp[random_integer]}")

                avg_rsp_time_buffer [j] = time_ep[rt_count] - time_ep[0]
            
            # print(avg_rsp_time_buffer)

            avg_rsp_time = round(np.mean(avg_rsp_time_buffer)*100)/100
            std_rsp_time = round(np.std(avg_rsp_time_buffer)*100)/100


            ######################################## Define average response time ########################################

            print(f"{75 + i} & {round(np.mean(vbuffer)*100)/100} & {tg_count_perc} & {avg_rsp_time} & {std_rsp_time}")
            



            # print(len(time_scope[1:]))
            # print(len(vbuffer))

            # print(len(time_ep))
            # print(len(test[1:]))


            # # plt.plot(np.linspace(1, len(vbuffer), len(vbuffer)), vbuffer)

            # samples_divider = 1

            # fig, ax1 = plt.subplots()
            # # plt.title(f"Charging {round(capacitor*1e6)}uF buffer (gain {75 + i})")
            # ax1.plot(time_ep[::samples_divider], buffer_voltage[::samples_divider], label = 'Harvester voltage')
            # ax1.plot(time_ep[1:][::samples_divider], vbuffer[::samples_divider], label = 'Buffer capacitor voltage')
            # # ax1.plot(time_ep,test)
            # ax1.set_xlabel("Time [s]")
            # ax1.set_ylabel("Voltage [V]")
            # ax1.grid()
            # ax1.legend(loc='lower right')
            # plt.show()


            # import tikzplotlib

            # tikzplotlib_fix_ncols(fig)

            # tikzplotlib.save(f"{exp_dir}/plot/tikz/{path_n}_{75 + i}_energy_buffer.tex")

meas(path_name[0])
meas(path_name[1])