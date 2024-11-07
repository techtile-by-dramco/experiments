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

to_plot = ["20241106115848"]  # "bf-ceiling-grid",

cmap = "inferno"

log_heatmap = np.zeros(len(to_plot)).tolist()

wavelen = 3e8 / 920e6

for i, tp in enumerate(to_plot):

    positions = np.load(f"../data/positions-{tp}.npy", allow_pickle=True)
    values = np.load(f"../data/values-{tp}.npy", allow_pickle=True)

    print(f"Processing {len(positions)} samples")

    # valid_values_idx = values>-90

    # positions = positions[valid_values_idx]
    # values = values[valid_values_idx]

    positions_list = PositionerValues(positions)

    grid_pos_ids, xi, yi = positions_list.group_in_grids(
        0.05, min_x=2.6, max_x=3.8, min_y=1.25, max_y=2.4
    )
    heatmap = np.zeros(shape=(len(yi), len(xi))) - 200

    for i_x, grid_along_y in enumerate(grid_pos_ids):
        for i_y, grid_along_xy_ids in enumerate(grid_along_y):
            heatmap[i_x, i_y] = np.mean(
                [10 ** (values[_id] / 10) for _id in grid_along_xy_ids]
            )
            if 0 in grid_along_xy_ids:
                x_bf = i_x
                y_bf = i_y

    zoom_val = 100

    fig, ax = plt.subplots()
    plt.title(tp)
    upsampled_heatmap = zoom(heatmap, zoom=zoom_val, order=1)
    plt.imshow(
        10 * np.log10(upsampled_heatmap) + 10,  # + 10 to account for
        vmin=np.max(10 * np.log10(upsampled_heatmap) + 10)-25,
        vmax=None,
        cmap=cmap,
        origin="lower",
    )
    plt.gca().set_xticks(
        zoom_val * np.arange(len(xi))[::4],
        labels=[f"{(x-xi[0])/wavelen:.2f}" for x in xi][::4],
    )
    plt.gca().set_yticks(
        zoom_val * np.arange(len(yi))[::4],
        labels=[f"{(y-yi[0])/wavelen:.2f}" for y in yi][::4],
    )
    ax.add_patch(Rectangle((y_bf-0.5, x_bf-0.5), 1, 1, fill=False, edgecolor="red", lw=3))
    plt.colorbar(label="dBm")
    # cbar.ax.set_ylabel("dBm")
    plt.xlabel("distance in wavelengths")
    plt.ylabel("distance in wavelengths")
    fig.tight_layout()
    plt.savefig(
        f"../results/{tp}/heatmap-dBm.png", bbox_inches="tight", transparent=True
    )
    # plt.show()

    fig, ax = plt.subplots()
    plt.title(tp)
    upsampled_heatmap = zoom(heatmap, zoom=zoom_val, order=1)
    p = ax.imshow(
        upsampled_heatmap * 1000 * 10, cmap=cmap, origin="lower"
    )  # * 10 to account for the cable loss
    ax.set_xticks(
        zoom_val * np.arange(len(xi))[::4],
        labels=[f"{(x-xi[0])/wavelen:.2f}" for x in xi][::4],
    )
    ax.set_yticks(
        zoom_val * np.arange(len(yi))[::4],
        labels=[f"{(y-yi[0])/wavelen:.2f}" for y in yi][::4],
    )
    ax.add_patch(
        Rectangle((y_bf - 0.5, x_bf - 0.5), 1, 1, fill=False, edgecolor="red", lw=3)
    )
    cbar = fig.colorbar(p)
    cbar.ax.set_ylabel("uW")
    ax.set_xlabel("distance in wavelengths")
    ax.set_ylabel("distance in wavelengths")
    fig.tight_layout()
    plt.savefig(
        f"../results/{tp}/heatmap-uW.png", bbox_inches="tight", transparent=True
    )
    plt.show()


# fig, ax = plt.subplots()
# p = ax.imshow(log_heatmap[-1] - (log_heatmap[0]+10*np.log10(37)))
# ax.set_xticks(np.arange(len(xi)), labels=[f"{(x-xi[0])/wavelen:.2f}" for x in xi])
# ax.set_yticks(np.arange(len(yi)), labels=[f"{(y-yi[0])/wavelen:.2f}" for y in yi])
# ax.add_patch(Rectangle((y_bf-0.5, x_bf-0.5), 1, 1, fill=False, edgecolor="red", lw=3))
# fig.colorbar(p)
# fig.tight_layout()
# plt.show()
