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
scope = Scope(config=config["scope"])
positioner = PositionerClient(config=config["positioning"], backend="zmq")
plt = TechtilePlotter(realtime=True)

positioner.start()

positions = []
values = []

script_started = time()

try:
    while True or time() - script_started > 8*60*60:
        power_dBm = scope.get_power_dBm()
        pos = positioner.get_data()

        if pos is not None:
            print(power_dBm)
            positions.append(pos)
            print(pos)
            values.append(power_dBm)
            plt.measurements_rt(pos.x, pos.y, pos.z, power_dBm)
        sleep(0.2)
except KeyboardInterrupt:
    positioner.stop()
finally:
    print("Ctrl+C pressed. Exiting loop and saving...")
    meas_name = "bf-ceiling-grid-9"
    np.save(arr=positions, file=f"../data/positions-{meas_name}")
    np.save(arr=values, file=f"../data/values-{meas_name}")
