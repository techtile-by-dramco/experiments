from TechtilePlotter.TechtilePlotter import TechtilePlotter
import numpy as np
from Positioner import PositionerValues
import matplotlib.pyplot as pplt


to_plot = ["bf", "bf-dwars"]
plt = TechtilePlotter()

for tp in to_plot:

    positions = np.load(f"positions-{tp}.npy", allow_pickle=True)
    values = np.load(f"values-{tp}.npy", allow_pickle=True)

    plt.measurements(positions, values)

plt.show()
