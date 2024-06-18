ssh techtile@192.108.0.1 -t "mkdir -p /storage/gilles/004_LP_only/"

ssh techtile@192.108.0.1 -t "scp pi@rpi-t03.local:~/experiments/00_calibration/004_LP_only/data_T03_* /storage/gilles/004_LP_only/"
ssh techtile@192.108.0.1 -t "scp pi@rpi-t04.local:~/experiments/00_calibration/004_LP_only/data_T04_* /storage/gilles/004_LP_only/"

scp techtile@192.108.0.1:/storage/gilles/004_LP_only/data_T* .
