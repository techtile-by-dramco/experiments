#!/bin/bash
git pull

# Initialize variables
phase=0
counter=0


while true; do
  python3 usrp-pilot.py --phase $phase
  if [ $? -ne 0 ]; then
    echo "your script encountered an error."
    # Optionally, you can add a break or continue statement here to handle errors
  fi

   # Increment the loop counter
  counter=$((counter + 1))

  # Every 10 loops, increment the phase by 5 modulo 360
  if [ $((counter % 10)) -eq 0 ]; then
    phase=$(( (phase + 5) % 360 ))
  fi
  
  sleep 0.1  # wait for 0.1 second before running the script again
done