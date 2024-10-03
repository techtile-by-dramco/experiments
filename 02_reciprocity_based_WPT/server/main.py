# ****************************************************************************************** #
#                                       IMPORTS / PATHS                                      #
# ****************************************************************************************** #

# *** Includes ***
from TechtileScope import Scope
from Positioner import PositionerClient

import os 
from yaml_utils import read_yaml_file
from time import sleep, time
import numpy as np

# Get the current directory of the script
server_dir = os.path.dirname(os.path.abspath(__file__))

config = read_yaml_file("config.yml")
scope = Scope(config=config["scope"])
positioner = PositionerClient(config=config["positioning"], backend="zmq")

positioner.start()

positions = []
values = []

try:
    while True:

        pos = positioner.get_data()
        power_dBm = scope.get_power_dBm()

        if pos is not None:
            print(power_dBm)
            positions.append(pos)
            print(pos)
            values.append(power_dBm)
        sleep(0.2)
except KeyboardInterrupt:
    print("Ctrl+C pressed. Exiting loop and saving...")

    positioner.stop()
    np.save(arr=positions, file="positions-nobf-G19-dwars")

    np.save(arr=values, file="values-nobf-G19-dwars")
