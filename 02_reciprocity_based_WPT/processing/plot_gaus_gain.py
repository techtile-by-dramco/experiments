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
    [j * np.pi / 180.0 for j in np.arange(0, 185, 5) for _ in range(1)]
)

std_options = np.arange(0, 185, 5)
# 20241015150457 (ging boven 180 graden) to be merged
#  20241015154322

sols = [0] * len(std_options)
plt.figure()
for i in range(1053):

    idx = int(i % len(std_options))

    std = std_options[idx] * np.pi / 180.0
    # positions = np.load(
    #     f"../data/positions-gausbf-ceiling-grid-{i+1}-20241015154322-{i+1}.npy",
    #     allow_pickle=True,
    # )
    values = np.load(
        f"../data/values-gausbf-ceiling-grid-{i+1}-20241015154322-{i+1}.npy",
        allow_pickle=True,
    )
    _mean = np.mean(10 ** (values / 10))
    if type(sols[idx]) is not list:
        sols[idx] = []
    sols[idx].append(_mean)
    plt.scatter(np.rad2deg(std), 10 * np.log10(_mean), color="black")

upper_stds = [0]*len(std_options)
down_stds = [0] * len(std_options)
means = [0] * len(std_options)
print(f"x, y")
for i, std_opt in enumerate(std_options):
    upper_stds[i] = 10 * np.log10(np.mean(sols[i]) + np.std(sols[i]))
    down_stds[i] = 10 * np.log10(np.mean(sols[i]) - np.std(sols[i]))
    means[i] = 10 * np.log10(np.median(sols[i]))
    plt.scatter(np.rad2deg(std_options[i] * np.pi / 180.0), 10 * np.log10(np.median(sols[i])), c="blue")
    print(
        f"{np.rad2deg(std_options[i] * np.pi / 180.0)}, {10 * np.log10(np.median(sols[i])):.4f}"
    )

plt.plot(np.rad2deg(std_options*np.pi / 180.0), means, color="blue", alpha=0.5)
# plt.fill_between(
#     np.rad2deg(std_options * np.pi / 180.0),
#     y1=upper_stds,
#     y2=down_stds,
#     color="blue",
#     alpha=0.2,
# )
plt.hlines(10 * np.log10(np.max(sols[0])), xmin=0, xmax=180)
plt.show()
