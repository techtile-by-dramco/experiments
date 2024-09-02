# plot hist of scope
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

plt.figure()
filename = "20240902115303_hist.csv"
data = np.genfromtxt(filename, dtype=float, delimiter=",", names=True)
x = data["X_Deg"]
x_idx = np.where(data["X_Deg"]>180) 
x[x_idx] = x[x_idx] - 360
y = data["Y_Hits"].astype(int)

idx_order = np.argsort(x)
x = x[idx_order]
y = y[idx_order]

data = np.repeat(x, y)

data = data - np.mean(data) 
data = np.abs(data)
x = np.sort(data)
N = len(data)
# get the cdf values of y
y = (np.arange(N) / float(N))*100


# plot the cdf
plt.plot(x, y)
plt.xlabel(
    f"Absolute hase error (degrees) between two USRPs (after removing mean angle diff. of {np.mean(data) :0.2f} degrees)"
)
plt.ylabel("CDF (%)")
plt.xlim(0.0,20.0)
plt.tight_layout()
plt.show()
