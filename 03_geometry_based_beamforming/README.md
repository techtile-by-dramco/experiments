# Geometry-based beamforming

Geometry-based beamforming is a technique used in wireless communication systems in massive MIMO technologies, to enhance the performance of directional communication and wireless power transfer links. It leverages the spatial characteristics of the wireless channel to optimize the transmission and reception of signals between a contact service points and the energy neurtal devices (END).

In contrast to experiments in 02, here the phase is not determined by an uplink pilot, but simulated based on the known position of the END (target device).

## Ansible

```sh
ansible-playbook -i inventory/hosts.yaml "../experiments/03_geometry_based_beamforming/ansible/run-DL-WPT.yml" -e tiles=ceiling
```


Approach | heatmap-dBm             |  heatmap-uW
:-------------------------:| :-------------------------:|:-------------------------:
Reciprocity | ![heatmap-dBm](https://github.com/techtile-by-dramco/experiments/blob/main/02_reciprocity_based_WPT/results/20241105202156/heatmap-dBm.png)  | ![heatmap-uW](https://github.com/techtile-by-dramco/experiments/blob/main/02_reciprocity_based_WPT/results/20241105202156/heatmap-uW.png)
Friis (ideal) | ![heatmap-dBm](https://github.com/techtile-by-dramco/experiments/blob/main/03_geometry_based_beamforming/031_Friis/results/ideal/heatmap-dBm.png) | ![heatmap-uW](https://github.com/techtile-by-dramco/experiments/blob/main/03_geometry_based_beamforming/031_Friis/results/ideal/heatmap-uW.png)
LoS BF | ![heatmap-dBm](https://github.com/techtile-by-dramco/experiments/blob/main/03_geometry_based_beamforming/031_Friis/results/20241106101220/heatmap-dBm.png) | ![heatmap-uW](https://github.com/techtile-by-dramco/experiments/blob/main/03_geometry_based_beamforming/031_Friis/results/20241106101220/heatmap-uW.png)
SMC | 
