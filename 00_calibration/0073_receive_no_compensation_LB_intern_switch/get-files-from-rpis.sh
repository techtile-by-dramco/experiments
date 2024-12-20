SCRIPT_DIR="$(basename $(pwd))"

read -p "Enter password: " password


sshpass -p "$password" ssh techtile@192.108.0.1 -t "mkdir -p /storage/gilles/$SCRIPT_DIR/"

sshpass -p "$password" ssh techtile@192.108.0.1 -t "scp pi@rpi-t03.local:~/experiments/00_calibration/$SCRIPT_DIR/data_T03_* /storage/gilles/$SCRIPT_DIR/"
sshpass -p "$password" ssh techtile@192.108.0.1 -t "scp pi@rpi-t04.local:~/experiments/00_calibration/$SCRIPT_DIR/data_T04_* /storage/gilles/$SCRIPT_DIR/"

sshpass -p "$password" scp techtile@192.108.0.1:/storage/gilles/$SCRIPT_DIR/data_T* .
