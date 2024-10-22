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
    "bf-ceiling-grid-4-20241013074614",
    "bf-ceiling-grid-5-20241013074614",
    "bf-ceiling-grid-6-20241013074614",
    "bf-ceiling-grid-7-20241013074614",
    "bf-ceiling-grid-8-20241013074614",
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
    wavelen/8.0, min_x=2.6, max_x=3.8, min_y=1.20, max_y=2.40
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

from numpy import unravel_index
c_x, c_y = unravel_index(upsampled_heatmap.argmax(), upsampled_heatmap.shape)

upsampled_heatmap = 10 * np.log10(upsampled_heatmap)


from collections import deque


def get_neighbouring_area(matrix, center_row, center_col, threshold=3):
    rows, cols = matrix.shape
    center_value = matrix[center_row, center_col]

    # To store whether we visited a cell
    visited = np.zeros_like(matrix, dtype=bool)

    # Directions for neighbors (up, down, left, right)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Starting from the center
    queue = deque([(center_row, center_col)])
    visited[center_row, center_col] = True
    area = [(center_row, center_col)]

    while queue:
        r, c = queue.popleft()

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc]:
                if abs(matrix[nr, nc] - center_value) <= threshold:
                    queue.append((nr, nc))
                    visited[nr, nc] = True
                    area.append((nr, nc))

    return area

valid_cells = get_neighbouring_area(upsampled_heatmap, c_x, c_y)


p = ax.imshow(
    upsampled_heatmap, vmin=-65, origin="lower"
)  # + 10 including the cable loss

# for ix,iy in valid_cells:
#     ax.add_patch(
#         Rectangle((iy - 0.5, ix - 0.5), 1, 1, fill=False, edgecolor="red", lw=0.1)
#     )

print(((wavelen / 8.0) / zoom_val) ** 2 * len(valid_cells))


def get_neighbouring_area_border(matrix, center_row, center_col, threshold=3):
    rows, cols = matrix.shape
    center_value = matrix[center_row, center_col]

    # To store whether we visited a cell
    visited = np.zeros_like(matrix, dtype=bool)

    # Directions for neighbors (up, down, left, right)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Starting from the center
    queue = deque([(center_row, center_col)])
    visited[center_row, center_col] = True
    area = [(center_row, center_col)]

    while queue:
        r, c = queue.popleft()

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc]:
                if abs(matrix[nr, nc] - center_value) <= threshold:
                    queue.append((nr, nc))
                    visited[nr, nc] = True
                    area.append((nr, nc))

    # Identify border cells
    border = []
    for r, c in area:
        # A cell is on the border if one of its neighbors is not in the area
        is_border = False
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < rows and 0 <= nc < cols) or not visited[nr, nc]:
                is_border = True
                break
        if is_border:
            border.append((r, c))

    return border


def plot_border(matrix, border_cells, ax):

    # Extract x and y coordinates of the border cells
    x_vals = [c for r, c in border_cells]
    y_vals = [r for r, c in border_cells]

    # Connect the border cells by plotting lines
    plt.scatter(x_vals, y_vals, s=0.1)

border_cells = get_neighbouring_area_border(upsampled_heatmap, c_x, c_y)
# plot_border(matrix, border_cells, ax)

ax.set_xticks(
    (np.arange(len(xi))* zoom_val)[::4], labels=[f"{(x-xi[0])/wavelen:.2f}" for x in xi][::4]
)
ax.set_yticks(
    (np.arange(len(yi)) * zoom_val)[::4],
    labels=[f"{(y-yi[0])/wavelen:.2f}" for y in yi][::4],
)

fig.colorbar(p)
fig.tight_layout()


import tikzplotlib

tikzplotlib.save("heatmap-power-spot.tex")

plt.show()

np.save("../data/positions-bf-ceiling-grid-merged-20241013074614", all_positions)

np.save("../data/values-bf-ceiling-grid-merged-20241013074614", all_values)

np.savetxt("heatmap-power-spot.csv", upsampled_heatmap, delimiter=",", fmt="%.3f")

print(upsampled_heatmap.shape)

_str = ""
for x in range(upsampled_heatmap.shape[0]):
    for y in range(upsampled_heatmap.shape[0]):
        _str += f"({y},{x}) [{upsampled_heatmap[y,x]:.2f}] "
    _str += "\n"

with open("heatmap-power-spot.txt", "w") as text_file:
    text_file.write(_str)
