ssh techtile@192.108.0.1 -t "mkdir -p /storage/gilles/003_repeated_setup/"

ssh techtile@192.108.0.1 -t "scp pi@rpi-t03.local:~/experiments/00_calibration/003_repeated_setup/data_T03_* /storage/gilles/003_repeated_setup/"
ssh techtile@192.108.0.1 -t "scp pi@rpi-t04.local:~/experiments/00_calibration/003_repeated_setup/data_T04_* /storage/gilles/003_repeated_setup/"

scp techtile@192.108.0.1:/storage/gilles/003_repeated_setup/data_T* .
