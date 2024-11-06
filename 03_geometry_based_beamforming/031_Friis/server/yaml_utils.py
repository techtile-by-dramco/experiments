import yaml

def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        try:
            # Load YAML file data into a Python dictionary
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as exc:
            print(f"Error reading YAML file: {exc}")
            return None
        
def write_yaml_file(file_path, data):
    with open(file_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)
        
# Function to read YAML file and check parameter existence
def check_yaml_parameter(yaml_data, parameter_name):
    # Check if the parameter exists in the YAML data
    if parameter_name in yaml_data:
        return True
    else:
        return False