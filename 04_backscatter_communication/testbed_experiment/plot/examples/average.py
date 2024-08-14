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

end_name = "20_m1"

x1 = []
x2 = []
x1_max = []
x2_max = []
x1_min = []
x2_min = []
y = []

no_meas = 8

for i in range(no_meas):
    # Define the pattern to search for
    pattern = os.path.join(f"{exp_dir}/data/one_tone_phase_duration_{end_name}", f"phase_{75 + i}_*.csv")

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

        dc = np.average(pwr_nw/1e3)
        rf = np.average(10**(dbm/10)*1e3)
        dc_max = np.max(pwr_nw/1e3)
        rf_max = np.max(10**(dbm/10)*1e3)
        dc_min = np.min(pwr_nw/1e3)
        rf_min = np.min(10**(dbm/10)*1e3)

        print(max(pwr_nw/1e3))

        print(f"DC mean {np.mean(pwr_nw/1e3)}")
        print(f"RF mean {np.mean(10**(dbm/10)*1e3)}")

        print(f"max dc: {dc_max}")

        x1.append(dc)
        x1_max.append(dc_max)
        x2.append(rf)
        x2_max.append(rf_max)

        x1_min.append(dc_min)
        x2_min.append(rf_min)

x = np.linspace(75,75+no_meas,no_meas)


# plt.figure(figsize=(10, 6))
# plt.plot(x, x1, label = 'DC power (EP profiler)')
# plt.plot(x, x2, label = 'RF power (FFT scope)')
# plt.plot(x, np.array(x1)/np.array(x2)*100, label = 'Average efficiency harvester')
# plt.xlabel('USRP gain [-]')
# plt.ylabel('Power (uW)')
# plt.title(f"Average harvested DC and RF power related to the USRP gain (and phase duration {10} seconds)")
# # plt.title(f"Measured harvested and RF power with USRP gain {gain} dB and duration {duration} seconds")
# plt.grid(True)
# plt.legend()
# plt.xticks(rotation=45)  # Rotate the x-axis labels for better readability
# plt.tight_layout()  # Adjust layout to prevent clipping of labels
# plt.show()


# Create the main plot
fig, ax1 = plt.subplots(figsize=(10, 6))
plt.grid(True)
ax1.plot(x, x1, label = 'DC power (EP profiler)', color="red")
ax1.plot(x, x2, label = 'RF power (FFT scope)', color="blue")
# ax1.plot(x, x1_max, label = 'Max. DC power (EP profiler)',ls="--", color="red")
# ax1.plot(x, x2_max, label = 'Max. RF power (FFT scope)',ls="--", color="blue")
# ax1.plot(x, x1_min, label = 'Min. DC power (EP profiler)',ls="dotted", color="red")
# ax1.plot(x, x2_min, label = 'Min. RF power (FFT scope)',ls="dotted", color="blue")
ax1.set_xlabel('USRP gain [dB]')
ax1.set_ylabel('Power (uW)')
ax2 = ax1.twinx()
ax2.plot(x, np.array(x1)/np.array(x2)*100, label = 'Average efficiency harvester', color='g')
ax2.set_ylabel('Average efficiency harvester [-]', color='g')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
plt.title('Plot with Two Y-Axes')
plt.show()
