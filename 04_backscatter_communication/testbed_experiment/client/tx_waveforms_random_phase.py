"""
0. start server "random_phases_ZMQ"
1. wait till random phase (step 2) or STOP (step 4) command of server
2. change phase randomnly and transmit for 'duration' seconds at next PPS
3. go to step 1.
4. stop

--ip "IP OF ZMQ SERVER"

Server port: 5558 topic: phase commands: start or stop


optionally you can specify --noip and it will not wait for sever commands

python3 tx_waveforms_random_phase_v2.py -f 917E6 -c 0 1 --gain 40 -d 10 --noip --rate 250E3

"""

import time
import argparse
import numpy as np
import uhd
from datetime import datetime, timedelta
#from uhd.usrp import dram_utils
import yaml

def update(args, new_args:dict):
    for k, v in new_args.items():
        setattr(args, k, v)


def parse_args():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--args", default="", type=str)
    parser.add_argument("-f", "--freq", type=float)#, required=True)
    parser.add_argument("-r", "--rate", default=1e6, type=float)
    parser.add_argument("-d", "--duration", default=1.0, type=float)
    parser.add_argument("-c", "--channels", default=0, nargs="+", type=int)
    parser.add_argument("-lo", "--lo_offsets", default=0, nargs="+", type=int)
    parser.add_argument("-g", "--gain", type=float, default=10.0)
    parser.add_argument("--ip", type=str)
    parser.add_argument("--noip", action='store_true')
    parser.add_argument("--config", type=str)

    args = parser.parse_args()

    if args.config:
        # read from config file
        with open("config.yaml", "r") as yaml_file:
            config_data = yaml.safe_load(yaml_file)["client"]["hosts"]
            print(config_data)
            if config_data["all"]:
                update(args, config_data["all"])
                # args.config should contain the ansible hostname 
            try:
                if config_data[args.config]:
                    update(args, config_data[args.config])
            except:
                None
            
    print(args)
    return args

import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)


def wait_till_go_from_server(timeout=False):
    """Wait till a message is received at ip:5557 for topic phase.

    Args:
        ip (str): IP Address of the server
    """

    # Check if there are any incoming messages without blocking
    if timeout:
        socks = dict(poller.poll(timeout=0))
        if socket in socks and socks[socket] == zmq.POLLIN:
            # Receives a string format message
            topic = socket.recv_string()
            # todo check topic
            cmd = socket.recv_string()
        else:
            print("No message available")
            cmd = "start"  # default value
    else:
        # Receives a string format message
        topic = socket.recv_string()
        # todo check topic
        cmd = socket.recv_string()
        print(cmd)

    return cmd.lower()=="start"

def config_streamer(args, usrp):
    st_args = uhd.usrp.StreamArgs("fc32", "fc32")
    st_args.channels = args.channels
    return usrp.get_tx_stream(st_args)

def tx(duration, tx_streamer, rate, channels):
    metadata = uhd.types.TXMetadata()

    buffer_samps = tx_streamer.get_max_num_samps()
    samps_to_send = int(rate*duration)

    signal = np.ones((len(channels), buffer_samps), dtype=np.complex64)
    signal *= np.exp(1j*np.random.rand(len(channels), 1)*2*np.pi)*0.8 # 0.8 to not exceed to 1.0 threshold


    print(signal[:,0])

    send_samps = 0

    while send_samps < samps_to_send:
        samples = tx_streamer.send(signal, metadata)
        send_samps += samples
    # Send EOB to terminate Tx
    metadata.end_of_burst = True
    tx_streamer.send(np.zeros((len(channels), 1), dtype=np.complex64), metadata)
    # Help the garbage collection
    return send_samps

CLOCK_TIMEOUT = 1000  # 1000mS timeout for external clock locking

def setup_clock(usrp, clock_src, num_mboards):
    usrp.set_clock_source(clock_src)

    end_time = datetime.now() + timedelta(milliseconds=CLOCK_TIMEOUT)

    print("Now confirming lock on clock signals...")

    # Lock onto clock signals for all mboards
    for i in range(num_mboards):
        is_locked = usrp.get_mboard_sensor("ref_locked", i)
        while (not is_locked) and (datetime.now() < end_time):
            time.sleep(1e-3)
            is_locked = usrp.get_mboard_sensor("ref_locked", i)
        if not is_locked:
            print("Unable to confirm clock signal locked on board %d", i)
            return False
        else:
            print("Clock signals are locked")
    return True


def setup_pps(usrp, pps):
    """Setup the PPS source"""
    usrp.set_time_source(pps)
    return True
    
def multi_usrp_tx(args):
    """
    multi_usrp based TX example
    """
    usrp = uhd.usrp.MultiUSRP(args.args)
    setup_clock(usrp, "external", usrp.get_num_mboards())
    setup_pps(usrp, "external")

    for ichan, chan in enumerate(args.channels):
        usrp.set_tx_rate(args.rate, chan)
        usrp.set_tx_freq(uhd.types.TuneRequest(args.freq, args.lo_offsets[ichan]), chan)
        usrp.set_tx_gain(args.gain, chan)


    while not usrp.get_rx_sensor("lo_locked").to_bool():
        time.sleep(0.01)

    print("RX LO is locked")

    while not usrp.get_tx_sensor("lo_locked").to_bool():
        time.sleep(0.01)

    print("TX LO is locked")
      
    tx_streamer = config_streamer(args, usrp)

    socket.connect(f"tcp://{args.ip}:{5558}")  # Connect to the publisher's address

    # Subscribe to topics
    socket.subscribe("phase")

    # if noip then we skip the wait till server and just continue
    
    start = wait_till_go_from_server(timeout=args.noip)
    while(start or args.noip):
        tx(args.duration, tx_streamer, args.rate, args.channels)
        start = wait_till_go_from_server(timeout=True)

def main():
    """TX samples based on input arguments"""
    args = parse_args()
    if not isinstance(args.channels, list):
        args.channels = [args.channels]
    multi_usrp_tx(args)

if __name__ == "__main__":
    main()
