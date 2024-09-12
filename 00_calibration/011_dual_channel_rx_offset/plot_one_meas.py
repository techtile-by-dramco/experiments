import numpy as np
import tools
import matplotlib.pyplot as plt


measurements = "T04_20240910062816"
meas_id = 100


filename = f"data/data_{measurements}_{meas_id}.npy"

iq_samples = np.load(filename)

iq_ch0 = tools.apply_bandpass(iq_samples[0, :])
iq_ch1 = tools.apply_bandpass(iq_samples[1, :])

plt.figure()

plt.plot(np.real(iq_ch0), color="red")
plt.plot(np.real(iq_ch1), color="red", ls="--")

plt.plot(np.imag(iq_ch0), color="blue")
plt.plot(np.imag(iq_ch1), color="blue", ls="--")


plt.show()

angles_ch0 = np.angle(iq_ch0)
angles_ch1 = np.angle(iq_ch1)

# angles_ch0 = np.angle(iq_samples[0, :])
# angles_ch1 = np.angle(iq_samples[1, :])

angle_diff = tools.to_min_pi_plus_pi(np.rad2deg(angles_ch0 - angles_ch1)) - 83.75
plt.figure()
plt.plot(angle_diff)
plt.show()
