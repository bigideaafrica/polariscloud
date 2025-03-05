#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Uninstalling Polaris Subnet ===${NC}"

# Activate virtual environment if it exists
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
    
    # Uninstall the package
    echo -e "${YELLOW}Uninstalling Polaris package...${NC}"
    pip uninstall -y polaris-subnet
    echo -e "${GREEN}Polaris package uninstalled.${NC}"
    
    # Deactivate virtual environment
    deactivate
fi

# Ask if the user wants to remove the virtual environment
read -p "Do you want to remove the virtual environment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Removing virtual environment...${NC}"
    rm -rf venv
    echo -e "${GREEN}Virtual environment removed.${NC}"
fi

# Ask if the user wants to remove the configuration directory
read -p "Do you want to remove Polaris configuration directory? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Removing configuration directory...${NC}"
    rm -rf ~/.polaris
    echo -e "${GREEN}Configuration directory removed.${NC}"
fi

# Remove activation script
if [ -f "activate_polaris.sh" ]; then
    echo -e "${YELLOW}Removing activation script...${NC}"
    rm activate_polaris.sh
    echo -e "${GREEN}Activation script removed.${NC}"
fi

echo -e "${GREEN}=== Polaris Subnet Uninstallation Complete ===${NC}" 