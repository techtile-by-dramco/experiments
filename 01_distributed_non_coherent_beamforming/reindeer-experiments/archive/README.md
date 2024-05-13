# Reindeer experiments

❗❗ script should be exectuted in Python on LINUX server

▶️ First test exectuted with vitual machine (Jarne)

## Transmitter side

### 1️⃣ Equipment
- Techtile base infrastructure N tile with RPI + USRP + PSU
- Max. 280 path antennas (917 MHz) can be used for these measurements.
- (PPS and 10 MHz are not used, thus no frequency synchronisation)

### 2️⃣ Controlling Techtile transmitters (non coherent)

❗❗ Change name of the scripts

Start transmitters
```
ansible-playbook -i inventory/hosts.yaml start_waveform.yaml -e "tiles=walls" -e "gain=100"
```
Stop transmitters
```
ansible-playbook -i inventory/hosts.yaml kill-transmitter.yaml -e tiles=walls"
```

## Receiver side

The following image provides a setup overview, consisting of the Qualisys system for determining the location and the receiver antenna. The scope in the background receives the RF signals and determines the received power.

<!-- TODO <img src="images/setup-photo-1.jpg" height="300"> -->

More information of the receiver, see following requirements

### 1️⃣ Equipment at the mobile receiver
- Qualisys markers for location
- Part 1: Measurement of RF levels (spectrum)
  - Receiver device --> Tektronix MSO64B
  - Receive antenna --> 917 MHz dipole antenna
- Part 2: Measuremnt harvested DC energy (NXP harverster)
  - Energy profiler [firmware/hardware files](https://github.com/techtile-by-dramco/END-design/tree/main/00-END-EF-Profiler)
  - Power bank/battery for energy profiler
  - BLE Adv. receiver board 

### 2️⃣ RSS script (calculate receive power [dBm])

Communicate with the oscilloscope and apply Parseval’s Theorem of Fourier Transform.
- [example script only peaks](https://github.com/techtile-by-dramco/experiments/blob/main/examples/read_MSO6_peaks_only.py) combines only spectral peaks

### 3️⃣ Script to get location in Techtile
The location will be determined via Qualisys system. 
- Qualisys system running on remote computer publishing ZeroMQ data.
- Running ZeroMQ script --> broadcasting 'timestamp' + 'xyz' location

## Combined to perform measurements

Script ... combines following scripts:
- TX Ansible instructions to control Techtile transmitters
- RX **Location script**
- RX **RSS oscilloscope script**
- RX **Energy profiler data**

## Experiment details

Tiles of the ceiling are involved in following measurements.

### 1️⃣ Transmit signals with exactly the same frequency

| Raspberry pi/usrp script | Asnible script |
|-|-|
| [script](https://github.com/techtile-by-dramco/ansible/blob/main/src/client/tx_waveforms_random_phase.py) | ... |

Measurement settings
- gain 70
- fixed frequency 920 MHz

### 2️⃣ Transmit signals with exactly the same frequency and change phase randomly

### 3️⃣ Random beamforming


## Results

<!-- | Gain | USRP TX power (per channel) | # active antennas | Total TX power | Average measured RX power | Link to plot |
|-|-|-|-|-|-|
| 100 | 18 dBm | 112 | 38.5 dBm | -4.3 dBm | [link plot gain 100](https://techtile-by-dramco.github.io/experiments/01_distributed_non_coherent_beamforming/plot/1709111155_gain_100.html)
| 80 | 13.4 dBm | 112 | 33.9 dBm | -10.8 dBm | [link plot gain 80](https://techtile-by-dramco.github.io/experiments/01_distributed_non_coherent_beamforming/plot/1709111890_gain_80.html)
| 65 | -0.4 dBm | 112 | 20.1 dBm | -25.5 dBm | [link plot gain 65](https://techtile-by-dramco.github.io/experiments/01_distributed_non_coherent_beamforming/plot/1709112625_gain_65.html) -->




