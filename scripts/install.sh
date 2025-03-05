#!/bin/bash
# Polaris Subnet Installation Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Polaris Subnet Installation ===${NC}"
echo "This script will install Polaris Subnet and its dependencies."

# Check if Python 3.8+ is installed
echo -e "\n${YELLOW}Checking Python version...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d '.' -f 1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d '.' -f 2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        echo -e "${GREEN}Python $PYTHON_VERSION detected. Continuing...${NC}"
        PYTHON_CMD=python3
    else
        echo -e "${RED}Python 3.8+ is required. Found $PYTHON_VERSION${NC}"
        exit 1
    fi
else
    echo -e "${RED}Python 3 not found. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Check if Docker is installed
echo -e "\n${YELLOW}Checking Docker installation...${NC}"
if command -v docker &>/dev/null; then
    echo -e "${GREEN}Docker is installed. Continuing...${NC}"
else
    echo -e "${YELLOW}Docker is not installed. Some features may not work.${NC}"
    echo "Visit https://docs.docker.com/get-docker/ to install Docker."
    read -p "Continue without Docker? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Installation aborted.${NC}"
        exit 1
    fi
fi

# Create virtual environment
echo -e "\n${YELLOW}Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Skipping...${NC}"
else
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}Virtual environment created.${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip

# Try to install from requirements.txt, fallback to dependency_files if needed
if [ -f "requirements.txt" ]; then
    if pip install -r requirements.txt; then
        echo -e "${GREEN}Dependencies installed from requirements.txt.${NC}"
    else
        echo -e "${YELLOW}Failed to install from requirements.txt. Trying alternative locations...${NC}"
        if [ -f "dependency_files/production.txt" ]; then
            pip install -r dependency_files/production.txt
            echo -e "${GREEN}Dependencies installed from dependency_files/production.txt.${NC}"
        else
            echo -e "${RED}Could not find dependency files. Installing directly from setup.py...${NC}"
        fi
    fi
else
    echo -e "${YELLOW}requirements.txt not found. Trying alternative locations...${NC}"
    if [ -f "dependency_files/production.txt" ]; then
        pip install -r dependency_files/production.txt
        echo -e "${GREEN}Dependencies installed from dependency_files/production.txt.${NC}"
    else
        echo -e "${RED}Could not find dependency files. Installing directly from setup.py...${NC}"
    fi
fi

# Install the package
echo -e "\n${YELLOW}Installing Polaris Subnet...${NC}"
pip install -e .
echo -e "${GREEN}Polaris Subnet installed.${NC}"

# Create configuration directory
echo -e "\n${YELLOW}Creating configuration directory...${NC}"
mkdir -p ~/.polaris/config
mkdir -p ~/.polaris/logs
echo -e "${GREEN}Configuration directory created.${NC}"

# Create activation script
echo -e "\n${YELLOW}Creating activation script...${NC}"
cat > activate_polaris.sh << 'EOF'
#!/bin/bash
# Activate Polaris environment

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Set environment variables
export POLARIS_HOME="$HOME/.polaris"

echo "Polaris environment activated."
echo "Run 'polaris --help' to see available commands."
EOF

chmod +x activate_polaris.sh
echo -e "${GREEN}Activation script created.${NC}"

echo -e "\n${GREEN}=== Installation Complete ===${NC}"
echo -e "To activate the Polaris environment, run:"
echo -e "${YELLOW}source ./activate_polaris.sh${NC}"
echo -e "Then you can use the 'polaris' command."
echo -e "For example: ${YELLOW}polaris status${NC}" 