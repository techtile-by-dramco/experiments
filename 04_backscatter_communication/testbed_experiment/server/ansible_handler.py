import ansible_runner

def ansible_copy_files(user_name, exp_dir, ansible_config_yaml, client_config_yaml, client_experiment_name):    
    r = ansible_runner.run(
        inventory=f"/home/{user_name}/Documents/GitHub/ansible/inventory/{ansible_config_yaml.get('inventory')}",
        playbook=f"/home/{user_name}/Documents/GitHub/ansible/experiments/{ansible_config_yaml.get('copy_client_script')}",
        extravars={"tiles": f"{client_config_yaml.get('tiles')}", 
                   "script_file_path": f"{exp_dir}/client/{client_config_yaml.get('script')}", 
                   "config_file_path": f"{exp_dir}/config.yaml", 
                   "experiment_name": f"{client_experiment_name}"
                   }
    )
    return r

def ansible_start_client_script(user_name, ansible_config_yaml, client_config_yaml, client_experiment_name):
    r = ansible_runner.run(
    inventory=f"/home/{user_name}/Documents/GitHub/ansible/inventory/{ansible_config_yaml.get('inventory')}",
    playbook=f"/home/{user_name}/Documents/GitHub/ansible/experiments/{ansible_config_yaml.get('start_client_script')}",
    extravars={"script": client_config_yaml.get('script'), 
                "tiles": client_config_yaml.get('tiles'), 
                "zmq_ip": client_config_yaml.get('ip'),
                "experiment_name": f"{client_experiment_name}",
                }
    )
    return r

def ansible_stop_client_script(user_name, tiles_to_kill, ansible_config_yaml, client_config_yaml):
    r = ansible_runner.run(
        inventory=f'/home/{user_name}/Documents/GitHub/ansible/inventory/{ansible_config_yaml.get("inventory")}',
        playbook=f'/home/{user_name}/Documents/GitHub/ansible/experiments/{ansible_config_yaml.get("stop_client_script")}',
        extravars={"tiles": tiles_to_kill, 
                   "script_name": f"{client_config_yaml.get('script')}"}
    )
    return r