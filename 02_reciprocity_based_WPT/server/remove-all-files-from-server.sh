SCRIPT_DIR="$(basename $(pwd))"

read -p "Enter password: " password


sshpass -p "$password" ssh techtile@192.108.0.1 -t "rm /storage/gilles/$SCRIPT_DIR/data_T* "
