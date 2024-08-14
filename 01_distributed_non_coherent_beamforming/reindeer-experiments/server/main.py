# /bin/python3 -m experiments.01_distributed_non_coherent_beamforming.main
# see for relative import: https://stackoverflow.com/a/68315950/3590700

# *** Includes ***
import sys
import os

# Get the current directory of the script
server_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate one folder back to reach the parent directory
exp_dir = os.path.abspath(os.path.join(server_dir, os.pardir))

# *** Includes continuation ***
sys.path.append(f"{exp_dir}/server/position")
from position import AcousticPositioner
sys.path.append(f"{exp_dir}/server/scope")
from scope import Scope
sys.path.append(f"{exp_dir}/server/rfep")
from rfep import RFEP
import time
import zmq
import threading

# *** Local includes ***
from yaml_utils import *
from export_data import *

#   Read YAML file
config = read_yaml_file(f"{exp_dir}/config.yaml")

#   INFO
info = config.get('info', {})
exp_name = info.get('exp_name')
server_user_name = info.get('server_user_name')
data_save_path = info.get('data_save_path')

#   CONTROL
control_yaml = config.get('control', {})

#   ANSIBLE SETTINGS
ansible_yaml = config.get('ansible', {})

#   LOCATION SYSTEM SETTINGS --> ToDo Check if it is definied in config file
positioning_yaml = config.get('positioning', {})

#   ENERGY PROFILER SYSTEM SETTINGS --> ToDo Check if it is definied in config file
scope_yaml = config.get('scope', {})

#   ENERGY PROFILER SYSTEM SETTINGS --> ToDo Check if it is definied in config file
ep_yaml = config.get('ep', {})

#   CLIENT
client = config.get('client', {})

#   Log ansible results
ansible_results = {}

if client.get("enable_client_script"):
    from connect_to_clients import *

def send_zmq_cmd(socket, cmd):
    print(cmd.encode())
    socket.send_multipart([b"phase", cmd.encode()])

def func_ctrl_thread(ctrl_thread_stop_flag, init_event, start_event, stop_event, close_event):
    global tx_gain

    # Create a poller object
    poller = zmq.Poller()
    poller.register(sub_socket, zmq.POLLIN)

    while not ctrl_thread_stop_flag.is_set():

        # Wait for events on the socket(s) for up to 1000 milliseconds (1 second)
        events = dict(poller.poll(1000))  # Timeout set to 1000 milliseconds

        if sub_socket in events:
            # Receive message
            ctrl_msg = sub_socket.recv_string()
            print(f"Received message: {ctrl_msg}")
        
            if ctrl_msg == "init":
                init_event.set()
                stop_event.clear() # Can be removed
            elif ctrl_msg == "start":
                start_event.set()
                print("Start logging")
                stop_event.clear() # Can be removed
            elif ctrl_msg == "stop":
                init_event.clear()
                start_event.clear()
                stop_event.set()
            elif ctrl_msg == 'close':
                close_event.set()
                break

    print("Control thread successfully terminated.")

if __name__ == '__main__':

    #   Subscribe to control script
    context = zmq.Context()
    sub_socket = context.socket(zmq.SUB)
    sub_socket.connect(f"tcp://{info.get('ip')}:{info.get('port')}")
    print(f"Connecting to {info.get('ip')}:{info.get('port')}")
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    #   Subscribe to the localisation system
    positioner = AcousticPositioner(positioning_yaml.get('ip'), positioning_yaml.get('port'))

    #   Subscribe to the energy profiler gateway
    energyprofiler = RFEP(ep_yaml.get('ip'), ep_yaml.get('port'))

    #   Connect with scope
    if scope_yaml.get('enabled'):
        try:
            scope = Scope(scope_yaml.get("ip"))
            scope.setup(scope_yaml.get("bandwidth_hz"), scope_yaml.get("center_hz"), scope_yaml.get("span_hz"), scope_yaml.get("rbw_hz"))
        except:
            print("Can not connect to the scope or something went wrong!")
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

    #   Define experiment name
    meas_init_time = round(time.time())
    client_experiment_name = f"{exp_name}_{meas_init_time}"

    #   Check if data folder excists
    try:
        # Create the directory
        path = f"{exp_dir}/{data_save_path}"
        os.makedirs(path, exist_ok=True)
        print(f"Directory '{path}' created successfully")
    except OSError as error:
        print(f"Error: {error}")

    #   Save config file
    save_config_file(exp_dir, data_save_path, client_experiment_name, config)
    
    print("(1) Copy python script from server to client to folder 'home/ip/exp/{client_experiment_name}'")

    #   Check or copy files to the clients
    if client.get("enable_client_script"):
        copy_files(ansible_results, server_user_name, exp_dir, ansible_yaml, client, client_experiment_name)
        log_info(ansible_results, exp_dir, data_save_path, client_experiment_name)

    print("(2) Start control thread")

    init_event = threading.Event()
    start_event = threading.Event()
    stop_event = threading.Event()
    close_event = threading.Event()

    #   Automatic?
    if control_yaml.get('transmission') == 'auto':
        print('Automatic enabled')
        init_event.set()
        start_event.set()

        #   Open socket for direct instructions to USRPs
        context = zmq.Context()
        pub_socket = context.socket(zmq.PUB)
        pub_socket.bind("tcp://*:5558")

    #   Define a shared 'stop' flag to control the 'control' zmq thread
    ctrl_thread_stop_flag = threading.Event()

    #   Create and link function to this new thread
    ctrl_thread = threading.Thread(target=func_ctrl_thread, 
                                   args=(ctrl_thread_stop_flag,init_event,start_event,stop_event,close_event))

    #   Start thread (To read out external values)
    ctrl_thread.start()

    # Variables
    pos = None
    data_start = None
    no_active_transmitters = None
    csv_file_time = None

    print("(3) Waiting for ZMQ 'init' command")

    # Loop
    while not close_event.is_set():
        
        # Check start event is set
        if init_event.is_set() and not initialized:

            # save n.o. active URPS in variable
            no_active_transmitters = 1

            if client.get("enable_client_script"):
                # Start transmitters
                tile_states_global, no_active_transmitters, no_not_active = start_up(ansible_results, server_user_name, ansible_yaml, client, client_experiment_name)

            # Save configurations and tile info to yaml file
            log_info(ansible_results, exp_dir, data_save_path, client_experiment_name)

            # Define start time
            data_start = time.time()

            # Init done
            initialized = True

            print("(4) Waiting for ZMQ 'start' command")

            # Init start time for automatic control
            start_time = time.time()

            # Start all client scripts automatically
            if control_yaml.get('transmission') == 'auto':
                for i in range(5):
                    time.sleep(1)
                    print(f"Starting transmitters in {5-i}")
                send_zmq_cmd(pub_socket, "start")
                time.sleep(1)
                send_zmq_cmd(pub_socket, "start")
                time.sleep(1)
        
        if init_event.is_set() and initialized:

            if start_event.is_set():
    
                #   Get position
                pos = positioner.get_pos()
                while pos is None:
                    pos = positioner.get_pos()

                #   Check is ep is enabled
                if ep_yaml.get("enabled"):
                    #   Get ep data
                    ep_data = energyprofiler.get_data()
                    
                    while ep_data is None:
                        ep_data = energyprofiler.get_data()

                    ep_data_csv = ep_data.to_csv()
                    print(f"EP: Voltage [mV] {ep_data_csv[0]} - DC Power [uW] {ep_data_csv[2]/1e3}")
                else:
                    ep_data = [0, 0, 0]

                #   Check is scope is enabled
                if scope_yaml.get("enabled"):
                    #   Get rsv power via scope
                    power_dBm, peaks = scope.get_power_dBm_peaks(scope_yaml.get("cable_loss"), no_active_transmitters)

                    #   Print power
                    print(f"Power [dBm] {power_dBm:.2f} - NO Peaks {len(peaks)}")
                else:
                    power_dBm = -100
                    peaks = [1]

                #   Save data
                try:
                    data_to_append = [time.time(), *pos.to_csv(), power_dBm, *ep_data.to_csv()]
                    header = ["timestamp"] + positioning_yaml.get("csv_header") + scope_yaml.get("csv_header") + ep_yaml.get("csv_header")
                    append_to_csv(f"{exp_dir}/{data_save_path}{client_experiment_name}.csv", data_to_append, header)
                except Exception as e:
                    print(e)

                #   Automatic?
                if control_yaml.get('transmission') == 'auto':
                    if time.time() - start_time > control_yaml.get('duration'):
                        stop_event.set()
                else:
                    print(f"Time remaining: {round(time.time() - start_time - control_yaml.get('duration'))} seconds")
            else:
                #   Update start time
                start_time = time.time()

        if stop_event.is_set():
            #   Reset init variable
            initialized = True

            # Start all client scripts automatically
            if control_yaml.get('transmission') == 'auto':
                send_zmq_cmd(pub_socket, "stop")
            
            #   Clear stop event
            stop_event.clear()

            #   Clean up all threads
            if ansible_yaml.get("enable_client_script") and check_yaml_parameter(ansible_yaml, "stop_client_script"):
                clean_up(server_user_name, tile_states_global['ok'])

            #   Measurement ended
            print("Measurement DONE")

            #   ToDo Current script not ready to start new measurement without closing
            break

    #   Set the stop flag to signal the thread to exit
    ctrl_thread_stop_flag.set()

    #   Wait for the thread to complete
    ctrl_thread.join()

    #   Check positioning and energy profiler thread are terminated
    positioner.stop()
    energyprofiler.stop()

exit()