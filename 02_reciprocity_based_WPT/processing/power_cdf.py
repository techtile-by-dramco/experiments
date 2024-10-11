# script to compute the power distribution
from TechtilePlotter.TechtilePlotter import TechtilePlotter
import numpy as np
from Positioner import PositionerValues
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


# to_plot = [
#     "nobf-D07-ceiling",
#     "nobf-ceiling",
#     "bf-ceiling",
#     "bf-ceiling-2",
#     "bf-ceiling-3"]

to_plot = ["randombf-ceiling-grid-2", "bf-ceiling-sinlge-point-1"]  # "bf-ceiling-grid",
heatmap = None

fig, axes = plt.subplots(1, 2)

for i, tp in enumerate(to_plot):

    positions = np.load(f"../data/positions-{tp}.npy", allow_pickle=True)
    values = np.load(f"../data/values-{tp}.npy", allow_pickle=True)

    print(f"Processing {len(positions)} samples")

    valid_values_idx = values > -90

    positions = positions[valid_values_idx]
    values = values[valid_values_idx]

    positions_list = PositionerValues(positions)

    grid_pos_ids, xi, yi = positions_list.group_in_grids(
        0.4, min_x=2.50, max_x=4.00, min_y=1.00, max_y=2.5
    )

    heatmap = [[[] for _ in xi] for _ in yi]

    for i_x, grid_along_y in enumerate(grid_pos_ids):
        for i_y, grid_along_xy_ids in enumerate(grid_along_y):
            heatmap[i_x][i_y].extend(values[grid_along_xy_ids])
            if 0 in grid_along_xy_ids:
                x_bf = i_x
                y_bf = i_y

    

    _all = []
    for ix, row in enumerate(heatmap):
        for iy, cell in enumerate(row):
            print(len(cell))
            axes[0].plot(
                np.sort(cell),
                np.linspace(0, 1, len(cell), endpoint=False),
                # label=f"({ix},{iy})",
            )
            _all.extend(cell)

    axes[1].plot(
        np.sort(_all),
        np.linspace(0, 1, len(_all), endpoint=False),
        label="ALL",
    )
# heatmap = heatmap / len(to_plot)
plt.legend()
fig.tight_layout()
plt.show()
