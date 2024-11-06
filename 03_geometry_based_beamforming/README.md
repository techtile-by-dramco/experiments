# Geometry-based beamforming

Geometry-based beamforming is a technique used in wireless communication systems in massive MIMO technologies, to enhance the performance of directional communication and wireless power transfer links. It leverages the spatial characteristics of the wireless channel to optimize the transmission and reception of signals between a contact service points and the energy neurtal devices (END).

In contrast to experiments in 02, here the phase is not determined by an uplink pilot, but simulated based on the known position of the END (target device).

## Ansible

```sh
ansible-playbook -i inventory/hosts.yaml "../experiments/03_geometry_based_beamforming/ansible/run-DL-WPT.yml" -e tiles=ceiling
```

### Interesting captures


#### 20241106081231

Friis based DL transmission
