import argparse

parser = argparse.ArgumentParser(description='Signal configurator')

# Optional arguments
parser.add_argument('--frequency', type=float, default=920E6, help='Center frequency')
parser.add_argument('--offset', type=float, default=1E2, help='Frequency offset')
# parser.add_argument('--multitone', type=bool, default=False, help='Multitone enabled/disabled')
group = parser.add_mutually_exclusive_group()
group.add_argument('--multitone', action='store_true', help='Enable multitone')
group.add_argument('--singletone', action='store_false', dest='multitone', help='Disable multitone')

args = parser.parse_args()

multitone_enabled = args.multitone
center_freq = args.frequency
frequency_offset = args.offset

print(multitone_enabled, center_freq, frequency_offset)

#   ***** Parser DONE *****

# *** Includes ***
import sys
import os

# Get the current directory of the script
server_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate one folder back to reach the parent directory
exp_dir = os.path.abspath(os.path.join(server_dir, os.pardir))

# *** Local includes ***
sys.path.append(f"{exp_dir}/server")
from yaml_utils import *

#   Read YAML file
config = read_yaml_file(f"{exp_dir}/config.yaml")

#   INFO
info = config.get('info', {})
exp_name = info.get('exp_name')
server_user_name = info.get('server_user_name')
data_save_path = info.get('data_save_path')

#   CONTROL
control_yaml = config.get('control', {})

#   ANSIBLE SETTINGS
ansible_yaml = config.get('ansible', {})

#   LOCATION SYSTEM SETTINGS --> ToDo Check if it is definied in config file
positioning_yaml = config.get('positioning', {})

#   ENERGY PROFILER SYSTEM SETTINGS --> ToDo Check if it is definied in config file
scope_yaml = config.get('scope', {})

#   ENERGY PROFILER SYSTEM SETTINGS --> ToDo Check if it is definied in config file
ep_yaml = config.get('ep', {})

#   CLIENT
client = config.get('client', {})

def generate_frequencies(center_freq, frequency_offset, num_offsets):
    """
    Generate a list of frequencies around the center frequency.
    
    Parameters:
    center_freq (float): The center frequency in Hz.
    frequency_offset (float): The frequency offset between each frequency in Hz.
    num_offsets (int): The number of offsets to generate on each side of the center frequency.
    
    Returns:
    list: A list of frequencies around the center frequency.
    """
    frequencies = []

    for i in range(-num_offsets, num_offsets + 1):
        if multitone_enabled:
            freq = center_freq + i * frequency_offset
            frequencies.append(freq)
        else:
            frequencies.append(center_freq)
    
    return frequencies

# Get hosts
hosts = client.get("hosts")

# Define the segments and the range of numbers
segments = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
start = 5
end = 10

# Generate the list of tiles
tiles = [f"{segment}{num:02}" for segment in segments for num in range(start, end + 1)]

# NO tiles
number_of_tiles = len(tiles)

print(number_of_tiles)

num_offsets = int(number_of_tiles/2)  # Number of offsets to generate on each side

frequencies = generate_frequencies(center_freq, frequency_offset*2, num_offsets)[0:num_offsets*2]
print(frequencies)


for i, tile in enumerate(tiles):
    hosts[tile] = {'freq': frequencies[i]}


config['client']['hosts'] = hosts

if multitone_enabled:
    config['client']['hosts']['all']['lo_offsets'] = [0, int(frequency_offset)]
else:
    config['client']['hosts']['all']['lo_offsets'] = [0, 0]

print(config['client']['hosts'])


write_yaml_file(f"{exp_dir}/config.yaml", config)
