#!/bin/bash
git pull

counter=1
gain=0
fixed_gain=37
NUM_MEAS=1


HOSTNAME=$(hostname)
HOSTNAME=${HOSTNAME:4}  # Slice the hostname starting from the 5th character
echo $HOSTNAME

unique_id=$(date -u +"%Y%m%d%H%M%S")

while true; do
  echo "starting with gain $gain ID: $unique_id"
  echo "$counter,$fixed_gain,$gain" >> "data_config_${HOSTNAME}_${unique_id}.csv"

  python3 usrp-cal.py --meas $counter --gain $fixed_gain $gain --exp $unique_id
  if [ $? -ne 0 ]; then
    echo "your script encountered an error."
    # Optionally, you can add a break or continue statement here to handle errors
  fi
  
  # Every 2 loops, decrement the gain by 1dB
  if [ $((counter % NUM_MEAS)) -eq 0 ]; then
    gain=$((gain + 1))
  fi

  # Increment the loop counter
  counter=$((counter + 1))


  # Check if phase has reached 360 degrees
  if [ $gain -eq 78 ]; then
    echo "Gain has reached 78dB. Stopping the script."
    break
  fi
   

  sleep 0.1 # wait for 0.1 second before running the script again
done