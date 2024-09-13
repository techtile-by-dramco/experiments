#!/bin/bash
git pull
global_counter=1
counterch0=1
counterch1=1

gainch0=0
gainch1=0

maxgain=77

NUM_MEAS=1

unique_id=$(date -u +"%Y%m%d%H%M%S")

HOSTNAME=$(hostname)
HOSTNAME=${HOSTNAME:4}  # Slice the hostname starting from the 5th character
echo $HOSTNAME


while [ $gainch0 -le $maxgain ]; do  # Outer loop for gainch0
  # Decrement gainch0 every NUM_MEAS iterations
  

  gainch1=0 # reset

  while [ $gainch1 -le $maxgain ]; do  # Inner loop for gainch1
    # Run the Python script with the current phase and gain values
    echo "Running with gainch0=$gainch0 and gainch1=$gainch1"
    echo "$global_counter,$gainch0,$gainch1" >> "data_config_${HOSTNAME}_${unique_id}.csv"
    python3 usrp-cal.py --meas $global_counter --gain $gainch0 $gainch1 --exp $unique_id
    
    # Check if the Python script encountered an error
    if [ $? -ne 0 ]; then
      echo "Your script encountered an error."
      break
    fi

    # Increment the loop counter
    global_counter=$((global_counter + 1))
    counterch1=$((counterch1 + 1))

    # Every NUM_MEAS loops, decrement gainch1 by 5
    if [ $((counterch1 % NUM_MEAS)) -eq 0 ]; then
      gainch1=$((gainch1 + 1))
      echo "Incrementing gainch1 to $gainch1"
    fi
  done

  counterch0=$((counterch0 + 1))

  # Every NUM_MEAS loops, decrement gainch0 by 5
  if [ $((counter % NUM_MEAS)) -eq 0 ]; then
    gainch0=$((gainch0 + 1))
    echo "Incrementing gainch0 to $gainch0"
  fi
done