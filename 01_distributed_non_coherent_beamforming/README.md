# Distrubuted non-coherent beamforming

Distributed non-coherent beamforming is a technique used in wireless communication and signal processing where multiple transmitters or antennas collaborate to transmit a signal without precise phase synchronization or coherent processing. In non-coherent beamforming, the individual transmitters or antennas do not need to have perfect knowledge of each other's phases or timing. This is in contrast to coherent beamforming, where the phase and timing of the signals from different transmitters are carefully synchronized to maximize constructive interference.

## Experiments

### 1️⃣ Initial experiments

The initial experiments were conducted using the two walls from Techtile and the acoustic setup to determine the antenna location.

**Purpose**
* Test of Techtile infrastructure
* Get idea of power levels that could be received related to the USRP transmission gain of the TX antennas

### 2️⃣ Reindeer experiments

The reindeer experiments 4aa should investigate how the END devices could capture there initial energy.

**Purpose**
* Best approach to power ENDs during initial access phase
* Compare different signalling methodes
* Sensitivity level to start up the harvester and provide backscatter communication
* Behaviour of NXP harvester to these non coherent signals


## Mapping USRP gain to output power (Gain calibration)

| USRP Gain [dB] | 100 | 95 | 90 | 85 | 80 | 75 | 70 | 65 | 60 | 55 |
|-|-|-|-|-|-|-|-|-|-|-|
| Output power [dBm] |  18.2   |  18.0  |  18.4  |  17.4  |  13.4  |  9.1  |  4.6  |  -0.4  |  -5.6  |  -10.8  |

| USRP Gain [dB] | 50 | 45 | 40 | 35 | 30 | 25 | 20 | 15 | 10 | 5 | 0 |
|-|-|-|-|-|-|-|-|-|-|-|-|
| Output power [dBm] |  -15.7  |  -20.8  |  -26.4  |  -30.4  |  -37.0  |  -42.5  |  -46.5  |  -51.3  |  -56.3  |  -61.1  |  -67.4  |
