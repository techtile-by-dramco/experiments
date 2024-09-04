#!/bin/bash
git pull
counter=1

while true; do
  python3 usrp-cal.py --meas $counter
  if [ $? -ne 0 ]; then
    echo "your script encountered an error."
    # Optionally, you can add a break or continue statement here to handle errors
  fi
  # Increment the loop counter
  counter=$((counter + 1))
  sleep 0.1 # wait for 0.1 second before running the script again
done
