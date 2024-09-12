import glob
import os
import re

import numpy as np
import pandas as pd
import csv

import tools

to_process = [False, False, False, True]
measurements = [
    "T03_20240909114249",
    "T04_20240909190225",
    "T04_20240910062816",
    "T03_20240910085457",
]

max_gains = [78, 44, None, None]
min_gains = [0, 10, None, None]
NUM_MEAS_PER_EXPS = [2, 2,1, 1]
scope_angles = [
    -(277.1 - 360),
    -83.75,
    83.75,
    83.75,
]  # measured angle diff on the scope

for meas, SCOPE_ANGLE, NUM_MEAS_PER_EXP, max_gain, min_gain, tp in zip(
    measurements,
    scope_angles,
    NUM_MEAS_PER_EXPS,
    max_gains,
    min_gains,
    to_process,
    strict=True,  # ensure equal length arss in zip (in Python 3.10)
):

    if not tp:
        continue

    # check if mapping exists:
    mapping_file = f"data/data_config_{meas}.csv"
    if os.path.exists(mapping_file):
        with open(mapping_file, mode="r", encoding="utf-8") as file:
            csv_reader = list(csv.reader(file))  # Convert to a list
            max_suffix_number = int(csv_reader[-1][0])  # Get the last row, first value
            gains_ch0 = np.zeros(max_suffix_number)
            gains_ch1 = np.zeros(max_suffix_number)
            for row in csv_reader:
                idx = int(row[0]) - 1
                gains_ch0[idx] = int(row[1])
                gains_ch1[idx] = int(row[2])
    else:
        # I know it is ugly, but it does the job:
        gains_ch0 = []
        gains_ch1 = []
        for gain1 in np.asarray(range(min_gain, max_gain + 1))[::-1]:
            for gain0 in np.asarray(range(min_gain, max_gain + 1))[::-1]:
                gains_ch0.append(gain0)
                gains_ch1.append(gain1)

        gains_ch0 = np.repeat(gains_ch0, NUM_MEAS_PER_EXP)
        gains_ch1 = np.repeat(gains_ch1, NUM_MEAS_PER_EXP)

    df_list = []

    # Define the file pattern
    pattern = "data_" + meas + r"_(\d+)\.npy"
    # Compile the regex pattern for efficiency
    compiled_pattern = re.compile(pattern)

    # Use glob to find all files matching the pattern
    file_list = []

    # Initialize an empty list to store the arrays

    num_files_found = 0
    # Iterate over each file and load it using np.load, then append to the list
    for filename in glob.glob("data/*.npy"):
        base_name = os.path.basename(filename)  # Get just the filename part
        # Check if the filename matches the regex
        if compiled_pattern.match(base_name):
            num_files_found += 1
            print(f"{base_name} found")

    print(f"{num_files_found} files found")
    array_list = [0] * num_files_found
    all_iq_samples_list = [0] * num_files_found

    # Iterate over each file and load it using np.load, then append to the list
    for filename in glob.glob("data/*.npy"):
        base_name = os.path.basename(filename)  # Get just the filename part
        # Check if the filename matches the regex
        if compiled_pattern.match(base_name):
            match = re.search(pattern, filename)
            assert match
            suffix_number = int(match.group(1))
            print(f"Reading file {suffix_number}")
            file_list.append(base_name)
            iq_samples = np.load(filename)
            # angles = np.angle(iq_samples, deg=True)

            iq_ch0 = tools.apply_bandpass(iq_samples[0, :])
            iq_ch1 = tools.apply_bandpass(iq_samples[1, :])

            angles_ch0 = np.angle(iq_ch0)
            angles_ch1 = np.angle(iq_ch1)

            # angles_ch0 = tools.get_phases_and_remove_CFO(iq_samples[0, :])
            # angles_ch1 = tools.get_phases_and_remove_CFO(iq_samples[1, :])

            angle_diff = tools.to_min_pi_plus_pi(
                np.rad2deg(angles_ch0 - angles_ch1), deg=True
            )

            # "meas_id", "node_id", "rx_gain", "rx_gain_diff", "angle_diff"

            max_I = np.max(np.abs(np.real(iq_samples[0, :])))
            max_Q = np.max(np.abs(np.imag(iq_samples[0, :])))

            max_IQ_vals_ch0 = max_I if max_I > max_Q else max_Q

            max_I = np.max(np.abs(np.real(iq_samples[1, :])))
            max_Q = np.max(np.abs(np.imag(iq_samples[1, :])))

            max_IQ_vals_ch1 = max_I if max_I > max_Q else max_Q

            node_id = meas.split("_")[0]
            meas_id = meas.split("_")[-1]

            gain_ch0 = gains_ch0[suffix_number - 1]
            gain_ch1 = gains_ch1[suffix_number - 1]

            mean_anlge_diff = np.mean(angle_diff)

            print(f"CH0: {gain_ch0} CH1: {gain_ch1} phase: {mean_anlge_diff:.2f} degr")

            d = {
                "exp_id": meas_id,
                "node_id": node_id,
                "rx_gain_ch0": gain_ch0,
                "rx_gain_ch1": gain_ch1,
                "rx_gain_diff": gain_ch1 - gain_ch0,
                "angle_diff": mean_anlge_diff,
                "real_diff": SCOPE_ANGLE,
                "angle_diff_std": np.std(np.abs(angle_diff)),
                "max_IQ_ampl_ch0": max_IQ_vals_ch0,
                "max_IQ_ampl_ch1": max_IQ_vals_ch1,
            }

            df_list.append(d)

    df = pd.DataFrame(df_list)

    df.to_csv(f"{meas}.csv", index=False)
