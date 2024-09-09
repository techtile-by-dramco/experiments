#!/bin/bash
git pull
counter=1
gain=78
fixed_gain=37

unique_id=$(date -u +"%Y%m%d%H%M%S")

while true; do
  echo "starting with gain $gain ID: $unique_id"


  python3 usrp-cal.py --meas $counter --gain $fixed_gain $gain --exp $unique_id
  if [ $? -ne 0 ]; then
    echo "your script encountered an error."
    # Optionally, you can add a break or continue statement here to handle errors
  fi
  
  # Every 2 loops, decrement the gain by 1dB
  if [ $((counter % 2)) -eq 0 ]; then
    gain=$((gain - 1))
  fi

  # Increment the loop counter
  counter=$((counter + 1))


  # Check if phase has reached 360 degrees
  if [ $gain -eq -1 ]; then
    echo "Gain has reached 0dB. Stopping the script."
    break
  fi
   

  sleep 0.1 # wait for 0.1 second before running the script again
done
