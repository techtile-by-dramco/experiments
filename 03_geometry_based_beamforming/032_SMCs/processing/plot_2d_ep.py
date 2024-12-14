from TechtilePlotter.TechtilePlotter import TechtilePlotter
import numpy as np
from Positioner import PositionerValues
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.ndimage import zoom

from ep import RFEP

to_plot = ["20241107114752", "20241107124328","20241107091548"]  # 20241107124328 20241107091548

cmap = "inferno"

log_heatmap = np.zeros(len(to_plot)).tolist()

wavelen = 3e8 / 920e6

for i, tp in enumerate(to_plot):

    positions = np.load(f"../data/positions-{tp}.npy", allow_pickle=True)
    o_values = np.load(f"../data/values-{tp}.npy", allow_pickle=True)

    print(f"Processing {len(positions)} samples")

    # valid_values_idx = values>-90

    # positions = positions[valid_values_idx]
    # values = values[valid_values_idx]

    print("CHANGE OF X POSITION DUE TO QTM position not same as antenna position")
    y_positions = [p.y+0.1 for p in positions]

    temp_pos_list = PositionerValues(positions)

    positions_list = PositionerValues.from_xyz(
        temp_pos_list.get_x_positions(), y_positions, temp_pos_list.get_z_positions()
    )

    values = [v.pwr_nw / 10**6 for v in o_values]

    print(f"MAX POWER: {np.max(values):.2f} uW")

    grid_pos_ids, xi, yi = positions_list.group_in_grids(
        0.03, min_x=2.7, max_x=3.9, min_y=1.25, max_y=2.4
    )
    heatmap = np.zeros(shape=(len(yi), len(xi)))

    for i_x, grid_along_y in enumerate(grid_pos_ids):
        for i_y, grid_along_xy_ids in enumerate(grid_along_y):
            heatmap[i_x, i_y] = np.mean(
                [values[_id] for _id in grid_along_xy_ids]
            )
            if 0 in grid_along_xy_ids:
                x_bf = i_x
                y_bf = i_y

    zoom_val = 2

    ue_position = Rectangle(
        ((y_bf - 0.5) * zoom_val, (x_bf - 0.5) * zoom_val),
        1,
        1,
        fill=False,
        edgecolor="red",
        lw=3,
    )

    fig, ax = plt.subplots()
    plt.title(tp)
    upsampled_heatmap = zoom(heatmap, zoom=zoom_val, order=1)
    p = ax.imshow(upsampled_heatmap, cmap=cmap, origin="lower")
    ax.set_xticks(
        zoom_val * np.arange(len(xi))[::4],
        labels=[f"{(x-xi[0])/wavelen:.2f}" for x in xi][::4],
    )
    ax.set_yticks(
        zoom_val * np.arange(len(yi))[::4],
        labels=[f"{(y-yi[0])/wavelen:.2f}" for y in yi][::4],
    )
    ax.add_patch(ue_position)
    cbar = fig.colorbar(p)
    cbar.ax.set_ylabel("uW")
    ax.set_xlabel("distance in wavelengths")
    ax.set_ylabel("distance in wavelengths")
    fig.tight_layout()
    plt.savefig(
        f"../results/{tp}/heatmap-uW.png", bbox_inches="tight", transparent=True, dpi=600
    )

    fig, ax = plt.subplots()
    plt.title(tp)
    upsampled_heatmap = zoom(heatmap, zoom=zoom_val, order=1)
    plt.imshow(
        10 * np.log10(upsampled_heatmap/10e3),  # /10e3 as it is expressed in uW to go to mW
        vmin=None,
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
    # ax.add_patch(Rectangle((y_bf-0.5, x_bf-0.5), 1, 1, fill=False, edgecolor="red", lw=3))
    plt.colorbar(label="dBm")
    # cbar.ax.set_ylabel("dBm")
    plt.xlabel("distance in wavelengths")
    plt.ylabel("distance in wavelengths")
    fig.tight_layout()
    plt.savefig(
        f"../results/{tp}/heatmap-dBm.png",
        bbox_inches="tight",
        transparent=True,
        dpi=600,
    )

    values = [v.buffer_voltage_mv if v.buffer_voltage_mv<3000 else 0 for v in o_values]
    heatmap = np.zeros(shape=(len(yi), len(xi)))
    for i_x, grid_along_y in enumerate(grid_pos_ids):
        for i_y, grid_along_xy_ids in enumerate(grid_along_y):
            heatmap[i_x, i_y] = np.mean(
                [values[_id] for _id in grid_along_xy_ids]
            )
            if 0 in grid_along_xy_ids:
                x_bf = i_x
                y_bf = i_y

    fig, ax = plt.subplots()
    plt.title(tp)
    upsampled_heatmap = zoom(heatmap, zoom=zoom_val, order=1)
    p = ax.imshow(upsampled_heatmap/1e3, cmap=cmap, vmin=1.2, origin="lower")
    ax.set_xticks(
        zoom_val * np.arange(len(xi))[::4],
        labels=[f"{(x-xi[0])/wavelen:.2f}" for x in xi][::4],
    )
    ax.set_yticks(
        zoom_val * np.arange(len(yi))[::4],
        labels=[f"{(y-yi[0])/wavelen:.2f}" for y in yi][::4],
    )
    # ax.add_patch(
    #     Rectangle((y_bf - 0.5, x_bf - 0.5), 1, 1, fill=False, edgecolor="red", lw=3)
    # )
    cbar = fig.colorbar(p)
    cbar.ax.set_ylabel("V")
    ax.set_xlabel("distance in wavelengths")
    ax.set_ylabel("distance in wavelengths")
    fig.tight_layout()
    plt.savefig(
        f"../results/{tp}/heatmap-V.png", bbox_inches="tight", transparent=True, dpi=600
    )

    fig, ax = plt.subplots()
    plt.title(tp)
    upsampled_heatmap[upsampled_heatmap<1750] = np.nan
    p = ax.imshow(upsampled_heatmap / 1e3, cmap=cmap, origin="lower")
    ax.set_xticks(
        zoom_val * np.arange(len(xi))[::4],
        labels=[f"{(x-xi[0])/wavelen:.2f}" for x in xi][::4],
    )
    ax.set_yticks(
        zoom_val * np.arange(len(yi))[::4],
        labels=[f"{(y-yi[0])/wavelen:.2f}" for y in yi][::4],
    )
    # ax.add_patch(
    #     Rectangle((y_bf - 0.5, x_bf - 0.5), 1, 1, fill=False, edgecolor="red", lw=3)
    # )
    cbar = fig.colorbar(p)
    cbar.ax.set_ylabel("V")
    ax.set_xlabel("distance in wavelengths")
    ax.set_ylabel("distance in wavelengths")
    fig.tight_layout()
    plt.savefig(
        f"../results/{tp}/heatmap-Vth.png",
        bbox_inches="tight",
        transparent=True,
        dpi=600,
    )

    plt.show()
