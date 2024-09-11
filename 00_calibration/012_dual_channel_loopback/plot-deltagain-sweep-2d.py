"""This script plots the processed deltaGain sweep experiments. First run process_gain_sweep_meas.py prior to running this file.
"""


import matplotlib.pyplot as plt
import numpy as np
import yaml

import matplotlib.colors as mcolors
import pandas as pd

import seaborn as sns
import tools

import plotly.graph_objects as go
import plotly.express as px


to_process = [False, False, True, True]
measurements = [
    "T03_20240909114249",
    "T04_20240909190225",
    "T04_20240910062816",
    "T03_20240910085457",
]

max_gains = [78, 44, None, None]
min_gains = [0, 10, None, None]
NUM_MEAS_PER_EXPS = [2, 2, 1, 1]
scope_angles = [
    -(277.1 - 360),
    -83.75,
    83.75,
    83.75,
]  # measured angle diff on the scope


linestyles = ["dashed", "dashed", "dotted", "dotted"]
colors = list(mcolors.TABLEAU_COLORS)

plt.figure()
for meas, SCOPE_ANGLE, NUM_MEAS_PER_EXP, max_gain, min_gain, tp in zip(
    measurements,
    scope_angles,
    NUM_MEAS_PER_EXPS,
    max_gains,
    min_gains,
    to_process,
    strict=True,  # ensure equqal length arss in zip (in Python 3.10)
):
    if not tp:
        continue
    df = pd.read_csv(f"{meas}.csv")

    df["phase_error"] = tools.to_min_pi_plus_pi(df["angle_diff"] - df["real_diff"], deg=True)

    fig = go.Figure(
        data=[
            go.Scatter3d(
                z=df["angle_diff"] - df["real_diff"],
                x=df["rx_gain_ch0"],
                y=df["rx_gain_ch1"],
                mode="markers",
            )
        ]
    )
    fig.update_scenes(yaxis_autorange="reversed")
    # fig = px.surface_3d(df, x="rx_gain_ch0", y="rx_gain_ch1", z="angle_diff")
    fig.show()

    x_vals = np.sort(df["rx_gain_ch0"].unique())
    y_vals = np.sort(df["rx_gain_ch1"].unique())
    z_vals = np.zeros(shape=(len(x_vals), len(y_vals)))

    for ix, x in enumerate(x_vals):
        for iy, y in enumerate(y_vals):
            qry = df.query(f"rx_gain_ch0=={x} and rx_gain_ch1=={y}")
            if qry is not None and not qry.empty:
                selected_row = qry.iloc[0]
                z_vals[ix, iy] = selected_row["phase_error"]
            else:
                z_vals[ix, iy] = None

    fig = go.Figure(data=[go.Surface(z=z_vals, x=x_vals, y=y_vals)])
    fig.write_html(f"2d-sweep-{meas}.html")
    fig.show()

    selected_df1 = df.query("rx_gain_ch1==37")
    selected_df2 = df.query("rx_gain_ch1==20")

    plt.plot(
        selected_df1["rx_gain_ch0"],
        selected_df1["phase_error"],
        label=f"37 ({meas})",
        alpha=0.5,
        # s=2,
    )
    plt.plot(
        selected_df2["rx_gain_ch0"],
        selected_df2["phase_error"],
        label=f"20 ({meas})",
        alpha=0.5,
        # s=2,
    )
    plt.ylim(-180.0,180.0)
    plt.legend()

plt.show()
