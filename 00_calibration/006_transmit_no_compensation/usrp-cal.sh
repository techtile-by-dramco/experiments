#!/bin/bash
git pull
while true; do
  python3 usrp-cal.py
  if [ $? -ne 0 ]; then
    echo "your script encountered an error."
    # Optionally, you can add a break or continue statement here to handle errors
  fi
  sleep 1  # wait for 1 second before running the script again
done