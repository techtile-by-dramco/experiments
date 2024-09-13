from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import AutoMinorLocator
import numpy as np


gain_table_sub_1300mhz = [[0x00, 0x00, 0x20],
    [0x00, 0x00, 0x00],
    [0x00, 0x00, 0x00],
    [0x00, 0x01, 0x00],
    [0x00, 0x02, 0x00],
    [0x00, 0x03, 0x00],
    [0x00, 0x04, 0x00],
    [0x00, 0x05, 0x00],
    [0x01, 0x03, 0x20],
    [0x01, 0x04, 0x00],
    [0x01, 0x05, 0x00],
    [0x01, 0x06, 0x00],
    [0x01, 0x07, 0x00],
    [0x01, 0x08, 0x00],
    [0x01, 0x09, 0x00],
    [0x01, 0x0A, 0x00],
    [0x01, 0x0B, 0x00],
    [0x01, 0x0C, 0x00],
    [0x01, 0x0D, 0x00],
    [0x01, 0x0E, 0x00],
    [0x02, 0x09, 0x20],
    [0x02, 0x0A, 0x00],
    [0x02, 0x0B, 0x00],
    [0x02, 0x0C, 0x00],
    [0x02, 0x0D, 0x00],
    [0x02, 0x0E, 0x00],
    [0x02, 0x0F, 0x00],
    [0x02, 0x10, 0x00],
    [0x02, 0x2B, 0x20],
    [0x02, 0x2C, 0x00],
    [0x04, 0x28, 0x20],
    [0x04, 0x29, 0x00],
    [0x04, 0x2A, 0x00],
    [0x04, 0x2B, 0x00],
    [0x24, 0x20, 0x20],
    [0x24, 0x21, 0x00],
    [0x44, 0x20, 0x20],
    [0x44, 0x21, 0x00],
    [0x44, 0x22, 0x00],
    [0x44, 0x23, 0x00],
    [0x44, 0x24, 0x00],
    [0x44, 0x25, 0x00],
    [0x44, 0x26, 0x00],
    [0x44, 0x27, 0x00],
    [0x44, 0x28, 0x00],
    [0x44, 0x29, 0x00],
    [0x44, 0x2A, 0x00],
    [0x44, 0x2B, 0x00],
    [0x44, 0x2C, 0x00],
    [0x44, 0x2D, 0x00],
    [0x44, 0x2E, 0x00],
    [0x44, 0x2F, 0x00],
    [0x44, 0x30, 0x00],
    [0x44, 0x31, 0x00],
    [0x44, 0x32, 0x00],
    [0x64, 0x2E, 0x20],
    [0x64, 0x2F, 0x00],
    [0x64, 0x30, 0x00],
    [0x64, 0x31, 0x00],
    [0x64, 0x32, 0x00],
    [0x64, 0x33, 0x00],
    [0x64, 0x34, 0x00],
    [0x64, 0x35, 0x00],
    [0x64, 0x36, 0x00],
    [0x64, 0x37, 0x00],
    [0x64, 0x38, 0x00],
    [0x65, 0x38, 0x20],
    [0x66, 0x38, 0x20],
    [0x67, 0x38, 0x20],
    [0x68, 0x38, 0x20],
    [0x69, 0x38, 0x20],
    [0x6A, 0x38, 0x20],
    [0x6B, 0x38, 0x20],
    [0x6C, 0x38, 0x20],
    [0x6D, 0x38, 0x20],
    [0x6E, 0x38, 0x20],
    [0x6F, 0x38, 0x20]]

table = gain_table_sub_1300mhz
# [0] -> D6 D5 (LNA gain)
# [0] -> D3-D0 (mixer gain)

# [1] -> D5 (TIA gain)
# [1] -> D4-D0 (LPF gain)

# [2] -> D4-D0 (digital gain)

def bin_to_int(bin):
    return int(bin, 2)

# https://wiki.analog.com/resources/tools-software/linux-drivers/iio-transceiver/ad9361#rx_gain_control

min_gain = -1
max_gain = 73

# reg_0x131: Ext LNA, Int LNA, & Mixer Gain Word
# reg_0x132: TIA & LPF Word
# reg_0x133: DC Cal bit & Dig Gain Word

# gain table of AD: https://github.com/analogdevicesinc/linux/blob/main/firmware/ad9361_std_gaintable


# The ad9361_rf_dc_offset_calib function configures and runs
# the RF DC calibration. Setting this bit performs an RF dc offset
# calibration of the Rx signal paths and the bit self-clears when
# the calibration completes.


# details see: https://www.farnell.com/datasheets/2007082.pdf page 47/128
ilna_gains = [5,17,19,24]
mixer_gains = [0,3,9]
mixer_gains.extend([i + 10 for i in range(3,16)])
tia_gains = [-6, 0]
lpf_gains = list(range(25))
digital_gains = list(range(32))

gain_indices = list(range(77))
total_gains = [0]*77

ilna_gain_vals = [0] * 77
mixer_gain_vals = [0] * 77
tia_gain_vals = [0] * 77
lpf_gain_vals = [0] * 77
digital_gain_vals = [0] * 77


for g in gain_indices:
    register_val_0 = f"{table[g][0]:0>8b}"  # 0x131
    register_val_1 = f"{table[g][1]:0>8b}"  # 0x132
    register_val_2 = f"{table[g][2]:0>8b}"  # 0x133

    ilna_gain_idx = bin_to_int(register_val_0[1:3])
    mixer_gain_idx = bin_to_int(register_val_0[4:8])

    # The transimpedance amplifier gain. If this bit is 0, TIA gain
    # equals −6 dB and if the bit is set, the gain equals 0 dB.
    tia_gain_idx = bin_to_int(register_val_1[2])

    lpf_gain_idx = bin_to_int(register_val_1[3:8])

    digital_gain_idx = bin_to_int(register_val_2[3:8])

    # gain values
    ilna_gain = ilna_gains[ilna_gain_idx]
    mixer_gain = mixer_gains[mixer_gain_idx]
    tia_gain = tia_gains[tia_gain_idx]
    lpf_gain = lpf_gains[lpf_gain_idx]
    digital_gain = digital_gains[digital_gain_idx]

    total_gain = ilna_gain + mixer_gain + tia_gain + lpf_gain + digital_gain
    total_gains[g] = total_gain

    ilna_gain_vals[g] = ilna_gains[ilna_gain_idx]
    mixer_gain_vals[g] = mixer_gains[mixer_gain_idx]
    tia_gain_vals[g] = tia_gains[tia_gain_idx]
    lpf_gain_vals[g] = lpf_gains[lpf_gain_idx]
    digital_gain_vals[g] = digital_gains[digital_gain_idx]

    print(
        f"{g}: {ilna_gain_idx} {ilna_gain} {mixer_gain_idx} {mixer_gain} {tia_gain_idx} {tia_gain} {lpf_gain_idx} {lpf_gain} {digital_gain_idx} {digital_gain} {total_gain}dB ({hex(table[g][0])} {hex(table[g][1])} {hex(table[g][2])})"
    )


fig = plt.figure()
ax = fig.gca()
plt.plot(gain_indices, ilna_gain_vals, label="iLNA", alpha=0.8, marker=",")
plt.plot(gain_indices, mixer_gain_vals, label="mixer", alpha=0.8, marker=".")
plt.plot(gain_indices, tia_gain_vals, label="TIA", alpha=0.8, marker=".")
plt.plot(gain_indices, lpf_gain_vals, label="LPF", alpha=0.4, ls="--", marker=".")
plt.plot(
    gain_indices, digital_gain_vals, label="digital", alpha=0.4, ls="--", marker="."
)
plt.ylabel("Configured Gain")
plt.xlabel("Gain index")
plt.grid(axis="x")
ax.xaxis.get_ticklocs(minor=True)
ax.minorticks_on()
ax.xaxis.set_minor_locator(AutoMinorLocator(10))
plt.grid(which="minor", linestyle=":", linewidth=0.5)

ax.fill_between(range(28), -10, 25, alpha=0.1)
ax.fill_between(range(30,66), -10, 25, alpha=0.1)
ax.fill_between(range(20,30), -10, 25, alpha=0.1)


# ax.add_patch(Rectangle((7, -10), 1, 35, edgecolor = 'blue',
#              fill=False,
#              lw=0.5))

# ax.add_patch(Rectangle((19, -10), 1, 35, edgecolor = 'blue',
#              fill=False,
#              lw=0.5))

# ax.add_patch(Rectangle((33, -10), 1, 35, edgecolor="blue", fill=False, lw=0.5))

# ax.add_patch(Rectangle((35, -10), 1, 35, edgecolor="blue", fill=False, lw=0.5))

# ax.add_patch(Rectangle((54, -10), 1, 35, edgecolor="blue", fill=False, lw=0.5))

# ax.add_patch(Rectangle((27, -10), 1, 35, edgecolor="blue", fill=False, lw=0.5))

sec = ax.secondary_xaxis(location=1)
sec.set_xticks(
    [7.5, 19.5, 33.5, 35.5, 54.5, 27.5],
    labels=[
        "7$\\rightarrow$8",
        "19$\\rightarrow$20",
        "33$\\rightarrow$34",
        "35$\\rightarrow$36",
        "54$\\rightarrow$55",
        "27$\\rightarrow$28",
    ],
)
sec.xaxis.label.set_color("red")
sec.tick_params(axis="x", colors="red")

plt.legend()
plt.tight_layout()
plt.show()
