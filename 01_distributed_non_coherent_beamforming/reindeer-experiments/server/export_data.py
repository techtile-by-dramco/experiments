import ansible_runner
import yaml
import csv
import os

def start_up(log_data, user_name, ansible_config_yaml, client_config_yaml, client_experiment_name):

    all_ansible_runner_results = []

    antenna_states = {'ok': [], 'dark': []}

    r = ansible_runner.run(
        inventory=f"/home/{user_name}/ansible/inventory/{ansible_config_yaml.get('inventory')}",
        playbook=f"/home/{user_name}/ansible/{ansible_config_yaml.get('start_client_script')}",
        extravars={"script": client_config_yaml.get('start_client_script'), 
                   "tiles": client_config_yaml.get('tiles'),
                   "experiment_name": f"{client_experiment_name}",
                   }
    )

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
    log_data["tile_states"] = tile_states

    #   Save in yml file
    log_data["antenna_states"] = antenna_states
    
    num_unreachable = len(tile_states['dark']) #len(r.stats['dark'].keys())
    num_processed = len(tile_states['ok']) #len(r.stats['ok'].keys())

    print(num_unreachable)
    print(num_processed)

    return tile_states, num_processed, num_unreachable


def clean_up(user_name, tiles_to_kill, ansible_config_yaml):
    # print(f"Kill: {tiles_to_kill}")

    r = ansible_runner.run(
        inventory=f'/home/{user_name}/ansible/inventory/{ansible_config_yaml.get("inventory")}',
        playbook=f'/home/{user_name}/ansible/{ansible_config_yaml.get("stop_client_script")}',
        extravars={"tiles": tiles_to_kill}
    )

# Log info about the tiles (E.g. find info if one tile was broken during startup measurement)
def log_info(info_data, exp_dir, client_experiment_name):

    # Save information of measurement
    with open(f"{exp_dir}/{client_experiment_name}.yml", "w", newline="") as yml_file:
        yml_file.write(yaml.dump(info_data))


def append_to_csv(csv_file_path, data, csv_header):

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