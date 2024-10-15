#!/bin/bash
git pull

# Initialize variables
phase=0
counter=0
std=0
max_std=180        # 1 degrees

while true; do
  echo "Start with  $std and counter: $counter"
  python3 usrp-cal-gausbf.py --std $std --adaptive
  if [ $? -ne 0 ]; then
    echo "your script encountered an error."
    # Optionally, you can add a break or continue statement here to handle errors
  fi

  # Increment counter
  counter=$((counter+1))

  # Every 10 iterations, increment std by 0.1
  if [ $((counter % 1)) -eq 0 ]; then
    std=$std + 5
    # Ensure std doesn't exceed 2*pi
    if ($std > $max_std); then
      echo "std reached the min value of one degree, restarting"
      # restarting
      std=0
    fi
  fi

  sleep 0.1  # wait for 0.1 second before running the script again
done