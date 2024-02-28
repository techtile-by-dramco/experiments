import glob
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from scipy.stats import norm, circmean, circstd

import threading
import datetime

from tqdm import tqdm 

import allantools
#TODO CHECK ALLAN DEV

RECENT_FIRST = True

PLOT_HIST = False
PLOT_TIME_DURATION = False
PLOT_SAMPLE_INTERVALS = False
PLOT_MEAN_STD = True
STORE = False

# Define the pattern to match the file names
file_pattern0 = 'received_data_CH0_ALL'
file_pattern1 = 'received_data_CH1_ALL'

# Get the directory where the script is located
script_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))

print(script_dir)

# Get a list of file paths matching the pattern in the script directory
file_paths = [f for f in os.listdir(script_dir) if os.path.isfile(os.path.join(script_dir, f)) and f.endswith('.dat') and (f.startswith(file_pattern0) or f.startswith(file_pattern1)) ]

# Define a function to extract timestamp
def extract_timestamp(filename):
    parts = filename.split('_')
    date_part = parts[-2]
    time_part = parts[-1].split('.')[0]
    return datetime.datetime.strptime(date_part + "_" + time_part, '%Y-%m-%d_%H-%M-%S')

# Sort the list based on timestamp
file_paths = sorted(file_paths, key=extract_timestamp, reverse=RECENT_FIRST)

print(file_paths)

# Define a function to be the target for each thread
def circmean_thread(thread_id, results, val):
    results[thread_id] = my_circmean(val)

def my_circmean(phases):
    return np.angle(np.sum(np.exp(phases*1j))) # circular mean https://en.wikipedia.org/wiki/Circular_mean

def circmedian(angs):
    pdists = angs[np.newaxis, :] - angs[:, np.newaxis]
    pdists = (pdists + np.pi) % (2 * np.pi) - np.pi
    pdists = np.abs(pdists).sum(1)
    return angs[np.argmin(pdists)]
def std_mean(samples, mean):
    return np.sqrt(np.mean(np.abs(samples - mean)**2))

# Iterate over each file and read its contents as np.float32
for file_path in file_paths:
    # Construct the full path to the file
    file_path = os.path.join(script_dir, file_path)

    # Read the binary file and cast to np.float32
    raw_data = np.fromfile(file_path, dtype=np.float32)
    
    CH_STR = "CH0" if "CH0" in file_path else "CH1"
    
    num_samples = len(raw_data)
    
    raw_phase_deg = raw_data
    raw_phase_rad = np.deg2rad(raw_phase_deg)
    total_mean_rad = circmean(raw_phase_rad)
    
    
    data = raw_data
    print(f"Num samples: {num_samples}")

    # avg_phase = np.rad2deg(data[::2])
    # std_phase = np.rad2deg(data[1::2])
    
    # data = np.where(data < 0, data + 360, data)
    rate = 250e3
    
    # median = np.median(data)
    
    # data = (data - median) + 180
    
    
    
    # PLOT HIST OF COLLECTED PHASES
    if PLOT_HIST:
        print("Plotting histogram")
        plt.figure()
        plt.title(
            f"[{CH_STR}][{extract_timestamp(file_path)}] Histogram of all phases (bins = 360*2)")
        hist, bins = np.histogram(raw_phase_rad, density= False, bins=360*100)
        plt.plot(np.rad2deg(bins[:-1]), hist)
        # Plot the PDF.
        # xmin, xmax = plt.xlim()
        # mu, std = norm.fit(data) 
        # x = np.linspace(xmin, xmax, 1000)
        # p = norm.pdf(x, mu, std)
        # label = f"Fit Values: mu={mu:.2f} and std={mu:.2f}"
        # plt.plot(x, p, 'k', linewidth=2, label=label)
        plt.legend()
        if STORE:
            plt.savefig(file_path[:-4]+"-hist.png")


    x_times_rate = num_samples // rate
    num_samples_range = [1e2,1e3,1e4]
    num_samples_range.extend(list(np.linspace(1,x_times_rate/2)*rate))
    num_samples_range.extend([num_samples])
    
    
    if PLOT_TIME_DURATION:
        print("Plotting time duration")
        res = []
        time = []
        
        
        for i in tqdm(num_samples_range):
            i = int(i)
            res.append(circmean(raw_phase_rad[:i]))
            # median.append(np.median(phase[:i]))
            time.append(i/rate)
            
        plt.figure()
        plt.title(
            f"[{CH_STR}][{extract_timestamp(file_path)}] Mean phase over the time interval")
        plt.plot(time, res, '-o' )
        plt.ylabel("Mean Phase (radians)")
        plt.xlabel("Time sampling (seconds) starting from time 0s")
        # plt.plot(time, median, label="median")
        plt.legend()
        if STORE:
            plt.savefig(file_path[:-4]+"-time-interval.png")
        plt.show()
    
    if PLOT_SAMPLE_INTERVALS:
        print("Plotting time intervals")
        
        stds = []
        time = []
        for i in tqdm(num_samples_range):
            phase = np.array_split(raw_phase_rad, num_samples // i)
            num_frames = len(phase)
            means = np.array([circmean(phase[i]) for i in range(num_frames)])
            std = std_mean(means, total_mean_rad)
            stds.append(std)
            time.append(i/rate)
                
            
        plt.figure()
        plt.title(
            f"[{CH_STR}][{extract_timestamp(file_path)}] Std phase over the time interval")
        plt.ylabel("Std Phase (degrees)")
        plt.xlabel("Sample intervals (in seconds)")
        plt.plot(time, np.rad2deg(stds), label = "mean")
        plt.ticklabel_format(style='plain',useOffset=False)    # to prevent scientific notation.
        # plt.plot(time, median, label="median")
        plt.legend()
        if STORE:
            plt.savefig(file_path[:-4]+"-sample-interval.png")
    
    
    if PLOT_MEAN_STD:
        print("Plotting mean stds")
        sample_size = int(rate)
        phase = np.array_split(raw_phase_rad, len(raw_data) // sample_size)
        num_frames = len(phase)
        means = np.array([my_circmean(phase[i]) for i in range(num_frames)])
        stds =  np.array([circstd(phase[i]) for i in  range(num_frames)])
        x = np.array(range(num_frames)) * (sample_size/rate) # in seconds  60 seconds
        
        plt.figure()
        plt.title(f"[{CH_STR}][{extract_timestamp(file_path)}] Std of all {np.rad2deg(circstd(raw_phase_rad)):.2f} std of of means {np.rad2deg(circstd(means)):.2f} with sample interval {sample_size/rate:.2f}s")
        plt.fill_between(x, np.rad2deg(means-stds), np.rad2deg(means+stds), facecolor='blue', alpha=0.5)
        plt.plot(x, np.rad2deg(means))
        plt.grid(which='both', axis='x')  # Show both major and minor grid lines
        plt.ticklabel_format(style='plain', useOffset=False)    # to prevent scientific notation.
        plt.xlabel("Time (in seconds)")
        plt.ylabel("Phase (degrees)")
        if STORE:
            plt.savefig(file_path[:-4]+"-means-std.png")
    
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
    
    
