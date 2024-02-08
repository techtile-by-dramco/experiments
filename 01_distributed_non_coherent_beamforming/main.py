# /bin/python3 -m experiments.01_distributed_non_coherent_beamforming.main
# see for relative import: https://stackoverflow.com/a/68315950/3590700

from ..scope.scope import Scope
from ..location.Position import AcousticPositioner
import time 
import ansible_runner
import sys
import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect(f"tcp://localhost:5555")
socket.setsockopt_string(zmq.SUBSCRIBE, "")




scope = Scope("192.108.0.251")
positioner = AcousticPositioner("192.108.0.15")

measurements = []
current_meas = []

current_pos = positioner.get_pos()

def clean_up():
    r = ansible_runner.run(
        inventory='/home/gilles/ansible/inventory/hosts.yaml',
        playbook='/home/gilles/ansible/kill-transmitter.yaml',
        # host_pattern='G03'
    )
    positioner.stop()
    exit()


if __name__ == '__main__':
    # todo resolve in python to absolute path
    r = ansible_runner.run(
        inventory='/home/gilles/ansible/inventory/hosts.yaml',
        playbook='/home/gilles/ansible/start_waveform.yaml',
        # host_pattern='G03'
    )

    print(r.stats)
    
    num_unreachable = len(r.stats['dark'].keys())
    num_processed = len(r.stats['ok'].keys())

    print(num_unreachable)
    print(num_processed)

    # blocking wait till start

    while True:
        while socket.recv_string() != "START":
            if socket.recv_string() == "DONE":
                clean_up()

        # we have a go
        # get positions + power

        positions= []
        power = []

        while socket.recv_string(flags=zmq.NOBLOCK) != "DONE" or "STOP":
            positions.append(positioner.get_pos())
            power_dBm = scope.get_power_dBm() 
            power.append(power_dBm)







    
    