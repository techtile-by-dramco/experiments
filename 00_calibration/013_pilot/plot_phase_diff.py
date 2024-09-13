import matplotlib.pyplot as plt
import numpy as np
import yaml
import os
import re
import tools

import matplotlib.colors as mcolors


with open("cal-settings.yml", "r") as file:
    vars = yaml.safe_load(file)
    RATE = vars["RATE"]


import glob


MIN_Y = -7.5
MAX_Y = 7.5


# MEAS 1: T04_20240905130028
# MEAS 2: T04_20240905140237
# MEAS 3: T03_20240905144640

# measurements = [
#     "T04_20240905130028",
#     "T04_20240905140237",
#     "T03_20240905144640",
#     "T03_20240906082810", # forgot to enable RF generator, we can ignore this measurement
# ]

measurements = ["T03_20240906123800", "T04_20240906123807", "T04_20240909130803"]
to_plot = [False, False, True]
NUM_MEAS_PER_EXPS = [2, 2, 2]
scope_angles = [125.1, 122.3,  -83.75]  # measured angle diff on the scope
gains_sweeps = [40, 40, 76]


# scope_angles = [-151.8, -151.8, -151.8, -51.8]  # measured angle diff on the scope
linestyles = ["dashed", "dotted", "solid"]
colors = list(mcolors.TABLEAU_COLORS)


for meas, ls, SCOPE_ANGLE, NUM_MEAS_PER_EXP, tp, max_gain in zip(
    measurements, linestyles, scope_angles, NUM_MEAS_PER_EXPS, to_plot, gains_sweeps
):
    if not tp:
        continue

    # Define the file pattern
    pattern = "data_"+meas+r"_(\d+)\.npy"
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
            num_files_found+=1
            print(f"{base_name} found")

    print(f"{num_files_found} files found")
    array_list = [0] * num_files_found
    all_iq_samples_list = [0] * num_files_found

    window_sizes_list = [0] * num_files_found

    # plt.figure()
    gains = np.zeros(num_files_found)
    mean_angles = np.zeros(num_files_found)

    gain_sweeps = np.asarray(range(max_gain+1))[::-1]  # reverse as started from 39
    gain_sweeps = np.repeat(gain_sweeps, NUM_MEAS_PER_EXP).flatten()

    # Iterate over each file and load it using np.load, then append to the list
    for filename in glob.glob("data/*.npy"):
        base_name = os.path.basename(filename)  # Get just the filename part
        # Check if the filename matches the regex
        if compiled_pattern.match(base_name):
            match = re.search(pattern, filename)
            assert match
            suffix_number = int(match.group(1))
            print(f'Reading file {suffix_number}')
            file_list.append(filename)
            iq_samples = np.load(filename)

            angles_ch0 = tools.get_phases_and_remove_CFO(iq_samples[0, :])
            angles_ch1 = tools.get_phases_and_remove_CFO(iq_samples[1, :])

            # angles_ch0 = np.angle(iq_samples[0, :])
            # angles_ch1 = np.angle(iq_samples[1, :])

            angle_diff = tools.to_min_pi_plus_pi(np.rad2deg(angles_ch0 - angles_ch1))

            array_list[suffix_number-1] = angle_diff
            mean_angles[suffix_number - 1] = np.mean(angle_diff)
            all_iq_samples_list[suffix_number-1] = iq_samples

            gains[suffix_number - 1] = gain_sweeps[suffix_number - 1]

            window_sizes_list[suffix_number - 1] = iq_samples.shape[-1]
            print(f"Num samples: {iq_samples.shape[-1]}")

    # plt.scatter(gain_sweeps, mean_angles + SCOPE_ANGLE)
    # plt.show(block=False)

    # Combine all arrays into a single array
    angles_degrees = np.concatenate(array_list)
    all_iq_samples = np.hstack(all_iq_samples_list)

    _min = np.min(angles_degrees)
    _max = np.max(angles_degrees)

    print(all_iq_samples.shape)

    # compute mean per window (NOTE no moving average! as in real-scenario this will also not be the case)
    num_total_samples = len(angles_degrees)

    window_sizes_sec = [0.1] #[0.1,0.5,1,2] 

    max_deg_value = -360

    fig, ax = plt.subplots()
    plt.title(meas)

    ax2 = ax.twinx()

    ax2.set_ylabel("max. amplitude I / Q", color="green")
    ax2.spines["right"].set_color("green")
    ax2.tick_params(axis="y", colors="green")
    ax2.set_ylim(-0.02, 1.02)

    for i_nw, nw in enumerate(window_sizes_sec):
        window_size = RATE * nw
        num_windows = int(num_total_samples // window_size)
        mean_angles_degrees = np.zeros(num_windows)
        x = [0] * num_windows
        max_IQ_vals = np.zeros(num_windows)
        mean_I_vals = np.zeros(num_windows)
        mean_Q_vals = np.zeros(num_windows)
        std_angles_degrees = np.zeros(num_windows)
        for n in range(num_windows):

            window_slice = slice(int(n*window_size),int((n+1)*window_size))

            mean_angles_degrees[n] = np.mean(angles_degrees[window_slice])
            std_angles_degrees[n] = np.std(angles_degrees[window_slice])

            if i_nw ==0:

                abs_I = np.abs(np.real(all_iq_samples[:, window_slice]))
                abs_Q = np.abs(np.imag(all_iq_samples[:, window_slice]))

                max_I = np.max(abs_I)
                max_Q = np.max(abs_Q)

                mean_I = np.mean(abs_I)
                mean_Q = np.mean(abs_Q)

                max_IQ_vals[n] = max_I if max_I > max_Q else max_Q

                mean_I_vals[n] = mean_I
                mean_Q_vals[n] = mean_Q

                max_deg_value = (
                    max_deg_value
                    if max_deg_value > mean_angles_degrees[n]
                    else mean_angles_degrees[n]
                )
            x[n] = n * window_size/RATE

        if i_nw == 0:
            ax2.plot(x, max_IQ_vals, ls=ls, label=f"max IQ {nw}s", color="green")
            ax2.plot(x, mean_I_vals, label=f"avg I {nw}s", color="green", ls="--")
            ax2.plot(
                x, mean_Q_vals, label=f"avg Q {nw}s", color="green", ls="--"
            )

        ax.plot(
            x,
            np.asarray(mean_angles_degrees) + SCOPE_ANGLE,
            label=f"Average angle difference (window of {nw}s)",
            alpha=0.8,
            ls=ls,
            color=colors[i_nw]
        )
        ax.fill_between(
            x,
            mean_angles_degrees - std_angles_degrees + SCOPE_ANGLE,
            mean_angles_degrees + std_angles_degrees + SCOPE_ANGLE,
            color=colors[i_nw],
            ls=ls,
            alpha=0.2,
        )

    # plot measurement ID
    gain_vals_x = []
    gain_vals_y = []
    for file in file_list:
        num_samples = len(np.load(file)[0,:])
        match = re.search(pattern, file)
        if match:
            suffix_number = int(match.group(1))
            print(f"Processing file: {file}, Suffix number: {suffix_number}")

            print(suffix_number * (num_samples // 2) / RATE)

            if int(suffix_number-1) % NUM_MEAS_PER_EXP == 0:
                if(76 - (suffix_number - 1) // 2 ) % 2 == 0:
                    # to create alternating pattern
                    ax.axvspan(
                        (suffix_number - 1) * (num_samples / RATE),
                        (suffix_number - 1) * (num_samples / RATE)
                        + NUM_MEAS_PER_EXP*(num_samples / RATE),
                        alpha=0.05,
                        color="red",
                    )
                gain_vals_x.append(
                    (suffix_number - 1) * (num_samples / RATE)
                    + (NUM_MEAS_PER_EXP * (num_samples / RATE)/2)
                )
                gain_vals_y.append(76 - (suffix_number - 1) // 2)
            #     ax.vlines(
            #         x=(suffix_number - 1) * (num_samples / RATE),
            #         ymin=MIN_Y,
            #         ymax=MAX_Y,
            #         linestyles="dashed",
            #         color="red",
            #         alpha=0.2,
            #     )
            #     ax.annotate(
            #         76 - (suffix_number-1)//2,
            #         xy=(
            #             (suffix_number - 1) * (num_samples / RATE)
            #             + (num_samples // 2) / RATE,
            #             max_deg_value + 1,
            #         ),
            #         xytext=(
            #             (suffix_number - 1) * (num_samples / RATE)
            #             + (num_samples // 2) / RATE,
            #             max_deg_value + 1,
            #         ),
            #         # arrowprops=dict(facecolor="green", shrink=0.01),
            #     )

            # ax.vlines(
            #     x=(suffix_number - 1) * (num_samples / RATE),
            #     ymin=MIN_Y,
            #     ymax=MAX_Y,
            #     linestyles="dashed",
            #     alpha=0.1,
            # )

            # ax.annotate(
            #     suffix_number,
            #     xy=(
            #         (suffix_number - 1) * (num_samples / RATE) + (num_samples // 2) / RATE,
            #         max_deg_value + 1,
            #     ),
            #     xytext=(
            #         (suffix_number - 1) * (num_samples / RATE) + (num_samples // 2) / RATE,
            #         max_deg_value+1,
            #     ),
            #     # arrowprops=dict(facecolor="green", shrink=0.01),
            # )

    total_mean = np.mean(angles_degrees)
    # ax.hlines(
    #     total_mean,
    #     xmin=0,
    #     xmax=num_total_samples / RATE, ls=ls,
    #     label=f"total mean {total_mean:.2f} degrees",
    # )

    sec = ax.secondary_xaxis(location=1)
    sec.set_xticks(
        gain_vals_x,
        labels=gain_vals_y,
    )
    sec.xaxis.label.set_color("red")
    sec.tick_params(axis="x", colors="red")
    # sec.xaxis.grid(True)
    # for x in gain_vals_x:
    #     ax.axvline(x, color="red", zorder=-1, linestyle="--", linewidth=0.5)

    ax.hlines(0.0, xmin=-5, xmax=(num_total_samples / RATE) + 20, color="red")

    ax.set_ylim(MIN_Y, MAX_Y)
    ax.legend()
    ax2.legend()

    import tikzplotlib

    tikzplotlib.save("phase_diff_same_gain.tex")
    plt.show()
