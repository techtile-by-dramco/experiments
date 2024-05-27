#!/bin/bash
gnome-terminal -- /bin/sh -c 'sshpass -p LookVogelDomPot229 ssh techtile@192.108.0.1 "ssh pi@rpi-t02.local && ls && exec bash"; exec bash'
# gnome-terminal -e -- "bash -c 'sshpass -p LookVogelDomPot229 ssh techtile@192.108.0.1' && ssh pi@rpi-t02.local" | gnome-terminal -e "bash -c 'sshpass -p LookVogelDomPot229 ssh techtile@192.108.0.1' && ssh pi@rpi-t03.local" |  gnome-terminal -e "bash -c 'sshpass -p LookVogelDomPot229 ssh techtile@192.108.0.1' && ssh pi@rpi-t04.local"


sshpass -p LookVogelDomPot229 ssh techtile@192.108.0.1
ssh pi@rpi-t04.local
cd experiments/00_calibration/002_repeated_setup/