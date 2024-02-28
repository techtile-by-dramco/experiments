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
import os
import zmq

CLOCK_TIMEOUT = 1000  # 1000mS timeout for external clock locking
INIT_DELAY = 1.2 # 1200ms initial delay before transmit

RATE = 250e3
DURATION = 60

TOPIC_CH0 = b"CH0"
TOPIC_CH1 = b"CH1"


context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind(f"tcp://*:{50001}")

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
       
def tx_async_th(tx_streamer, quit_event):
    async_metadata = uhd.types.TXAsyncMetadata()

    try:
        while not quit_event.is_set():
            if not tx_streamer.recv_async_msg(async_metadata, 0.01):
                continue
            else:
                logger.error(async_metadata.event_code)
    except KeyboardInterrupt:
        pass

    
def tx_ref(usrp, tx_streamer, quit_event):
    # TODO 
    num_channels = tx_streamer.get_num_channels()
    max_samps_per_packet = tx_streamer.get_max_num_samps()

    # amplitude = np.asarray(amplitude)
    # phase = np.asarray(phase)

    # sample = amplitude*np.exp(phase*1j)

    # print(sample)

    # transmit_buffer = np.tile(np.asarray([1.0, 1.0], dtype=np.complex64), (1000*max_samps_per_packet, 1)).transpose()

    # print(transmit_buffer.shape)

    # transmit_buffer = np.ones((num_channels, max_samps_per_packet), dtype=np.complex64)*sample
    tx_md = uhd.types.TXMetadata()
    tx_md.time_spec = uhd.types.TimeSpec(usrp.get_time_now().get_real_secs()+ INIT_DELAY)
    tx_md.has_time_spec = bool(num_channels)

   

    transmit_buffer = np.ones((num_channels, 1000*max_samps_per_packet), dtype=np.complex64)*0.8

    try:
        while not quit_event.is_set():
            tx_streamer.send(transmit_buffer, tx_md)
            tx_md.has_time_spec = False # need to be false in order for the following samples to start immediatly following the prev.
    except KeyboardInterrupt:
        pass
    finally: 
        # Send a mini EOB packet
        logger.debug("CTRL+C is pressed, closing off")
        tx_md.end_of_burst = True
        tx_streamer.send(np.zeros((num_channels, 0), dtype=np.complex64), tx_md)

def setup(usrp):
    rate= RATE
    mcr = 16e6 
    #assert (rate/mcr).is_integer(), "The masterclock rate should be an integer multiple of the sampling rate"
    
    usrp.set_master_clock_rate(mcr) # Manual selection of master clock rate may also be required to synchronize multiple B200 units in time.
    
    tx_gain = 80 # TX gain 89.9dB
    channels = [0,1]

    freq=920E6
    
    usrp.set_clock_source("external")
    usrp.set_time_source("external")

    usrp.set_rx_dc_offset(False, 0)

    usrp.set_time_unknown_pps(uhd.types.TimeSpec(0.0))

    # Channel 0 settings
    usrp.set_tx_rate(rate, 0)
    usrp.set_tx_freq(freq, 0)
    usrp.set_tx_gain(tx_gain, 0)

    # Channel 1 settings
    usrp.set_tx_rate(rate, 1)
    usrp.set_tx_freq(freq, 1)
    usrp.set_tx_gain(tx_gain, 1)


    # streaming arguments
    st_args = uhd.usrp.StreamArgs("fc32","fc32")
    st_args.channels = channels
    st_args.args = uhd.types.DeviceAddr()

    # streamers
    tx_streamer = usrp.get_tx_stream(st_args)

    return tx_streamer

def tx_thread(usrp, tx_streamer, quit_event, phase=[0,0], amplitude=[0.8, 0.8]):
    tx_thread = threading.Thread(target=tx_ref,
                                    args=(usrp, tx_streamer, quit_event))
    tx_thread.setName("TX_thread")
    tx_thread.start()

    return tx_thread

def tx_meta_thread(tx_streamer, quit_event):
    tx_meta_thr = threading.Thread(target=tx_async_th,
                                    args=(tx_streamer, quit_event))
    tx_meta_thr.setName("TX_META_thread")
    tx_meta_thr.start()
    return tx_meta_thr

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
    tx_streamer = setup(usrp)
    

    # Make a signal for the threads to stop running
    quit_event = threading.Event()
    
    try:

        ########### TX & RX Thread ###########
        tx_thr = tx_thread(usrp, tx_streamer, quit_event, amplitude=[0.8,0.8])
        tx_meta_thr = tx_meta_thread(tx_streamer, quit_event)
        #wait till both threads are done before proceding
        tx_thr.join()
        tx_meta_thr.join()
    except KeyboardInterrupt:
        print('Interrupted')
        # Interrupt and join the threads
        logger.debug("Sending signal to stop!")
        quit_event.set()
        # wait till finished before closing of
        tx_thr.join()
        tx_meta_thr.join()
    finally: 
        socket.close()
        context.term()
        sys.exit(130)



if __name__ == "__main__":
    main()
