# /bin/python3 -m experiments.01_distributed_non_coherent_beamforming.main
# see for relative import: https://stackoverflow.com/a/68315950/3590700

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
positioner = PositionerClient(config=config["positioning"])

positioner.start()


current = time()
count = 0

positions = []
values = []

try:
    while True:
        power_dBm = scope.get_power_dBm()

        pos = positioner.get_data()
        if pos is not None:
            print(power_dBm)
            positions.append(pos)
            values.append(power_dBm)
            count +=1
        sleep(0.2)
except KeyboardInterrupt:
    print("Ctrl+C pressed. Exiting loop and saving...")

    positioner.stop()
    np.save(arr=positions, file="positions-bf")

    np.save(arr=values, file="values-bf")
