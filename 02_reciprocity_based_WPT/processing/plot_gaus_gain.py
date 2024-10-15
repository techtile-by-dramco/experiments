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

stds = np.rad2deg(
    [j * np.pi / 180.0 for j in np.arange(0, 181, 1) for _ in range(10)]
)


plt.figure()
for i in range(330):

    positions = np.load(
        f"../data/positions-gausbf-ceiling-grid-{i+1}-20241014211156-{i+1}.npy",
        allow_pickle=True,
    )
    values = np.load(
        f"../data/values-gausbf-ceiling-grid-{i+1}-20241014211156-{i+1}.npy",
        allow_pickle=True,
    )
    plt.scatter(stds[i], 10*np.log10(np.mean(10**(values/10))))


plt.show()
