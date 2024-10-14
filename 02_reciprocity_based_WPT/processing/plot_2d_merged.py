from TechtilePlotter.TechtilePlotter import TechtilePlotter
import numpy as np
from Positioner import PositionerValues
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.ndimage import zoom


to_plot = [
    # "nobf-D07-ceiling",
    # "nobf-ceiling",
    # "bf-ceiling",
    # "bf-ceiling-2",
    # "bf-ceiling-3",
    # "bf-ceiling-grid-2",
    # "bf-ceiling-grid-3",
    # "bf-ceiling-grid-4",
    # "bf-ceiling-grid-5",
    # "bf-ceiling-grid-6",
    # "bf-ceiling-grid-7",
    # "bf-ceiling-bf-grid-8",
    # "bf-ceiling-grid-9",
    "bf-ceiling-grid-2-20241012210548",
    "bf-ceiling-grid-3-20241012210548",
]

# to_plot = ["bf-ceiling-grid-2-20241012210548"]  # "bf-ceiling-grid",

heatmaps = [0] * len(to_plot)

wavelen = 3e8 / 920e6

all_positions = []
all_values = []

for i, tp in enumerate(to_plot):

    positions = np.load(f"../data/positions-{tp}.npy", allow_pickle=True)
    values = np.load(f"../data/values-{tp}.npy", allow_pickle=True)

    print(f"Reading {len(positions)} samples")

    all_positions.extend(positions.tolist())
    all_values.extend(values.tolist())

    # valid_values_idx = values>-90

    # positions = positions[valid_values_idx]
    # values = values[valid_values_idx]

print(f"Processing {len(all_values)} samples")
positions_list = PositionerValues(all_positions)

grid_pos_ids, xi, yi = positions_list.group_in_grids(
    wavelen/8.0, min_x=2.6, max_x=3.9, min_y=1.20, max_y=2.45
)
heatmap = np.zeros(shape=(len(yi), len(xi))) - 200

for i_x, grid_along_y in enumerate(grid_pos_ids):
    for i_y, grid_along_xy_ids in enumerate(grid_along_y):
        heatmap[i_x, i_y] = np.mean(
            [10 ** (all_values[_id] / 10) for _id in grid_along_xy_ids]
        )
        if 0 in grid_along_xy_ids:
            x_bf = i_x
            y_bf = i_y


fig, ax = plt.subplots()
zoom_val = 10
upsampled_heatmap = zoom(heatmap, zoom=zoom_val, order=1)
p = ax.imshow(10 * np.log10(upsampled_heatmap))
ax.set_xticks(
    np.arange(len(xi))* zoom_val, labels=[f"{(x-xi[0])/wavelen:.2f}" for x in xi]
)
ax.set_yticks(
    np.arange(len(yi)) * zoom_val,
    labels=[f"{(y-yi[0])/wavelen:.2f}" for y in yi],
)
# ax.add_patch(
#     Rectangle((y_bf - 0.5, x_bf - 0.5), 1, 1, fill=False, edgecolor="red", lw=3)
# )
fig.colorbar(p)
fig.tight_layout()
plt.show()
