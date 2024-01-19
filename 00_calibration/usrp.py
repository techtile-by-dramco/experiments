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

def rx_ref(usrp, rx_streamer, quit_event):
    # TODO
    while not quit_event.is_set(): 
        pass

def tx_ref(usrp, tx_streamer, quit_event):
    # TODO
    while not quit_event.is_set(): 
        pass

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
    tx_gain = 0.7
    rx_gain = 45
    channels = [0,1]
    duration = 10.0 # seconds


    usrp.set_clock_source("external")
    usrp.set_time_source("external")

    usrp.set_time_unknown_pps(uhd.types.TimeSpec(0.0))

    threads = []
    # Make a signal for the threads to stop running
    quit_event = threading.Event()

    ########### TX Thread ###########
    usrp.set_tx_rate(rate)
    st_args = uhd.usrp.StreamArgs()
    st_args.channels = channels
    st_args.args = uhd.types.DeviceAddr()
    tx_streamer = usrp.get_tx_stream(st_args)
    tx_thread = threading.Thread(target=tx_ref,
                                    args=(usrp, tx_streamer, quit_event))
    threads.append(tx_thread)
    tx_thread.start()
    tx_thread.setName("TX_thread")

    ########### RX Thread ###########

    usrp.set_rx_rate(rate)
    st_args = uhd.usrp.StreamArgs()
    st_args.channels = channels
    st_args.args = uhd.types.DeviceAddr()
    rx_streamer = usrp.get_rx_stream(st_args)
    rx_thread = threading.Thread(target=rx_ref,
                                    args=(usrp, rx_streamer, quit_event))
    threads.append(rx_thread)
    rx_thread.start()
    rx_thread.setName("RX_thread")


    time.sleep(duration)
    # Interrupt and join the threads
    logger.debug("Sending signal to stop!")
    quit_event.set()
    for thr in threads:
        thr.join()

if __name__ == "__main__":
    main()