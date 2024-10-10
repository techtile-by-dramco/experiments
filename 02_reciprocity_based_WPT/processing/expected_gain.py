from TechtilePlotter.TechtilePlotter import TechtilePlotter
import numpy as np
from Positioner import PositionerValues
import matplotlib.pyplot as pplt
from matplotlib.patches import Rectangle


tp = "bf-ceiling-grid-2"
plt = TechtilePlotter(realtime=True)

ceiling = [
    "A05",
    "A06",
    "A07",
    "A08",
    "A09",
    "A10",
    "B05",
    "B06",
    "B07",
    "B08",
    "B09",
    "B10",
    "C05",
    "C06",
    "C07",
    "C08",
    "C09",
    "C10",
    "D05",
    "D06",
    "D07",
    "D08",
    "D09",
    "D10",
    "E05",
    "E06",
    "E07",
    "E08",
    "E09",
    "E10",
    "F05",
    "F06",
    "F07",
    "F08",
    "F09",
    "F10",
    "G05",
    "G06",
    "G07",
    "G08",
    "G09",
    "G10",
]


all_tile_pos = np.zeros(shape=(len(ceiling), 3))

values = []

c = 299792458
wave_len = 920e6/c

i =0
for tile in plt.sdr_descr:
    name = tile["tile"]

    if name in ceiling:
        ch = tile["channels"][1]
        x = ch["x"]
        y = ch["y"]
        z = ch["z"]
        all_tile_pos[i, :] = [x, y, z]
        i +=1


positions = np.load(f"../data/positions-{tp}.npy", allow_pickle=True)

bf_pos = positions[0].get_coords()

applied_phases = np.asarray(
    [
        2 * np.pi * (np.linalg.norm(bf_pos - tile_pos) / wave_len)
        for tile_pos in all_tile_pos
    ]
)

for target_pos in positions:
    distances = np.asarray([np.linalg.norm(target_pos.get_coords() - tile_pos) for tile_pos in all_tile_pos])
    phases = (2 * np.pi * distances) / wave_len

    receveid_phases = phases - applied_phases

    received_power = 20 * np.log10(np.abs(np.sum((1.0/distances)*np.exp(1j * receveid_phases))))
    print(received_power)
    values.append(received_power)


positions_list = PositionerValues(positions)

grid_pos_ids, xi, yi = positions_list.group_in_grids(0.04, min_x=0, max_x=8, min_y=0, max_y=4)

heatmap = np.zeros(shape=(len(yi), len(xi))) - 200

for i_x, grid_along_y in enumerate(grid_pos_ids):
    for i_y, grid_along_xy_ids in enumerate(grid_along_y):
        heatmap[i_x, i_y] = np.mean([10**(values[_id]/10) for _id in grid_along_xy_ids])
        if 0 in grid_along_xy_ids:
            x_bf = i_x
            y_bf = i_y

fig, ax = pplt.subplots()
log_heatmap = 10 * np.log10(heatmap)
p = ax.imshow(10 * np.log10(heatmap), cmap="viridis")
ax.set_xticks(np.arange(len(xi)), labels=[f"{x:.2f}" for x in xi])
ax.set_yticks(np.arange(len(yi)), labels=[f"{y:.2f}" for y in yi])
ax.add_patch(Rectangle((y_bf-0.5, x_bf-0.5), 1, 1, fill=False, edgecolor="red", lw=3))
fig.colorbar(p)
fig.tight_layout()
pplt.show()
