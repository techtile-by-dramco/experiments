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

# Get the current directory of the script
server_dir = os.path.dirname(os.path.abspath(__file__))

config = read_yaml_file("config.yml")
positioner = PositionerClient(config=config["positioning"], backend="zmq")
plt = TechtilePlotter(realtime=True)

positioner.start()

prev_pos = None

try:
    while True:
        sleep(0.4)
        pos = positioner.get_data()
        # check if pos is changed is to save the number of saved positions
        if pos is None:
            continue 
        if prev_pos is not None and prev_pos.is_closer_than(pos, 0.1):
                continue
        plt.measurements_rt(pos.x, pos.y, pos.z, 0)
        prev_pos = pos
except KeyboardInterrupt:
    positioner.stop()

    print("Ctrl+C pressed.")
