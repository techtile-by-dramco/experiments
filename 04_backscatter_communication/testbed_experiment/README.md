# Testbed backscatter experiment 🧪

▶️ These experiments are conducted for the H2020 Reindeer project. The main objective here is to collect information about the backscatter uplink Bit Error Rate (BER) and deduce information about the possible uplink speeds. Two scenarios will be tested: (i) the END is placed in a test setup with a quasi uniform power density and (ii) a power spot is created at the backscatter device. The research hypothesis claims that in the latter case, a higher SNR and thus data rate can be acheived with the same hardware.

Results of these experiments will be reported in Experiment 4b: communicationg with energy neutral devices.

## Transmitter side

### 1️⃣ Equipment
- Techtile base infrastructure N tile with RPI + USRP + PSU
- Max. 280 path antennas (917 MHz) can be used for these measurements.
- PPS and 10 MHz required for these measurements????

### 2️⃣ Controlling Techtile ...

#### Experiment details

Tiles of the ceiling and side walls are involved in following measurements.



#### Script locations

| Script name | Info | Location |
|-|-|-|
| Client (RPI) script | Controlling USRP |  |
| Ansible copy files | Copy config.yaml and SCRIPT_NAME.py to all hosts/clients |  |
| Ansible start up | Start up all client scripts |  |
| Measurement script | Control capture EP/scope/location data | [OOK_demod_REINDEER.py](https://github.com/techtile-by-dramco/experiments/blob/main/04_backscatter_communication/testbed_experiment/client/OOK_demod_REINDEER.py) |
| BERT script| Bit error rate tests the incoming bitstream| [BERT.py](https://github.com/techtile-by-dramco/experiments/blob/main/04_backscatter_communication/testbed_experiment/client/BERT.py) ||
|...|||
|...|||



## Receiver side



The following image provides a setup overview, ..


## High level measurement setup

The techtile transceivers should be categorized into two types of implementation. A part of the SDR's should transmit a continuous carrier signal with a random phase (adaptive single-tone?), another part should receive the backscattered signal. \
Proposal:
* ☝️ceiling tiles☝️--> generating the carrier wave to enable backscattering (and/or to provide initial access energy)
* 👈left and right walls👉 --> try to demodulate the signals

> ❗❗Adaptive single-tone signals could potentially cause corrupte messages ❗❗\
>  Specifically, if the received power level is changed during backscatter operartion

### Transmitter side

Transmit carrier signal with random phase: this results in a room with a quasi-uniform power density. The transmitter side determines the center frequency of the received signal.

### END side:

Backscatter the pseudo random binary sequence (found [HERE](https://github.com/techtile-by-dramco/experiments/blob/main/04_backscatter_communication/testbed_experiment/client/pseudorandombinarysequence.txt) |
The signal is a preamble (80 bits) followed by pseudo-random binary sequence of 32848 bits. Long sequence lengths offer more randomness, which stresses the interface more, leading to a higher likelihood of inducing bit-errors. However, they have the disadvantage of taking a longer time to complete the entire sequence, which can be a significant issue at lower bit rates. As a result, it is generally recommended that
short PRBS patterns be used at low bit rates and long PRBS patterns be used at the highest bitrates. The pseudo random bit sequence used in this tests can be foun in ???.
The END side determines the offset frequency, the bit error sequency length and the symbol rate. 


### Receiver side

Each receiver should perform a OOK demodulation of the received signal and perform a BERT. Depending on the distance (SNR influenc) to the transmitter, different BER should be acheived.


OOK_demod_REINDEER.py main goal is to perform an adaptive OOK demodulation and resampling of the received backscatter signal. This is done in a couple of steps:

- STEP 1: Receive the signal by the USRP source. The information of has a frequency offset (f_offset = 512 KHz) away from the center frequency (at  f_carrier = 917 MHz). This signal of interest is received by perform a XLATING FIR filtering (band-pass filter) over frequency shifted information signal.
- STEP 2: Getting the OOK signal (floats) by performing a complex to mag^2 conversion. This signal is weak, so an Automatic Gain Control block is used to amplify the signal. 
- Step 3: Filtering the higher noise out of the signal with a low pass filter and creating a block wave out of the data signal with a threshold detector with hysteresis. The threshold itself is set dynamically by performing a moving average and using that average as the threshold when the received signal is larger than the noise flour. 
- Step 4: the block waves are downsampled and synced to the symbol rate with a Gardner symbol sync. The output with a lower data rate is again made binary by implementing a fixed threshold detector.
- Step 5: The floats are packed, so only 1 bit per sample is used and writen to a binary file with a file sink.

Post-processing is done by BERT.py program, which reads the saved binary file and returns the bitstream as a string of '0's and '1's, checks for the preamble, and compares it to the pseudo-random binary bit sequence, and calculates the BER.

## Perform measurements

## Results






