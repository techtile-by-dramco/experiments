This is to check the different perceived phase differences between 2 USRP rx RF chains.


50 ohm terminators used at RX and TX not in use.
loopback FPGA is used.

synced to 10mhz + pps (with splitter)

# Configuration

ref signal: cable to RF signal generator 920 MHz

Loopback: via switch (loopback FPGA image)

TX/RX B: antenna
RX B: 50ohm terminator

RX A: ref signal
RX/TX A: to scope

10Mz: octoclock (no splitter port 1 and 2)
PPS: splitter to octoclock

# Measurements

## with 50ohm terminators
Timestamp: 20240830114328

## With antennas
Timestamp: 20240902115303

## de-synced PPS
To check the effect of the PPS accuracy, we used 2 different cable lengths (60cm and 8m).

Timestamp:  20240902131719