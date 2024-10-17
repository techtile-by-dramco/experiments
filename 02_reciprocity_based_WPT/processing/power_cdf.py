# script to compute the power distribution
from TechtilePlotter.TechtilePlotter import TechtilePlotter
import numpy as np
from Positioner import PositionerValues
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.colors as mcolors

# to_plot = [
#     "nobf-D07-ceiling",
#     "nobf-ceiling",
#     "bf-ceiling",
#     "bf-ceiling-2",
#     "bf-ceiling-3"]

to_plot = [
    "bf-ceiling-grid-merged-20241013074614",
    "randombf-ceiling-grid-2",
    "nobf-ceiling-E08-grid-1",
    "gausbf-ceiling-grid-pidiv2",
    # "nobf-ceiling-E07-grid-1",
    # "nobf-ceiling-D07-grid-1",
]  # "bf-ceiling-grid",

labels = ["BF", "AS", "SISO E08", "SISO E07", "SISO D07"]


heatmap = None

fig, axes = plt.subplots()

wavelen = 3e8 / 920e6

colors = list(mcolors.TABLEAU_COLORS)


for i, (tp, label) in enumerate(zip(to_plot,labels)):

    positions = np.load(f"../data/positions-{tp}.npy", allow_pickle=True)
    values = np.load(f"../data/values-{tp}.npy", allow_pickle=True)

    print(f"Processing {len(positions)} samples")

    # valid_values_idx = values > -100

    # positions = positions[valid_values_idx]
    # values = values[valid_values_idx]

    positions_list = PositionerValues(positions)

    grid_pos_ids, xi, yi = positions_list.group_in_grids(
        wavelen/2, min_x=2.50, max_x=4.00, min_y=1.00, max_y=2.5
    )

    heatmap = [[[] for _ in xi] for _ in yi]

    max_power = -200

    for i_x, grid_along_y in enumerate(grid_pos_ids):
        for i_y, grid_along_xy_ids in enumerate(grid_along_y):
            heatmap[i_x][i_y].extend(values[grid_along_xy_ids])
            if i == 0: #THIS IS BF CASE
                if np.median(values[grid_along_xy_ids]) > max_power:
                    max_power = np.median(values[grid_along_xy_ids])
                    x_bf = i_x
                    y_bf = i_y

    _all = []
    for ix, row in enumerate(heatmap):
        for iy, cell in enumerate(row):
            _all.extend(cell)

    _all_nobf = []
    _all_bf = []
    for ix, row in enumerate(heatmap):
        for iy, cell in enumerate(row):
            if ix == x_bf and iy == y_bf:
                _all_bf.extend(cell)
            else:
                _all_nobf.extend(cell)

    x = np.sort(_all_nobf)
    y = np.linspace(0, 1, len(_all_nobf), endpoint=False)
    axes.plot(x, y, label=f"outside BF - {label}", c=colors[i], ls="--")
    idx_intersect = np.argmin(np.abs(y-0.5))
    # plt.vlines(x[idx_intersect], ymax=y[idx_intersect], ymin=0, ls="--", color="gray")

    x = np.sort(_all_bf)
    y = np.linspace(0, 1, len(_all_bf), endpoint=False)
    axes.plot(x, y, label=f"inside BF - {label}", c=colors[i])
    idx_intersect = np.argmin(np.abs(y - 0.5))
    # plt.vlines(
    #     x[idx_intersect], ymax=y[idx_intersect], ymin=0, ls="--", color="gray"
    # )

    # x = np.sort(_all)
    # y = np.linspace(0, 1, len(_all), endpoint=False)
    # axes.plot(
    #     x,
    #     y,
    #     label=f"{tp}",
    # )
    # idx_intersect = np.argmin(np.abs(y-0.5))
    # plt.vlines(x[idx_intersect], ymax=y[idx_intersect], ymin=0, ls="--", color="gray")

    x = np.sort(_all_bf)
    y = np.linspace(0, 1, len(_all_bf), endpoint=False)
    axes.plot(
        x,
        y,
        label=f"inside BF - {label}",
    )
    # idx_intersect = np.argmin(np.abs(y - 0.5))
    # plt.vlines(
    #     x[idx_intersect], ymax=y[idx_intersect], ymin=0, ls="--", color="gray"
    # )

    # x = np.sort(_all)
    # y = np.linspace(0, 1, len(_all), endpoint=False)
    # axes.plot(
    #     x,
    #     y,
    #     label=f"{tp}",
    # )
    # # idx_intersect = np.argmin(np.abs(y-0.5))
    # plt.vlines(x[idx_intersect], ymax=y[idx_intersect], ymin=0, ls="--", color="gray")

# plt.hlines(0.5, ls="--", xmax=-42, xmin=-70)
# heatmap = heatmap / len(to_plot)
plt.xlim(xmin=-80)
plt.legend()
fig.tight_layout()

import tikzplotlib

tikzplotlib.clean_figure()
tikzplotlib.save("power-cdf.tex", float_format=".4g")


plt.show()
