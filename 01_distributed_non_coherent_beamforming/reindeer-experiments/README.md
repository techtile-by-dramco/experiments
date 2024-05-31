# Reindeer experiments 🧪

▶️ These experiments are conducted for the european Reindeer project. The main objective here is to find out how much energy is available in the Techtile space at initial access for a certain energy neutral device. A subset of tiles is taken to perform the measurements. Three techniques to provide the energy during the initial access phase are compared.

## Transmitter side

### 1️⃣ Equipment
- Techtile base infrastructure N tile with RPI + USRP + PSU
- Max. 280 path antennas (917 MHz) can be used for these measurements.
- PPS and 10 MHz required for these measurements.

### 2️⃣ Controlling Techtile transmitters (non coherent)

#### Experiment details

Tiles of the ceiling are involved in following measurements.

Via this ZMQ [script](https://github.com/techtile-by-dramco/ansible/blob/main/src/server/random_phases_ZMQ.py), the server can take control over client phases and start captures.
- Send "init" --> The server will start all the client scripts.
- Send "start"
  - --> The client script will start the transmission. (Only if client script is active.)
  - --> The server will start logging the 'measurement data'.
- Send "stop" --> Alle clients scripts will be terminated.
- Send "close" --> Close the server script.

#### Script locations

| Script name | Info | Location |
|-|-|-|
| Client (RPI) script | Controlling USRP | [tx_waveforms_random_phase.py](https://github.com/techtile-by-dramco/ansible/blob/main/src/client/tx_waveforms_random_phase.py) |
| Ansible copy files | Copy config.yaml and SCRIPT_NAME.py to all hosts/clients | [copy_client_script.yaml](https://github.com/techtile-by-dramco/ansible/blob/main/experiments/copy_client_script.yaml) |
| Ansible start up | Start up all client scripts | [start_client_script.yaml](https://github.com/techtile-by-dramco/ansible/blob/main/experiments/start_client_script.yaml) |
| Measurement script | Control capture EP/scope/location data | [main.py](https://github.com/techtile-by-dramco/experiments/blob/main/01_distributed_non_coherent_beamforming/reindeer-experiments/server/main.py) |

<!--
❗❗ Change name of the scripts

Start transmitters
```
ansible-playbook -i inventory/hosts.yaml start_waveform.yaml -e "tiles=walls" -e "gain=100"
```
Stop transmitters
```
ansible-playbook -i inventory/hosts.yaml kill-transmitter.yaml -e tiles=walls"
```
-->

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

Server script [server/main.py](https://github.com/techtile-by-dramco/experiments/blob/main/01_distributed_non_coherent_beamforming/reindeer-experiments/server/main.py) supports following features:
- TX Ansible instructions to control Techtile transmitters
- RX **Location script**
- RX **RSS oscilloscope script**
- RX **Energy profiler data**


### 1️⃣ Experiment 4aa PART 1: 🧪 >> Transmit signals with exactly the same frequency << 🧪

#### Purpose
- Proof occurance of dead spots in the room (This is expected, caused by frequency synchronization)
- Measure harvested power with energy profiler

Ceiling tile [A -> G][5 -> 10] could be set by using the 'all' function (in the [config.yaml](https://github.com/techtile-by-dramco/experiments/blob/main/01_distributed_non_coherent_beamforming/reindeer-experiments/config.yaml) file under client/hosts/all).
```
client:
  hosts:
    all:
      freq: 920000000.0
      gain: 70
      channels: [0, 1]
      duration: 3600
```
Measurement settings
- USRP gain 70
- LO frequency 920 MHz
- Duration 3600 seconds (should be sufficient high, otherwize the relative phases between multiple USRPs will change.)

### 2️⃣ Experiment 4aa PART 2: 🧪 >> Transmit signals with exactly the same frequency and change phase randomly << 🧪

Ceiling tile [A -> G][5 -> 10] could be set by using the 'all' function.
```
client:
  hosts:
    all:
      freq: 917000000.0
      gain: 80
      channels: [0, 1]
      duration: 1
```

### 3️⃣ Experiment 4aa PART 3: 🧪 >> Random beamforming << 🧪

Ceiling tile [A -> G][5 -> 10] should be set individually by selecting a different frequency for every tile.
```
client:
  hosts:
    all:
      freq: 917000000.0
      gain: 80
      channels: [0, 1]
      duration: 1
    G05:
      freq: 917000000.0
    G06:
      freq: 917500000.0
```

## Results

<!-- | Gain | USRP TX power (per channel) | # active antennas | Total TX power | Average measured RX power | Link to plot |
|-|-|-|-|-|-|
| 100 | 18 dBm | 112 | 38.5 dBm | -4.3 dBm | [link plot gain 100](https://techtile-by-dramco.github.io/experiments/01_distributed_non_coherent_beamforming/plot/1709111155_gain_100.html)
| 80 | 13.4 dBm | 112 | 33.9 dBm | -10.8 dBm | [link plot gain 80](https://techtile-by-dramco.github.io/experiments/01_distributed_non_coherent_beamforming/plot/1709111890_gain_80.html)
| 65 | -0.4 dBm | 112 | 20.1 dBm | -25.5 dBm | [link plot gain 65](https://techtile-by-dramco.github.io/experiments/01_distributed_non_coherent_beamforming/plot/1709112625_gain_65.html) -->




