#!/bin/bash
git pull
counter=1
gain=39

unique_id=$(date -u +"%Y%m%d%H%M%S")

while true; do
  echo "starting with gain $gain"
  python3 usrp-cal.py --meas $counter --gain $gain --exp $unique_id
  if [ $? -ne 0 ]; then
    echo "your script encountered an error."
    # Optionally, you can add a break or continue statement here to handle errors
  fi
  # Increment the loop counter
  counter=$((counter + 1))

  # Every 10 loops, decrement the gain by 1dB
  if [ $((counter % 4)) -eq 0 ]; then
    gain=$((gain - 1))
  fi

   # Check if phase has reached 360 degrees
  if [ $gain -eq 0 ]; then
    echo "Gain has reached 20dB. Stopping the script."
    break
  fi

  sleep 0.1 # wait for 0.1 second before running the script again
done
