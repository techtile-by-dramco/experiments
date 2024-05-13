

import sys
import os
script_patch = os.getcwd()
sys.path.append(f"{script_patch}/location")
from position import AcousticPositioner
sys.path.append(f"{script_patch}/scope")
from scope import Scope
sys.path.append(f"{script_patch}/rfep")
from rfep import RFEP
import time 
import ansible_runner
import zmq
import csv
import yaml
import pandas as pd

#   EP SETTINGS
target_voltage = 1600   #   Not adjustable at the moment
ep_gateway_ip = '192.108.0.13'
ep_zmq_port = '5556'


positioning_system_server_ip = "192.108.0.13" # IP address of Qualisys server
positioning_system_zmq_port = '5555'


#   Subscribe to the energy profiler gateway
energyprofiler = RFEP(ep_gateway_ip, ep_zmq_port)

positioner = AcousticPositioner(positioning_system_server_ip, positioning_system_zmq_port)

counter = 0

while 1:
    new_data = energyprofiler.get_data()
    print(new_data)
    pos = positioner.get_pos()
    print(pos)
    time.sleep(1)
    counter+=1
    print(counter)
    if counter > 3:
        break

energyprofiler.stop()
positioner.stop()
print("Script ended")


# import zmq
# import json
# import time



# # Create a ZeroMQ context
# context = zmq.Context()

# # Create a ZeroMQ PUSH socket
# socket = context.socket(zmq.PUB)
# socket.bind("tcp://0.0.0.0:5555")  # Bind to local address and port

# status_now = 'capture_bs_start'

# while 1:

#     file_timestamp = round(time.time())

#     if status_now == 'capture_bs_start':
#         status_now = 'capture_bs_stop'
#     else:
#         status_now = 'capture_bs_start'

#     data = dict(name=file_timestamp,
#                 status=status_now,
#                 )

#     print(data)

#     # Send JSON data over the socket
#     socket.send_string(json.dumps(data))

#     time.sleep(1)


# # Close the socket and ZeroMQ context
# socket.close()
# context.term()