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

The MISO backscattering experiments are conducted in the context of the European Reindeer Project. These experiments are described in subsection 4b from D5.X deliverable.

#### 2.1) Experiment 4b PART 1: 🧪 >> Siso Bistatic backscattering << 🧪

<img src="https://github.com/techtile-by-dramco/experiments/blob/main/04_backscatter_communication/figures/Siso_Bistatic_backscattering.jpg" width="200"/>

##### Assumptions
* 📍 Consider one single position for backscatter device in Techtile
* ⚡ Backscatter device is powered with power supply ⚡
  
##### Purpose 
* Measure 📈 BER 📈 related to data rate


#### 2.2) Experiment 4b PART 2: 🧪 >> Carrier suppression with local oscillator << 🧪

<img src="https://github.com/techtile-by-dramco/experiments/blob/main/04_backscatter_communication/figures/Carrier_suppression_lo.jpg" width="200"/>

##### Assumptions
* 📍 Consider one single position for backscatter device in Techtile
* ⚡ Backscatter device is powered with power supply ⚡
  
##### Purpose 
* Measure 📈 BER 📈 related to data rate
* Compare performance with measurement 1 (lower data rate, better SNR?)

##### Experiment hardware and scripts
* Single tone signal transmitted ONE (or more?) USRP(s) --> "tx_waveform.py" script
* MCU firmware should backscatter data using two timers
	* MCU clock speed (Currently 1024 kHz)
	* Two timers
		* ⏱️ One timer for LO ✅ (Currently 512 kHz)
  		* ⏱️ One timer for data rate ✅ (Currently 1000 bps)
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
 	* ❗ ToDo  create new demodulation script '>>NAME<<.py' + ❗ADD FILE LOCATION❗ BERT C.
  	*  GnuRadio file can be found [here](https://github.com/BertCox/EN-device-backscatter/blob/main/gnuradio/receiver/OOK_demod_resample.grc).
  	* Explanation of the script can be found [here](https://github.com/techtile-by-dramco/EN-device-backscatter/blob/main/gnuradio/Demodulation.md).
   	* Testdata can be found on [Sharepoint](https://kuleuven.sharepoint.com/:u:/r/sites/T0002057/Shared%20Documents/General/03_Research/01_Projects/Reindeer/Dataset/20240521_testdataBackscattering/backscatterdata_917MHz_20cm_13dBm?csf=1&web=1&e=IOmhK7) 	
  	* Previous work is located [here](https://github.com/techtile-by-dramco/EN-device-backscatter/tree/main/gnuradio/receiver)

##### Detail experiment desciption

1. Ansible startup TX USRP (transmit carrier wave)
2. Ansible start sampling script for RX USRPs and wait for ZMQ "start_bc_capture" command (write data to >>NAME<<_>>TILE_NR<<.csv)
3. 📧 Server send "start_bc_capture" ZMQ command
4. Start backscatter device data transfer (❗❗is currently not controllable)
5. 📧 Server send "stop_bc_capture" ZMQ command
6. Each RPI saves captured data to >>NAME<<_>>TILE_NR<<.csv
7. Server collect captured CSVs for central processing

#### 2.3) Experiment 4b PART 3: 🧪 >> Carrier suppression with receiver selection << 🧪

<img src="https://github.com/techtile-by-dramco/experiments/blob/main/04_backscatter_communication/figures/Carrier_suppression_receiver_selection.jpg" width="200"/>

❗❗❗ Postponed due to need for coherent operation and power spot formation ❗❗❗

Check status of [experiment 4ac](https://github.com/techtile-by-dramco/experiments/tree/main/02_reciprocity_based_beamforming)
