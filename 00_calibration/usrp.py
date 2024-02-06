# start TX on both "frontends" (A and B)
# start RX on both "frontends" (A and B)

# measure the phase difference between both



# sudo make -j4 && ./init_usrp --ref="external" --tx-freq=900E6 --rx-freq=900E6 --tx-rate=250E3 --rx-rate=250E3 --tx-gain=0.7 --rx-gain=45 --tx-channels="0,1" --rx-channels="0,1"
from datetime import datetime, timedelta
import sys
import time
import threading
import logging
import numpy as np
import uhd
import zmq

CLOCK_TIMEOUT = 1000  # 1000mS timeout for external clock locking
INIT_DELAY = 0.2  # 200mS initial delay before transmit


context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind(f"tcp://*:{8080}")

class LogFormatter(logging.Formatter):
    """Log formatter which prints the timestamp with fractional seconds"""
    @staticmethod
    def pp_now():
        """Returns a formatted string containing the time of day"""
        now = datetime.now()
        return "{:%H:%M}:{:05.2f}".format(now, now.second + now.microsecond / 1e6)
        # return "{:%H:%M:%S}".format(now)

    def formatTime(self, record, datefmt=None):
        converter = self.converter(record.created)
        if datefmt:
            formatted_date = converter.strftime(datefmt)
        else:
            formatted_date = LogFormatter.pp_now()
        return formatted_date
    
def publish(data):
    for val in data:
        socket.send_string(str(val))

def rx_ref(usrp, rx_streamer, quit_event, phase_to_compensate, results):
    
    # Make a receive buffer
    num_channels = rx_streamer.get_num_channels()
    max_samps_per_packet = rx_streamer.get_max_num_samps()
    # TODO: The C++ code uses rx_cpu type here. Do we want to use that to set dtype?
    recv_buffer = np.empty((num_channels, max_samps_per_packet), dtype=np.complex64)
    metadata = uhd.types.RXMetadata()

    # Craft and send the Stream Command
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
    stream_cmd.stream_now = (num_channels == 1) 
    stream_cmd.time_spec = uhd.types.TimeSpec(usrp.get_time_now().get_real_secs() + 2*INIT_DELAY)
    rx_streamer.issue_stream_cmd(stream_cmd)

    angles = []
    powers = []

    while not quit_event.is_set(): 
        try:
            rx_streamer.recv(recv_buffer, metadata)
            powers.append(np.mean(np.abs(recv_buffer), axis=-1))
            angles.append(np.mean(recv_buffer, axis=-1))
        except RuntimeError as ex:
            logger.error("Runtime error in receive: %s", ex)
            return
    
    avg_angles =np.rad2deg(np.angle(np.mean(angles,axis=0)))
    avg_power = np.mean(powers,axis=0)
    print(f"Angle CH0:{avg_angles[0]:.2f} CH1:{avg_angles[1]:.2f}")
    print(f"Power CH0:{avg_power[0]:.2f} CH1:{avg_power[1]:.2f}")
    phase_to_compensate.extend(avg_angles)
    rx_streamer.issue_stream_cmd(uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont))
    publish(angles)
    

def tx_ref(usrp, tx_streamer, quit_event, phase=[0,0], amplitude=[0.8, 0.8]):
    # TODO
    num_channels = tx_streamer.get_num_channels()
    max_samps_per_packet = tx_streamer.get_max_num_samps()

    amplitude = np.asarray(amplitude)
    phase = np.asarray(phase)

    sample = amplitude*np.exp(phase*1j)

    print(sample)

    transmit_buffer = np.tile(sample, (max_samps_per_packet, 1)).transpose()

    print(transmit_buffer.shape)

    # transmit_buffer = np.ones((num_channels, max_samps_per_packet), dtype=np.complex64)*sample
    metadata = uhd.types.TXMetadata()
    metadata.time_spec = uhd.types.TimeSpec(usrp.get_time_now().get_real_secs()+ INIT_DELAY)
    metadata.has_time_spec = bool(num_channels)

    while not quit_event.is_set():
        tx_streamer.send(transmit_buffer, metadata)
    
    # Send a mini EOB packet
    metadata.end_of_burst = True
    tx_streamer.send(np.zeros((num_channels, 0), dtype=np.complex64), metadata)

def main():
    # Setup the logger with our custom timestamp formatting
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    logger.addHandler(console)
    formatter = LogFormatter(fmt='[%(asctime)s] [%(levelname)s] (%(threadName)-10s) %(message)s')
    console.setFormatter(formatter)

    usrp = uhd.usrp.MultiUSRP("")
    rate=250E3
    tx_gain = 50 # TX gain 89.9dB
    rx_gain = 45 # RX gain 76dB
    rx_gain_pll = 22
    channels = [0,1]
    duration = 10.0 # seconds
    freq=920E6


    usrp.set_clock_source("external")
    usrp.set_time_source("external")


    usrp.set_rx_dc_offset(False, 0);
    usrp.set_rx_dc_offset(False, 1);

    usrp.set_time_unknown_pps(uhd.types.TimeSpec(0.0))

    usrp.set_tx_rate(rate, 0)
    usrp.set_tx_freq(freq, 0)
    usrp.set_tx_gain(tx_gain, 0)
    usrp.set_rx_rate(rate, 0)
    usrp.set_rx_freq(freq, 0)
    usrp.set_rx_gain(rx_gain_pll, 0) # Ref PLL is 3dBm

    usrp.set_tx_rate(rate, 1)
    usrp.set_tx_freq(freq, 1)
    usrp.set_tx_gain(tx_gain, 1)
    usrp.set_rx_rate(rate, 1)
    usrp.set_rx_freq(freq, 1)
    usrp.set_rx_gain(rx_gain, 1) 

    threads = []
    # Make a signal for the threads to stop running
    quit_event = threading.Event()

    ########### TX Thread ###########
    usrp.set_tx_rate(rate)
    st_args = uhd.usrp.StreamArgs("fc32","fc32")
    st_args.channels = channels
    st_args.args = uhd.types.DeviceAddr()
    tx_streamer = usrp.get_tx_stream(st_args)
    
    tx_thread = threading.Thread(target=tx_ref,
                                    args=(usrp, tx_streamer, quit_event, [0.0,0.0],[0.0,0.8]))
    threads.append(tx_thread)
    tx_thread.start()
    tx_thread.setName("TX_thread")

    ########### RX Thread ###########

    usrp.set_rx_rate(rate)
    st_args = uhd.usrp.StreamArgs("fc32","fc32")
    st_args.channels = channels
    st_args.args = uhd.types.DeviceAddr()
    rx_streamer = usrp.get_rx_stream(st_args)
    phase_to_compensate = []
    rx_thread = threading.Thread(target=rx_ref,
                                    args=(usrp, rx_streamer, quit_event, phase_to_compensate))
    
    threads.append(rx_thread)
    rx_thread.start()
    rx_thread.setName("RX_thread")


    time.sleep(duration)
    # Interrupt and join the threads
    logger.debug("Sending signal to stop!")
    quit_event.set()
    for thr in threads:
        thr.join()
    
    print(phase_to_compensate)

    pll_phase = phase_to_compensate[0]
    tx_phase = phase_to_compensate[1]

    phase_comp = pll_phase-tx_phase

    threads = []
    phase_to_compensate = []
    # Make a signal for the threads to stop running
    quit_event = threading.Event()
    rx_thread = threading.Thread(target=rx_ref,
                                    args=(usrp, rx_streamer, quit_event, phase_to_compensate))
    tx_thread = threading.Thread(target=tx_ref,
                                    args=(usrp, tx_streamer, quit_event, [phase_comp,0.0],[0.8,0.0]))
    threads.append(tx_thread)
    tx_thread.start()
    tx_thread.setName("TX_thread")
    threads.append(rx_thread)
    rx_thread.start()
    rx_thread.setName("RX_thread")

    time.sleep(duration)
    # Interrupt and join the threads
    logger.debug("Sending signal to stop!")
    quit_event.set()
    for thr in threads:
        thr.join()

    print(phase_to_compensate)

    pll_phase = phase_to_compensate[0]
    tx_phase = phase_to_compensate[1]

    socket.close()
    context.term()

if __name__ == "__main__":
    main()