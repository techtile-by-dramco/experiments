from ep import RFEP

# ****************************************************************************************** #
#                                       IMPORTS / PATHS                                      #
# ****************************************************************************************** #

# *** Includes ***
from Positioner import PositionerClient
from TechtilePlotter.TechtilePlotter import TechtilePlotter

import os
from yaml_utils import read_yaml_file
from time import sleep, time
import numpy as np
import zmq

# Get the current directory of the script
SAVE_EVERY = 1.0 * 60
server_dir = os.path.dirname(os.path.abspath(__file__))

config = read_yaml_file("config.yml")
positioner = PositionerClient(config=config["positioning"], backend="zmq")
rfep = RFEP("192.108.0.13", "5556")

positioner.start()


script_started = time()

context = zmq.Context()

iq_socket = context.socket(zmq.PUB)

iq_socket.bind(f"tcp://*:{50001}")


def wait_till_go_from_server(ip="10.128.48.13"):

    global meas_id, file_open, data_file, file_name
    # Connect to the publisher's address
    print("Connecting to server %s.", ip)
    sync_socket = context.socket(zmq.SUB)
    sync_socket.connect(f"tcp://{ip}:{5557}")
    # Subscribe to topics
    sync_socket.subscribe("")

    # Receives a string format message
    print("Waiting on SYNC from server %s.", ip)

    meas_id, unique_id = sync_socket.recv_string().split(" ")

    print(meas_id)

    sync_socket.close()

    return meas_id, unique_id


plt = TechtilePlotter(realtime=True)
meas_id, unique_id = wait_till_go_from_server()
sleep(29.0)  # wake-up 10 seconds before rover starts to move

# start to measure for XX long
start = time()

positions = []
values = []

last_save = -1

while True:

    d = rfep.get_data()

    pos = positioner.get_data()

    if d is not None:
        print(d)
        positions.append(pos)
        print(pos)
        values.append(d) 
        plt.measurements_rt(pos.x, pos.y, pos.z, d.pwr_nw / 10**6)  # in uW
    sleep(0.1)

    if last_save + SAVE_EVERY < time():
        np.save(arr=positions, file=f"../data/positions-{unique_id}")
        np.save(arr=values, file=f"../data/values-{unique_id}")
        last_save = time()
print("Ctrl+C pressed. Exiting loop and saving...")
# meas_name = f"bf-ceiling-grid-20241105-70db-tx"
np.save(arr=positions, file=f"../data/positions-{unique_id}")
np.save(arr=values, file=f"../data/values-{unique_id}")
positioner.stop()
rfep.stop()