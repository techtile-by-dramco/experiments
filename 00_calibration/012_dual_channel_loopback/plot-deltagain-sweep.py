"""This script plots the processed deltaGain sweep experiments. First run process_gain_sweep_meas.py prior to running this file.
"""


import matplotlib.pyplot as plt
import numpy as np
import yaml

import matplotlib.colors as mcolors
import pandas as pd

import seaborn as sns
import tools


to_process = [False, False, True]

measurements = ["T03_20240911105349", "T04_20240911105338", "T04_20240911192544"]

for meas, process in zip(
    measurements,
    to_process,
    strict=True,  # ensure equqal length arss in zip (in Python 3.10)
):
    if process:
        df = pd.read_csv(f"{meas}.csv")

        df["rx_gain_diff"] = tools.to_min_pi_plus_pi(df["rx_gain_diff"])
        g = sns.scatterplot(data=df, x="rx_gain_diff", y="angle_diff")

        # save the plot as PNG file
        # plt.savefig(f"{meas}.png")
        plt.title(meas + f" {df['rx_gain_ch0'].iloc[0]}" + "dB")
        # g.axes.set_xticks((gain_sweeps[::-1] - df["rx_ch0_gain"].iloc[0]), minor=True)
        # plt.grid(which="minor", alpha=0.2)
        plt.grid(axis="x")
        plt.show(block=False)

        plt.figure()
        g = sns.scatterplot(data=df, x="rx_gain_diff", y="max_IQ_ampl_ch0")
        g = sns.scatterplot(data=df, x="rx_gain_diff", y="max_IQ_ampl_ch1")
        plt.title(meas + f"{df['rx_gain_ch0'].iloc[0]}" + "dB")
        # g.axes.set_xticks(gain_sweeps[::-1] - df["rx_ch0_gain"].iloc[0], minor=True)
        # plt.grid(which="minor", alpha=0.2)
        plt.grid(axis="x")
        plt.show(block=False)

        plt.figure()
        g = sns.scatterplot(data=df, x="rx_gain_diff", y="angle_diff_std")
        plt.title(meas + f" {df['rx_gain_ch0'].iloc[0]}" + "dB")
        # g.axes.set_xticks(gain_sweeps[::-1] - df["rx_ch0_gain"].iloc[0], minor=True)
        # plt.grid(which="minor", alpha=0.2)
        plt.grid(axis="x")
        plt.show(block=False)

        plt.show()
