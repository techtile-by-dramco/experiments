from TechtilePlotter.TechtilePlotter import TechtilePlotter
import numpy as np
from Positioner import PositionerValues
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

to_plot = [
    "bf-ceiling-bf-grid-8",
    "gausbf-ceiling-grid-pidiv8",
    "gausbf-ceiling-grid-pidiv4",
]  # "bf-ceiling-grid",

log_heatmap = np.zeros(len(to_plot)).tolist()

fig, axes = plt.subplots(1, len(to_plot), sharex=True, sharey=True)

for i, tp in enumerate(to_plot):

    positions = np.load(f"../data/positions-{tp}.npy", allow_pickle=True)
    values = np.load(f"../data/values-{tp}.npy", allow_pickle=True)

    print(f"Processing {len(positions)} samples")

    valid_values_idx = values>-90

    positions = positions[valid_values_idx]
    values = values[valid_values_idx]

    positions_list = PositionerValues(positions)

    grid_pos_ids, xi, yi = positions_list.group_in_grids(
        0.03, min_x=2.50, max_x=4.00, min_y=1.00, max_y=2.5
    )

    heatmap = np.zeros(shape=(len(yi), len(xi))) - 200

    for i_x, grid_along_y in enumerate(grid_pos_ids):
        for i_y, grid_along_xy_ids in enumerate(grid_along_y):
            heatmap[i_x, i_y] = np.mean([10**(values[_id]/10) for _id in grid_along_xy_ids])
            if 0 in grid_along_xy_ids:
                x_bf = i_x
                y_bf = i_y

    # fig, ax = plt.subplots()
    # plt.title(tp)
    log_heatmap[i] = 10 * np.log10(heatmap)

    _log_heatmap = 10 * np.log10(heatmap)

    max_val = np.nanmax(_log_heatmap)

    print(max_val)

    no_power_spot_idx = _log_heatmap < max_val - 3

    _log_heatmap[no_power_spot_idx] = np.nan

    p = axes[i].imshow(_log_heatmap, vmin=-85, vmax=-40, cmap="viridis")
    axes[i].set_xticks(np.arange(len(xi)), labels=[f"{x:.2f}" for x in xi])
    axes[i].set_yticks(np.arange(len(yi)), labels=[f"{y:.2f}" for y in yi])
    axes[i].add_patch(
        Rectangle((y_bf - 0.5, x_bf - 0.5), 1, 1, fill=False, edgecolor="red", lw=3)
    )
fig.colorbar(p)
fig.tight_layout()
plt.show()
