from TechtilePlotter.TechtilePlotter import TechtilePlotter
import numpy as np
from Positioner import PositionerValues
import matplotlib.pyplot as pplt


to_plot = ["bf-jarne"]
plt = TechtilePlotter()

for tp in to_plot:

    positions = np.load(f"positions-{tp}.npy", allow_pickle=True)
    values = np.load(f"values-{tp}.npy", allow_pickle=True)

    plt.measurements(positions, values)
    plt.add_ref(positions[0], values[0])

plt.show()
