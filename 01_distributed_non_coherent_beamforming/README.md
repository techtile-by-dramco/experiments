# Distrubuted non-coherent beamforming

Distributed non-coherent beamforming is a technique used in wireless communication and signal processing where multiple transmitters or antennas collaborate to transmit a signal without precise phase synchronization or coherent processing. In non-coherent beamforming, the individual transmitters or antennas do not need to have perfect knowledge of each other's phases or timing. This is in contrast to coherent beamforming, where the phase and timing of the signals from different transmitters are carefully synchronized to maximize constructive interference.

## Transmitter side 
Max. 280 path antennas (917 MHz) can be used for these measurements

Current situation:

ToDo
- **@Gilles** Make script with adaptable gain
- **@Gilles** Gain calibration (gain - tx power (dBm) ratio)
- **@geoffrey @gilles** How changing gain flexible for all USRPs

## Receiver side
Receiver device --> Tektronix MSO64B
Receive antenna --> 917 MHz dipole antenna

### Script the calculates receive power [dBm]
@Gilles where did we placed this script???

### Script that decides location
Location determined via acoustic system (DAQ + specific DAQ Windows PC)
Running ZeroMQ script --> broadcasting 'timestamp' + 'xyz' location
Receiving data via example code [receive location script](https://github.com/techtile-by-dramco/experiments/blob/main/01_distributed_non_coherent_beamforming/rx-loc-zmq.py)
