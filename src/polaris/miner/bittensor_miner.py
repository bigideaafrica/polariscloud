"""
Bittensor miner implementation for Polaris subnet.

This module handles the initialization, starting, stopping, and monitoring of a Bittensor miner.
It supports both regular mining (connected to the actual Bittensor network) and simulation mode
for testing and development purposes.
"""

import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
import random

import bittensor as bt
from rich.console import Console

from polaris.utils.logging import setup_logger

# Initialize console for rich output
console = Console()

# Setup logger
logger = setup_logger('miner')

# Constants
POLARIS_HOME = Path.home() / '.polaris'
BITTENSOR_CONFIG_PATH = POLARIS_HOME / 'bittensor'
PID_FILE = BITTENSOR_CONFIG_PATH / 'pids' / 'miner.pid'
LOG_FILE = BITTENSOR_CONFIG_PATH / 'logs' / 'miner.log'


def load_config():
    """Load miner configuration from file"""
    try:
        with open(BITTENSOR_CONFIG_PATH / 'config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Configuration file not found. Please run registration first.")
        console.print("[error]Configuration file not found. Please run registration first.[/error]")
        return None


def get_subtensor():
    """Initialize connection to the Bittensor network"""
    try:
        config = bt.subtensor.config()
        config.subtensor.network = 'finney'
        subtensor = bt.subtensor(config=config)
        return subtensor
    except Exception as e:
        logger.error(f"Failed to connect to Bittensor network: {str(e)}")
        return None


def write_pid(pid):
    """Write the process ID to the PID file"""
    BITTENSOR_CONFIG_PATH.mkdir(parents=True, exist_ok=True)
    (BITTENSOR_CONFIG_PATH / 'pids').mkdir(exist_ok=True)
    (BITTENSOR_CONFIG_PATH / 'logs').mkdir(exist_ok=True)
    
    with open(PID_FILE, 'w') as f:
        f.write(str(pid))


def remove_pid():
    """Remove the PID file"""
    if PID_FILE.exists():
        PID_FILE.unlink()


def log_message(message):
    """Log a message to the miner log file"""
    timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
    with open(LOG_FILE, 'a') as f:
        f.write(f"{timestamp} {message}\n")


def start_bittensor_miner(wallet_name, simulation_mode=False):
    """
    Start the Bittensor miner process
    
    Args:
        wallet_name (str): Name of the Bittensor wallet to use
        simulation_mode (bool): Whether to run in simulation mode without actual network connection
        
    Returns:
        bool: True if miner started successfully, False otherwise
    """
    if is_bittensor_running():
        logger.info("Bittensor miner is already running")
        console.print("[info]Bittensor miner is already running[/info]")
        return False
    
    # Setup logging directories
    BITTENSOR_CONFIG_PATH.mkdir(parents=True, exist_ok=True)
    (BITTENSOR_CONFIG_PATH / 'logs').mkdir(exist_ok=True)
    
    # If simulation mode is enabled, run the miner in simulation mode
    if simulation_mode:
        try:
            # Create a detached process
            cmd = [
                sys.executable, 
                '-c', 
                f'''
import sys
import time
import random
from datetime import datetime
from pathlib import Path

# Setup basic logging
log_file = Path.home() / '.polaris/bittensor/logs/miner.log'
def log(msg):
    with open(log_file, 'a') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        f.write(f"{{{{timestamp}}}} |       INFO       | bittensor:loggingmachine.py:377 |  - {{{{msg}}}} -\\n")

# Log startup
log("Starting Bittensor miner in simulation mode...")
log(f"Loaded wallet: wallet({wallet_name}, default, ~/.bittensor/wallets/)")
log("Local miner running in simulation mode...")

# Simulation loop
iteration = 1
while True:
    log(f"Miner iteration {{{{iteration}}}} at {{{{time.time()}}}}")
    request_type = "Storage"
    log(f"Received simulated request for {{{{request_type}}}} resources")
    
    # Simulate processing time (0.5-1.5 seconds)
    process_time = random.uniform(0.5, 1.5)
    time.sleep(process_time)
    
    log(f"Response: Processed {{{{request_type}}}} request in {{{{process_time:.2f}}}}s")
    
    # Random sleep between iterations (5-20 seconds)
    sleep_time = random.uniform(5, 20)
    log(f"Sleeping for {{{{sleep_time:.2f}}}}s")
    time.sleep(sleep_time)
    iteration += 1
'''
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Record the PID
            pid = process.pid
            write_pid(pid)
            
            # Log the start
            log_message(f"Started miner process in simulation mode with PID {pid}")
            logger.info(f"Started Bittensor miner in simulation mode (PID: {pid})")
            console.print(f"[success]Started Bittensor miner in simulation mode (PID: {pid})[/success]")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Bittensor miner in simulation mode: {str(e)}")
            console.print(f"[error]Failed to start Bittensor miner in simulation mode: {str(e)}[/error]")
            return False
    
    # Otherwise run in regular mode (connected to network)
    config = load_config()
    if not config:
        return False
    
    try:
        # Create a detached process
        cmd = [
            sys.executable, 
            '-c', 
            f'''
import bittensor as bt
import time
from datetime import datetime
from pathlib import Path

# Setup logging
bt.logging(
    debug=True,
    trace=False
)

# Log startup
bt.logging.info(f"Starting Bittensor miner...")

# Load wallet
wallet = bt.wallet(name="{wallet_name}")
bt.logging.info(f"Loaded wallet: {wallet}")

# Connect to network
subtensor = bt.subtensor(network="finney")

# Check if the wallet is registered
if not subtensor.is_hotkey_registered(wallet.hotkey.ss58_address, netuid=12):
    bt.logging.error(f"Wallet is not registered on subnet 12. Please register first.")
    exit(1)

# TODO: Implement miner logic for subnet 12 here
# This is a placeholder for the actual mining code
while True:
    # Mining logic would go here
    time.sleep(60)
'''
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )
        
        # Record the PID
        pid = process.pid
        write_pid(pid)
        
        # Log the start
        log_message(f"Started miner process with PID {pid}")
        logger.info(f"Started Bittensor miner (PID: {pid})")
        console.print(f"[success]Started Bittensor miner (PID: {pid})[/success]")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to start Bittensor miner: {str(e)}")
        console.print(f"[error]Failed to start Bittensor miner: {str(e)}[/error]")
        return False


def stop_bittensor_miner():
    """
    Stop the running Bittensor miner process
    
    Returns:
        bool: True if miner was stopped successfully, False otherwise
    """
    if not is_bittensor_running():
        logger.info("No Bittensor miner process is running")
        console.print("[info]No Bittensor miner process is running[/info]")
        return False
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        # Send SIGTERM to the process group
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            logger.info(f"Sent SIGTERM to miner process group (PID: {pid})")
        except:
            # If that fails, try to kill just the process
            os.kill(pid, signal.SIGTERM)
            logger.info(f"Sent SIGTERM to miner process (PID: {pid})")
        
        # Wait a moment and check if it's still running
        time.sleep(2)
        try:
            os.kill(pid, 0)  # This will raise an exception if the process doesn't exist
            # If we get here, the process is still running, so force kill it
            os.kill(pid, signal.SIGKILL)
            logger.info(f"Sent SIGKILL to miner process (PID: {pid})")
        except OSError:
            # Process is no longer running
            pass
        
        # Remove the PID file
        remove_pid()
        
        # Log the stop
        log_message(f"Stopped miner process")
        logger.info("Stopped Bittensor miner")
        console.print("[success]Stopped Bittensor miner[/success]")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to stop Bittensor miner: {str(e)}")
        console.print(f"[error]Failed to stop Bittensor miner: {str(e)}[/error]")
        return False


def check_miner_status():
    """
    Check the status of the Bittensor miner
    
    Returns:
        dict: Status information about the miner
    """
    status = {
        "running": is_bittensor_running(),
        "pid": None,
        "uptime": None,
    }
    
    if status["running"]:
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            status["pid"] = pid
            
            # Get process start time
            import psutil
            process = psutil.Process(pid)
            start_time = process.create_time()
            uptime = time.time() - start_time
            
            # Format uptime
            hours, remainder = divmod(uptime, 3600)
            minutes, seconds = divmod(remainder, 60)
            status["uptime"] = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        except:
            # If any errors occur while getting detailed status
            pass
    
    return status


def is_bittensor_running():
    """
    Check if the Bittensor miner process is running
    
    Returns:
        bool: True if miner is running, False otherwise
    """
    if not PID_FILE.exists():
        return False
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        # Try to send signal 0 to the process (doesn't actually send a signal,
        # but checks if the process exists)
        os.kill(pid, 0)
        return True
    except (FileNotFoundError, ProcessLookupError, PermissionError, ValueError):
        # Process doesn't exist or we don't have permission to check it
        remove_pid()  # Clean up the PID file
        return False 