#!/bin/bash

git pull

python3 usrp-cal.py

# while true; do
#   python3 usrp-cal.py
#   if [ $? -ne 0 ]; then
#     echo "your script encountered an error."
#     # Optionally, you can add a break or continue statement here to handle errors
#   fi

#   sleep 1 # give it some time
# done
