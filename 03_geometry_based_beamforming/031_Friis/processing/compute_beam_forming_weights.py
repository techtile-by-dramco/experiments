import numpy as np
import matplotlib.pyplot as plt
import requests
import yaml
from matplotlib.patches import Rectangle


#################### CONFIGURATIONS ####################
output_path = "../client/config-phase-friis.yml"
########################################################


positions_url = r"https://raw.githubusercontent.com/techtile-by-dramco/plotter/refs/heads/main/src/TechtilePlotter/positions.yml"

# Retrieve the file content from the URL
response = requests.get(positions_url, allow_redirects=True)
# Convert bytes to string
content = response.content.decode("utf-8")
# Load the yaml
config = yaml.safe_load(content)

antennas = dict()

for c in config["antennes"]:
    # only one antenna is used
    ch = c["channels"][1]
    tile = c["tile"]
    antennas[tile] = {
        "pos" : [ch["x"], ch["y"], ch["z"]],
        "tx_phase": 0
    }

# UE position (energy neutral device)
p_EN = np.array([3.172191162109375, 1.7955023193359374, 0.2552783966064453])

# Constants
f = 920e6  # Antenna frequency (Hz)
c = 3e8  # Speed of light (m/s)
lambda_ = c / f  # Wavelength (m)

with open(output_path, "w") as f:

    for tile_name, a in antennas.items():
        d_EN = np.linalg.norm(a["pos"]-p_EN)  # Scalar distances (L x 1)

        # True channel vector to the device
        # h = lambda_  / (np.sqrt(4 * np.pi) * d_EN) * np.exp(-1j * 2 * np.pi / lambda_ * d_EN)

        # NOTE I removed the power contribution, as only the phases are used.
        h = np.exp(-1j * 2 * np.pi / lambda_ * d_EN)

        # MRT weights
        w = np.conj(h)

        antennas[tile_name]["tx_phase"] = np.rad2deg(np.angle(np.conj(h)))
        f.write(f"{tile_name}: {np.rad2deg(np.angle(np.conj(h)))}\n")
