# %% load modules
import numpy as np
import matplotlib.pyplot as plt
import requests
import yaml
from matplotlib.patches import Rectangle

#### data storage and access
import h5py
import dss_utilities as du
import simulator_utilities as su
import plotting_functions as pf
import utility_functions as uf


#################### CONFIGURATIONS ####################
output_path = "config-phase-friis.yml"
output_path_sim = ".config-phase-friis-sim.yml"
env_filename = "/srv/thomasw/Git/KUL-TUG_simulator/matlab/data_/CLA/environment_techtile_v4-1_medium_grid.hdf5"

# output_path = "../client/config-phase-friis.yml"
# output_path_sim = "../client/config-phase-friis-sim.yml"
########################################################

# %% load techtile config
positions_url = r"https://raw.githubusercontent.com/techtile-by-dramco/plotter/refs/heads/main/src/TechtilePlotter/positions.yml"

# Retrieve the file content from the URL
response = requests.get(positions_url, allow_redirects=True)
# Convert bytes to string
content = response.content.decode("utf-8")
# Load the yaml
config = yaml.safe_load(content)

antennas = dict()
tile_idx = []

for c in config["antennes"]:
    # only one antenna is used
    ch = c["channels"][1]
    tile = c["tile"]
    antennas[tile] = {"pos": [ch["x"], ch["y"], ch["z"]], "tx_phase": 0}
    # tile_idx.append(t)

Nt = len(antennas)
tile_idx = np.arange(Nt)
# tile_idx = np.asarray(tile_idx) #needed to select corresponding virtual tiles from above

# UE position (energy neutral device)
p_EN = np.array([3.172191162109375, 1.7955023193359374, 0.2552783966064453])

# Constants
f = 920e6  # Antenna frequency (Hz)
c = 3e8  # Speed of light (m/s)
lambda_ = c / f  # Wavelength (m)


# %% load scenario file
df = h5py.File(env_filename, "r")

env = df["environment"]
data = du.collect_layer_data(env, omit="channel")

# environment setup:
# extract VAs from scenario file, VAs are mirror sources of the tiles, termed virtual tiles (VTs)
print(data["scenario"].keys())

# tiles as one large array
p_t = np.array(
    data["array"]["p"]
)  # (3 x Nt): positions of tiles (center point of two antennas pm_t in coordiantes relative to p)
N_t = data["array"]["p"].shape[1]  # number of tiles
pm_t = np.array(data["array"]["pm"])  # (3 x M): positions of all antennas
M = data["array"]["pm"].shape[1]  # number of all antennas
m_t = (
    np.array(data["array"]["BS_assoc"]) - 1
)  # (1 x M): association of antennas to tiles (-1 to convert to python indexing starting from 0)
j_t = np.array([np.arange(N_t)])

# virtual tiles based on mirror source model
is_active = np.array(data["scenario"]["VAData"]["active"])[0] != 0
N_vt = np.sum(is_active)
type_vt = np.array(data["scenario"]["VAData"]["VAtype"])[
    :, is_active
]  # (1 x Nvas): VA order, 0 (original tile), 1 (first order), 2 (second order)
p_vt = np.array(data["scenario"]["VAData"]["VA"])[
    :, is_active
]  # (3 x Nvas): position of all VAs
H_vt = np.array(data["scenario"]["VAData"]["H"])[
    :, :, is_active
]  # (3 x 3 x Nvas): householder matrix to mirror the array and obtain the correct orientation for the DOA at a tile
t_vt = (
    np.array(data["scenario"]["VAData"]["VABSassoc"])[:, is_active] - 1
)  # (1 x Nvas): original tile index

# mirror source visibility information over a grid
# (a finer grid can be exported, or a simple nearest neighbor visibility check can be used)
V_g = np.array(data["user"]["VAvis"])[:, is_active] != 0  # (N_g x N_vt)
p_g = np.array(data["user"]["position"])
N_g = p_g.shape[1]
xg = np.array(data["user"]["x_axis"])
yg = np.array(data["user"]["y_axis"])
zg = np.array(data["user"]["z_axis"])

# **short explanation**
# virtual tile positions are computed and can be used to compute the channels to any position.
# the visibility stored in V_g = (N_g x N_vt) indicates whether the virtual tiles are visibile at a position N_g
# - first order image sources will be visible over the whole environment for a box shaped room
# - second order image sources might not be visible everywhere (in the simple way implemented, every second order
#   reflection is represented by two image sources: one for the path wall A -- wall B, and another one for the
#   path wall B -- wall A. depending on the wall geometry ony one of these will be visible. In a box shaped room
#   these mirror sources are always on the same position)


# %% write to yml
with open(output_path, "w") as f:

    for tile_name, a in antennas.items():
        d_EN = np.linalg.norm(a["pos"] - p_EN)  # Scalar distances (L x 1)

        # True channel vector to the device
        # h = lambda_  / (np.sqrt(4 * np.pi) * d_EN) * np.exp(-1j * 2 * np.pi / lambda_ * d_EN)

        # NOTE I removed the power contribution, as only the phases are used.
        h = np.exp(-1j * 2 * np.pi / lambda_ * d_EN)

        # MRT weights
        w = np.conj(h)

        antennas[tile_name]["tx_phase"] = np.rad2deg(np.angle(np.conj(h)))
        f.write(f"{tile_name}: {np.rad2deg(np.angle(np.conj(h)))}\n")

# %% write sim to yml
this_grid_pos = np.argmin(
    np.linalg.norm(p_g - np.tile(p_EN.reshape(3, 1), (1, N_g)), axis=0)
)
this_ch = 1  # use the first antenna of the pair

# K_max = 0 #checked: produces the same result as written to {output_path}
K_max = 2

with open(output_path_sim, "w") as fsim:

    for tile_idx, (tile_name, a) in enumerate(antennas.items()):
        d_EN = np.linalg.norm(a["pos"] - p_EN)  # Scalar distances (L x 1)

        sel_vts = t_vt[0] == tile_idx
        sel_order = type_vt[0] <= K_max
        sel_vis = V_g[this_grid_pos]

        # indices of tile antennas
        m_tile = np.where(m_t[0] == tile_idx)[0]
        pm_tile = pm_t[:, [m_tile[this_ch]]] - np.mean(
            pm_t[:, m_tile], axis=1, keepdims=True
        )

        k_idx = np.where(sel_vts & sel_order & sel_vis)[
            0
        ]  # find VTs corresponding to tile index that have order <= K_max
        hk = np.zeros_like(k_idx, dtype=complex)
        for ik, kk in enumerate(k_idx):
            # selected mirror source position and necessary rotation due to mirroring at segement (needed to compute the correct antenna positions)
            p_kk = p_vt[:, [kk]]
            H_kk = H_vt[:, :, kk]

            # corresponding antenna position for selected channel
            pm_ch = p_kk + H_kk @ pm_tile

            # distances to END position
            dk = np.linalg.norm(
                p_EN.reshape(3, 1) - pm_ch, axis=0
            )  # compute distance to END position

            # channel of all MPCs up to selected order, add attenuation per MPC here:
            # gamma_k = (10**(-3/20))**(type_vt[0][kk]) #-3dB per reflection (order 0 = no att., order 1 = att. once, ...)
            gamma_k = 1
            hk[[ik]] = np.exp(-1j * 2 * np.pi / lambda_ * dk)

        # sum up MPCs
        h = np.sum(hk)

        # MRT weights
        w = np.conj(h)

        antennas[tile_name]["tx_phase"] = np.rad2deg(np.angle(np.conj(h)))
        fsim.write(f"{tile_name}: {np.rad2deg(np.angle(np.conj(h)))}\n")


# %%
