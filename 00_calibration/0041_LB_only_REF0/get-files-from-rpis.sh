read -p "Enter password: " password


sshpass -p "$password"  ssh techtile@192.108.0.1 -t "mkdir -p /storage/gilles/0041_LP_only_REF0/"

sshpass -p "$password"  ssh techtile@192.108.0.1 -t "scp pi@rpi-t03.local:~/experiments/00_calibration/0041_LP_only_REF0/data_T03_* /storage/gilles/0041_LP_only_REF0/"
sshpass -p "$password"  ssh techtile@192.108.0.1 -t "scp pi@rpi-t04.local:~/experiments/00_calibration/0041_LP_only_REF0/data_T04_* /storage/gilles/0041_LP_only_REF0/"
sshpass -p "$password"  ssh techtile@192.108.0.1 -t "scp pi@rpi-t01.local:~/experiments/00_calibration/0041_LP_only_REF0/data_T01_* /storage/gilles/0041_LP_only_REF0/"
sshpass -p "$password"  ssh techtile@192.108.0.1 -t "scp pi@rpi-t02.local:~/experiments/00_calibration/0041_LP_only_REF0/data_T02_* /storage/gilles/0041_LP_only_REF0/"

sshpass -p "$password"  scp techtile@192.108.0.1:/storage/gilles/0041_LP_only_REF0/data_T* .
