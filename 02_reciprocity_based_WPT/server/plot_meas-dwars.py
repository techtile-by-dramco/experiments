from TechtilePlotter.TechtilePlotter import TechtilePlotter
import numpy as np
from Positioner import PositionerValues
import matplotlib.pyplot as pplt


f, (ax0, ax1, ax2) = pplt.subplots(3,1, sharex=True)

positions_nobf = np.load("positions-nobf-dwars.npy", allow_pickle=True)

positions_nobf_list = PositionerValues(positions_nobf)

positions_nobf_rounded = positions_nobf_list.reduce_to_grid_size(
    size=0.15
).get_y_positions()


values_nobf = np.load("values-nobf-dwars.npy", allow_pickle=True)


ax0.scatter(positions_nobf_list.get_y_positions(), values_nobf, label="NO BF")


positions_bf = np.load("positions-bf-dwars.npy", allow_pickle=True)


bf_point = positions_bf[0].y

ax0.axvline(bf_point, ls="--")

positions_bf_list = PositionerValues(positions_bf)


positions_bf_rounded = positions_bf_list.reduce_to_grid_size(size=0.15).get_y_positions()

values_bf = np.load("values-bf-dwars.npy", allow_pickle=True)

ax0.scatter(positions_bf_list.get_y_positions(), values_bf, label="BF")


positions_nobf = np.load("positions-nobf-G19-dwars.npy", allow_pickle=True)

positions_nobf_list = PositionerValues(positions_nobf)

positions_nobf_rounded = positions_nobf_list.reduce_to_grid_size(
    size=0.15
).get_y_positions()


values_nobf = np.load("values-nobf-G19-dwars.npy", allow_pickle=True)

ax0.scatter(positions_nobf_list.get_y_positions(), values_nobf+10*np.log10(5), label="NO BF - G19 (incl. array gain)")


# average per position
(unique_positions_bf, unique_ids) = np.unique(positions_bf_rounded, return_inverse=True)

average_vals = np.zeros_like(unique_positions_bf)
total_vals = np.zeros_like(unique_positions_bf)

for val, u_pos_id in zip(values_bf, unique_ids):
    average_vals[u_pos_id] += val
    total_vals[u_pos_id] += 1

average_vals_bf = average_vals / total_vals


# average per position
(unique_positions_nobf, unique_ids) = np.unique(positions_nobf_rounded, return_inverse=True)

average_vals = np.zeros_like(unique_positions_nobf)
total_vals = np.zeros_like(unique_positions_nobf)

for val, u_pos_id in zip(values_bf, unique_ids):
    average_vals[u_pos_id] += val
    total_vals[u_pos_id] += 1

average_vals_nobf = average_vals / total_vals


ax1.scatter(unique_positions_nobf, average_vals_nobf, label="NO BF")
ax1.scatter(unique_positions_bf, average_vals_bf, label="BF")

# gain is where unique positions are the same
same_pos = []
gain = []
for pos_bf, val_bf in zip(unique_positions_bf, average_vals_bf):
    for pos_nobf, val_nobf in zip(unique_positions_nobf,average_vals_nobf):
        if pos_bf-pos_nobf == 0:
            same_pos.append(pos_bf)
            gain.append(val_bf-val_nobf)

ax2.plot(same_pos, gain, label="Gain")
ax0.set_title("Raw sample points")
ax0.legend()
ax1.set_title("Quantized sample points")
ax2.set_title("Gain")
ax1.legend()
pplt.legend()
pplt.tight_layout()
pplt.show()


plt = TechtilePlotter()
plt.measurements(positions_bf, values_bf)
# plt.antennas()
plt.show()
