#!/bin/bash
git pull
global_counter=1
counterch0=1
counterch1=1

gainch0=44
gainch1=44

NUM_MEAS=2

unique_id=$(date -u +"%Y%m%d%H%M%S")


while [ $gainch0 -ge 0 ]; do  # Outer loop for gainch0
  # Decrement gainch0 every NUM_MEAS iterations
  

  gainch1=44 # reset

  while [ $gainch1 -ge 0 ]; do  # Inner loop for gainch1
    # Run the Python script with the current phase and gain values
    echo "Running with gainch0=$gainch0 and gainch1=$gainch1"
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
      gainch1=$((gainch1 - 1))
      echo "Decrementing gainch1 to $gainch1"
    fi
  done

  counterch0=$((counterch0 + 1))

  # Every NUM_MEAS loops, decrement gainch0 by 5
  if [ $((counter % NUM_MEAS)) -eq 0 ]; then
    gainch0=$((gainch0 - 1))
    echo "Decrementing gainch0 to $gainch0"
  fi
done