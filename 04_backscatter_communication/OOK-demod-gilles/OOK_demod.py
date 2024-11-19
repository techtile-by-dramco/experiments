# %% %matplotlib notebook

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, find_peaks, decimate

import numpy as np
from scipy.signal import butter, sosfilt

def bandpass_filter_and_downconvert(iq_samples, sampling_rate, carrier_freq, bandwidth):
    """
    Bandpass filter complex-valued IQ samples and downconvert to baseband.
    
    Parameters:
        iq_samples (numpy.ndarray): Complex-valued IQ samples.
        sampling_rate (float): Sampling rate of the IQ samples in Hz.
        carrier_freq (float): Carrier frequency of the signal in Hz.
        bandwidth (float): Bandwidth of the filter in Hz.
    
    Returns:
        numpy.ndarray: Baseband IQ samples.
    """
    # Calculate the normalized frequency range for the filter
    nyquist_rate = sampling_rate / 2
    low_cutoff = (carrier_freq - bandwidth / 2) / nyquist_rate
    high_cutoff = (carrier_freq + bandwidth / 2) / nyquist_rate

    # Design a bandpass filter using a second-order sections (SOS) format
    sos = butter(N=8, Wn=[low_cutoff, high_cutoff], btype='bandpass', output='sos')

    # Apply the bandpass filter to the IQ samples
    filtered_samples = sosfilt(sos, iq_samples)

    # Downconvert the signal to baseband
    t = np.arange(len(filtered_samples)) / sampling_rate
    downconverted_samples = filtered_samples * np.exp(-2j * np.pi * carrier_freq * t)

    return downconverted_samples

def read_iq_samples(filename, count=-1):
    return np.fromfile(filename, count=count, dtype=np.complex64)

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return lfilter(b, a, data)

def downconvert(data, carrier_freq, fs):
    t = np.arange(len(data)) / fs
    return data * np.exp(-2j * np.pi * carrier_freq * t)

def decimate_signal(y, decimation_factor):

    remaining_dec = decimation_factor

    MAX_Q = 10

    while remaining_dec > 1:
        if remaining_dec < MAX_Q:
            q = remaining_dec
        else:
            q = MAX_Q  # max decimation is 13 https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.decimate.html
        y = decimate(y, q)
        assert remaining_dec % q == 0, f"Decimation factor should be divisible by {q}"
        remaining_dec = remaining_dec//q
    return y

def detect_signal(data, threshold):
    return (np.abs(data) > threshold).astype(int)

def find_preamble(data, preamble_bits):
    preamble_pattern = np.tile([0, 1], preamble_bits // 2)
    preamble_length = len(preamble_pattern)
    for i in range(len(data) - preamble_length):
        if np.array_equal(data[i:i + preamble_length], preamble_pattern):
            return i
    return None

def visualize_signals(iq_samples, filtered_signal, baseband_signal, detected_signal, fs, decimation_factor):
    t_original = np.arange(len(iq_samples)) / fs
    t_decimated = np.arange(len(detected_signal)) / (fs / decimation_factor)

    plt.figure(figsize=(12, 10))

    # Plot raw IQ samples
    plt.subplot(4, 1, 1)
    plt.plot(t_original, np.real(iq_samples), label='I (Real)', alpha=0.7)
    plt.plot(t_original, np.imag(iq_samples), label='Q (Imag)', alpha=0.7)
    plt.title("Raw IQ Samples")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.legend()

    # Plot filtered signal
    plt.subplot(4, 1, 2)
    plt.plot(t_original, np.abs(filtered_signal), label='Filtered Signal')
    plt.title("Bandpass Filtered Signal")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.legend()

    # Plot baseband signal
    plt.subplot(4, 1, 3)
    plt.plot(t_original[:len(baseband_signal)], np.abs(baseband_signal), label='Baseband Signal')
    plt.title("Baseband Signal")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.legend()

    # Plot detected OOK signal
    plt.subplot(4, 1, 4)
    plt.step(t_decimated, detected_signal, where='post', label='Detected OOK Signal')
    plt.title("Detected OOK Signal")
    plt.xlabel("Time (s)")
    plt.ylabel("Detected Bit")
    plt.legend()

    plt.tight_layout()
    plt.show()

def full_cross_correlation(arr, seq):
    # Full cross-correlation between the two arrays
    last_i = len(arr) - len(seq)

    corr = np.zeros(last_i)
    for i in range(last_i):
        samples = arr[i : i + len(seq)]
        samples = samples - np.mean(samples)
        corr[i] = np.sum(samples * seq) / np.sum(np.abs(samples))

    return corr

def read_bin_to_seq(file_path, binary=False):
    # Open the file and read its contents
    with open(file_path, "r") as file:
        # Read the file contents and strip any whitespace or newline characters
        binary_string = file.read().strip()

    # Convert the string into a list of integers (0s and 1s)
    binary_list = [int(char) for char in binary_string if char in "01"]

    if not binary:
        res_list = [-1 if b==0 else 1 for b in binary_list]
    else:
        res_list = binary_list
    return res_list

# %%
# Parameters
filename = "distance2.iq"  # IQ samples from GNURADIO, complex64 format
fs = 2e6
baudrate = 1000            # baudrate backscatter
bandwidth = 2*baudrate     # bandwidth low pass
preamble_bits = 80
FFT_SIZE = 2048*32

samples_per_bit = int(fs / baudrate)
decimation_factor = samples_per_bit // 10  # Decimate to oversampling

samples_per_symb = samples_per_bit // decimation_factor

NUM_AVG = 1600

iq_samples = read_iq_samples(filename, count=FFT_SIZE * NUM_AVG)  # read samples

plt.figure(figsize=(12, 10))
plt.subplot(6, 1, 1)

AVG_PSD = np.asarray([0]*FFT_SIZE, dtype=np.float64)
waterfall = np.zeros((NUM_AVG, FFT_SIZE))
for i, iq in enumerate(np.split(iq_samples, NUM_AVG)):
    AVG_PSD += np.abs(np.fft.fft(iq)) ** 2 / (FFT_SIZE * fs)
    waterfall[i, :] = np.abs(np.fft.fft(iq)) ** 2 / (FFT_SIZE * fs)


AVG_PSD /= NUM_AVG
PSD_log = 10.0 * np.log10(AVG_PSD)
PSD_shifted = np.fft.fftshift(PSD_log)


waterfall_dB = np.fft.fftshift(10.0 * np.log10(waterfall), axes=-1)

plt.figure()
plt.imshow(waterfall_dB)
plt.show()

f = np.arange(fs/-2.0, fs/2.0, fs/FFT_SIZE) # start, stop, step

plt.plot(f, PSD_shifted)
plt.xlabel("Frequency [Hz]")
plt.ylabel("Magnitude [dB]")

peaks, _ = find_peaks(PSD_shifted, height=-120, distance=FFT_SIZE/5)

sorted_idx = np.argsort(PSD_shifted[peaks])[::1]
sorted_peaks = peaks[sorted_idx]

for p in (sorted_peaks[1], sorted_peaks[2]):
    plt.scatter(f[p], PSD_shifted[p])
    print(f[p])
    print(f"Resolution {fs/FFT_SIZE:.2f} Hz")

plt.grid(True)

f_1 = f[sorted_peaks[1]]
f_2 = f[sorted_peaks[2]]

# give the right carrier freq
fc =  f_1 if f_1 > 0 else f_2

filtered_signal = bandpass_filter(
    iq_samples, fc - bandwidth / 2, fc + bandwidth / 2, fs
) 


waterfall = np.zeros((NUM_AVG, FFT_SIZE))
for i, iq in enumerate(np.split(filtered_signal, NUM_AVG)):
    waterfall[i, :] = np.abs(np.fft.fft(iq)) ** 2 / (FFT_SIZE * fs)

waterfall_dB = np.fft.fftshift(10.0 * np.log10(waterfall), axes=-1)

plt.figure()
plt.imshow(waterfall_dB)
plt.show()

filtered_signal /= np.max(np.abs(filtered_signal)) # scale so max = 1

plt.subplot(6, 1, 2)
FFT_SIZE = 1024
AVG_PSD = np.asarray([0] * FFT_SIZE, dtype=np.float64)
NUM_TIMES = len(filtered_signal) // FFT_SIZE
for iq in np.split(filtered_signal[: int(NUM_TIMES * FFT_SIZE)], NUM_TIMES):
    AVG_PSD += np.abs(np.fft.fft(iq)) ** 2 / (FFT_SIZE * fs)

AVG_PSD /= NUM_AVG
PSD_log = 10.0 * np.log10(AVG_PSD)
PSD_shifted = np.fft.fftshift(PSD_log)

f = np.arange(fs / -2.0, fs / 2.0, fs / FFT_SIZE)  # start, stop, step

plt.plot(f, PSD_shifted)
plt.xlabel("Frequency [Hz]")
plt.ylabel("Magnitude [dB]")

plt.grid(True)

baseband_signal = downconvert(filtered_signal, fc, fs) #downconvert to baseband

plt.subplot(6, 1, 3)
FFT_SIZE = 1024
AVG_PSD = np.asarray([0] * FFT_SIZE, dtype=np.float64)
NUM_TIMES = len(baseband_signal) // FFT_SIZE
for iq in np.split(baseband_signal[: int(NUM_TIMES * FFT_SIZE)], NUM_TIMES):
    AVG_PSD += np.abs(np.fft.fft(iq)) ** 2 / (FFT_SIZE * fs)

AVG_PSD /= NUM_AVG
PSD_log = 10.0 * np.log10(AVG_PSD)
PSD_shifted = np.fft.fftshift(PSD_log)

f = np.arange(fs / -2.0, fs / 2.0, fs / FFT_SIZE)  # start, stop, step

plt.plot(f, PSD_shifted)
plt.xlabel("Frequency [Hz]")
plt.ylabel("Magnitude [dB]")

plt.grid(True)

decimated_signal = decimate_signal(baseband_signal, decimation_factor) #decimate to reduce samples

plt.subplot(6, 1, 4)
new_fs = fs / decimation_factor

FFT_SIZE = 1024
AVG_PSD = np.asarray([0] * FFT_SIZE, dtype=np.float64)
NUM_TIMES = len(decimated_signal) // FFT_SIZE
for iq in np.split(decimated_signal[:int(NUM_TIMES*FFT_SIZE)], NUM_TIMES):
    AVG_PSD += np.abs(np.fft.fft(iq)) ** 2 / (FFT_SIZE * new_fs)

AVG_PSD /= NUM_AVG
PSD_log = 10.0 * np.log10(AVG_PSD)
PSD_shifted = np.fft.fftshift(PSD_log)

f = np.arange(new_fs / -2.0, new_fs / 2.0, new_fs / FFT_SIZE)  # start, stop, step

plt.plot(f, PSD_shifted)
plt.xlabel("Frequency [Hz]")
plt.ylabel("Magnitude [dB]")

plt.grid(True)

ax = plt.subplot(6, 1, 5)
iq_power = np.abs(decimated_signal) ** 2
plt.plot(iq_power)

# %%
# Example usage
file_path = 'pseudorandombinarysequence.txt'
print(len(read_bin_to_seq(file_path)))
total_sequence = read_bin_to_seq(file_path)
sequence = total_sequence[:100]

# preamble = np.asarray(
#     [[1] * samples_per_symb + [-1] * samples_per_symb] * 40
# ).flatten()


oversampled_sequence = np.repeat(sequence, samples_per_symb)

# Example usage
# print(len(iq_power))
# print(len(oversampled_sequence))

#
# print(oversampled_sequence)
correlation_result_full = full_cross_correlation(
    iq_power, oversampled_sequence)

start_idx = np.argmax(correlation_result_full)

plt.figure()
plt.subplot(2,1,1)
plt.plot(iq_power)
plt.subplot(2, 1, 2)
plt.scatter(start_idx, correlation_result_full[start_idx])
plt.plot(correlation_result_full)
plt.show()


# %%
# now we need to extract the positive power and negative power
over_sampled_preamble = np.repeat(sequence[:250], samples_per_symb)

signal = iq_power[start_idx:]

signal_preamble = signal[:len(over_sampled_preamble)]

zero_power = np.median(signal_preamble[over_sampled_preamble==-1])
one_power = np.median(signal_preamble[over_sampled_preamble==1])

threshold = (one_power - zero_power) / 2.0

R = len(signal) // samples_per_symb

signal = signal[: int(R * samples_per_symb)]

reshaped_data = signal.reshape(-1, samples_per_symb)

num_symb, _ = reshaped_data.shape

# %%

interval_len = 1000
total_symb = (num_symb // interval_len) * interval_len


num_intervals = total_symb// interval_len


demod = np.zeros(total_symb)
thresholds = [0] * num_intervals

# lets start from the beginning, including the preamble #TODO change this behavior
for i in range(num_intervals):
    thresholds[i] = threshold
    start_i = i*interval_len
    end_i = start_i+interval_len
    samples = reshaped_data[start_i:end_i, :]

    avg_signal = samples.mean(axis=1)

    demod_interval = np.zeros_like(avg_signal)
    demod_interval[avg_signal > threshold] = 1.0

    demod[start_i:end_i] = demod_interval

    # now that we have demodulated the signal, let re-compute the zero and one power

    # update threshold with new data
    zero_power = np.median(avg_signal[demod_interval == 0]) #here it is zero as per above, instead of -1 above
    one_power = np.median(avg_signal[demod_interval == 1])
    new_threshold = (one_power - zero_power) / 2.0

    threshold = 0.1*threshold + 0.9*new_threshold


# Compute the mean along axis 1 (row-wise average)
# avg_signal = reshaped_data.mean(axis=1)


# demod[avg_signal > threshold] = 1.0
# %%
plt.figure()
plt.plot(thresholds)
plt.show()
# %%

oversampled_sequence_bin = [0 if ui == -1 else 1 for ui in oversampled_sequence]

sequence_bin = oversampled_sequence_bin[::samples_per_symb]


# %matplotlib widget

plt.figure()
plt.hlines(y=zero_power, xmin=0, xmax=len(signal_preamble), ls="--")
plt.hlines(y=one_power, xmin=0, xmax=len(signal_preamble), ls="--")
plt.hlines(y=threshold, xmin=0, xmax=len(signal_preamble), ls="--")
plt.plot(signal_preamble)
plt.show()


# plt.figure()
# plt.plot(demod[: len(oversampled_sequence_bin)], label="demod")
# plt.plot(oversampled_sequence_bin, label="sequence")
# plt.legend()
# plt.show()

sequence_bin_full = read_bin_to_seq(file_path, binary=True)
plt.figure()
plt.plot(demod[:1000], label="demod", linestyle="None", marker="o")
plt.plot(sequence_bin_full[:1000], label="sequence", linestyle="None", marker="o")
plt.legend()
plt.show()


correct_symb = [
    1 if a == b else 0 for a, b in zip(demod[:1000], sequence_bin_full[:1000])
]
ber = 1 - (np.sum(correct_symb) / len(correct_symb))

plt.figure()
plt.plot(correct_symb[:1000], linestyle="None", marker="o")
plt.show()
print(ber)

print("done")

# %%
