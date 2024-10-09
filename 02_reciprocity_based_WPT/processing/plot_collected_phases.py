import numpy as np
import tools
from matplotlib import pyplot as plt

import matplotlib.colors as mcolors

colors = list(mcolors.TABLEAU_COLORS)

for meas_id in [52]:

    for i, tile in enumerate([19]):

        iq_samples_LB = np.load(
            f"data/data_G{tile}_20240925141143_{meas_id}_loopback.npy"
        )
        iq_samples_pilot = np.load(
            f"data/data_G{tile}_20240925141143_{meas_id}_pilot.npy"
        )

        iq_samples = iq_samples_LB

        angles_ch0 = tools.get_phases_and_remove_CFO(iq_samples[0,:])
        angles_ch1 = tools.get_phases_and_remove_CFO(iq_samples[1,:])

        angle_diff = tools.to_min_pi_plus_pi(np.rad2deg(angles_ch0 - angles_ch1))

        iq_max = np.max(np.abs(np.real(iq_samples_LB[1, :])))

        plt.plot(angle_diff, label=f"LB {tile} {iq_max:.4f}", color=colors[i])

        # iq_samples = iq_samples_pilot

        # angles_ch0 = tools.get_phases_and_remove_CFO(iq_samples[0, :])
        # angles_ch1 = tools.get_phases_and_remove_CFO(iq_samples[1, :])

        # angle_diff = tools.to_min_pi_plus_pi(np.rad2deg(angles_ch1))

        # plt.plot(angle_diff, label=f"pilot {tile} {meas_id}", color=colors[i], ls="--")


plt.legend()
plt.show()
