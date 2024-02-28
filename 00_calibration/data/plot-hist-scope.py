import glob
import numpy as np
import matplotlib.pyplot as plt
import os
import re


# Define the pattern to match the file names
files = ["CH0-CH1.csv", "PLL-PLL-phase.csv"]

# Get the directory where the script is located
script_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))

print(script_dir)

# Iterate over each file and read its contents as np.float32
for file in files:
    # Construct the full path to the file
    file_path = os.path.join(script_dir, file)

    # Read the CSV file
    data = np.genfromtxt(file_path, delimiter=',', skip_header=1)
    
    # Convert angles from 0-360 range to -180 to 180 range
    angles = data[:, 0]
    angles = np.where(angles > 180, angles - 360, angles)
    values = data[:, 1]

    # Filter out data points with a value below 10
    mask = data[:, 1] >= 10

    # Sort the filtered data based on the converted angles
    sorted_indices = np.argsort(angles[mask])
    sorted_angles = angles[mask][sorted_indices]
    sorted_values = values[mask][sorted_indices]
    plt.plot(sorted_angles, sorted_values, '-o' )
    plt.xlabel('Phase difference in degreees (-180 till 180)')
    plt.ylabel('Hits')
    plt.title(file)
    plt.grid(True)
    
    out_file_path = os.path.join(script_dir, file[:-4]+"-plot.png")
    plt.savefig(out_file_path) 
    plt.show()