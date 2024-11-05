#!/bin/bash
git pull

# Initialize variables
phase=0
counter=0
# Default value for IP
ip=""

# Parse options
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --ip) # If the argument is --ip, assign the next value to the ip variable
            ip="$2"
            shift # Shift past the value
            ;;
        *) # Unknown option
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift # Move to the next argument
done

# Check if the --ip argument was provided
if [[ -n "$ip" ]]; then
    echo "IP address provided: $ip"
else
    echo "No IP address provided."
fi


while true; do
  # Check if the --ip argument was provided
  if [[ -n "$ip" ]]; then
      python3 usrp-cal-bf.py --ip "$ip"
  else
      python3 usrp-cal-bf.py
  fi
  
  if [ $? -ne 0 ]; then
    echo "your script encountered an error."
    # Optionally, you can add a break or continue statement here to handle errors
  fi

  sleep 0.1  # wait for 0.1 second before running the script again
done