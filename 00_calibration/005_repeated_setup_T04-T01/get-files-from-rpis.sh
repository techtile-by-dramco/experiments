read -p "Enter password: " password


sshpass -p "$password" ssh techtile@192.108.0.1 -t "mkdir -p /storage/gilles/005_repeated_setup_T04-T01/"

sshpass -p "$password" ssh techtile@192.108.0.1 -t "scp pi@rpi-t01.local:~/experiments/00_calibration/005_repeated_setup_T04-T01/data_T01_* /storage/gilles/005_repeated_setup_T04-T01/"
sshpass -p "$password" ssh techtile@192.108.0.1 -t "scp pi@rpi-t04.local:~/experiments/00_calibration/005_repeated_setup_T04-T01/data_T04_* /storage/gilles/005_repeated_setup_T04-T01/"

sshpass -p "$password" scp techtile@192.108.0.1:/storage/gilles/005_repeated_setup_T04-T01/data_T* .
