read -p "Enter password: " password


sshpass -p "$password"  ssh techtile@192.108.0.1 -t "mkdir -p /storage/gilles/0042_PLL_only/"

sshpass -p "$password"  ssh techtile@192.108.0.1 -t "scp pi@rpi-t04.local:~/experiments/00_calibration/0042_PLL_only/data_T04_* /storage/gilles/0042_PLL_only/"
sshpass -p "$password"  ssh techtile@192.108.0.1 -t "scp pi@rpi-t01.local:~/experiments/00_calibration/0042_PLL_only/data_T01_* /storage/gilles/0042_PLL_only/"

sshpass -p "$password"  scp techtile@192.108.0.1:/storage/gilles/0042_PLL_only/data_T* .
