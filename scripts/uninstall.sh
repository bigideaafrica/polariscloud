#!/bin/bash
# Polaris Subnet Uninstallation Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${RED}=== Polaris Subnet Uninstallation ===${NC}"
echo "This script will uninstall Polaris Subnet and remove its data."

# Confirm uninstallation
read -p "Are you sure you want to uninstall Polaris Subnet? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Uninstallation aborted.${NC}"
    exit 0
fi

# Stop running services
echo -e "\n${YELLOW}Stopping running services...${NC}"
if command -v polaris &>/dev/null; then
    # Try to stop miner if it's running
    polaris miner stop 2>/dev/null || true
    # Try to stop validator if it's running
    polaris validator stop 2>/dev/null || true
    echo -e "${GREEN}Services stopped.${NC}"
else
    echo -e "${YELLOW}Polaris command not found. Skipping service stop.${NC}"
fi

# Remove virtual environment
echo -e "\n${YELLOW}Removing virtual environment...${NC}"
if [ -d "venv" ]; then
    rm -rf venv
    echo -e "${GREEN}Virtual environment removed.${NC}"
else
    echo -e "${YELLOW}Virtual environment not found. Skipping...${NC}"
fi

# Ask if user wants to remove configuration
read -p "Do you want to remove Polaris configuration and data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${YELLOW}Removing Polaris configuration and data...${NC}"
    rm -rf ~/.polaris
    echo -e "${GREEN}Configuration and data removed.${NC}"
else
    echo -e "\n${YELLOW}Keeping Polaris configuration and data.${NC}"
fi

# Remove activation script
echo -e "\n${YELLOW}Removing activation script...${NC}"
if [ -f "activate_polaris.sh" ]; then
    rm activate_polaris.sh
    echo -e "${GREEN}Activation script removed.${NC}"
else
    echo -e "${YELLOW}Activation script not found. Skipping...${NC}"
fi

echo -e "\n${GREEN}=== Uninstallation Complete ===${NC}"
echo "Polaris Subnet has been uninstalled from your system." 