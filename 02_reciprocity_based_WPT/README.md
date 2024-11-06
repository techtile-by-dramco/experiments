# Reciprocity-based WPT DL beamforming

Reciprocity-based beamforming is a technique used in wireless communication systems, particularly in the context of time-division duplexing (TDD) systems, to simplify the calibration and implementation of beamforming. It relies on the principle of reciprocity, which states that the channel response between two antennas at the transmitter and receiver is the same (or very similar) when the roles of the transmitter and receiver are reversed. In other words, if you transmit a signal from antenna A to antenna B and measure the channel response, it should be nearly identical when you transmit from B to A.

## Folder structure


| folder name | Description |
|--|--|
| ansible| all yml files to start/stop an experiment |
| client| all files for the RPIs |
| data| |
| processing| all files in post-processing and plotting incl requirements.txt |
| server| files to be run centrally, e.g., record-measurement, rover, sync-server,... |



## Experiment Description and Procedure

All scripts are run in the experiment folder, unless mentioned otherwise.

0. Enable Techtile VPN
    - On your VM in the home dir: `./start_vpn.sh`

1. Start the Qualisys system and start the script on the Qualisys server.

```bash
# on Qualisys server
python Python_Stream_QTM_to_ZMQ\python_qualisys_streamQTM_to_ZMQ.py
```

2. Start the server. Change the `<wait seconds before sending START>` and `<NUM SUBSCRIBERS>` to your own configuration. Know that `<NUM SUBSCRIBERS>`  contains both the RPIs (USRPs) and the pilot and rover. Example: `python ./server/sync_server.py 2 42` waits for 42 subscribers, after receiving `42` messages, it sends a `start` after `2` seconds.

**TODO** start sync server auto in VM and distribute `server-ip` to all hosts.

```bash
# on VM
python ./server/sync_server.py <wait seconds before sending START> <NUM SUBSCRIBERS>
```

4. On the Qualisys server (or where the serial connection of the rover is), start the rover script. The rover waits now till a go from the server (change the IP in the file if needed). After which, it waits 60 seconds before moving, to be sure the reciprocity calibration is performed.

```bash
# on Qualisys server
python ./server/ACRO_control_functions.py
```

5. Run the RPIs from the ansible (clone it), assuming in same root dir as the experiments folder: 

```bash
# on VM
cd $HOME/ansible
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory/hosts.yaml ../experiments/02_reciprocity_based_WPT/ansible/run-DL-WPT.yml -e tiles=ceiling -e bf="bf"
```

Note, everything should be included in the ansible file in later stages.

### Interesting captures


#### 20241105202156

BF with TX gain of 70dB
heatmap-dBm             |  heatmap-nW
:-------------------------:|:-------------------------:
![heatmap-dBm](https://github.com/techtile-by-dramco/experiments/blob/74e286ac5447069129e0acbe486fbcd957288f2b/02_reciprocity_based_WPT/results/20241105202156/heatmap-dBm.png)  |  ![heatmap-nW](https://github.com/techtile-by-dramco/experiments/blob/74e286ac5447069129e0acbe486fbcd957288f2b/02_reciprocity_based_WPT/results/20241105202156/heatmap-nW.png)






