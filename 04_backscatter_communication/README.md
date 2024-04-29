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



#### Experiment 4b PART 2: Second backscatter measurements idea (>> Carrier suppression with local oscillator <<) 🧪

##### Assumptions
* 📍 Consider one single position for backscatter device in Techtile
* ⚡ Backscatter device is powered with power supply ⚡
  
##### Purpose 
* Measure 📈 BER 📈 related to data rate
* Compare performance with measurement 1 (lower data rate, better SNR?)

##### Detail experiment desciption
* Single tone signal 〰️ transmitted ONE (or more?) USRP(s) --> "tx_waveform.py" script
* MCU firmware should backscatter data using two timers
	* Two timers 
    		* ⏱️ One timer for LO ✅
    		* ⏱️ One timer for data rate ✅
	* ❗ ToDo ❗ Make timers adjustable in real time? UART?? (not so urgent)
* Send bytes
	* No START and/or STOP bits, all bytes sequentially transmitted without delays ✅
	* Send stream of bytes with the following format FIXED DATA !AVG = 0.5! (specifically for preamble) ✅
 	* Preamble (0xAA 2x) + Begin delimiter (0x02) + Data ✅
    	*  📙 Example data 📙
	        *  HEX 0xAA 0xAA 0x02 0x23 0x44 0xFF
	        *  BIN 10101010 10101010 00000010 00100011 01000100 11111111
 * Find firmware experiment 4b part 2 [here](https://github.com/techtile-by-dramco/EN-device-backscatter/tree/main/firmware-vscode-exp-4b-part-2)
 * Try to demodulate signal with multiple receivers
 	* ❗ ToDo  create new demodulation script '>>NAME<<.py' + ❗ADD FILE LOCATION❗
  	* Previous work is located [here](https://github.com/techtile-by-dramco/EN-device-backscatter/tree/main/gnuradio/receiver)





