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

to_plot = ["bf-ceiling-grid-2", "bf-ceiling-grid-3", "bf-ceiling-grid-4", "bf-ceiling-grid-5", "bf-ceiling-grid-6", "bf-ceiling-grid-7"]  # "bf-ceiling-grid",

heatmap = None

for i, tp in enumerate(to_plot):

    positions = np.load(f"../data/positions-{tp}.npy", allow_pickle=True)
    values = np.load(f"../data/values-{tp}.npy", allow_pickle=True)

    print(f"Processing {len(positions)} samples")

    valid_values_idx = values>-90

    positions = positions[valid_values_idx]
    values = values[valid_values_idx]

    positions_list = PositionerValues(positions)

    grid_pos_ids, xi, yi = positions_list.group_in_grids(0.03, min_x=2.50, max_x=4.00, min_y=1.00, max_y=2.5)

    if heatmap is None:
        heatmap = [[[] for _ in xi] for _ in yi]

    for i_x, grid_along_y in enumerate(grid_pos_ids):
        for i_y, grid_along_xy_ids in enumerate(grid_along_y):
            heatmap[i_x][i_y].extend([10 ** (values[_id] / 10) for _id in grid_along_xy_ids]) 
            if 0 in grid_along_xy_ids:
                x_bf = i_x
                y_bf = i_y

log_heatmap = np.zeros(shape=(len(heatmap), len(heatmap[0])))
for ix in range(len(log_heatmap)):
    for iy in range(len(log_heatmap[0])):
        log_heatmap[ix, iy] = 10 * np.log10(np.mean(heatmap[ix][iy]))
# heatmap = heatmap / len(to_plot)
fig, ax = plt.subplots()
p = ax.imshow(log_heatmap, cmap="viridis")
ax.set_xticks(np.arange(len(xi)), labels=[f"{x:.2f}" for x in xi])
ax.set_yticks(np.arange(len(yi)), labels=[f"{y:.2f}" for y in yi])
ax.add_patch(Rectangle((y_bf-0.5, x_bf-0.5), 1, 1, fill=False, edgecolor="red", lw=3))
fig.colorbar(p)
fig.tight_layout()
plt.show()
