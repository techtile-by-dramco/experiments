# /bin/python3 -m experiments.01_distributed_non_coherent_beamforming.main
# see for relative import: https://stackoverflow.com/a/68315950/3590700

import sys
import os
script_patch = os.getcwd()
sys.path.append(f"{script_patch}/location")
from position import AcousticPositioner
sys.path.append(f"{script_patch}/scope")
from scope import Scope
sys.path.append(f"{script_patch}/rfep")
from rfep import RFEP
import time 
import ansible_runner
import zmq
import csv
import yaml
import pandas as pd

# Local includes
from yaml_utils import *

# Get the current directory of the script
server_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate one folder back to reach the experiment directory
exp_dir = os.path.abspath(os.path.join(server_dir, os.pardir))



if __name__ == "__main__":

    config = read_yaml_file(exp_dir)


    r = ansible_runner.run(
        inventory=f'/home/{user_name}/ansible/inventory/{ansible_inventory_yaml}',
        playbook=f'/home/{user_name}/ansible/{ansible_stop_script_yaml}',
        extravars={"tiles": active_tile_list}
    )




exit()

#--------------------------------------------------------------#
#                   ***     SETTINGS    ***                    #
#--------------------------------------------------------------#
#   PATH SETTINGS
user_name = "/jarne"
csv_header = ['x', 'y', 'z', 'utc', 'dbm', 'buffer_voltage_mv', 'resistance', 'pwr_nw']

#   DESCRIPTION
height_cm = "multiple"
description = f"Measurement for WP5 Reindeer Exp. 4aa PART 1"
xaxisoffset = 0
yaxisoffset = 0
zaxisoffset = 0

#   LOCATION SYSTEM SETTINGS
positioning_system = "QUALYSIS"
positioning_system_server_ip = "192.108.0.13" # IP address of Qualisys server
positioning_system_zmq_port = '5555'

#   ANSIBLE SETTINGS
ansible_start_script_yaml = 'start_transmitters_random_phase.yaml'
ansible_stop_script_yaml = '>>NAME<<.yaml'
ansible_inventory_yaml = 'hosts.yaml'
ansible_enable_stop_script = False
tiles = "multiON" #ceiling 'TEST AANPASSEN !!!'

#   HOST SCRIPT SETTINGS
enable_host_script = True
host_script = 'tx_waveforms_random_phase.py'
#   ------> INTERNAL
tx_gain = 100
tx_frequency = 917E+06
channels = '0'#'0 1' 'TEST ENKEL KANAAL 0 AANPASSEN !!!'
duration = 60
server_ip_address = "192.108.0.204" # IP address for ZMQ messages (TX server) (RX RPIs)
#   ------> EXTERNAL
enable_external_host_settings = False # (enable_external_usrp_settings <-- FALSE)
external_conf_file = ">>NAME<<.csv"

#   SCOPE SETTINGS
scope_ip = "192.108.0.251"
bandwidth_hz = 6.0000E+09
center_hz = 917011E+03
span_hz = 5E+03
rbw_hz = 2E+00
cable_loss = 0 # ToDo 3.72 # Measured with the VNA (R&S ZVH8)

#   EP SETTINGS
target_voltage = 1600   #   Not adjustable at the moment
ep_gateway_ip = '192.108.0.13'
ep_zmq_port = '5556'

#   CONTROL script
ctrl_zmq_ip = 'localhost'
ctrl_zmq_port = '5558'
#--------------------------------------------------------------#
name_after_nr = "experiment_4aa_part_1"
info_name_after_nr = "info"
#--------------------------------------------------------------#
description_config = {
    "description": description,
    "xaxisoffset": xaxisoffset,
    "yaxisoffset": yaxisoffset,
    "zaxisoffset": zaxisoffset,
}

#   Save name of selected ansible sripts
ansible_config = {
    "ansible_start_script_yaml": ansible_start_script_yaml,
    "ansible_stop_script_yaml": ansible_stop_script_yaml,
    "ansible_inventory_yaml": ansible_inventory_yaml,
    "ansible_enable_stop_script": ansible_enable_stop_script,
    "tiles": tiles,
}

#   Create configuration dictionary usrp
if enable_host_script:
    if enable_external_host_settings:
        host_config = {
            "transmitters_enabled": enable_host_script,
            "host_script": host_script,
            "external_settings": enable_external_host_settings,
            "external_configuration_file": external_conf_file,
        }
    else:
        host_config = {
            "transmitters_enabled": enable_host_script,
            "host_script": host_script,
            "external_settings": enable_external_host_settings,
            "tx_gain": tx_gain,
            "tx_frequency": tx_frequency,
            "channels": channels,
            "duration": duration,
        }
else:
    host_config = {
        "transmitters_enabled": enable_host_script,
    }

    
#   Create configuration dictionary scope
scope_config = {
    "ip": scope_ip,
    "center_Hz": center_hz,
    "span_Hz": span_hz,
    "rbw_Hz": rbw_hz,
    "cable_loss": cable_loss,
}

#   Location system config
positioning_system_config = {
    "ip": positioning_system_server_ip,
    "system": positioning_system,
}

#   Combine all settings and configurations in "info"
info = {}
info["info"] = description_config
info["ansible"] = ansible_config
info["host"] = host_config
info["scope"] = scope_config
info["positioning"] = positioning_system_config

csv_file_path = None

#   Subscribe to control script
context = zmq.Context()
sub_socket = context.socket(zmq.SUB)
sub_socket.connect(f"tcp://{ctrl_zmq_ip}:{ctrl_zmq_port}")
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

#   Subscribe to the localisation system
positioner = AcousticPositioner(positioning_system_server_ip, positioning_system_zmq_port)

#   Subscribe to the energy profiler gateway
energyprofiler = RFEP(ep_gateway_ip, ep_zmq_port)

#   Connect with scope
try:
    scope = Scope(scope_ip)
    # scope.setup(bandwidth_hz, center_hz, span_hz, rbw_hz)
except:
    print("Can not connect to the scope!")
    print("1) Check network connection")
    print("2) (optionally) Reboot system")
    positioner.stop()
    energyprofiler.stop()
    exit()

ctrl_thread = None

initialized = False

measurements = []
current_meas = []

#   Save tile states in global varibale
tile_states_global = None

current_pos = positioner.get_pos()
import threading

def clean_up(active_tile_list):
    if enable_host_script and ansible_enable_stop_script:
        print(f"Kill: {tile_states_global['ok']}")

        r = ansible_runner.run(
            inventory=f'/home/{user_name}/ansible/inventory/{ansible_inventory_yaml}',
            playbook=f'/home/{user_name}/ansible/{ansible_stop_script_yaml}',
            extravars={"tiles": active_tile_list}
        )

def func_ctrl_thread(ctrl_thread_stop_flag, stop_event, start_event, close_event):
    global tx_gain
    
    while not ctrl_thread_stop_flag.is_set():
        ctrl_msg = sub_socket.recv_string()
        print(ctrl_msg)
        
        if ctrl_msg == "stop":
            stop_event.set()
            start_event.clear()
        elif ctrl_msg == "start":
            start_event.set()
            stop_event.clear() # Can be removed
        elif ctrl_msg == 'close':
            close_event.set()
            break
        elif ctrl_msg.startswith("change gain "):
            try:
                # Extract the gain value from the message
                tx_gain = int(ctrl_msg[12:])
                print(f"Gain changed to {tx_gain}")
            except ValueError:
                # Handle the case where the message is not in the expected format
                print("Invalid gain value received:", ctrl_msg)

    print("Control thread successfully terminated.")

def append_to_csv(csv_file_path, data):

    # Check if the CSV file exists
    file_exists = os.path.isfile(csv_file_path)

    # Open the CSV file in append mode
    with open(csv_file_path, mode='a', newline='') as file:
        # Create a CSV writer object
        writer = csv.writer(file)

        # Write header if the file is newly created
        if not file_exists:
            writer.writerow(csv_header)  # Modify header as needed

        # Write the data to the CSV file
        writer.writerow(data)

def start_up(info_data):

    all_ansible_runner_results = []

    antenna_states = {'ok': [], 'dark': []}

    #   Check external usrp settings file available
    if enable_external_host_settings:

        # Read the CSV file into a DataFrame
        df = pd.read_csv(f"{script_patch}/{external_conf_file}") 
 
        for index, row in df.iterrows():
            # Get data
            df_channel = row['ch']
            df_tile = row['tile']
            df_gain_dB = row['gain_dB']

            # print(df_channel, df_tile, df_gain_dB)
            
            # Check gain not zero
            if int(df_gain_dB) > 0:
                r = ansible_runner.run(
                    inventory=f'/home/{user_name}/ansible/inventory/{ansible_inventory_yaml}',
                    playbook=f'/home/{user_name}/ansible/{ansible_start_script_yaml}',
                    extravars={"script": host_script, "tiles": df_tile, "gain": float(df_gain_dB), "freq": tx_frequency, 
                               "duration": duration, "channels": df_channel, "ip": server_ip_address}
                )
            
                all_ansible_runner_results.append(r)
                
                #   Append antenna states
                if not list(r.stats['ok'].keys())[0] == None:
                    antenna_states['ok'].append({'tile': str(list(r.stats['ok'].keys())[0]), 'ch': int(df_channel)})
                else:
                    antenna_states['dark'].append({'tile': str(list(r.stats['dark'].keys())[0]), 'ch': int(df_channel)})

    #   Internal settings (desrcibed in the header) are used
    else:
        # todo resolve in python to absolute path
        r = ansible_runner.run(
            inventory=f'/home/{user_name}/ansible/inventory/{ansible_inventory_yaml}',
            playbook=f'/home/{user_name}/ansible/{ansible_start_script_yaml}',
            extravars={"script": host_script, "tiles": tiles, "gain": tx_gain, "freq": tx_frequency, 
                       "duration": duration, "channels": channels, "ip": server_ip_address}
        )
        # working: >>> ansible-playbook -i inventory/hosts.yaml start_transmitters_random_phase.yaml -e "tiles='T04'" 
        # -e "freq=900E6" -e "gain=70" -e "channels='0 1'" -e "duration=10" -e "ip='192.108.0.204'" <<<

        all_ansible_runner_results = [r]

    #   Create tile_state dictionary
    tile_states = {key: None for key in all_ansible_runner_results[0].stats.keys()}

    #   Fill in empty lists for all keys
    for key in tile_states:
        if tile_states[key] is None:
            tile_states[key] = []

    #   Iterate over all ansible_runner results
    for r in all_ansible_runner_results:

        #   Append tile lists to tile_states
        for key in r.stats.keys():
            tile_ids = r.stats[key].keys()
            tile_states[key].append(list(tile_ids))
        
    #   Simplify 2D lists to 1D lists in "tile_states" dictionary
    for key in tile_states:
        original_list = tile_states[key]
        tile_states[key] = [item for sublist in original_list for item in sublist]

    #   Save in yml file
    info_data["tile_states"] = tile_states

    #   Save in yml file
    info_data["antenna_states"] = antenna_states
    
    num_unreachable = len(tile_states['dark']) #len(r.stats['dark'].keys())
    num_processed = len(tile_states['ok']) #len(r.stats['ok'].keys())

    print(num_unreachable)
    print(num_processed)

    return tile_states, num_processed, num_unreachable


def save_info(info_data):

    # Save information of measurement
    with open(f"{csv_file_path}/{csv_file_time}_{info_name_after_nr}.yml", "w", newline="") as yml_file:
        yml_file.write(yaml.dump(info_data))


if __name__ == '__main__':

    stop_event = threading.Event()
    start_event = threading.Event()
    close_event = threading.Event()

    #   Define a shared 'stop' flag to control the 'control' zmq thread
    ctrl_thread_stop_flag = threading.Event()

    #   Create and link function to this new thread
    ctrl_thread = threading.Thread(target=func_ctrl_thread, 
                                   args=(ctrl_thread_stop_flag,stop_event,start_event,close_event))

    #   Start thread
    ctrl_thread.start()

    print("Init done")

    # Variables
    pos = None
    data_start = None
    no_active_transmitters = None
    csv_file_time = None

    print("Waiting for ZMQ 'start' command")

    # Loop
    while not close_event.is_set():

        # print("test")
        
        # Check start event is set
        if start_event.is_set() and not initialized:

            # Update path
            csv_file_path = f"{script_patch}/meas_data"
            csv_file_time = round(time.time())

            # save n.o. active URPS in variable
            no_active_transmitters = 1 #1 # At least one

            if enable_host_script:
                # Start transmitters
                tile_states_global, no_active_transmitters, no_not_active = start_up(info)

            # Save configurations and tile info to yaml file
            save_info(info)

            # Start logging
            print("Start logging")

            # Define start time
            data_start = time.time()

            # Init done
            initialized = True
        
        if start_event.is_set() and initialized:
    
            #   Get position
            pos = positioner.get_pos()
            while pos is None:
                pos = positioner.get_pos()

            #   Get ep data
            ep_data = energyprofiler.get_data()

            #   Get rsv power via scope
            power_dBm, peaks = scope.get_power_dBm_peaks(cable_loss, no_active_transmitters) 

            #   Print power
            print(f"Power [dBm] {power_dBm:.2f} - NO Peaks {len(peaks)}")

            #   Save data
            try:
                data_to_append = [*pos.to_csv(), power_dBm, *ep_data.to_csv()]
                append_to_csv(f"{csv_file_path}/{csv_file_time}_{name_after_nr}.csv", data_to_append)
            except Exception as e:
                print(e)

        if stop_event.is_set():
            #   Reset init variable
            initialized = True
            
            #   Clear stop event
            stop_event.clear()

            #   Clean up all threads
            clean_up(tile_states_global['ok'])

            #   Measurement ended
            print("Measurement DONE")

    #   Set the stop flag to signal the thread to exit
    ctrl_thread_stop_flag.set()

    #   Wait for the thread to complete
    ctrl_thread.join()

    #   Check positioning and energy profiler thread are terminated
    positioner.stop()
    energyprofiler.stop()
    


