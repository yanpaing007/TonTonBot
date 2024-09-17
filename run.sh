#!/bin/bash

# Check if virtual environment directory exists
if [ ! -d "venv" ]; then
    # Create virtual environment
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install packages from requirements.txt
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found"
fi

# Run the Python script
python main.py