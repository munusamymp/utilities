#!/bin/bash

# Check if log file is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <log_file>"
  exit 1
fi

LOG_FILE=$1

# Ensure the log file exists
if [ ! -f "$LOG_FILE" ]; then
  echo "Log file '$LOG_FILE' not found!"
  exit 2
fi

# Search and display only the lines that contain 'ERROR'
echo "Extracting error messages from $LOG_FILE..."
grep -i "ERROR" "$LOG_FILE"
