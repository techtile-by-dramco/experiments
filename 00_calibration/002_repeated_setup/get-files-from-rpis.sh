ssh techtile@192.108.0.1 -t "scp pi@rpi-t03.local:~/experiments/00_calibration/002_repeated_setup/data_T03_* /storage/gilles/"
ssh techtile@192.108.0.1 -t "scp pi@rpi-t04.local:~/experiments/00_calibration/002_repeated_setup/data_T04_* /storage/gilles/"

scp techtile@192.108.0.1:/storage/gilles/data_T* .
