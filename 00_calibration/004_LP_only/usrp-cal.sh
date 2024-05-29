#!/bin/bash
git pull
# Initialize counter
counter=0
timestamp=$(date -u +"%Y%m%d%H%M%S")

while true; do
  python3 usrp-cal.py "$counter" "$timestamp"
  if [ $? -ne 0 ]; then
    echo "your script encountered an error."
    # Optionally, you can add a break or continue statement here to handle errors
  fi
  # Increment the counter
  counter=$((counter + 1))
  sleep 1  # wait for 60 seconds before running the script again
done