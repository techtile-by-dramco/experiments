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
INIT_DELAY = 0.2  # 200ms initial delay before transmit

RATE = 250e3
DURATION = 60


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
    
def publish(data):
    import struct

    print(f"sending data of size {len(data)}")
    socket.send(data.tobytes())
    # for val in data:
    #     value_bytes = struct.pack('!d', val)  # Using double precision format
    #     socket.send(value_bytes)

def rx_ref(usrp, rx_streamer, quit_event, phase_to_compensate):
    # https://files.ettus.com/manual/page_sync.html#sync_phase_cordics
    # The CORDICs are reset at each start-of-burst command, so users should ensure that every start-of-burst also has a time spec set.
    
    # Make a receive buffer
    num_channels = rx_streamer.get_num_channels()
    max_samps_per_packet = rx_streamer.get_max_num_samps()
    # TODO: The C++ code uses rx_cpu type here. Do we want to use that to set dtype?
    recv_buffer = np.zeros((num_channels, 1000*max_samps_per_packet), dtype=np.complex64)
    rx_md = uhd.types.RXMetadata()

    # Craft and send the Stream Command
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
    stream_cmd.stream_now = False
    stream_cmd.time_spec = uhd.types.TimeSpec(usrp.get_time_now().get_real_secs() + 1.1*INIT_DELAY)
    rx_streamer.issue_stream_cmd(stream_cmd)

    # iq_data_mean  = []
    # powers = []

    # todo ensure thqt we stop RX before TX ends
    data_buffer = np.zeros((num_channels, int(RATE*DURATION)*2), dtype=np.complex64)

    num_rx = 0

    while not quit_event.is_set(): 
        try:
            num_rx_i  = rx_streamer.recv(recv_buffer, rx_md, 1.0)
            print(".", end="", flush=True)
            if rx_md.error_code != uhd.types.RXMetadataErrorCode.none:
                print(rx_md.error_code)
            # powers.append(np.mean(np.abs(recv_buffer), axis=-1))
            # iq_data_mean.append(np.mean(recv_buffer, axis=-1))
            data_buffer[:,num_rx:num_rx+num_rx_i] = recv_buffer[:,:num_rx_i]
            num_rx += num_rx_i
        except RuntimeError as ex:
            logger.error("Runtime error in receive: %s", ex)
            return
    # keep this just below this loop
    rx_streamer.issue_stream_cmd(uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont))

    marge = int(250e3) # remove prepending and appending second

    iq_data = data_buffer[:,marge:num_rx-marge]
    
    avg_angles = np.angle(np.sum(np.exp(np.angle(iq_data)*1j), axis=1)) # circular mean https://en.wikipedia.org/wiki/Circular_mean

    avg_ampl = np.mean(np.abs(iq_data),axis=1)

    print(f"Angle CH0:{np.rad2deg(avg_angles[0]):.2f} CH1:{np.rad2deg(avg_angles[1]):.2f}")
    print(f"Amplitude CH0:{avg_ampl[0]:.2f} CH1:{avg_ampl[1]:.2f}")
    phase_to_compensate.extend(avg_angles)
    

    publish(np.rad2deg(np.angle(iq_data[0])))
    publish(np.rad2deg(np.angle(iq_data[1])))

    
    

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

def setup(usrp):
    rate= RATE
    mcr = 16e6 
    #assert (rate/mcr).is_integer(), "The masterclock rate should be an integer multiple of the sampling rate"
    
    usrp.set_master_clock_rate(mcr) # Manual selection of master clock rate may also be required to synchronize multiple B200 units in time.
    
    tx_gain = 80 # TX gain 89.9dB
    rx_gain = 30 # RX gain 76dB
    rx_gain_pll = 20
    channels = [0,1]

    rx_bw = 200e3 # smallest as possible (https://files.ettus.com/manual/page_usrp_b200.html#b200_fe_bw)
    freq=920E6
    
    usrp.set_clock_source("external")
    usrp.set_time_source("external")

    usrp.set_rx_dc_offset(False, 0)
    usrp.set_rx_dc_offset(False, 1)

    usrp.set_time_unknown_pps(uhd.types.TimeSpec(0.0))

    # Channel 0 settings
    usrp.set_tx_rate(rate, 0)
    usrp.set_tx_freq(freq, 0)
    usrp.set_tx_gain(tx_gain, 0)
    usrp.set_rx_rate(rate, 0)
    usrp.set_rx_freq(freq, 0)
    usrp.set_rx_gain(rx_gain, 0) # Ref PLL is 3dBm
    usrp.set_rx_bandwidth(rx_bw, 0)

    # Channel 1 settings
    usrp.set_tx_rate(rate, 1)
    usrp.set_tx_freq(freq, 1)
    usrp.set_tx_gain(tx_gain, 1)
    usrp.set_rx_rate(rate, 1)
    usrp.set_rx_freq(freq, 1)
    usrp.set_rx_gain(rx_gain_pll, 1) 
    usrp.set_rx_bandwidth(rx_bw, 1)


    # streaming arguments
    st_args = uhd.usrp.StreamArgs("fc32","fc32")
    st_args.channels = channels
    st_args.args = uhd.types.DeviceAddr()

    # streamers
    tx_streamer = usrp.get_tx_stream(st_args)
    rx_streamer = usrp.get_rx_stream(st_args)

    return tx_streamer, rx_streamer

def tx_thread(usrp, tx_streamer, quit_event, phase=[0,0], amplitude=[0.8, 0.8]):
    tx_thread = threading.Thread(target=tx_ref,
                                    args=(usrp, tx_streamer, quit_event, phase, amplitude))
    tx_thread.setName("TX_thread")
    tx_thread.start()

    return tx_thread

def rx_thread(usrp, rx_streamer, quit_event, phase_to_compensate):
    rx_thread = threading.Thread(target=rx_ref,
                                    args=(usrp, rx_streamer, quit_event, phase_to_compensate))
    rx_thread.setName("RX_thread")
    rx_thread.start()

    return rx_thread

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
    tx_streamer, rx_streamer = setup(usrp)
    

    # Make a signal for the threads to stop running
    quit_event = threading.Event()

    ########### TX & RX Thread ###########
    tx_thr = tx_thread(usrp, tx_streamer, quit_event, amplitude=[0.0,0.8])
    phase_to_compensate = []
    rx_thr = rx_thread(usrp, rx_streamer, quit_event, phase_to_compensate)

    time.sleep(DURATION)
    
    # Interrupt and join the threads
    logger.debug("Sending signal to stop!")
    quit_event.set()
    
    #wait till both threads are done before proceding
    tx_thr.join()
    rx_thr.join()


    # time.sleep(DURATION) #sleep between two measurements

    # Make a signal for the threads to stop running
    quit_event = threading.Event()
    
    
    try:

        ########### TX & RX Thread ###########
        tx_thr = tx_thread(usrp, tx_streamer, quit_event, amplitude=[0.0,0.8])
        phase_to_compensate = []
        rx_thr = rx_thread(usrp, rx_streamer, quit_event, phase_to_compensate)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            # Interrupt and join the threads
            logger.debug("Sending signal to stop!")
            quit_event.set()
            
            #wait till both threads are done before proceding
            tx_thr.join()
            rx_thr.join()
            
            socket.close()
            context.term()
            sys.exit(130)
        except SystemExit:
            os._exit(130)

    # time.sleep(DURATION)
    
    

    
    # print(phase_to_compensate)

    # tx_phase = phase_to_compensate[0]
    
    # pll_phase = phase_to_compensate[1]

    # phase_comp = -tx_phase

    # print(np.rad2deg(phase_comp))

    # threads = []
    # phase_to_compensate = []
    # # Make a signal for the threads to stop running
    # quit_event = threading.Event()
    # rx_thread = threading.Thread(target=rx_ref,
    #                                 args=(usrp, rx_streamer, quit_event, phase_to_compensate))
    # # tx_thread = threading.Thread(target=tx_ref,
    # #                                 args=(usrp, tx_streamer, quit_event, [phase_comp,0.0], [0.0,0.8]))

    # tx_thread = threading.Thread(target=tx_ref,
    #                                 args=(usrp, tx_streamer, quit_event, [0.0,0.0],[0.0,0.8]))
    

    # threads.append(tx_thread)
    # tx_thread.start()
    # tx_thread.setName("TX_thread")
    # threads.append(rx_thread)
    # rx_thread.start()
    # rx_thread.setName("RX_thread")

    # time.sleep(duration)
    # # Interrupt and join the threads
    # logger.debug("Sending signal to stop!")
    # quit_event.set()
    # for thr in threads:
    #     thr.join()

    # print(phase_to_compensate)

    # pll_phase = phase_to_compensate[0]
    # tx_phase = phase_to_compensate[1]

    

if __name__ == "__main__":
    main()