"""This script plots the processed deltaGain sweep experiments. First run process_gain_sweep_meas.py prior to running this file.
"""


import matplotlib.pyplot as plt
import numpy as np
import yaml

import matplotlib.colors as mcolors
import pandas as pd

import seaborn as sns
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

linestyles = ["dashed", "dashed", "dotted", "dotted"]
colors = list(mcolors.TABLEAU_COLORS)


# header: exp_id, meas_id, node_id, rx_gain, rx_gain_diff, angle_diff
columns = ["exp_id", "node_id", "rx_gain", "rx_gain_diff", "angle_diff"]


for meas, gs, mst, NUM_MEAS_PER_EXP in zip(
    measurements, gains_sweeps, to_process, NUM_MEAS_PER_EXPS, strict=True
):
    if mst:
        gain_sweeps = np.asarray(range(gs + 1))[::-1]
        gain_sweeps = np.repeat(gain_sweeps, NUM_MEAS_PER_EXP)
        df = pd.read_csv(f"{meas}.csv")

        df["rx_gain_diff"] = tools.to_min_pi_plus_pi(df["rx_gain_diff"])
        g = sns.scatterplot(data=df, x="rx_gain_diff", y="angle_diff")
        g.axes.axhline(-df["real_diff"].iloc[0], ls="--", color="red")

        # save the plot as PNG file
        # plt.savefig(f"{meas}.png")
        plt.title(meas + f" {df['rx_ch0_gain'].iloc[0]}" + "dB")
        # g.axes.set_xticks((gain_sweeps[::-1] - df["rx_ch0_gain"].iloc[0]), minor=True)
        # plt.grid(which="minor", alpha=0.2)
        plt.grid(axis="x")
        plt.show(block=False)

        plt.figure()
        g = sns.scatterplot(data=df, x="rx_gain_diff", y="max_IQ_ampl_ch0")
        g = sns.scatterplot(data=df, x="rx_gain_diff", y="max_IQ_ampl_ch1")
        plt.title(meas + f"{df['rx_ch0_gain'].iloc[0]}" + "dB")
        # g.axes.set_xticks(gain_sweeps[::-1] - df["rx_ch0_gain"].iloc[0], minor=True)
        # plt.grid(which="minor", alpha=0.2)
        plt.grid(axis="x")
        plt.show(block=False)

        plt.figure()
        g = sns.scatterplot(data=df, x="rx_gain_diff", y="angle_diff_std")
        plt.title(meas + f" {df['rx_ch0_gain'].iloc[0]}" + "dB")
        # g.axes.set_xticks(gain_sweeps[::-1] - df["rx_ch0_gain"].iloc[0], minor=True)
        # plt.grid(which="minor", alpha=0.2)
        plt.grid(axis="x")
        plt.show(block=False)

        plt.show()
