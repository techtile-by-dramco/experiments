import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import os

# Get the absolute path of the currently executing Python script
current_script_path = os.path.abspath(__file__)

# TODO --> average dbm values for same position data

user_name = "/jarne"
path_to_repo = "/Documents/GitHub"
nr = "1708519348"

csv_file_path = f"/home{user_name}{path_to_repo}/experiments/01_distributed_non_coherent_beamforming/meas_data/{nr}_nc_data.csv"

# Read the CSV file
df = pd.read_csv(csv_file_path, header=None, names=['nr', 'x', 'y', 'z', 'utc', 'dbm'])

# Round data
df = df.round(decimals=3)

# Create a layout with a specified aspect ratio
layout = go.Layout(
    scene=dict(
        aspectmode='manual',
        aspectratio=dict(x=2, y=1, z=1)  # Adjust x and y ratio to make it rectangular
    )
)

fig = go.Figure(data=go.Scatter3d(
    x=df['x'],
    y=df['y'],
    z=df['z'],
    text=df['dbm'],
    mode='markers',
    marker=dict(color=df.dbm,colorscale='Viridis', size=14, colorbar=dict(thickness=20))
), layout=layout)

# Define fixed dimensions for the axes
fig.update_layout(
    scene=dict(
        xaxis=dict(range=[0, 8.4]),  # Set the range for the x-axis
        yaxis=dict(range=[0, 4]),  # Set the range for the y-axis
        zaxis=dict(range=[0, 2.4])   # Set the range for the z-axis
    )
)

# fig.show()

# Save to html
fig.write_html(f"{os.path.dirname(current_script_path)}/{nr}_plot.html")
