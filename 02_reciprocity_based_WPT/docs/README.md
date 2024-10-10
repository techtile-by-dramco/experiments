# Reciprocity-based beamforming

Reciprocity-based beamforming is a technique used in wireless communication systems, particularly in the context of time-division duplexing (TDD) systems, to simplify the calibration and implementation of beamforming. It relies on the principle of reciprocity, which states that the channel response between two antennas at the transmitter and receiver is the same (or very similar) when the roles of the transmitter and receiver are reversed. In other words, if you transmit a signal from antenna A to antenna B and measure the channel response, it should be nearly identical when you transmit from B to A.

## The idea

![rbb](https://github.com/techtile-by-dramco/experiments/blob/main/02_reciprocity_based_beamforming/rbb-end-csp-phase-representation.png)


## How to start an experiment


### Start Qualysis

Body: `robot-new`


### 1. Start REF USRP

Start the transmission of the REF USRP to distribute the desired LO frequency.

```bash
uhd_siggen --args 'mode_n=integer' --freq 920e6 --clock-source 'external' --sync 'pps' --const -g 60 --offset 0 -m 0.8
```

### Enable the sync-server: `sync_server.py <delay> <num_subscribers>`

- Change the `server_ip` in `cal-settings.yml` in the client directory to the IP of the "sync-server".
- The `delay` argument is the time the sync server waits to give the start command after getting a connection request of `num_subscribers` USRPs.


### Ansible

```bash
ansible-playbook -i inventory/hosts.yaml experiments/run-DL-WPT.yml -e "tiles=ceiling" -e "bf=bf"
```


##  Experiments

## Robot-based


## CNC-grid-based

### nobf-ceiling-D07-grid-1
```python
x = np.arange(0, 1200, 30) + 25 #np.arange(25, 1200, 300/100) + 25
y = np.arange(0, 1200, 30) + 25
```

Only D07 was transmitting. Stopped almost at the end as the power cable came lose.

