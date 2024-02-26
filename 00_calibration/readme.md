# Calibration Procedure

- ⬛ PLL Phase Stability Test
  * ☑️ PLL Phase when clocked from the same Octoclock
  * ⬛ PLL Phase when clocked from different Octoclock
- ⬛ USRP Phase Stability Test   
  * ☑️ USRP CH0-CH1 Phase stability
  * ⬛ USRP0 CH0 USRP1 CH0 Phase stability
- ⬛ PLL-USRP Sync
  * ⬛ PLL-RX CH0 Phase stability
- ⬛ USRP Loopback Sync
  * ⬛ TX CH0-RX CH0 Phase stability
- ⬛ USRP Ref Sync
  * ⬛ PLL + loopback



## PLL Phase Stability Test

### PLL Phase when clocked from the same Octoclock

| Parameter | Value |
|-|-|
|Start time | 22/02/2024 14:16|
|Stop time | 22/02/2024 14:20|
|PLL Frequency|920MHz|


![PLL-PLL-phase](data/PLL-PLL-phase-plot.png)


### PLL Phase when clocked from different Octoclock

## USRP Phase stability

### USRP CH0-CH1 Phase stability

| Parameter | Value |
|-|-|
|Start time | 22/02/2024 14:25|
|Stop time | 22/02/2024 14:30|
|PLL Frequency|920MHz|

```python
python3 tx_waveforms.py -w const -f 910E6 -c 0 1 --wave-freq 0  --gain 50 --wave-ampl 1.0 -d 600
```

![CH0-CH1](data/CH0-CH1-plot.png)

## USRP0 CH0 USRP1 CH0 Phase stability

## PLL-USRP Sync

### PLL-RX CH0 Phase stability

Proecure:
Where you want to store the phase values:
```python
python3 sub.py 192.108.0.222
```

Start script on the tile:
```python
python3 usrp-phase-stab.py
```

Plot phase on "server"
```python
python3 plot-phase.py
```

| Parameter | Value |
|-|-|
|Start time | 22/02/2024 14:42|
|Stop time | 22/02/2024 14:30|
|PLL Frequency|920MHz|


## USRP Loopback Sync

## USRP Ref Sync

