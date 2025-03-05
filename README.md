# Polaris Compute Subnet

A modern development workspace manager for distributed compute resources. Polaris simplifies managing compute resources, monitoring their status, and automating key tasks in a distributed environment.

## Features

- **Register and manage compute resources:** Add and monitor distributed compute nodes.
- **Monitor system status:** View system health and active processes.
- **Manage SSH connections:** Automate and configure secure SSH connections.
- **Direct connection support:** Establish secure connections using your public IP.
- **Cross-platform support:** Works on Windows, Linux, and macOS.
- **Bittensor integration:** Run miners and validators on the Bittensor network.

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/bigideainc/polaris-subnet.git
cd polaris-subnet

# Install using the provided script
./scripts/install.sh
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/bigideainc/polaris-subnet.git
cd polaris-subnet

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

## Usage

### Command Line Interface

Polaris provides a comprehensive CLI for managing all aspects of the system:

```bash
# Show overall system status
polaris status

# Manage miners
polaris miner start --wallet my_wallet
polaris miner stop
polaris miner status

# Manage validators
polaris validator start --wallet my_wallet
polaris validator stop
polaris validator status

# Manage wallets
polaris wallet list
polaris wallet create --name my_wallet

# Register with a subnet
polaris subnet register --wallet my_wallet --netuid 12 --pow
```

### Running in Simulation Mode

For testing and development, you can run the miner in simulation mode:

```bash
polaris miner start --wallet my_wallet --simulation
```

## Project Structure

The project is organized into the following components:

```
polaris-subnet/
├── src/                    # Source code
│   └── polaris/            # Main package
│       ├── cli/            # CLI functionality
│       ├── core/           # Core business logic
│       ├── miner/          # Miner implementation
│       ├── validator/      # Validator implementation
│       ├── networking/     # Network functionality
│       └── utils/          # Shared utilities
├── scripts/                # Installation and utility scripts
├── tests/                  # Test suite
├── docs/                   # Documentation
├── dependency_files/       # Dependency specification files
├── config/                 # Configuration files and user settings
├── logs/                   # Log files
└── external/               # External references and dependencies
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/bigideainc/polaris-subnet.git
cd polaris-subnet

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r dependency_files/development.txt
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Format code
black src tests

# Sort imports
isort src tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 