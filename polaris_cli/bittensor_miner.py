import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import bittensor as bt
import questionary
from rich.console import Console

console = Console()

POLARIS_HOME = Path.home() / '.polaris'
BITTENSOR_CONFIG_PATH = POLARIS_HOME / 'bittensor'
PID_FILE = BITTENSOR_CONFIG_PATH / 'pids' / 'miner.pid'
LOG_FILE = BITTENSOR_CONFIG_PATH / 'logs' / 'miner.log'

def load_config():
    """Load miner configuration from file."""
    try:
        with open(BITTENSOR_CONFIG_PATH / 'config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        console.print("[error]Configuration file not found. Please run registration first.[/error]")
        return None
    except json.JSONDecodeError:
        console.print("[error]Invalid configuration file.[/error]")
        return None

def setup_logging():
    """Setup logging configuration."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    return LOG_FILE

def get_subtensor():
    """Initialize and return subtensor connection."""
    try:
        subtensor = bt.subtensor(network='finney')
        return subtensor
    except Exception as e:
        console.print(f"[error]Failed to connect to subtensor: {str(e)}[/error]")
        return None

def write_pid(pid):
    """Write process ID to file."""
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PID_FILE, 'w') as f:
        f.write(str(pid))

def remove_pid():
    """Remove PID file."""
    try:
        PID_FILE.unlink()
    except FileNotFoundError:
        pass

def log_message(message):
    """Write message to log file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

def get_wallet_hotkeys(wallet_name):
    """Fetch hotkeys associated with a given wallet."""
    try:
        result = subprocess.run(
            ["btcli", "wallet", "list"],
            check=True,
            capture_output=True,
            text=True
        )
        hotkeys = []
        is_target_wallet = False
        
        for line in result.stdout.splitlines():
            if f"Wallet Name: {wallet_name}" in line:
                is_target_wallet = True
                continue
            if is_target_wallet and "Hotkey:" in line:
                hotkey_name = line.split("Hotkey:")[-1].strip()
                if hotkey_name:
                    hotkeys.append(hotkey_name)
            if is_target_wallet and "Wallet Name:" in line:  # Next wallet section
                break
        
        return hotkeys
    except subprocess.CalledProcessError:
        console.print(f"[error]Failed to fetch hotkeys for wallet '{wallet_name}'.[/error]")
        return []

def get_selected_network():
    """Fetch the saved network selection."""
    network_config_path = POLARIS_HOME / "network_config.json"
    if network_config_path.exists():
        try:
            with open(network_config_path, "r") as f:
                config = json.load(f)
                return config.get("network", "finney")  # Default to finney if missing
        except json.JSONDecodeError:
            console.print("[error]Invalid network configuration file.[/error]")
    return "finney"  # Fallback to mainnet

def start_bittensor_miner(wallet_name):
    """Start the Bittensor miner process with correct wallet and network details."""
    if PID_FILE.exists():
        console.print("[warning]Miner process is already running.[/warning]")
        return False

    config = load_config()
    if not config:
        return False

    # Fetch the correct hotkey(s) for the given wallet
    hotkeys = get_wallet_hotkeys(wallet_name)
    if not hotkeys:
        console.print(f"[error]No hotkeys found for wallet '{wallet_name}'. Create one with 'btcli wallet new_hotkey'.[/error]")
        return False

    # Prompt user to select a hotkey if multiple exist
    hotkey = hotkeys[0]  # Default to first if only one
    if len(hotkeys) > 1:
        hotkey = questionary.select(
            "Select a hotkey to use:",
            choices=hotkeys,
            style=None
        ).ask()

    network = get_selected_network()

    log_file = setup_logging()
    
    try:
        # Start the miner process
        process = subprocess.Popen(
            [
                'btcli', 'run',
                '--wallet.name', wallet_name,
                '--wallet.hotkey', hotkey,
                '--netuid', '12',  # Consider making this dynamic if needed
                '--subtensor.network', network,
                '--logging.debug'
            ],
            stdout=open(log_file, 'a'),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
        
        # Write PID to file
        write_pid(process.pid)
        
        console.print(f"[success]Started Bittensor miner (PID: {process.pid})[/success]")
        log_message(f"Started miner process with PID {process.pid} using hotkey '{hotkey}' on network '{network}'")
        
        return True
        
    except Exception as e:
        console.print(f"[error]Failed to start miner: {str(e)}[/error]")
        log_message(f"Failed to start miner: {str(e)}")
        return False

def stop_bittensor_miner():
    """Stop the Bittensor miner process."""
    try:
        if not PID_FILE.exists():
            console.print("[warning]No running miner process found.[/warning]")
            return True

        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())

        # Try to kill the process
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            time.sleep(2)  # Give it some time to shutdown gracefully
            
            # Force kill if still running
            if os.kill(pid, 0):
                os.killpg(os.getpgid(pid), signal.SIGKILL)
                
        except ProcessLookupError:
            pass  # Process already terminated
        
        remove_pid()
        log_message("Stopped miner process")
        return True
        
    except Exception as e:
        console.print(f"[error]Failed to stop miner: {str(e)}[/error]")
        log_message(f"Failed to stop miner: {str(e)}")
        return False

def check_miner_status():
    """Check the status of the miner process."""
    if not PID_FILE.exists():
        return False
        
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
            
        # Check if process is running
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, FileNotFoundError):
        remove_pid()
        return False
    except Exception:
        return False

# Alias function for checking if the Bittensor miner is running
def is_bittensor_running():
    return check_miner_status()