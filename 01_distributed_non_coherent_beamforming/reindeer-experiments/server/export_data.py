import yaml
import csv
import os

# Log info about the tiles (E.g. find info if one tile was broken during startup measurement)
def log_info(info_data, exp_dir, data_save_path, client_experiment_name):

    # Save information of measurement
    with open(f"{exp_dir}/{data_save_path}{client_experiment_name}_log.yaml", "w", newline="") as yml_file:
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

def save_config_file(exp_dir, data_save_path, client_experiment_name, config):
      with open(f"{exp_dir}/{data_save_path}{client_experiment_name}_config.yaml", "w") as yml_file:
        yaml.dump(config, yml_file, default_flow_style=False)