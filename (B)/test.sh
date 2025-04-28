#!/bin/bash

# Make sure the script exits on any error
set -e

# Get the mode (yes/no) from the first argument
USE_TKINTER=$1

# Get the input file from the second argument (optional)
INPUT_FILE=$2

# Check if mode is yes or no
if [ "$USE_TKINTER" == "yes" ]; then
    python3 main.py yes
elif [ "$USE_TKINTER" == "no" ]; then
    if [ -z "$INPUT_FILE" ]; then
        echo "Error: File name is required when using 'no' mode."
        exit 1
    fi
    python3 main.py no --file "$INPUT_FILE"
else
    echo "Error: First argument must be 'yes' or 'no'."
    exit 1
fi
