SCRIPT_DIR="$(basename $(pwd))"

# rsync -uv pi@rpi-g20.local:~/experiments/00_calibration/$SCRIPT_DIR/data_* ./data/
rsync -uv pi@192.108.0.150:~/experiments/00_calibration/$SCRIPT_DIR/data_* ./data/
# rsync -uv pi@rpi-g18.local:~/experiments/00_calibration/$SCRIPT_DIR/data_* ./data/
# rsync -uv pi@rpi-g17.local:~/experiments/00_calibration/$SCRIPT_DIR/data_* ./data/
# rsync -uv pi@rpi-g16.local:~/experiments/00_calibration/$SCRIPT_DIR/data_* ./data/
# rsync -uv pi@rpi-g15.local:~/experiments/00_calibration/$SCRIPT_DIR/data_* ./data/
