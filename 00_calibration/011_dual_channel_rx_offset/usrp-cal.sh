#!/bin/bash
git pull
counter=1
gain=76

unique_id=$(date -u +"%Y%m%d%H%M%S")


HOSTNAME=$(hostname)
HOSTNAME=${HOSTNAME:4}  # Slice the hostname starting from the 5th character
echo $HOSTNAME


while true; do
  echo "starting with gain $gain for ID $unique_id"
  echo "$counter,$gain,$gain" >> "data_config_${HOSTNAME}_${unique_id}.csv"
  python3 usrp-cal.py --meas $counter --gain $gain --exp $unique_id
  if [ $? -ne 0 ]; then
    echo "your script encountered an error."
    # Optionally, you can add a break or continue statement here to handle errors
  fi
  
  gain=$((gain - 1))


  # Increment the loop counter
  counter=$((counter + 1))

   # Check if phase has reached 360 degrees
  if [ $gain -eq -1 ]; then
    echo "Gain has reached 0dB. Stopping the script."
    break
  fi
done
