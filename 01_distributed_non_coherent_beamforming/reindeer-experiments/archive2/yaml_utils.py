import yaml


# Function to read YAML file
def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        try:
            # Load YAML file data into a Python dictionary
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as exc:
            print(f"Error reading YAML file: {exc}")
            return None