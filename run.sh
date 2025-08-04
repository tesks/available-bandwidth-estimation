#!/usr/bin/env bash

# Set up python virtual environment
if [ ! -d "./venv" ]; then
    python -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install any missing python dependencies
pip install -r requirements.txt

# Run the main script
python main_vps_packet_delay_logger.py

