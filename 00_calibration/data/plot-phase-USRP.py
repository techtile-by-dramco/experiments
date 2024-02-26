import glob
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from scipy.stats import norm, circmean, circstd

import threading
from datetime import datetime, timedelta
from matplotlib.dates import HourLocator, MinuteLocator

import allantools
#TODO CHECK ALLAN DEV

# Define the pattern to match the file names
file_pattern0 = 'received_data_CH0_ALL'
file_pattern1 = 'received_data_CH1_ALL'

# Get the directory where the script is located
script_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))

print(script_dir)

# Get a list of file paths matching the pattern in the script directory
file_paths = [f for f in os.listdir(script_dir) if os.path.isfile(os.path.join(script_dir, f)) and f.endswith('.dat') and (f.startswith(file_pattern0) or f.startswith(file_pattern1)) ]

print(file_paths)

# Define a function to be the target for each thread
def circmean_thread(thread_id, results, val):
    results[thread_id] = my_circmean(val)

def my_circmean(phases):
    return np.angle(np.sum(np.exp(phases*1j))) # circular mean https://en.wikipedia.org/wiki/Circular_mean

# Iterate over each file and read its contents as np.float32
for file_path in file_paths:
    # Construct the full path to the file
    file_path = os.path.join(script_dir, file_path)

    # Read the binary file and cast to np.float32
    data = np.fromfile(file_path, dtype=np.float32)
    
    print(f"Num samples: {len(data)}")

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
    label = f"Fit Values: mu={mu:.2f} and std={mu:.2f}"
    plt.plot(x, p, 'k', linewidth=2, label=label)
    

    plt.legend()
    plt.savefig(file_path[:-4]+"-hist.png")
    plt.show()
    
    plt.figure()
    plt.title(file_path)
    
    phase = np.deg2rad(data)
    
    # sample rate is 1e6
    rate = 1e6
    
    sample_size = int(1e6)
    

    phase = np.array_split(phase, len(phase) / sample_size)
    print("split done")
    num_frames = len(phase)
    
    # means = np.zeros(num_frames)
    # stds =  np.zeros(num_frames)
    
    means = np.array([my_circmean(phase[i]) for i in range(num_frames)])
    
    
    
    
    # threads = []
    # means = [None] * num_frames
    # for i in range(num_frames):
    #     th = threading.Thread(target=circmean_thread, args=(i, means, phase[i]))
    #     th.start()
    #     threads.append(th)
        
    # # Wait for all threads to finish
    # for thread in threads:
    #     thread.join()

    
    print("means done")
    stds =  np.array([circstd(phase[i]) for i in  range(num_frames)])
    print("stds done")
    
    # for i in range(num_frames):
    #     means[i] = circmean(phase[i])
    #     stds[i]  = circstd(phase[i])
    
    x = np.array(range(num_frames)) * (sample_size/rate) # in seconds  60 seconds
    
    
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
    
    plt.fill_between(x, np.rad2deg(means-stds), np.rad2deg(means+stds), facecolor='blue', alpha=0.5)
    plt.plot(x, np.rad2deg(means))
    plt.grid(which='both', axis='x')  # Show both major and minor grid lines
    plt.xlabel("Time (in seconds)")
    plt.title(np.rad2deg(circstd(means)))

    plt.show()