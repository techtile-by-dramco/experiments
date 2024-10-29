import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.pyplot as plt
import requests
import yaml
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d import Axes3D  # Import 3D plotting toolkit


# Specify the relative path to ffmpeg.exe (same folder as the script)
ffmpeg_path = "./ffmpeg.exe"
plt.rcParams["animation.ffmpeg_path"] = ffmpeg_path

#################### CONFIGURATIONS ####################
PLOT_ONLY_XY_PLANE = False
PLOT_ONLE_ACTIVE_TILES = False
########################################################

positions_url = r"https://raw.githubusercontent.com/techtile-by-dramco/plotter/refs/heads/main/src/TechtilePlotter/positions.yml"

active_tiles = [
    "A05", "A06", "A07", "A08", "A09", "A10",
    "B05", "B06", "B07", "B09", "B10",
    "C05", "C06", "C07", "C08", "C09", "C10",
    "D05", "D07", "D08", "D09", "D10",
    "E05", "E06", "E08", "E09",
    "F06", "F07", "F09",
    "G05", "G07", "G08"
]

# Retrieve the file content from the URL
response = requests.get(positions_url, allow_redirects=True)
content = response.content.decode("utf-8")
config = yaml.safe_load(content)
antenna_positions = []

for c in config["antennes"]:
    if c["tile"] in active_tiles or not PLOT_ONLE_ACTIVE_TILES:
        ch = c["channels"][1]
        antenna_positions.append([ch["x"], ch["y"], ch["z"]])

antenna_positions = np.asarray(antenna_positions)


# Constants
f = 920e6  # Antenna frequency (Hz)
c = 3e8  # Speed of light (m/s)
lambda_ = c / f  # Wavelength (m)

L = len(antenna_positions)  # Number of antennas

if PLOT_ONLY_XY_PLANE:
    X_MIN, X_MAX = 2.6, 3.9
    Y_MIN, Y_MAX = 1.20, 2.45
else:
    X_MIN, X_MAX = 0, 8  # x-limits within the floorplan
    Y_MIN, Y_MAX = 0, 4  # y-limits within the floorplan

dx, dy = lambda_ / 10, lambda_ / 10  # spatial resolution in x and y directions

# Define the number of frames for the video
num_frames = 30


L = len(antenna_positions)  # Number of antennas

# Define grid for mesh
xv_ = np.arange(X_MIN, X_MAX + dx, dx)
yv_ = np.arange(Y_MIN, Y_MAX + dy, dy)
x_mesh, y_mesh = np.meshgrid(xv_, yv_)
z_mesh = np.zeros_like(x_mesh) + 0.5

# Create a figure for 3D plot
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# Function to update each frame with new random phase
def update_frame(frame_number):
    ax.clear()  # Clear the plot for the next frame

    # Random phase between 0 and 2π
    random_phase = np.random.uniform(0, 2 * np.pi, L)
    
    # True channel vector with random phase
    h = np.exp(1j * random_phase)

    # MRT weights
    w = np.conj(h) 
    
    # Initialize y for path gain values
    y = np.zeros(x_mesh.shape, dtype=complex)

    # Compute path gain for each grid point
    for gg in range(x_mesh.size):
        pg = np.array([x_mesh.flat[gg], y_mesh.flat[gg], z_mesh.flat[gg]])
        rag = np.tile(pg.reshape(3, 1), (1, L)) - antenna_positions.T  # Vector distances from array to grid point
        dag = np.linalg.norm(rag, axis=0)  # Scalar distances (L x 1)

        # Channel vector at grid point
        hg = lambda_ / (4 * np.pi * dag) * np.exp(-1j * 2 * np.pi / lambda_ * dag)

        # Path gain at grid point
        y.flat[gg] = np.dot(w.T, hg)
    
    # Compute the path gain in dB
    PG_dB = 10 * np.log10(np.abs(y) ** 2)

    # Plot the surface
    surf = ax.plot_surface(x_mesh, y_mesh, PG_dB, vmin=-30, vmax=0, cmap='viridis')
    ax.set_zlim(-30,0)


    # Set labels and title
    ax.set_xlabel('X in m')
    ax.set_ylabel('Y in m')
    ax.set_zlabel('Path Gain (PG) in dB')
    ax.set_title(f'Frame {frame_number + 1}')

    # Add colorbar (for first frame only to avoid overlap)
    # if frame_number == 0:
    #     fig.colorbar(surf)

# Create an animation
anim = FuncAnimation(fig, update_frame, frames=num_frames, interval=1)

# Save the animation as an MP4 file
anim.save('random_phase_path_gain.mp4', writer='ffmpeg', fps=10)

plt.close(fig)
