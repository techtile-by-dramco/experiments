import glob
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from scipy.stats import norm

from datetime import datetime, timedelta
from matplotlib.dates import HourLocator, MinuteLocator

# Define the pattern to match the file names
file_pattern0 = 'received_data_CH0_ALL'
file_pattern1 = 'received_data_CH1_ALL'

# Get the directory where the script is located
script_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))

print(script_dir)

# Get a list of file paths matching the pattern in the script directory
file_paths = [f for f in os.listdir(script_dir) if os.path.isfile(os.path.join(script_dir, f)) and f.endswith('.dat') and (f.startswith(file_pattern0) or f.startswith(file_pattern1)) ]

print(file_paths)

# Iterate over each file and read its contents as np.float32
for file_path in file_paths:
    # Construct the full path to the file
    file_path = os.path.join(script_dir, file_path)

    # Read the binary file and cast to np.float32
    data = np.fromfile(file_path, dtype=np.float32)

    # avg_phase = np.rad2deg(data[::2])
    # std_phase = np.rad2deg(data[1::2])
    
    data = np.where(data < 0, data + 360, data)
    
    # median = np.median(data)
    
    # data = (data - median) + 180
    
    
    
    
    plt.figure()
    
    plt.title(file_path)
    
    hist, bins = np.histogram(data, density= True, bins=360*2)
    
    
    plt.plot(bins[:-1], hist)
    
    
    
    
    
    # Plot the PDF.
    xmin, xmax = plt.xlim()
    mu, std = norm.fit(data) 
    x = np.linspace(xmin, xmax, 1000)
    p = norm.pdf(x, mu, std)
    label = "Fit Values: mu={:.2f} and std={:.2f}".format(mu, std)
    plt.plot(x, p, 'k', linewidth=2, label=label)
    

    plt.legend()
    plt.savefig(file_path[:-4]+".png")
    plt.show()
    
    # # Now you can work with your data as np.float32 array
    # milli_seconds_array = np.arange(len(avg_phase))*(1020000.0/250000.0)*1000.0
    # print(milli_seconds_array)
    
    # # dates = np.datetime64('2024-02-10 10:22:15.0') +  np.timedelta64(milli_seconds_array, 'ms')
    
    # dates = [datetime(2024,2,10,10,22,15) + timedelta(milliseconds = ms) for ms in milli_seconds_array]
    
    # print("Data from file:", file_path)
    # plt.title(file_path)
    # plt.plot(dates, avg_phase)
    # plt.gcf().autofmt_xdate()  # Auto format x-axis date labels
    
    # # Set major ticks to hours and minor ticks to minutes
    # plt.gca().xaxis.set_major_locator(HourLocator(interval=1))  # Major ticks every hour
    # plt.gca().xaxis.set_minor_locator(MinuteLocator(interval=15))  # Minor ticks every 15 minutes
    
    # plt.fill_between(dates, avg_phase-std_phase, avg_phase+std_phase, facecolor='blue', alpha=0.5)
    # plt.grid(which='both', axis='x')  # Show both major and minor grid lines

    # plt.show()