#!/bin/bash
# get_subnet_resources.sh
# Script to install dependencies and run the Bittensor subnet resource generator

set -e

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Installing required packages..."
pip install -r requirements_scraper.txt

echo "Running the Bittensor subnet resource generator..."
python bittensor_subnet_resources.py

echo "Completed! The resource document is available at:"
echo "$SCRIPT_DIR/bittensor_subnet_resources.md"

# Make the script executable
chmod +x get_subnet_resources.sh 