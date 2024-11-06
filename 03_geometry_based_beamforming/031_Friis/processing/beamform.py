import numpy as np
import matplotlib.pyplot as plt
import requests
import yaml
from matplotlib.patches import Rectangle


#################### CONFIGURATIONS ####################
PLOT_ONLY_XY_PLANE = True
PLOT_ONLE_ACTIVE_TILES = True
########################################################


positions_url = r"https://raw.githubusercontent.com/techtile-by-dramco/plotter/refs/heads/main/src/TechtilePlotter/positions.yml"

active_tiles = [
    "A05",
    "A06",
    "A07",
    "A08",
    "A09",
    "A10",
    "B05",
    "B06",
    "B07",
    "B09",
    "B10",
    "C05",
    "C06",
    "C07",
    "C08",
    "C09",
    "C10",
    "D05",
    "D07",
    "D08",
    "D09",
    "D10",
    "E05",
    "E06",
    "E08",
    "E09",
    "F06",
    "F07",
    "F09",
    "G05",
    "G07",
    "G08",
]


# Retrieve the file content from the URL
response = requests.get(positions_url, allow_redirects=True)
# Convert bytes to string
content = response.content.decode("utf-8")
# Load the yaml
config = yaml.safe_load(content)
antenna_positions = []

for c in config["antennes"]:
    if c["tile"] in active_tiles or not PLOT_ONLE_ACTIVE_TILES:
        # only one antenna is used
        ch = c["channels"][1]
        # for ch in c["channels"]:
        antenna_positions.append([ch["x"], ch["y"], ch["z"]])

antenna_positions = np.asarray(antenna_positions)

# UE position (energy neutral device)
p_EN = np.array([3.14234423828125, 1.9168280029296876, 0.2558418731689453])

# Constants
f = 920e6  # Antenna frequency (Hz)
c = 3e8  # Speed of light (m/s)
lambda_ = c / f  # Wavelength (m)

L = len(antenna_positions)  # Number of antennas


if PLOT_ONLY_XY_PLANE:
    X_MIN, X_MAX = 2.6, 3.9
    Y_MIN, Y_MAX = 1.20, 2.45
else:
    # Grid limits and resolution
    X_MIN, X_MAX = 0, 8  # x-limits within the floorplan
    Y_MIN, Y_MAX = 0, 4  # y-limits within the floorplan

dx, dy = lambda_ / 50, lambda_ / 50  # spatial resolution in x and y directions

# Compute true channel and optimal weights
P_array = antenna_positions.transpose()  # (3 x L) matrix of antenna positions
r_EN = (
    np.tile(p_EN.reshape(3, 1), (1, L)) - P_array
)  # Vector distances from array to device
d_EN = np.linalg.norm(r_EN, axis=0)  # Scalar distances (L x 1)

# True channel vector to the device
# h = lambda_  / (np.sqrt(4 * np.pi) * d_EN) * np.exp(-1j * 2 * np.pi / lambda_ * d_EN)

# NOTE I removed the power contribution, as only the phases are used.
h = np.exp(-1j * 2 * np.pi / lambda_ * d_EN)

# MRT weights
w = np.conj(h) / np.linalg.norm(h)

# Create meshgrid for 2D window
xv_ = np.arange(X_MIN, X_MAX + dx, dx)
yv_ = np.arange(Y_MIN, Y_MAX + dy, dy)
x_mesh, y_mesh = np.meshgrid(xv_, yv_)
z_mesh = np.zeros_like(x_mesh) + p_EN[-1]  # Same z-level as array (ground plane)
Ng = x_mesh.size  # Number of grid points
print(f"Evaluating {Ng} points")

# Initialize y for path gain values
y = np.zeros(x_mesh.shape, dtype=complex)

# Loop through grid points
for gg in range(Ng):
    pg = np.array([x_mesh.flat[gg], y_mesh.flat[gg], z_mesh.flat[gg]])
    rag = (
        np.tile(pg.reshape(3, 1), (1, L)) - P_array
    )  # Vector distances from array to grid point
    dag = np.linalg.norm(rag, axis=0)  # Scalar distances (L x 1)

    # Channel vector at grid point
    hg = lambda_ / (4 * np.pi * dag) * np.exp(-1j * 2 * np.pi / lambda_ * dag)

    # Path gain at grid point
    y.flat[gg] = np.dot(w.T, hg)

print("Done.")

# Compute path gain at EN device
raEN = np.tile(p_EN.reshape(3, 1), (1, L)) - P_array
daEN = np.linalg.norm(raEN, axis=0)
hEN = lambda_ / (np.sqrt(4 * np.pi) * daEN) * np.exp(-1j * 2 * np.pi / lambda_ * daEN)
y_EN = np.dot(w.T, hEN)
PG_EN = 10 * np.log10(np.abs(y_EN) ** 2)
print(f"Path Gain at UE is {PG_EN:.2f} dB")

# Plot scenario
plt.figure(figsize=(8, 5))
PG_dB = 10 * np.log10(np.abs(y) ** 2)
plt.imshow(PG_dB, extent=[X_MIN, X_MAX, Y_MIN, Y_MAX], origin="lower", aspect="auto")
plt.plot(p_EN[0], p_EN[1], "bo", markersize=10)
plt.colorbar(label="PG in dB")


# Add rectangle around specified position
min_x, max_x = 2.6, 3.9
min_y, max_y = 1.20, 2.45
rect = Rectangle(
    (min_x, min_y),
    max_x - min_x,
    max_y - min_y,
    linewidth=2,
    edgecolor="r",
    facecolor="none",
)
plt.gca().add_patch(rect)


plt.xlabel("x in m")
plt.ylabel("y in m")
plt.clim(np.max(PG_dB) - 25, np.max(PG_dB))
plt.title("Path Gain (PG)")
plt.grid(True)
plt.show()
