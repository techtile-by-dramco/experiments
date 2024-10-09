# ****************************************************************************************** #
#                                       IMPORTS / PATHS                                      #
# ****************************************************************************************** #

# *** Includes ***
from TechtileScope import Scope
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

try:
    while True:
        pos = positioner.get_data()
        if pos is not None:
            plt.measurements_rt(pos.x, pos.y, pos.z, 0)
        sleep(0.4)
except KeyboardInterrupt:
    positioner.stop()

    print("Ctrl+C pressed.")
