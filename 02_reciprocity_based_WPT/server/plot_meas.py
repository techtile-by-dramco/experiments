from TechtilePlotter.TechtilePlotter import TechtilePlotter
import numpy as np
from Positioner import PositionerValues
import matplotlib.pyplot as pplt


f, (ax1, ax2) = pplt.subplots(2,1, sharex=True)

positions_nobf = np.load("positions-nobf.npy", allow_pickle=True)

positions_nobf_list = PositionerValues(positions_nobf)

positions_nobf_rounded = np.round(positions_nobf_list.get_x_positions(), decimals=1)


values_nobf = np.load("values-nobf.npy", allow_pickle=True)

positions_bf = np.load("positions-bf.npy", allow_pickle=True)
positions_bf_list = PositionerValues(positions_bf)
positions_bf_rounded = np.round(positions_bf_list.get_x_positions(), decimals=1)

values_bf = np.load("values-bf.npy", allow_pickle=True)


# average per position
(unique_positions_bf, unique_ids) = np.unique(positions_bf_rounded, return_inverse=True)

average_vals = np.zeros_like(unique_positions_bf)
total_vals = np.zeros_like(unique_positions_bf)

for val, u_pos_id in zip(values_bf, unique_ids):
    average_vals[u_pos_id] += val
    total_vals[u_pos_id] += 1

average_vals_bf = average_vals / total_vals


ax1.scatter(unique_positions_bf, average_vals_bf, label="BF")


# average per position
(unique_positions_nobf, unique_ids) = np.unique(positions_nobf_rounded, return_inverse=True)

average_vals = np.zeros_like(unique_positions_nobf)
total_vals = np.zeros_like(unique_positions_nobf)

for val, u_pos_id in zip(values_bf, unique_ids):
    average_vals[u_pos_id] += val
    total_vals[u_pos_id] += 1

average_vals_nobf = average_vals / total_vals


ax1.scatter(unique_positions_nobf, average_vals_nobf, label="NO BF")


# gain is where unique positions are the same
same_pos = []
gain = []
for pos_bf, val_bf in zip(unique_positions_bf, average_vals_bf):
    for pos_nobf, val_nobf in zip(unique_positions_nobf,average_vals_nobf):
        if pos_bf-pos_nobf == 0:
            same_pos.append(pos_bf)
            gain.append(val_bf-val_nobf)

ax2.plot(same_pos, gain, label="Gain")
pplt.legend()
pplt.show()


# plt = TechtilePlotter()
# plt.measurements(positions_bf, values_bf)
# plt.show()
