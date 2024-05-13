import pandas as pd
# import matplotlib.pyplot as plt
# import plotly.express as px
# import plotly.graph_objects as go
import os
import numpy as np
from TechtilePlotter.TechtilePlotter import TechtilePlotter
import yaml

# Get the absolute path of the currently executing Python script
current_script_path = os.path.abspath(__file__)

# TODO --> average dbm values for same position data

linux = "/home"
windows = "C:/Users"

cable_loss_correction = 0 #dB

init_path = linux
user_name = "/jarne"
path_to_repo = "/Documents/Git/65b36553836d607fe7f7acf2/measurements"
nr = "1712835125"
name_after_nr = "esl_paper_meas"
info_name_after_nr = "info"
title = "ESL paper 'How to Perform Distributed Precoding to Wirelessly Power Shelf Labels: Signal Processing and Measurements'"

csv_file_path = f"{init_path}{user_name}{path_to_repo}/meas_data/{nr}_{name_after_nr}.csv"
csv_file_path_info = f"{init_path}{user_name}{path_to_repo}/meas_data/{nr}_{info_name_after_nr}.yml"

# Read the CSV file
# df = pd.read_csv(csv_file_path, header=None, names=['x', 'y', 'z', 'utc', 'rm', 'x_tx', 'y_tx', 'z_tx', 'rm_tx', 'x_rx', 'y_rx', 'z_rx', 'rm_rx', 'dbm', 'tx_gain', 'cable_loss'])
df = pd.read_csv(csv_file_path, header=None, names=['x', 'y', 'z', 'utc', 'rm', 'dbm', 'tx_gain', 'cable_loss'])


# Filter out data points below -60 dBm
df = df[df['dbm'] >= -60]

# Read info file
data = yaml.safe_load(open(csv_file_path_info, 'r'))

# Read list of active tiles and store in variable
active_tiles_list = None
if data.get('usrp', {}).get('transmitters_enabled'):
    tile_states = data.get('tile_states', {})
    active_tiles_list = tile_states.get('changed', [])
    dark_tiles_list = tile_states.get('dark', [])
    print(dark_tiles_list)

# Round data
df = df.round(decimals=3)

# Retrieve the mean of the measured values
print(np.mean(df.dbm))

plt = TechtilePlotter(f"{title}")
if not active_tiles_list == None:
    plt.antennas(active_tiles_list, color="green") #ToDo give "active_tiles_list" as parameter
if not dark_tiles_list == None:    
    plt.antennas(dark_tiles_list, color="red")
plt.measurements(df['x'], df['y'], df['z'], df['dbm'] + cable_loss_correction, label = df['dbm'] + cable_loss_correction)

# # Plot transmitter
# plt.measurements(df['x_tx'][:2], df['y_tx'][:2], df['z_tx'][:2], 1, color='red', label = "Transmitter", size = 15)

# # Plot receiver
# # plt.measurements(np.mean(np.asarray(df['x_rx']))*np.ones(2), np.mean(np.asarray(df['y_rx']))*np.ones(2), np.mean(np.asarray(df['z_rx']))*np.ones(2), 1, color='hotpink', label = "Receiver", size = 15)
# plt.measurements(df['x_rx'], df['y_rx'], df['z_rx'], 1, color='hotpink', label = "Receiver", size = 15)


# Show the plot
plt.show()

# Save the plot to html
# plt.html(f"{os.path.dirname(current_script_path)}/{nr}.html")