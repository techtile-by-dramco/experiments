from ansible_handler import *
from export_data import *
import zmq
import time

#   Copy config and script file to the client /home/pi/exp/<<MEAS_NAME>>_<<TIMESTAMP>> directorty
def copy_files(log_data, user_name, exp_dir, ansible_config_yaml, client_config_yaml, client_experiment_name):
    r = ansible_copy_files(user_name, exp_dir, ansible_config_yaml, client_config_yaml, client_experiment_name)

    #   Format results for logging
    create_log_dict("copy_files", log_data, r)


    return analyse("copy_files", log_data, r)


#   Start up client scripts
def start_up(log_data, user_name, ansible_config_yaml, client_config_yaml, client_experiment_name):

    #   Add ansible output to list
    #   For future extention (e.g. running multiple client scripts on different tiles)
    # r = []

    # antenna_states = {'ok': [], 'dark': []}

    #   Start up all USRP/client scripts
    # all_ansible_runner_results = []
    r = ansible_start_client_script(user_name, ansible_config_yaml, client_config_yaml, client_experiment_name)

    create_log_dict("start_client_script", log_data, r)

    return analyse("start_client_script", log_data, r)

    # #   Create tile_state dictionary
    # tile_states = {key: None for key in all_ansible_runner_results[0].stats.keys()}

    # #   Fill in empty lists for all keys
    # for key in tile_states:
    #     if tile_states[key] is None:
    #         tile_states[key] = []

    # #   Iterate over all ansible_runner results
    # for r in all_ansible_runner_results:

    #     #   Append tile lists to tile_states
    #     for key in r.stats.keys():
    #         tile_ids = r.stats[key].keys()
    #         tile_states[key].append(list(tile_ids))
        
    # #   Simplify 2D lists to 1D lists in "tile_states" dictionary
    # for key in tile_states:
    #     original_list = tile_states[key]
    #     tile_states[key] = [item for sublist in original_list for item in sublist]

    # #   Save in yaml file
    # log_data["tile_states"] = tile_states

    # #   Save in yaml file
    # log_data["antenna_states"] = antenna_states
    
    # num_unreachable = len(tile_states['dark']) #len(r.stats['dark'].keys())
    # num_processed = len(tile_states['ok']) #len(r.stats['ok'].keys())

    # print(num_unreachable)
    # print(num_processed)

    # return analyse(r, log_data)


def clean_up(user_name, tiles_to_kill, ansible_config_yaml, client_config_yaml):

    ansible_stop_client_script(user_name, tiles_to_kill, ansible_config_yaml, client_config_yaml)

#   Creat log dictonairy from ansible results
def create_log_dict(playbook_name, log_data_dict, ansible_result):
    task_name_keys = []

    #   Search for tasknames
    for result in ansible_result.events:
        if result['event'] == 'runner_on_ok':
            task_name = result['event_data']['task']

            if task_name not in task_name_keys:
                task_name_keys.append(task_name)

    #   Create dictionary with default values (e.g., None)
    task_results_dict = {key: [] for key in task_name_keys}
    
    for result in ansible_result.events:
        if result['event'] == 'runner_on_ok':
            task_results_dict[result['event_data']['task']].append(result['event_data']['remote_addr'])

    log_data_dict[f"playbook_{playbook_name}"] = task_results_dict


def analyse(playbook_name, log_data_dict, ansible_result):

    tile_state_dict = {}

    #   Create tile_state dictionary
    tile_states = {key: None for key in ansible_result.stats.keys()}

    #   Fill in empty lists for all keys
    for key in tile_states:
        if tile_states[key] is None:
            tile_states[key] = []

    #   Append tile lists to tile_states
    for key in ansible_result.stats.keys():
        tile_ids = ansible_result.stats[key].keys()
        tile_states[key].append(list(tile_ids))
        
    #   Simplify 2D lists to 1D lists in "tile_states" dictionary
    for key in tile_states:
        original_list = tile_states[key]
        tile_states[key] = [item for sublist in original_list for item in sublist]

    #   Save in yaml file
    tile_state_dict["tile_states"] = tile_states
    
    num_unreachable = len(tile_states['dark']) #len(r.stats['dark'].keys())
    num_processed = len(tile_states['ok']) #len(r.stats['ok'].keys())

    log_data_dict[f"playbook_{playbook_name}"].update(tile_state_dict)

    return tile_states, num_processed, num_unreachable

def send_zmq_cmd(socket, cmd):
    print(cmd.encode())
    socket.send_multipart([b"phase", cmd.encode()])
