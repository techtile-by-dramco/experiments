import sys
import os
import time

# Get the current directory of the script
server_dir = os.path.dirname(os.path.abspath(__file__))

print(server_dir)

# Navigate two folder back to reach the parent directory
exp_dir = os.path.abspath(os.path.join(os.path.abspath(os.path.join(server_dir, os.pardir)), os.pardir))

# *** Includes continuation ***
sys.path.append(f"{exp_dir}/server/scope")
from scope import Scope

# *** Local includes ***
sys.path.append(f"{exp_dir}/server")
from yaml_utils import *

#   Read YAML file
config = read_yaml_file(f"{exp_dir}/config.yaml")

#   INFO
info = config.get('info', {})

#   ENERGY PROFILER SYSTEM SETTINGS --> ToDo Check if it is definied in config file
scope_yaml = config.get('scope', {})

scope = Scope(scope_yaml.get("ip"), scope_yaml.get("cable_loss"), f"{exp_dir}/scope.csv", scope_yaml.get("csv_header"))
scope.setup(scope_yaml.get("bandwidth_hz"), scope_yaml.get("center_hz"), scope_yaml.get("span_hz"), scope_yaml.get("rbw_hz"), 84)

counter = 0
prev_time = 0

#while 1:
#    no_active_transmitters = 1
#    power_dBm, peaks = scope.get_power_dBm_peaks(scope_yaml.get("cable_loss"), no_active_transmitters)
#    #power_dBm = scope.get_power_dBm()
#
#
#    counter = counter + 1
#
#
#    if (time.time() - prev_time) > 1:
#        prev_time = time.time()
#
#        print(f"{counter} messages send per second")
#
#        print(power_dBm)
#
#        counter = 0