SCRIPT_DIR="$(basename $(pwd))"

# read -p "Enter password: " password


sshpass -p "$1" ssh techtile@192.108.0.1 -t "mkdir -p /storage/gilles/$SCRIPT_DIR/"

sshpass -p "$1" ssh techtile@192.108.0.1 -t "rsync -uv pi@rpi-t03.local:~/experiments/00_calibration/$SCRIPT_DIR/data_* /storage/gilles/$SCRIPT_DIR/"
sshpass -p "$1" ssh techtile@192.108.0.1 -t "rsync -uv pi@rpi-t04.local:~/experiments/00_calibration/$SCRIPT_DIR/data_* /storage/gilles/$SCRIPT_DIR/"

sshpass -p "$1" rsync -uv techtile@192.108.0.1:/storage/gilles/$SCRIPT_DIR/data_* ./data/