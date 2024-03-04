import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np
from TechtilePlotter.TechtilePlotter import TechtilePlotter

# Get the absolute path of the currently executing Python script
current_script_path = os.path.abspath(__file__)

# TODO --> average dbm values for same position data

linux = "/home"
windows = "C:/Users"

init_path = windows
user_name = "/jarne"
path_to_repo = "/Documents/GitHub"
nr = "1709112625"

csv_file_path = f"{init_path}{user_name}{path_to_repo}/experiments/01_distributed_non_coherent_beamforming/meas_data/{nr}_nc_data.csv"

# Read the CSV file
df = pd.read_csv(csv_file_path, header=None, names=['x', 'y', 'z', 'utc', 'dbm', 'tx_gain', 'cable_loss'])

# Round data
df = df.round(decimals=3)

# Retrieve the mean of the measured values
print(np.mean(df.dbm))

plt = TechtilePlotter(f"RX power plot in [dBm] with TX gain {df.tx_gain[0]}")
plt.antennas()
plt.measurements(df['x'], df['y'], df['z'], df['dbm'], label = df['dbm'])

# Show the plot
# plt.show()

# Save the plot to html
plt.html(f"{os.path.dirname(current_script_path)}/{nr}_gain_{df.tx_gain[0]}.html")