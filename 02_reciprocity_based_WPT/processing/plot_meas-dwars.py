from TechtilePlotter.TechtilePlotter import TechtilePlotter
import numpy as np
from Positioner import PositionerValues
import matplotlib.pyplot as pplt


f, (ax0, ax1, ax2) = pplt.subplots(3, 1, sharex=True)

to_plot = ["nobf", "bf", "nobf-G19"]

for tp in to_plot:

    positions= np.load(f"positions-{tp}-dwars.npy", allow_pickle=True)
    values = np.load(f"values-{tp}-dwars.npy", allow_pickle=True)
    positions_list = PositionerValues(positions)
    positions_rounded = positions_list.reduce_to_grid_size(
        size=0.05
    ).get_y_positions()

    if tp ==  "nobf-G19":
        # add array gain
        values = values + 10 * np.log10(5)

    ax0.scatter(positions_list.get_y_positions(), values, label=tp)

    if tp == "bf":
        bf_point = positions[0].y
        print(positions[0])

        ax0.axvline(bf_point, ls="--")
        ax1.axvline(bf_point, ls="--")
        ax2.axvline(bf_point, ls="--")

    # averaging!
    inds = positions_rounded.argsort()

    sorted_values = values[inds]
    sorted_positions = positions_rounded[inds]

    unique_values = []
    unique_positions = []
    current_pos = None
    idx = -1

    # below only works if sorted
    for p, v in zip(sorted_positions, sorted_values):
        if current_pos is None or p != current_pos:
            idx += 1
            current_pos = p
            unique_values.append([])
            unique_positions.append(p)

        unique_values[idx].append(v)

    # average those
    unique_avg_values = [np.mean(uv) for uv in unique_values]

    ax1.scatter(unique_positions, unique_avg_values, label=tp)

    if tp == "bf":
        unique_positions_bf = np.asarray(unique_positions)
        unique_avg_values_bf = np.asarray(unique_avg_values)
    if tp == "nobf":
        unique_positions_nobf = np.asarray(unique_positions)
        unique_avg_values_nobf = np.asarray(unique_avg_values)
    if tp == "nobf-G19":
        unique_positions_nobfG19 = np.asarray(unique_positions)
        unique_avg_values_nobfG19 = np.asarray(unique_avg_values)


xy, x_ind, y_ind = np.intersect1d(unique_positions_bf, unique_positions_nobf, assume_unique=True, return_indices=True)

pos_gains = xy
gain = unique_avg_values_bf[x_ind] - unique_avg_values_nobf[y_ind]

ax2.scatter(pos_gains, gain, label="gain wrt no BF")


xy, x_ind, y_ind = np.intersect1d(
    unique_positions_bf,
    unique_positions_nobfG19,
    assume_unique=True,
    return_indices=True,
)

pos_gains = xy
gain = unique_avg_values_bf[x_ind] - unique_avg_values_nobfG19[y_ind]

ax2.scatter(pos_gains, gain, label="gain wrt G19")

# # average per position
# (unique_positions_bf, unique_ids) = np.unique(
#     positions_rounded, return_inverse=True
# )

# average_vals = np.zeros_like(unique_positions_bf)
# total_vals = np.zeros_like(unique_positions_bf)

# for val, u_pos_id in zip(values_bf, unique_ids):
#     average_vals[u_pos_id] += val
#     total_vals[u_pos_id] += 1

# average_vals_bf = average_vals / total_vals


# # average per position
# (unique_positions_nobf, unique_ids) = np.unique(
#     positions_nobf_rounded, return_inverse=True
# )

# average_vals = np.zeros_like(unique_positions_nobf)
# total_vals = np.zeros_like(unique_positions_nobf)

# for val, u_pos_id in zip(values_bf, unique_ids):
#     average_vals[u_pos_id] += val
#     total_vals[u_pos_id] += 1

# average_vals_nobf = average_vals / total_vals


# ax1.scatter(unique_positions_nobf, average_vals_nobf, label="NO BF")
# ax1.scatter(unique_positions_bf, average_vals_bf, label="BF")

# # gain is where unique positions are the same
# same_pos = []
# gain = []
# for pos_bf, val_bf in zip(unique_positions_bf, average_vals_bf):
#     for pos_nobf, val_nobf in zip(unique_positions_nobf, average_vals_nobf):
#         if pos_bf - pos_nobf == 0:
#             same_pos.append(pos_bf)
#             gain.append(val_bf - val_nobf)

# ax2.plot(same_pos, gain, label="Gain")
ax0.set_title("Raw sample points")
ax0.legend()
ax1.set_title("Quantized sample points")
ax2.set_title("Gain")
ax1.legend()
pplt.legend()
pplt.tight_layout()
pplt.show()


# plt = TechtilePlotter()
# plt.measurements(positions_bf, values_bf)
# # plt.antennas()
# plt.show()
