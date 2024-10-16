# start TX on both "frontends" (A and B)

# start RX on both "frontends" (A and B)


# measure the phase difference between both

import argparse
import logging
import os
import sys
import threading
import time
from datetime import datetime

import numpy as np
import uhd
import yaml
import zmq
from scipy.stats import circmean, circvar
from datetime import datetime, timedelta

CMD_DELAY = 0.05  # set a 50mS delay in commands
# default values which will be overwritten by the conf YML
RX_TX_SAME_CHANNEL = True  # if loopback is done from one channel to the other channel
CLOCK_TIMEOUT = 1000  # 1000mS timeout for external clock locking
INIT_DELAY = 0.2  # 200ms initial delay before transmit
RATE = 250e3
LOOPBACK_TX_GAIN = 70  # empirical determined
LOOPBACK_RX_GAIN = 23  # empirical determined
REF_RX_GAIN = 22  # empirical determined 22 without splitter, 27 with splitter
CAPTURE_TIME = 10
server_ip = "10.128.52.53"
MAX_RETRIES = 10

with open(os.path.join(os.path.dirname(__file__), "cal-settings.yml"), 'r') as file:
    vars = yaml.safe_load(file)
    globals().update(vars)  # update the global variables with the vars in yaml


# Setup the logger with our custom timestamp formatting
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


global logger
global begin_time

begin_time = 2.0

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()

logger.addHandler(console)

formatter = LogFormatter(
    fmt="[%(asctime)s] [%(levelname)s] (%(threadName)-10s) %(message)s")

console.setFormatter(formatter)

TOPIC_CH0 = b"CH0"
TOPIC_CH1 = b"CH1"

if RX_TX_SAME_CHANNEL:
    REF_RX_CH = FREE_TX_CH = 0
    LOOPBACK_RX_CH = LOOPBACK_TX_CH = 1
    logger.debug("\nPLL REF-->CH0 RX\nCH1 TX-->CH1 RX\nCH0 TX -->")
else:
    LOOPBACK_RX_CH = FREE_TX_CH = 0
    REF_RX_CH = LOOPBACK_TX_CH = 1
    logger.debug("\nPLL REF-->CH1 RX\nCH1 TX-->CH0 RX\nCH0 TX -->")

context = zmq.Context()

socket = context.socket(zmq.PUB)

socket.bind(f"tcp://*:{50001}")

sync_socket = context.socket(zmq.SUB)





def publish(data, channel: int):
    # logger.debug(f"sending data of size {len(data)}")

    if channel == 0:
        topic = TOPIC_CH0
    elif channel == 1:
        topic = TOPIC_CH1
    else:
        logger.error(f"Channel should be 0 or 1, not {channel}")

    socket.send_multipart([topic, data.tobytes()])


def send_rx(samples):
    # avg_angles = np.angle(np.sum(np.exp(np.angle(samples)*1j), axis=1)) # circular mean https://en.wikipedia.org/wiki/Circular_mean

    # avg_ampl = np.mean(np.abs(samples),axis=1)

    # print(f"Angle CH0:{np.rad2deg(avg_angles[0]):.2f} CH1:{np.rad2deg(avg_angles[1]):.2f}")

    # print(f"Amplitude CH0:{avg_ampl[0]:.2f} CH1:{avg_ampl[1]:.2f}")

    angles = np.rad2deg(np.angle(samples))

    publish(angles[0], 0)

    publish(angles[1], 1)


def rx_ref(usrp, rx_streamer, quit_event, phase_to_compensate, duration, start_time=None):
    # https://files.ettus.com/manual/page_sync.html#sync_phase_cordics

    # The CORDICs are reset at each start-of-burst command, so users should ensure that every start-of-burst also has a time spec set.

    num_channels = rx_streamer.get_num_channels()

    max_samps_per_packet = rx_streamer.get_max_num_samps()

    iq_data = np.empty(
        (num_channels, int(duration * RATE * 2)), dtype=np.complex64)

    # Make a rx buffer

    # TODO: The C++ code uses rx_cpu type here. Do we want to use that to set dtype?

    # recv_buffer = np.zeros((num_channels, min([1000 * max_samps_per_packet, int(duration * RATE * 2)])),
    #                        dtype=np.complex64, )\

    recv_buffer = np.zeros(
        (num_channels, max_samps_per_packet), dtype=np.complex64)

    rx_md = uhd.types.RXMetadata()

    # Craft and send the Stream Command

    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)

    # The stream now parameter controls when the stream begins. When true, the device will begin streaming ASAP. When false, the device will begin streaming at a time specified by time_spec.
    stream_cmd.stream_now = False

    timeout = 1.0
    if start_time is not None:
        stream_cmd.time_spec = start_time
        time_diff = start_time.get_real_secs() - usrp.get_time_now().get_real_secs()
        if time_diff > 0:
            timeout = 1.0 + time_diff
    else:
        stream_cmd.time_spec = uhd.types.TimeSpec(
            usrp.get_time_now().get_real_secs() + INIT_DELAY + 0.1)

    rx_streamer.issue_stream_cmd(stream_cmd)

    try:

        num_rx = 0

        while not quit_event.is_set():

            try:

                num_rx_i = rx_streamer.recv(recv_buffer, rx_md, timeout)

                if rx_md.error_code != uhd.types.RXMetadataErrorCode.none:
                    logger.error(rx_md.error_code)

                else:

                    if num_rx_i > 0:
                        # samples = recv_buffer[:,:num_rx_i]
                        # send_rx(samples)

                        samples = recv_buffer[:, :num_rx_i]

                        iq_data[:, num_rx: num_rx + num_rx_i] = samples

                        # threading.Thread(target=send_rx,
                        #                  args=(samples,)).start()

                        num_rx += num_rx_i

            except RuntimeError as ex:

                logger.error("Runtime error in receive: %s", ex)
                return

    except KeyboardInterrupt:
        pass

    finally:

        logger.debug("CTRL+C is pressed or duration is reached, closing off ")

        rx_streamer.issue_stream_cmd(
            uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont))

        samples = iq_data[:, :num_rx]

        # np.angle(np.sum(np.exp(np.angle(samples)*1j), axis=1)) # circular mean https://en.wikipedia.org/wiki/Circular_mean
        avg_angles = circmean(np.angle(samples[:, int(RATE//10):]), axis=1)
        var_angles = circvar(np.angle(samples[:, int(RATE//10):]), axis=1)

        phase_to_compensate.extend(avg_angles)

        avg_ampl = np.mean(np.abs(samples), axis=1)

        logger.debug(
            f"Angle CH0:{np.rad2deg(avg_angles[0]):.2f} CH1:{np.rad2deg(avg_angles[1]):.2f}")
        logger.debug(
            f"Angle var CH0:{var_angles[0]:.2f} CH1:{var_angles[1]:.2f}")
        # keep this just below this final stage
        logger.debug(f"Amplitude CH0:{avg_ampl[0]:.2f} CH1:{avg_ampl[1]:.2f}")


def wait_till_go_from_server(ip):

    # Connect to the publisher's address
    sync_socket.connect(f"tcp://{ip}:{5557}")
    # Subscribe to topics
    sync_socket.subscribe("SYNC")
    logger.debug("Waiting on SYNC from server %s.", ip)
    # Receives a string format message
    sync_socket.recv_string()


def tx_ref(usrp, tx_streamer, quit_event, phase, amplitude, start_time=None):
    num_channels = tx_streamer.get_num_channels()

    max_samps_per_packet = tx_streamer.get_max_num_samps()

    amplitude = np.asarray(amplitude)

    phase = np.asarray(phase)

    sample = amplitude * np.exp(phase * 1j)

    # print(sample)

    # transmit_buffer = np.ones((num_channels, 1000*max_samps_per_packet), dtype=np.complex64) * sample[:, np.newaxis]

    # amplitude[:,np.newaxis]
    transmit_buffer = np.ones(
        (num_channels, 1000 * max_samps_per_packet), dtype=np.complex64)

    transmit_buffer[0, :] *= sample[0]

    transmit_buffer[1, :] *= sample[1]

    # print(transmit_buffer.shape)

    # transmit_buffer = np.ones((num_channels, max_samps_per_packet), dtype=np.complex64)*sample

    tx_md = uhd.types.TXMetadata()

    if start_time is not None:
        tx_md. time_spec = start_time
    else:
        tx_md.time_spec = uhd.types.TimeSpec(
            usrp.get_time_now().get_real_secs() + INIT_DELAY)

    tx_md.has_time_spec = True

    try:

        while not quit_event.is_set():
            tx_streamer.send(transmit_buffer, tx_md)

    except KeyboardInterrupt:
        logger.debug("CTRL+C is pressed, closing off")

    finally:
        # Send a mini EOB packet

        tx_md.end_of_burst = True

        tx_streamer.send(np.zeros((num_channels, 0),
                         dtype=np.complex64), tx_md)


def setup_clock(usrp, clock_src, num_mboards):
    usrp.set_clock_source(clock_src)

    logger.debug("Now confirming lock on clock signals...")
    end_time = datetime.now() + timedelta(milliseconds=CLOCK_TIMEOUT)

    # Lock onto clock signals for all mboards
    for i in range(num_mboards):
        is_locked = usrp.get_mboard_sensor("ref_locked", i)
        while (not is_locked) and (datetime.now() < end_time):
            time.sleep(1e-3)
            is_locked = usrp.get_mboard_sensor("ref_locked", i)
        if not is_locked:
            logger.error(
                "Unable to confirm clock signal locked on board %d", i)
            return False
        else:
            logger.debug("Clock signals are locked")
    return True


def setup_pps(usrp, pps):
    """Setup the PPS source"""
    usrp.set_time_source(pps)
    return True


def print_tune_result(tune_res):
    return "Tune Result:\n    Target RF  Freq: {:.2f} (MHz)\n Actual RF  Freq: {:.2f} (MHz)\n Target DSP Freq: {:.2f} " \
           "(MHz)\n " \
           "Actual DSP Freq: {:.2f} (MHz)\n".format((tune_res.target_rf_freq / 1e6), (tune_res.actual_rf_freq / 1e6),
                                                    (tune_res.target_dsp_freq / 1e6), (tune_res.actual_dsp_freq / 1e6))


def wait_till_time(usrp, at_time):
    logger.debug("Wait till command is executed")
    while usrp.get_time_now().get_real_secs() < at_time + CMD_DELAY:
        time.sleep(0.01)
    usrp.clear_command_time()


def tune_usrp(usrp, freq, channels, at_time):
    """Synchronously set the device's frequency.
       If a channel is using an internal LO it will be tuned first
       and every other channel will be manually tuned based on the response.
       This is to account for the internal LO channel having an offset in the actual DSP frequency.
       Then all channels are synchronously tuned."""

    treq = uhd.types.TuneRequest(freq)

    usrp.set_command_time(uhd.types.TimeSpec(at_time))

    treq.dsp_freq = 0.0
    treq.target_freq = freq
    treq.rf_freq = freq
    treq.rf_freq_policy = uhd.types.TuneRequestPolicy(ord('M'))
    treq.dsp_freq_policy = uhd.types.TuneRequestPolicy(ord('M'))
    args = uhd.types.DeviceAddr("mode_n=integer")
    treq.args = args

    for chan in channels:
        logger.debug(print_tune_result(usrp.set_rx_freq(treq, chan)))
        logger.debug(print_tune_result(usrp.set_tx_freq(treq, chan)))

    wait_till_time(usrp, at_time) 


    while not usrp.get_rx_sensor("lo_locked").to_bool():
        time.sleep(0.01)

    logger.info("RX LO is locked")

    while not usrp.get_tx_sensor("lo_locked").to_bool():
        time.sleep(0.01)

    logger.info("TX LO is locked")


def setup(usrp, server_ip):

    rate = RATE

    mcr = 20e6

    assert (
        mcr / rate).is_integer(), f"The masterclock rate {mcr} should be an integer multiple of the sampling rate {rate}"

    # Manual selection of master clock rate may also be required to synchronize multiple B200 units in time.
    usrp.set_master_clock_rate(mcr)
    channels = [0, 1]
    setup_clock(usrp, "external", usrp.get_num_mboards())
    setup_pps(usrp, "external")

    # smallest as possible (https://files.ettus.com/manual/page_usrp_b200.html#b200_fe_bw)
    rx_bw = 200e3

    for chan in channels:
        usrp.set_rx_rate(rate, chan)
        usrp.set_tx_rate(rate, chan)
        usrp.set_rx_dc_offset(False, chan)
        usrp.set_rx_bandwidth(rx_bw, chan)

    # specific settings from loopback/REF PLL
    usrp.set_tx_gain(LOOPBACK_TX_GAIN, LOOPBACK_TX_CH)
    usrp.set_tx_gain(LOOPBACK_TX_GAIN, FREE_TX_CH)

    usrp.set_rx_gain(LOOPBACK_RX_GAIN, LOOPBACK_RX_CH)
    usrp.set_rx_gain(REF_RX_GAIN, REF_RX_CH)



    # streaming arguments

    st_args = uhd.usrp.StreamArgs("fc32", "sc16")
    st_args.channels = channels

    # streamers
    tx_streamer = usrp.get_tx_stream(st_args)
    rx_streamer = usrp.get_rx_stream(st_args)

    # Step1: wait for the last pps time to transition to catch the edge
    # Step2: set the time at the next pps (synchronous for all boards)
    # this is better than set_time_next_pps as we wait till the next PPS to transition and after that we set the time.
    # this ensures that the FPGA has enough time to clock in the new timespec (otherwise it could be too close to a PPS edge)
    wait_till_go_from_server(server_ip)
    logger.info("Setting device timestamp to 0...")
    usrp.set_time_unknown_pps(uhd.types.TimeSpec(0.0))
    logger.debug("[SYNC] Resetting time.")
    # we wait 2 seconds to ensure a PPS rising edge occurs and latches the 0.000s value to both USRPs.
    time.sleep(2)

    tune_usrp(usrp, FREQ, channels, at_time=begin_time)

    logger.info(
        f"USRP has been tuned and setup. ({usrp.get_time_now().get_real_secs()})")

    return tx_streamer, rx_streamer


def tx_thread(usrp, tx_streamer, quit_event, phase=[0, 0], amplitude=[0.8, 0.8], start_time=None):
    tx_thread = threading.Thread(target=tx_ref, args=(
        usrp, tx_streamer, quit_event, phase, amplitude, start_time))

    tx_thread.setName("TX_thread")
    tx_thread.start()

    return tx_thread


def rx_thread(usrp, rx_streamer, quit_event, phase_to_compensate, duration, start_time=None):
    rx_thread = threading.Thread(target=rx_ref,
                                 args=(usrp, rx_streamer, quit_event, phase_to_compensate, duration, start_time))

    rx_thread.setName("RX_thread")
    rx_thread.start()

    return rx_thread


def tx_async_th(tx_streamer, quit_event):
    async_metadata = uhd.types.TXAsyncMetadata()

    try:

        while not quit_event.is_set():

            if not tx_streamer.recv_async_msg(async_metadata, 0.01):
                continue

            else:
                if async_metadata.event_code != uhd.types.TXMetadataEventCode.burst_ack:
                    logger.error(async_metadata.event_code)

    except KeyboardInterrupt:
        pass


def tx_meta_thread(tx_streamer, quit_event):
    tx_meta_thr = threading.Thread(
        target=tx_async_th, args=(tx_streamer, quit_event))

    tx_meta_thr.setName("TX_META_thread")
    tx_meta_thr.start()
    return tx_meta_thr


def delta(usrp, at_time):
    return at_time - usrp.get_time_now().get_real_secs()


def starting_in(usrp, at_time):
    return f"Starting in {delta(usrp, at_time):.2f}s"


def measure_loopback(usrp, tx_streamer, rx_streamer, at_time) -> float:
    logger.debug(" ########### STEP 1 - measure self TX-RX phase ###########")

    quit_event = threading.Event()

    amplitudes = [0.0, 0.0]

    amplitudes[LOOPBACK_TX_CH] = 0.8

    phase_to_compensate = []

    start_time = uhd.types.TimeSpec(at_time)

    logger.debug(starting_in(usrp, at_time))

    tx_thr = tx_thread(usrp, tx_streamer, quit_event, amplitude=amplitudes, phase=[
                       0.0, 0.0], start_time=start_time)

    tx_meta_thr = tx_meta_thread(tx_streamer, quit_event)
    rx_thr = rx_thread(usrp, rx_streamer, quit_event, phase_to_compensate,
                       duration=CAPTURE_TIME, start_time=start_time)

    time.sleep(CAPTURE_TIME + delta(usrp, at_time))

    quit_event.set()

    # wait till both threads are done before proceding

    tx_thr.join()

    rx_thr.join()

    # logger.debug(f"Phases to compensate: {phase_to_compensate}")

    tx_meta_thr.join()

    # #TODO double check
    # import math
    # def closest_multiple_of(value, base=math.pi/8):
       
    #     if value < 0:
    #         value = value + math.pi*2

    #     return base * round(value/base)

    # # ensure it is a multiple of 45 degrees, as we would expect @ this frequency given the dividers
    # phase_to_compensate[LOOPBACK_RX_CH] = closest_multiple_of(phase_to_compensate[LOOPBACK_RX_CH])

    return phase_to_compensate[LOOPBACK_RX_CH]


def measure_pll(usrp, rx_streamer, at_time) -> float:
    # Make a signal for the threads to stop running

    logger.debug("########### STEP 2 - Measure PLL REF phase ###########")

    quit_event = threading.Event()

    phase_to_compensate = []

    start_time = uhd.types.TimeSpec(at_time)

    logger.debug(starting_in(usrp, at_time))

    rx_thr = rx_thread(usrp, rx_streamer, quit_event, phase_to_compensate,
                       duration=CAPTURE_TIME, start_time=start_time)

    time.sleep(CAPTURE_TIME + delta(usrp, at_time))

    quit_event.set()

    # wait till both threads are done before proceding
    rx_thr.join()

    pll_phase = phase_to_compensate[REF_RX_CH]

    return pll_phase


def check_loopback(usrp, tx_streamer, rx_streamer, phase_corr, at_time) -> float:
    logger.debug(
        " ########### STEP 3 - Check self-correction TX-RX phase ###########")

    quit_event = threading.Event()

    amplitudes = [0.0, 0.0]

    amplitudes[LOOPBACK_TX_CH] = 0.8

    phases = [0.0, 0.0]

    phases[LOOPBACK_TX_CH] = phase_corr

    start_time = uhd.types.TimeSpec(at_time)

    logger.debug(starting_in(usrp, at_time))

    phase_to_compensate = []

    tx_thr = tx_thread(usrp, tx_streamer, quit_event,
                       amplitude=amplitudes, phase=phases, start_time=start_time)
    tx_meta_thr = tx_meta_thread(tx_streamer, quit_event)
    rx_thr = rx_thread(usrp, rx_streamer, quit_event, phase_to_compensate,
                       duration=CAPTURE_TIME, start_time=start_time)

    time.sleep(CAPTURE_TIME + delta(usrp, at_time))

    quit_event.set()

    # wait till both threads are done before proceeding

    tx_thr.join()

    rx_thr.join()

    tx_meta_thr.join()

    return phase_to_compensate[LOOPBACK_RX_CH]


def tx_phase_coh(usrp, tx_streamer, quit_event, phase_corr, at_time):
    logger.debug("########### STEP 4 - TX with adjusted phases ###########")

    phases = [0.0, 0.0]
    amplitudes = [0.0, 0.0]

    phases[FREE_TX_CH] = phase_corr
    amplitudes[FREE_TX_CH] = 0.8

    start_time = uhd.types.TimeSpec(at_time)

    logger.debug(starting_in(usrp, at_time))

    logger.debug(
        f"Applying phase correction CH0:{np.rad2deg(phases[0]):.2f} and CH1:{np.rad2deg(phases[1]):.2f}")

    tx_thr = tx_thread(usrp, tx_streamer, quit_event,
                       amplitude=amplitudes, phase=phases, start_time=start_time)

    tx_meta_thr = tx_meta_thread(tx_streamer, quit_event)

    return tx_thr, tx_meta_thr


def get_current_time(usrp):
    return usrp.get_time_now().get_real_secs()




def main():
    # "mode_n=integer" # 

    # start_PLL()

    usrp = uhd.usrp.MultiUSRP(
        "fpga=/home/pi/experiments/00_calibration/usrp_b210_fpga_loopback.bin, mode_n=integer")
    logger.info("Using Device: %s", usrp.get_pp_string())
    tx_streamer, rx_streamer = setup(usrp, server_ip)

    tx_thr = tx_meta_thr = None

    try:

        
        

        margin = 10.0
        cmd_time = CAPTURE_TIME + margin

        start_time = begin_time + margin

        tx_rx_phase = measure_loopback(
            usrp, tx_streamer, rx_streamer, at_time=start_time)
        print("DONE")

        phase_corr = - tx_rx_phase

        start_time += cmd_time + margin
        pll_rx_phase = measure_pll(
            usrp, rx_streamer, at_time=start_time)
        print("DONE")

        start_time += cmd_time + margin
        remainig_phase = check_loopback(usrp, tx_streamer, rx_streamer,
                       phase_corr=phase_corr, at_time=start_time)
        
        calibrated = False
        logger.debug(f"Remaining phase is {np.rad2deg(remainig_phase)} degrees.")
        calibrated = (np.rad2deg(remainig_phase) <
                      1 or np.rad2deg(remainig_phase) > 359)
        # num_calibrated = 0

        # while not calibrated and num_calibrated < MAX_RETRIES:
        #     remainig_phase = check_loopback(usrp, tx_streamer, rx_streamer,
        #                                     phase_corr=phase_corr, at_time=begin_time+(4*(num_calibrated+1))*cmd_time)
        #     logger.debug(
        #         f"Remaining phase is {np.rad2deg(remainig_phase)} degrees.")
        #     calibrated = (np.rad2deg(remainig_phase) <
        #                   1 or np.rad2deg(remainig_phase) > 359)
        #     pll_rx_phase = measure_pll(
        #         usrp, rx_streamer, at_time=get_current_time(usrp)+2)
        #     if not calibrated:
        #         phase_corr -= remainig_phase
        #         logger.debug("Adjusting phase and retrying.")
        #         num_calibrated += 1

        # if num_calibrated >= MAX_RETRIES:
        #     logger.error("Could not calibrate")

        print("DONE")

        quit_event = threading.Event()
        start_time += cmd_time + margin
        tx_thr, tx_meta_thr = tx_phase_coh(usrp, tx_streamer, quit_event, phase_corr=(pll_rx_phase - tx_rx_phase),
                                           at_time=start_time)

    except KeyboardInterrupt:

        # Interrupt and join the threads

        logger.debug("Sending signal to stop!")

        quit_event.set()

        # wait till finished before closing of

        if tx_thr:
            tx_thr.join()
        if tx_meta_thr:
            tx_meta_thr.join()

    finally:

        socket.close()
        context.term()
        time.sleep(0.1) # give it some time to close

        sys.exit(130)

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

    # threads.append(tx_thread)  # tx_thread.start()

    # tx_thread.setName("TX_thread")  # threads.append(rx_thread)  # rx_thread.start()

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
