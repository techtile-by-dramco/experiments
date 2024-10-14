from TechtilePlotter.TechtilePlotter import TechtilePlotter
import numpy as np
from Positioner import PositionerValues
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import glob
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation
from scipy.ndimage import zoom

# Specify the relative path to ffmpeg.exe (same folder as the script)
ffmpeg_path = "./ffmpeg.exe"
plt.rcParams["animation.ffmpeg_path"] = ffmpeg_path

import os


pattern = "values-gausbf-ceiling-grid-*-20241011193104.npy"

# Construct the full path pattern
full_pattern = os.path.join("../data", pattern)

# Get all matching filenames
filenames = glob.glob(full_pattern)

heatmaps = [0]*len(filenames)

print(f"{len(filenames)} files found.")


BF_heatmap = None
positions = np.load(
    f"../data/positions-bf-ceiling-grid-merged-20241013074614.npy", allow_pickle=True
)
values = np.load(
    f"../data/values-bf-ceiling-grid-merged-20241013074614.npy", allow_pickle=True
)
positions_list = PositionerValues(positions)
grid_pos_ids, xi, yi = positions_list.group_in_grids(0.3/4.0, min_x=2.6, max_x=3.8, min_y=1.3, max_y=2.5)

heatmap = [[[] for _ in xi] for _ in yi]

for i_x, grid_along_y in enumerate(grid_pos_ids):
    for i_y, grid_along_xy_ids in enumerate(grid_along_y):
        heatmap[i_x][i_y] = np.mean([10 ** (values[_id] / 10) for _id in grid_along_xy_ids]) 

upsampled_heatmap = zoom(heatmap, zoom=100, order=1)

BF_heatmap = 10 * np.log10(upsampled_heatmap)

for i, tp in enumerate(filenames):
    tp = os.path.basename(tp)
    print(tp)

    # remove "values" and "npy"
    tp = tp[7:-4]

    positions = np.load(f"../data/positions-{tp}.npy", allow_pickle=True)
    values = np.load(f"../data/values-{tp}.npy", allow_pickle=True)

    print(f"Processing {len(positions)} samples")

    positions_list = PositionerValues(positions)

    grid_pos_ids, xi, yi = positions_list.group_in_grids(0.3/4.0, min_x=2.6, max_x=3.8, min_y=1.3, max_y=2.5)

    heatmap = [[[] for _ in xi] for _ in yi]

    for i_x, grid_along_y in enumerate(grid_pos_ids):
        for i_y, grid_along_xy_ids in enumerate(grid_along_y):
            heatmap[i_x][i_y] = np.mean([10 ** (values[_id] / 10) for _id in grid_along_xy_ids]) 

    upsampled_heatmap = zoom(heatmap, zoom=100, order=1)

    heatmaps[i] = 10 * np.log10(upsampled_heatmap)

# fig, ax = plt.subplots()
# p = ax.imshow(log_heatmap, cmap="viridis")
# ax.set_xticks(np.arange(len(xi)), labels=[f"{x:.2f}" for x in xi])
# ax.set_yticks(np.arange(len(yi)), labels=[f"{y:.2f}" for y in yi])
# ax.add_patch(Rectangle((y_bf-0.5, x_bf-0.5), 1, 1, fill=False, edgecolor="red", lw=3))
# fig.colorbar(p)
# fig.tight_layout()
# plt.show()


fig, ax = plt.subplots()
# Display the initial frame using imshow
im = ax.imshow(
    heatmaps[0],
    cmap="viridis",
    animated=True,
    vmin=-68,
    vmax=-48
)
# Add colorbar
cbar = plt.colorbar(im, ax=ax)

# Function to update the data for each frame
def update(frame):
    im.set_array(heatmaps[frame])
    return [im]


# Create the animation object
ani = FuncAnimation(fig, update, frames=len(heatmaps), blit=True)

# Save the animation as MP4 with the relative path to ffmpeg
writer = animation.FFMpegWriter(fps=1, metadata=dict(artist="Gilles Callebaut"))
ani.save("animation_gausbf.mp4", writer=writer)


heatmaps = heatmaps - BF_heatmap

fig, ax = plt.subplots()
# Display the initial frame using imshow
im = ax.imshow(heatmaps[0], cmap="viridis", animated=True)
# Add colorbar
cbar = plt.colorbar(im, ax=ax)

# Create the animation object
ani = FuncAnimation(fig, update, frames=len(heatmaps), blit=True)

# Save the animation as MP4 with the relative path to ffmpeg
writer = animation.FFMpegWriter(fps=1, metadata=dict(artist="Gilles Callebaut"))
ani.save("animation_gausbf_gain.mp4", writer=writer)
