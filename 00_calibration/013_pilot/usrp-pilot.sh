#!/bin/bash
git pull

# Initialize variables
phase=0
counter=0


while true; do
  python3 usrp-pilot.py --phase 0
  if [ $? -ne 0 ]; then
    echo "your script encountered an error."
    # Optionally, you can add a break or continue statement here to handle errors
  fi

  sleep 0.1  # wait for 0.1 second before running the script again
done