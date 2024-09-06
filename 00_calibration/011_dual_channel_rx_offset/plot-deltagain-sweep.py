import matplotlib.pyplot as plt
import numpy as np
import yaml
import os
import re

import matplotlib.colors as mcolors
import pandas as pd


with open("cal-settings.yml", "r") as file:
    vars = yaml.safe_load(file)
    RATE = vars["RATE"]


import glob

NUM_MEAS_PER_EXP = 4


MIN_Y = -10
MAX_Y = 10


# MEAS 1: T04_20240905130028
# MEAS 2: T04_20240905140237
# MEAS 3: T03_20240905144640

measurements = [
    "T04_20240905130028",
    "T04_20240905140237",
    "T03_20240905144640",
    "T03_20240906082810",
]
scope_angles = [-151.8, -151.8, -151.8, -51.8]  # measured angle diff on the scope
linestyles = ["dashed", "dashed", "dotted", "dotted"]
colors = list(mcolors.TABLEAU_COLORS)
gain_sweeps = np.asarray(range(39))[::-1] #reverse as started from 39


gain_sweeps = np.repeat(gain_sweeps, NUM_MEAS_PER_EXP)

# header: exp_id, meas_id, node_id, rx_gain, rx_gain_diff, angle_diff
columns=["exp_id", "node_id", "rx_gain", "rx_gain_diff", "angle_diff"]


for meas, ls, SCOPE_ANGLE in zip(
    measurements, linestyles, scope_angles):

    df_list = []

    # Define the file pattern
    pattern = "data_"+meas+r"_(\d+)\.npy"
    # Compile the regex pattern for efficiency
    compiled_pattern = re.compile(pattern)

    # Use glob to find all files matching the pattern
    file_list = []

    # Initialize an empty list to store the arrays

    num_files_found = 0
    # Iterate over each file and load it using np.load, then append to the list
    for filename in glob.glob("*.npy"):
        base_name = os.path.basename(filename)  # Get just the filename part
        # Check if the filename matches the regex
        if compiled_pattern.match(base_name):
            num_files_found+=1
            print(f"{base_name} found")

    print(f"{num_files_found} files found")
    array_list = [0] * num_files_found
    all_iq_samples_list = [0] * num_files_found

    # Iterate over each file and load it using np.load, then append to the list
    for filename in glob.glob("*.npy"):
        base_name = os.path.basename(filename)  # Get just the filename part
        # Check if the filename matches the regex
        if compiled_pattern.match(base_name):
            match = re.search(pattern, filename)
            assert match
            suffix_number = int(match.group(1))
            print(f'Reading file {suffix_number}')
            file_list.append(base_name)
            iq_samples = np.load(filename)
            angles = np.angle(iq_samples, deg=True)
            angle_diff = angles[0, :] - angles[1, :]
            idx = angle_diff > 180
            angle_diff[idx] =  angle_diff[idx] - 360

            # "meas_id", "node_id", "rx_gain", "rx_gain_diff", "angle_diff"

            node_id = meas.split("_")[0]
            meas_id = meas.split("_")[-1]

            gain = gain_sweeps[suffix_number]

            print(meas_id, node_id, gain, gain - 31, np.mean(angle_diff))

            d = {
                "exp_id": meas_id,
                "node_id": node_id,
                "rx_gain": gain,
                "rx_gain_diff": gain - 31,
                "angle_diff": np.mean(angle_diff),
            }

            df_list.append(pd.DataFrame(d, index=[0]))

            df = pd.concat(df_list, ignore_index=True)

            df.to_csv(f"{meas}.csv", index=False)


