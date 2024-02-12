import glob
import numpy as np
import matplotlib.pyplot as plt
import os
import re

from datetime import datetime

# Define the pattern to match the file names
file_pattern = 'received_data_CH1_*\.dat'

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.realpath(__file__))

print(script_dir)

# Get a list of file paths matching the pattern in the script directory
file_paths = [f for f in os.listdir(script_dir) if os.path.isfile(os.path.join(script_dir, f)) and f.endswith('.dat')]

print(file_paths)

# Iterate over each file and read its contents as np.float32
for file_path in file_paths:
    # Construct the full path to the file
    file_path = os.path.join(script_dir, file_path)

    # Read the binary file and cast to np.float32
    data = np.fromfile(file_path, dtype=np.float32)

    avg_phase = np.rad2deg(data[::2])
    std_phase = np.rad2deg(data[1::2])
    
    # Now you can work with your data as np.float32 array
    milli_seconds_array = np.arange(len(avg_phase))*(1020000.0/250000.0)*1000.0
    
    dates = datetime(2024, 2, 10, 10,22,15) +  np.timedelta64(milli_seconds_array, 'ms')
    
    print("Data from file:", file_path)
    plt.title(file_path)
    plt.plot(dates, avg_phase)
    
    plt.fill_between(dates, avg_phase-std_phase, avg_phase+std_phase, facecolor='blue', alpha=0.5)
    plt.show()