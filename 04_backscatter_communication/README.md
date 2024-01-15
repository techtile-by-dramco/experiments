# Backscatter communication 📡

Backscatter communication is a wireless communication technique that enables devices to communicate by reflecting or modulating existing radio frequency (RF) signals instead of generating their own signals. This approach is energy-efficient and can be suitable for low-power and low-cost devices, making it advantageous for certain applications like the Internet of Things (IoT). It enables the development of energy-neutral devices due to significantly lower energy requirements compared to powered active transmitters.

## Why backscatter communication in Techtile?

1) The reciprocity based approach seems to be the most suitable and feasible solution to enable coherent beamforming. For this to work, backscatter communication is required. Potential implementation method explained in [experiment 3](https://github.com/techtile-by-dramco/experiments/tree/main/03_geometry_based_beamforming).

2) **Optional** What data rates can be achieved, and is there an advantage to be gained from the radio wave infrastructure in terms of communication speed?


## Backscatter experiments 🧪

### 1) SISO backscattering

Progress: [███████░░░] 70%

Repository [backscatter with EN-device](https://github.com/techtile-by-dramco/EN-device-backscatter) contains the embedded-C code to backscatter wave at a certain local oscillator speed with a certain baudrate speed.
Moreover, it contains demodulator GNU radio code to demodulate current simple ASK backscatter waves.

| Status | Device | Description/remarks | Links | 
|-|-|-|-|
|✔️ | Modulator | Backscattering frames can be easily changed in code | [Link to firmware](https://github.com/techtile-by-dramco/EN-device-backscatter/tree/main/firmware-vscode) |
|⚙️ | Demodulator | **ToDo** work further on demodulator method in GNURadio | [Link to GNU Radio](https://github.com/techtile-by-dramco/EN-device-backscatter/tree/main/gnuradio/receiver) |

Do we need to measure something? 🤔

### 2) MISO backscattering

Progress: [█░░░░░░░░░] 10%

