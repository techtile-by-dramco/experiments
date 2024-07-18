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


for i in range(11):

    #   Read YAML file
    config = read_yaml_file(f"{exp_dir}/config.yaml")

    config['info']['description'] = "Measurement one tone signals"
    config['info']['exp_name'] = f"phase_{75+i}"
    config['info']['data_save_path'] = "data/one_tone_phase_duration_10_m5/"
    config['client']['hosts']['all']['gain'] = 75 + i
    config['client']['hosts']['all']['duration'] = 10
    config['control']['duration'] = 60*120

    # Write the updated YAML content back to the file
    with open(f"{exp_dir}/config.yaml", 'w') as file:
        yaml.safe_dump(config, file)

    # Path to the second script
    script_path = f"{exp_dir}/server/main.py"

    # Run the second script
    result = subprocess.run(['python3', script_path], capture_output=True, text=True)

    # # Print the output of the second script
    # print(result.stdout)
    print(f"Measurement {i}: DONE")

    # # Check if the script executed successfully
    # if result.returncode == 0:
    #     print("Script executed successfully")
    # else:
    #     print(f"Script execution failed with return code {result.returncode}")

for i in range(11):

    #   Read YAML file
    config = read_yaml_file(f"{exp_dir}/config.yaml")

    config['info']['description'] = "Measurement one tone signals"
    config['info']['exp_name'] = f"phase_{75+i}"
    config['info']['data_save_path'] = "data/one_tone_phase_duration_20_m1/"
    config['client']['hosts']['all']['gain'] = 75 + i
    config['client']['hosts']['all']['duration'] = 20
    config['control']['duration'] = 60*120

    # Write the updated YAML content back to the file
    with open(f"{exp_dir}/config.yaml", 'w') as file:
        yaml.safe_dump(config, file)

    # Path to the second script
    script_path = f"{exp_dir}/server/main.py"

    # Run the second script
    result = subprocess.run(['python3', script_path], capture_output=True, text=True)

    # # Print the output of the second script
    # print(result.stdout)
    print(f"Measurement {i}: DONE")

    # # Check if the script executed successfully
    # if result.returncode == 0:
    #     print("Script executed successfully")
    # else:
    #     print(f"Script execution failed with return code {result.returncode}")

for i in range(11):

    #   Read YAML file
    config = read_yaml_file(f"{exp_dir}/config.yaml")

    config['info']['description'] = "Measurement one tone signals"
    config['info']['exp_name'] = f"phase_{75+i}"
    config['info']['data_save_path'] = "data/one_tone_phase_duration_5_m1/"
    config['client']['hosts']['all']['gain'] = 75 + i
    config['client']['hosts']['all']['duration'] = 5
    config['control']['duration'] = 60*120

    # Write the updated YAML content back to the file
    with open(f"{exp_dir}/config.yaml", 'w') as file:
        yaml.safe_dump(config, file)

    # Path to the second script
    script_path = f"{exp_dir}/server/main.py"

    # Run the second script
    result = subprocess.run(['python3', script_path], capture_output=True, text=True)

    # # Print the output of the second script
    # print(result.stdout)
    print(f"Measurement {i}: DONE")

    # # Check if the script executed successfully
    # if result.returncode == 0:
    #     print("Script executed successfully")
    # else:
    #     print(f"Script execution failed with return code {result.returncode}")