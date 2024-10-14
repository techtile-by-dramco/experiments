"positions-"

from TechtilePlotter.TechtilePlotter import TechtilePlotter
import numpy as np
from Positioner import PositionerValues
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.ndimage import zoom


# to_plot = [
#     "nobf-D07-ceiling",
#     "nobf-ceiling",
#     "bf-ceiling",
#     "bf-ceiling-2",
#     "bf-ceiling-3"]


heatmap = None

stds = np.rad2deg([np.pi/j for _ in range(10) for j in np.arange(0.5, 180, 2)])


plt.figure()
for i in range(3):

    positions = np.load(
        f"../data/positions-gausbf-ceiling-grid-{i+1}-20241014122525-{i+1}.npy",
        allow_pickle=True,
    )
    values = np.load(
        f"../data/values-gausbf-ceiling-grid-{i+1}-20241014122525-{i+1}.npy",
        allow_pickle=True,
    )
    plt.scatter(stds[i], 10*np.log10(np.mean(10**(values/10))))


plt.show()
