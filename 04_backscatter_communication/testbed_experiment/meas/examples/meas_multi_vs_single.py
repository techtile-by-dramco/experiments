import subprocess
import os
import sys
import yaml

# Get the current directory of the script
server_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate one folder back to reach the parent directory
exp_dir = os.path.abspath(os.path.join(server_dir, os.pardir))

sys.path.append(f"{exp_dir}/server")
from yaml_utils import *

number_of_measurements_per_config = 11

# # Change frequencies settings in config.yaml to multi tone
# script_path = f"{exp_dir}/meas/config_signal_args.py"
# subprocess.run(['python3', script_path, '--frequency', '920E6', '--offset', '1E2', '--multitone'], capture_output=False, text=True)

# for i in range(number_of_measurements_per_config):

#     #   Read YAML file
#     config = read_yaml_file(f"{exp_dir}/config.yaml")

#     config['info']['description'] = "Measurement multi tone signals"
#     config['info']['exp_name'] = f"phase_{75+i}" 
#     config['info']['data_save_path'] = "data/multi_tone_m1/"
#     config['client']['hosts']['all']['gain'] = 75 + i 
#     config['client']['hosts']['all']['duration'] = 3600 # high enough that phases not change
#     config['control']['duration'] = 60*30

#     # Write the updated YAML content back to the file
#     with open(f"{exp_dir}/config.yaml", 'w') as file:
#         yaml.safe_dump(config, file)

#     # Path to the second script
#     script_path = f"{exp_dir}/server/main.py"

#     # Run the second script
#     result = subprocess.run(['python3', script_path], capture_output=False, text=True)

#     print(f"Measurement {i}: DONE")


# Change frequencies settings in config.yaml to single tone
script_path = f"{exp_dir}/meas/config_signal_args.py"
subprocess.run(['python3', script_path, '--frequency', '920E6', '--singletone'], capture_output=False, text=True)

for i in range(1, number_of_measurements_per_config): # <<<<<<<<<<<<<<<<<------------ *** 1 *** WEG DOEN

    #   Read YAML file
    config = read_yaml_file(f"{exp_dir}/config.yaml")

    config['info']['description'] = "Measurement one tone signals"
    config['info']['exp_name'] = f"phase_{75+i}" 
    config['info']['data_save_path'] = "data/one_tone_phase_duration_5_m1/"
    config['client']['hosts']['all']['gain'] = 75 + i 
    config['client']['hosts']['all']['duration'] = 5
    config['control']['duration'] = 60*30

    # Write the updated YAML content back to the file
    with open(f"{exp_dir}/config.yaml", 'w') as file:
        yaml.safe_dump(config, file)

    # Path to the second script
    script_path = f"{exp_dir}/server/main.py"

    # Run the second script
    result = subprocess.run(['python3', script_path], capture_output=False, text=True)

    print(f"Measurement {i}: DONE")


print('All measurements *** DONE ***')