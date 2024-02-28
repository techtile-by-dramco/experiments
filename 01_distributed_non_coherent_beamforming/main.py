# /bin/python3 -m experiments.01_distributed_non_coherent_beamforming.main
# see for relative import: https://stackoverflow.com/a/68315950/3590700

user_name = "/jarne"
path_to_repo = "/Documents/GitHub"
scope_ip = "192.108.0.251"
DAQ_server_ip = "192.108.0.15"
cable_loss = 10
default_tx_gain = 100
tiles = "walls"

tx_gain = default_tx_gain

import sys
sys.path.append(f"/home{user_name}{path_to_repo}/experiments/location")
from Position import AcousticPositioner
sys.path.append(f"/home{user_name}{path_to_repo}/experiments/scope")
from scope import Scope
import time 
import ansible_runner
import zmq
import csv

csv_file_path = None

context = zmq.Context()
sub_socket = context.socket(zmq.SUB)
sub_socket.connect(f"tcp://localhost:5555")
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

# pub_socket = context.socket(zmq.PUB)
# pub_socket.bind("tcp://0.0.0.0:5555")

scope = Scope(scope_ip)
positioner = AcousticPositioner(DAQ_server_ip, ttl=2.0)

ctrl_thread = None

measurements = []
current_meas = []

current_pos = positioner.get_pos()
import threading

def clean_up():
    r = ansible_runner.run(
        inventory='/home/' + user_name + '/ansible/inventory/hosts.yaml',
        # To change hosts !!! change in kill-transmitter.yaml file !!! current --> measnc
        playbook='/home/' + user_name + '/ansible/kill-transmitter.yaml',
        extravars={"tiles": tiles}
    )
    #positioner.stop()
    #ctrl_thread.stop()
    # exit()

def ctrl_thread(stop_event, start_event):
    global tx_gain
    while True:
        ctrl_msg = sub_socket.recv_string()
        if  ctrl_msg == "STOP":
            stop_event.set()
            start_event.clear()
        elif ctrl_msg == "START":
            start_event.set()
            stop_event.clear()
        elif ctrl_msg.startswith("change gain "):
            try:
                # Extract the gain value from the message
                tx_gain = int(ctrl_msg[12:])
                print(f"Gain changed to {tx_gain}")
            except ValueError:
                # Handle the case where the message is not in the expected format
                print("Invalid gain value received:", ctrl_msg)

def append_to_csv(csv_file_path, data):
    # Open the CSV file in append mode
    with open(csv_file_path, mode='a', newline='') as file:
        # Create a CSV writer object
        writer = csv.writer(file)

        # Write the data to the CSV file
        writer.writerow(data)

def start_up():
    # todo resolve in python to absolute path
    r = ansible_runner.run(
        inventory=f'/home/{user_name}/ansible/inventory/hosts.yaml',
        # To change hosts !!! change in waveform.yaml file !!! current --> measnc
        playbook=f'/home/{user_name}/ansible/start_waveform.yaml',
        extravars={"tiles": tiles, "gain": tx_gain}
    )

    print(r.stats)

    # Save information of measurement
    with open(f"{csv_file_path}/{csv_file_time}_info.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=r.stats.keys())
        writer.writeheader()
        writer.writerow(r.stats)
    
    num_unreachable = len(r.stats['dark'].keys())
    num_processed = len(r.stats['ok'].keys())

    print(num_unreachable)
    print(num_processed)



if __name__ == '__main__':

    stop_event = threading.Event()
    start_event = threading.Event()

    ctrl_thread = threading.Thread(target=ctrl_thread, args=(stop_event,start_event))
    ctrl_thread.start()

    # Loop
    while True:
        print("Waiting for ZMQ 'START' command")
        
        # Blocking wait till start
        while not start_event.is_set():
            pass

        # Update path
        csv_file_path = f"/home{user_name}{path_to_repo}/experiments/01_distributed_non_coherent_beamforming/meas_data"
        csv_file_time = round(time.time())

        # Start transmitters
        start_up()

        print("Start logging")

        # Init vars
        pos = None
        data_start = time.time()
    
        while not stop_event.is_set():
            #   Get position
            pos = positioner.get_pos()
            while pos is None:
                pos = positioner.get_pos()

            #   Get rsv power via scope
            # power_dBm = scope.get_power_dBm(cable_loss) 
            power_dBm, peaks = scope.get_power_dBm_peaks(cable_loss) 

            #   Print power
            print(f"Power [dBm] {power_dBm:.2f} - NO Peaks {len(peaks)}")

            #   Save data
            data_to_append = [*pos.to_csv(), power_dBm, tx_gain, cable_loss]
            append_to_csv(f"{csv_file_path}/{csv_file_time}_nc_data.csv", data_to_append)

        clean_up()
        print("DONE")



