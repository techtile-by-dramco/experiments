import numpy as np
from matplotlib import pyplot as plt


res = np.load("output.npy")[0,:]

print(res.dtype)


plt.figure()


bins = 180
plt.hist(
    np.rad2deg(np.angle(res)), bins=bins, label="03", alpha=0.5
)  # arguments are passed to np.histogram
plt.legend()


plt.show()

plt.figure()
bins = 180
plt.hist(
    np.abs(res), bins=bins, label="03", alpha=0.5
)  # arguments are passed to np.histogram
plt.legend()
plt.show()


fig, ax1 = plt.subplots()


ax1.set_ylabel("angle")
ax1.plot(np.rad2deg(np.angle(res)), alpha=0.5)
ax2 = ax1.twinx()

ax2.set_ylabel("amplitude", color="orange")
ax2.plot(np.abs(res), color="orange", alpha=0.5)
ax2.tick_params(axis="y", labelcolor="orange")

fig.tight_layout()
plt.show()


fig, ax1 = plt.subplots()

ax1.set_ylabel("Re")
ax1.plot(np.real(res), alpha=0.5)
ax2 = ax1.twinx()

ax2.set_ylabel("Im", color="orange")
ax2.plot(np.imag(res), color="orange", alpha=0.5)
ax2.tick_params(axis="y", labelcolor="orange")

fig.tight_layout()
plt.show()


plt.figure()
plt.plot(np.unwrap(np.angle(res)), alpha=0.5)
plt.show()
