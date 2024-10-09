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

to_plot = ["bf-ceiling-grid-4"]  # "bf-ceiling-grid",

log_heatmap = np.zeros(len(to_plot)).tolist()

for i, tp in enumerate(to_plot):

    positions = np.load(f"positions-{tp}.npy", allow_pickle=True)
    values = np.load(f"values-{tp}.npy", allow_pickle=True)

    print(f"Processing {len(positions)} samples")

    valid_values_idx = values>-90

    positions = positions[valid_values_idx]
    values = values[valid_values_idx]

    positions_list = PositionerValues(positions)

    grid_pos_ids, xi, yi = positions_list.group_in_grids(0.1, min_x=0, max_x=8, min_y=0, max_y=4)

    heatmap = np.zeros(shape=(len(yi), len(xi))) - 200

    for i_x, grid_along_y in enumerate(grid_pos_ids):
        for i_y, grid_along_xy_ids in enumerate(grid_along_y):
            heatmap[i_x, i_y] = np.mean([10**(values[_id]/10) for _id in grid_along_xy_ids])
            if 0 in grid_along_xy_ids:
                x_bf = i_x
                y_bf = i_y

    fig, ax = plt.subplots()
    plt.title(tp)
    log_heatmap[i] = 10 * np.log10(heatmap)
    p = ax.imshow(10 * np.log10(heatmap), vmin=-60,cmap="viridis")
    ax.set_xticks(np.arange(len(xi)), labels=[f"{x:.2f}" for x in xi])
    ax.set_yticks(np.arange(len(yi)), labels=[f"{y:.2f}" for y in yi])
    ax.add_patch(Rectangle((y_bf-0.5, x_bf-0.5), 1, 1, fill=False, edgecolor="red", lw=3))
    fig.colorbar(p)
    fig.tight_layout()
    plt.show()


fig, ax = plt.subplots()
p = ax.imshow(log_heatmap[-1] - (log_heatmap[0]+10*np.log10(37)))
ax.set_xticks(np.arange(len(xi)), labels=[f"{x:.2f}" for x in xi])
ax.set_yticks(np.arange(len(yi)), labels=[f"{y:.2f}" for y in yi])
ax.add_patch(Rectangle((y_bf-0.5, x_bf-0.5), 1, 1, fill=False, edgecolor="red", lw=3))
fig.colorbar(p)
fig.tight_layout()
plt.show()
