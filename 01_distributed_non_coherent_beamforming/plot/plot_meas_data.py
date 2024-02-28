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

user_name = "/jarne"
path_to_repo = "/Documents/GitHub"
nr = "1709111155"

csv_file_path = f"/home{user_name}{path_to_repo}/experiments/01_distributed_non_coherent_beamforming/meas_data/{nr}_nc_data.csv"

# Read the CSV file
df = pd.read_csv(csv_file_path, header=None, names=['x', 'y', 'z', 'utc', 'dbm', 'tx_gain', 'cable_loss'])

# Round data
df = df.round(decimals=3)

print(np.mean(df.dbm))

plt = TechtilePlotter(f"RX power plot in [dBm] with TX gain {df.tx_gain[0]}")
#plt.antennas()
plt.measurements(df['x'], df['y'], df['z'], df['dbm'])

# # Create a layout with a specified aspect ratio
# layout = go.Layout(
#     scene=dict(
#         aspectmode='manual',
#         aspectratio=dict(x=2, y=1, z=1)  # Adjust x and y ratio to make it rectangular
#     )
# )

# fig = go.Figure(data=go.Scatter3d(
#     x=df['x'],
#     y=df['y'],
#     z=df['z'],
#     text=df['dbm'],
#     mode='markers',
#     marker=dict(color=df.dbm,colorscale='Viridis', size=14, colorbar=dict(thickness=20))
# ), layout=layout)

# # Define fixed dimensions for the axes
# fig.update_layout(
#     title=f"RX power plot in [dBm] with TX gain {df.tx_gain[0]}",
# )
# fig.update_layout(
#     scene=dict(
#         xaxis=dict(range=[0, 8.4]),  # Set the range for the x-axis
#         yaxis=dict(range=[0, 4]),  # Set the range for the y-axis
#         zaxis=dict(range=[0, 2.4])   # Set the range for the z-axis
#     )

# )



# fig.show()

# Save to html
plt.html(f"{os.path.dirname(current_script_path)}/{nr}_gain_{df.tx_gain[0]}.html")