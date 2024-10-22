"positions-"

from TechtilePlotter.TechtilePlotter import TechtilePlotter
import numpy as np
from Positioner import PositionerValues
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.ndimage import zoom


# to_plot = [
#     "nobf-D07-ceiling",
#     "nobf-ceiling",
#     "bf-ceiling",
#     "bf-ceiling-2",
#     "bf-ceiling-3"]


heatmap = None

stds = np.rad2deg(
    [j * np.pi / 180.0 for j in np.arange(0, 185, 5) for _ in range(1)]
)

std_options = np.arange(0, 185, 5)
# 20241015150457 (ging boven 180 graden) to be merged
#  20241015154322

sols = [0] * len(std_options)
plt.figure()
for i in range(1053):

    idx = int(i % len(std_options))

    std = std_options[idx] * np.pi / 180.0
    # positions = np.load(
    #     f"../data/positions-gausbf-ceiling-grid-{i+1}-20241015154322-{i+1}.npy",
    #     allow_pickle=True,
    # )
    values = np.load(
        f"../data/values-gausbf-ceiling-grid-{i+1}-20241015154322-{i+1}.npy",
        allow_pickle=True,
    )
    _mean = np.mean(10 ** (values / 10))
    if type(sols[idx]) is not list:
        sols[idx] = []
    sols[idx].append(_mean)
    if idx == len(std_options) - 1 or idx == 0:
        continue
    plt.scatter(np.rad2deg(std), 10 * np.log10(_mean), color="black", s=2.0)
    scatter_points.append((np.rad2deg(std), 10 * np.log10(_mean)))

upper_stds = [0]*len(std_options)
down_stds = [0] * len(std_options)
means = [0] * len(std_options)
print(f"x, y")
for i, std_opt in enumerate(std_options):
    upper_stds[i] = 10 * np.log10(np.mean(sols[i]) + np.std(sols[i]))
    down_stds[i] = 10 * np.log10(np.mean(sols[i]) - np.std(sols[i]))
    means[i] = 10 * np.log10(np.median(sols[i]))
    plt.scatter(
        np.rad2deg(std_options[i] * np.pi / 180.0),
        10 * np.log10(np.mean(sols[i])),
        c="blue",
        s=2.0,
    )

# plt.plot(np.rad2deg(std_options*np.pi / 180.0), means, color="blue", alpha=0.5)
# plt.fill_between(
#     np.rad2deg(std_options * np.pi / 180.0),
#     y1=upper_stds,
#     y2=down_stds,
#     color="blue",
#     alpha=0.2,
# )
plt.hlines(
    10 * np.log10(np.max(sols[0])),
    xmin=0,
    xmax=180,
    label="BF" + f" { 10 * np.log10(np.max(sols[0])):.2f}dB",
)

to_plot = [
    "randombf-ceiling-grid-2",
    "nobf-ceiling-E08-grid-1",
    "nobf-ceiling-E07-grid-1",
    "nobf-ceiling-D07-grid-1",
] 

labels = [
    "AS",
    "SISO E08",
    "SISO E07",
    "SISO D07"
]
colors = ["red", "blue", "blue", "blue"]

for label, tp, c in zip(labels, to_plot, colors):
    values = np.load(
            f"../data/values-{tp}.npy",
            allow_pickle=True,
        )
    positions = np.load(
        f"../data/positions-{tp}.npy",
        allow_pickle=True,
    )
    valid_idx = []
    p0 = positions[0]
    for i, p in enumerate(positions):
        if p0.x- 0.05 > p.x <  p0.x + 0.05 and  p0.y- 0.05 > p.y < p0.y + 0.05:
            valid_idx.append(i)

    print(len(valid_idx))
    plt.hlines(
        10 * np.log10(np.mean(10 ** (values[valid_idx] / 10))), xmin=0, xmax=180, label=label+f" {10 * np.log10(np.mean(10 ** (values[valid_idx] / 10))):.2f}dB", color=c
    )
plt.ylabel("RSS")
plt.xlabel("Applied std in degrees")

plt.tight_layout()

# import tikzplotlib

# tikzplotlib.save("plot_gaus_gain.tex", float_format=".2g")

import csv

with open("gaus_gain.csv", "w") as f:
    f.write("x, y\\\\\n")
    for row in scatter_points:
        f.write(f"{row[0]}, {row[1]}\\\\\n")

plt.show()
