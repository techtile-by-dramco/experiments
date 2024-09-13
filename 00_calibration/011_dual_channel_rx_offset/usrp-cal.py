import logging
import os
import socket
import sys
import threading
import time
from datetime import datetime, timedelta

import numpy as np
import uhd
import yaml

from scipy import signal

CMD_DELAY = 0.05  # set a 50mS delay in commands
# default values which will be overwritten by the conf YML
RX_TX_SAME_CHANNEL = True  # if loopback is done from one channel to the other channel
CLOCK_TIMEOUT = 1000  # 1000mS timeout for external clock locking
INIT_DELAY = 0.2  # 200ms initial delay before transmit
RATE = 250e3
LOOPBACK_TX_GAIN = 70  # empirical determined
RX_GAIN = 22  # empirical determined 22 without splitter, 27 with splitter
CAPTURE_TIME = 10
# server_ip = "10.128.52.53"
meas_id = 0
exp_id = 0
gains_bash = []
results = []


with open(os.path.join(os.path.dirname(__file__), "cal-settings.yml"), "r") as file:
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
connected_to_server = False
begin_time = 2.0
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
logger.addHandler(console)
formatter = LogFormatter(
    fmt="[%(asctime)s] [%(levelname)s] (%(threadName)-10s) %(message)s"
)
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
HOSTNAME = socket.gethostname()[4:]
file_open = False
server_ip = None  # populated by settings.yml
from scipy.signal import butter, sosfilt


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = butter(order, [low, high], analog=False, btype="band", output="sos")
    return sos


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    sos = butter_bandpass(lowcut, highcut, fs, order=order)
    y = sosfilt(sos, data)
    return y


def rx_ref(
    usrp, rx_streamer, quit_event, phase_to_compensate, duration, res, start_time=None
):
    # https://files.ettus.com/manual/page_sync.html#sync_phase_cordics
    # The CORDICs are reset at each start-of-burst command, so users should ensure that every start-of-burst also has a time spec set.
    logger.debug(f"GAIN IS CH0: {usrp.get_rx_gain(0)} CH1: {usrp.get_rx_gain(1)}")

    global results
    num_channels = rx_streamer.get_num_channels()
    max_samps_per_packet = rx_streamer.get_max_num_samps()
    iq_data = np.empty((num_channels, int(duration * RATE * 2)), dtype=np.complex64)
    # Make a rx buffer
    # TODO: The C++ code uses rx_cpu type here. Do we want to use that to set dtype?
    # recv_buffer = np.zeros((num_channels, min([1000 * max_samps_per_packet, int(duration * RATE * 2)])),
    #                        dtype=np.complex64, )\
    recv_buffer = np.zeros((num_channels, max_samps_per_packet), dtype=np.complex64)
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
            usrp.get_time_now().get_real_secs() + INIT_DELAY + 0.1
        )
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
                        iq_data[:, num_rx : num_rx + num_rx_i] = samples
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
            uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont)
        )
        samples = iq_data[:, int(RATE // 10) : num_rx]
        results = samples
        avg_angles = [0.0, 0.0]
        var_angles = [0.0, 0.0]
        f0 = 1e3
        cutoff = 500
        fs = RATE
        lowcut = f0 - cutoff
        highcut = f0 + cutoff
        # results = np.zeros_like(samples, dtype=float)
        for ch in [0, 1]:
            y_re = butter_bandpass_filter(
                np.real(samples[ch, :]), lowcut, highcut, fs, order=9
            )
            y_imag = butter_bandpass_filter(
                np.imag(samples[ch, :]), lowcut, highcut, fs, order=9
            )
            angle_unwrapped = np.unwrap(np.angle(y_re + 1j * y_imag))
            t = np.arange(0, len(y_re)) * (1 / fs)
            from scipy import stats

            lin_regr = stats.linregress(t, angle_unwrapped)
            print(lin_regr.slope)
            phase_rad = angle_unwrapped - lin_regr.slope * t
            # store phases
            # results[ch, :] = phase_rad
            avg_phase = np.mean(phase_rad)
            var_angles[ch] = np.var(phase_rad)
            avg_angles[ch] = avg_phase
            logger.debug(f"Frequency offset CH{ch}:{lin_regr.slope/(2*np.pi):.4f}")
            logger.debug(
                f"Intercept (phase) degrees CH{ch}:{np.rad2deg(lin_regr.intercept):.4f}"
            )
        # np.angle(np.sum(np.exp(np.angle(samples)*1j), axis=1)) # circular mean https://en.wikipedia.org/wiki/Circular_mean
        # avg_angles = circmean(np.angle(samples[:, int(RATE//10):]), axis=1)
        # var_angles = np.var(np.angle(samples[:, int(RATE//10):]), axis=1)
        # min_angles = np.min(np.angle(samples[:, int(RATE // 10) :]), axis=1)
        # max_angles = np.max(np.angle(samples[:, int(RATE // 10) :]), axis=1)
        # median_angles0 = circmedian(np.angle(samples[0, int(RATE//10):]))
        # median_angles1 = circmedian(np.angle(samples[1, int(RATE//10):]))
        phase_to_compensate.extend(avg_angles)
        avg_ampl = np.mean(np.abs(samples), axis=1)
        var_ampl = np.var(np.abs(samples), axis=1)

        max_I = np.max(np.abs(np.real(samples)), axis=1)
        max_Q = np.max(np.abs(np.imag(samples)), axis=1)

        logger.debug(
            f"MAX AMPL IQ CH0: I {max_I[0]:.2f} Q {max_Q[0]:.2f} CH1:I {max_I[1]:.2f} Q {max_Q[1]:.2f}"
        )

        logger.debug(
            f"Angle (mean) CH0:{np.rad2deg(avg_angles[0]):.2f} CH1:{np.rad2deg(avg_angles[1]):.2f}"
        )
        # logger.debug(
        #     f"Angle (median) CH0:{np.rad2deg(median_angles0):.2f} CH1:{np.rad2deg(median_angles1):.2f}")
        # logger.debug(
        #     f"Angle min max CH0:{np.rad2deg(min_angles[0]):.2f} {np.rad2deg(max_angles[0]):.2f} CH1:{np.rad2deg(min_angles[1]):.2f} {np.rad2deg(max_angles[1]):.2f}"
        # )
        logger.debug(f"Angle var CH0:{var_angles[0]:.2f} CH1:{var_angles[1]:.2f}")
        # keep this just below this final stage
        logger.debug(f"Amplitude CH0:{avg_ampl[0]:.2f} CH1:{avg_ampl[1]:.2f}")
        res.extend([var_angles[0], var_angles[1], var_ampl[0], var_ampl[1]])


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
            logger.error("Unable to confirm clock signal locked on board %d", i)
            return False
        else:
            logger.debug("Clock signals are locked")
    return True


def setup_pps(usrp, pps):
    logger.debug("Setting PPS")
    """Setup the PPS source"""
    usrp.set_time_source(pps)
    return True


def print_tune_result(tune_res):
    return (
        "Tune Result:\n    Target RF  Freq: {:.6f} (MHz)\n Actual RF  Freq: {:.6f} (MHz)\n Target DSP Freq: {:.6f} "
        "(MHz)\n "
        "Actual DSP Freq: {:.6f} (MHz)\n".format(
            (tune_res.target_rf_freq / 1e6),
            (tune_res.actual_rf_freq / 1e6),
            (tune_res.target_dsp_freq / 1e6),
            (tune_res.actual_dsp_freq / 1e6),
        )
    )


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
    treq.rf_freq_policy = uhd.types.TuneRequestPolicy(ord("M"))
    treq.dsp_freq_policy = uhd.types.TuneRequestPolicy(ord("M"))
    args = uhd.types.DeviceAddr("mode_n=integer")
    treq.args = args
    rx_freq = freq - 1e3
    rreq = uhd.types.TuneRequest(rx_freq)
    rreq.rf_freq = rx_freq
    rreq.target_freq = rx_freq
    rreq.dsp_freq = 0.0
    rreq.rf_freq_policy = uhd.types.TuneRequestPolicy(ord("M"))
    rreq.dsp_freq_policy = uhd.types.TuneRequestPolicy(ord("M"))
    rreq.args = uhd.types.DeviceAddr("mode_n=fractional")
    for chan in channels:
        logger.debug(print_tune_result(usrp.set_rx_freq(rreq, chan)))
        logger.debug(print_tune_result(usrp.set_tx_freq(treq, chan)))
    while not usrp.get_rx_sensor("lo_locked").to_bool():
        print(".")
        time.sleep(0.01)
    logger.info("RX LO is locked")
    while not usrp.get_tx_sensor("lo_locked").to_bool():
        print(".")
        time.sleep(0.01)
    logger.info("TX LO is locked")


def setup(usrp, server_ip, connect=True):
    rate = RATE
    mcr = 20e6
    assert (
        mcr / rate
    ).is_integer(), f"The masterclock rate {mcr} should be an integer multiple of the sampling rate {rate}"
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
        # NOTE DC offset is enabled
        usrp.set_rx_dc_offset(True, chan)
        usrp.set_rx_bandwidth(rx_bw, chan)
        usrp.set_rx_agc(False, chan)
    # specific settings from loopback/REF PLL
    usrp.set_tx_gain(LOOPBACK_TX_GAIN, LOOPBACK_TX_CH)
    usrp.set_tx_gain(LOOPBACK_TX_GAIN, FREE_TX_CH)
    usrp.set_rx_gain(gains_bash[LOOPBACK_RX_CH], LOOPBACK_RX_CH)
    usrp.set_rx_gain(gains_bash[REF_RX_CH], REF_RX_CH)
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
    logger.info("Setting device timestamp to 0...")
    usrp.set_time_unknown_pps(uhd.types.TimeSpec(0.0))
    logger.debug("[SYNC] Resetting time.")
    logger.info(f"RX GAIN PROFILE CH0: {usrp.get_rx_gain_names(0)}")
    logger.info(f"RX GAIN PROFILE CH1: {usrp.get_rx_gain_names(1)}")
    # we wait 2 seconds to ensure a PPS rising edge occurs and latches the 0.000s value to both USRPs.
    time.sleep(2)
    tune_usrp(usrp, FREQ, channels, at_time=begin_time)
    logger.info(
        f"USRP has been tuned and setup. ({usrp.get_time_now().get_real_secs()})"
    )
    return tx_streamer, rx_streamer


def rx_thread(
    usrp, rx_streamer, quit_event, phase_to_compensate, duration, res, start_time=None
):
    rx_thread = threading.Thread(
        target=rx_ref,
        args=(
            usrp,
            rx_streamer,
            quit_event,
            phase_to_compensate,
            duration,
            res,
            start_time,
        ),
    )
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


def delta(usrp, at_time):
    return at_time - usrp.get_time_now().get_real_secs()


def get_current_time(usrp):
    return usrp.get_time_now().get_real_secs()


def measure_channel_coherence(usrp, rx_streamer, quit_event):
    logger.debug("########### Measure channel coherence ###########")
    phase_to_compensate = []
    res = []
    rx_thr = rx_thread(
        usrp,
        rx_streamer,
        quit_event,
        phase_to_compensate,
        duration=CAPTURE_TIME,
        res=res,
        start_time=None,
    )

    time.sleep(CAPTURE_TIME)
    quit_event.set()

    # wait till both threads are done before proceding
    rx_thr.join()


def parse_arguments():
    import argparse

    global meas_id, gains_bash, exp_id

    # Create the parser
    parser = argparse.ArgumentParser(description="Transmit with phase difference.")

    # Add the --phase argument
    parser.add_argument("--meas", type=int, help="measurement ID", required=True)

    parser.add_argument("--gain", type=int, nargs="+", help="gain_db", required=True)

    parser.add_argument("--exp", type=str, help="exp ID", required=True)

    # Parse the arguments
    args = parser.parse_args()

    # Set the global variable tx_phase to the value of --phase
    meas_id = args.meas

    # Access the gain values
    gains = args.gain

    # Handle cases where either one or two gain values are provided
    if len(gains) == 1:
        gains_bash = [gains[0], gains[0]]
    elif len(gains) == 2:
        gains_bash = gains
        print(f"Gain 1: {gains_bash[0]}, Gain 2: {gains_bash[1]}")
    else:
        print("Error: Too many gain values provided.")

    exp_id = args.exp


def main():
    global meas_id

    parse_arguments()

    file_name = f"data_{HOSTNAME}_{exp_id}_{meas_id}"

    try:
        usrp = uhd.usrp.MultiUSRP("fpga=usrp_b210_fpga_loopback.bin, mode_n=integer")
        logger.info("Using Device: %s", usrp.get_pp_string())
        _, rx_streamer = setup(usrp, server_ip, connect=False)
        quit_event = threading.Event()
        measure_channel_coherence(usrp, rx_streamer, quit_event)
        # results now contain the phases of the two channels
        # store that phase difference to a file
        # phase_diff = results[0, :] - results[1, :]
        print("DONE")
        # downsample to reduce storage space
        # decimated_results = signal.decimate(results, q=100, ftype="fir", axis=-1, zero_phase=True)
        np.save(file_name, results)
    except KeyboardInterrupt:
        # Interrupt and join the threads
        logger.debug("Sending signal to stop!")
        quit_event.set()
    finally:
        time.sleep(0.1)  # give it some time to close
        sys.exit(0)


if __name__ == "__main__":
    main()
