import glob
import os
import re

import numpy as np
import pandas as pd
import tools


to_process = [False, False, False, False, False, False, False, False, True, True]

measurements = [
    "T03_20240906105616",
    "T04_20240906105645",
    "T03_20240906123800",
    "T04_20240906123807",
    "T03_20240906135557",
    "T04_20240906134926",
    "T03_20240909074835",
    "T04_20240909074846",
    "T03_20240909091122",
    "T04_20240909083250",
]
rx_ch0_gains = [31, 31, 20, 20, 20, 20, 20, 20, 37, 37]
NUM_MEAS_PER_EXPS = [4, 4, 2, 2, 2, 2, 2, 2, 2, 2]
gains_sweeps = [39, 39, 40, 40, 40, 40, 78, 78, 78, 78]
scope_angles = [
    125.1,
    122.3,
    125.1,
    122.3,
    -(278.1 - 360),
    -(275.5 - 360),
    -(278.1 - 360),
    -(275.5 - 360),
    -(278.1 - 360),
    -(277.1 - 360),
]  # measured angle diff on the scope


for meas, SCOPE_ANGLE, rx_ch0_gain, NUM_MEAS_PER_EXP, gs, process in zip(
    measurements,
    scope_angles,
    rx_ch0_gains,
    NUM_MEAS_PER_EXPS,
    gains_sweeps,
    to_process,
    strict=True,  # ensure equqal length arss in zip (in Python 3.10)
):

    if not process:
        continue

    gain_sweeps = np.asarray(range(gs + 1))[::-1]  # reverse as started from 39
    gain_sweeps = np.repeat(gain_sweeps, NUM_MEAS_PER_EXP)

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

            angles_ch0 = tools.get_phases_and_remove_CFO(iq_samples[0, :])
            angles_ch1 = tools.get_phases_and_remove_CFO(iq_samples[1, :])

            angle_diff = tools.to_min_pi_plus_pi(np.rad2deg(angles_ch0 - angles_ch1))

            # angles = np.angle(iq_samples, deg=True)
            # angle_diff = angles[0, :] - angles[1, :]
            # idx = angle_diff > 180.0
            # angle_diff[idx] = angle_diff[idx] - 360.0

            # "meas_id", "node_id", "rx_gain", "rx_gain_diff", "angle_diff"

            max_I = np.max(np.abs(np.real(iq_samples[0, :])))
            max_Q = np.max(np.abs(np.imag(iq_samples[0, :])))

            max_IQ_vals_ch0 = max_I if max_I > max_Q else max_Q

            max_I = np.max(np.abs(np.real(iq_samples[1, :])))
            max_Q = np.max(np.abs(np.imag(iq_samples[1, :])))

            max_IQ_vals_ch1 = max_I if max_I > max_Q else max_Q

            node_id = meas.split("_")[0]
            meas_id = meas.split("_")[-1]

            gain = gain_sweeps[suffix_number - 1]

            # d = {
            #     "exp_id": [meas_id] * len(angle_diff),
            #     "node_id": [node_id] * len(angle_diff),
            #     "rx_gain": [gain] * len(angle_diff),
            #     "rx_gain_diff": [gain - 31] * len(angle_diff),
            #     "angle_diff": angle_diff,
            #     "real_diff": [SCOPE_ANGLE] * len(angle_diff),
            #     "rx_ch0_gain": [rx_ch0_gain]* len(angle_diff),
            # }

            d = {
                "exp_id": meas_id,
                "node_id": node_id,
                "rx_gain": gain,
                "rx_gain_diff": gain - rx_ch0_gain,
                "angle_diff": np.mean(angle_diff),
                "real_diff": SCOPE_ANGLE,
                "angle_diff_std": np.std(np.abs(angle_diff)),
                "max_IQ_ampl_ch0": max_IQ_vals_ch0,
                "max_IQ_ampl_ch1": max_IQ_vals_ch1,
                "rx_ch0_gain": rx_ch0_gain,
            }

            df_list.append(d)

    df = pd.DataFrame(df_list)

    df.to_csv(f"{meas}.csv", index=False)
