# polaris_cli/cli.py
import json
import os
import subprocess
import sys
from pathlib import Path
import requests
import time
import readchar

import click
import questionary
from questionary import Style
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

from .heartbeat_monitor import monitor_heartbeat
from .log_monitor import check_main
from .repo_manager import update_repository
from .start import (check_status, start_polaris, start_system, stop_polaris,
                    stop_system)
from .bittensor_miner import start_bittensor_miner, stop_bittensor_miner, is_bittensor_running
# For Commune registration we import the existing function from register.py
from .register import register_miner as commune_register

# Create a custom theme for rich console
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red",
    "success": "green"
})

console = Console(theme=custom_theme)

# Custom style for questionary
custom_style = Style([
    ('qmark', 'fg:#ff9d00 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#00ff00 bold'),
    ('pointer', 'fg:#ff9d00 bold'),
    ('highlighted', 'fg:#ff9d00 bold'),
    ('selected', 'fg:#00ff00'),
    ('separator', 'fg:#cc5454'),
    ('instruction', ''),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])

POLARIS_HOME = Path.home() / '.polaris'
BITTENSOR_CONFIG_PATH = POLARIS_HOME / 'bittensor'
SERVER_ENDPOINT = "https://your-server-endpoint.com/api/miners"  # Replace with your actual endpoint

def setup_directories():
    """Create necessary directories if they don't exist"""
    POLARIS_HOME.mkdir(exist_ok=True)
    BITTENSOR_CONFIG_PATH.mkdir(exist_ok=True)
    (BITTENSOR_CONFIG_PATH / 'pids').mkdir(exist_ok=True)
    (BITTENSOR_CONFIG_PATH / 'logs').mkdir(exist_ok=True)

def get_wallets():
    """Fetch and return a list of available wallet names using btcli."""
    try:
        result = subprocess.run(
            ["btcli", "wallet", "list"],
            check=True,
            capture_output=True,
            text=True
        )
        wallets = []
        for line in result.stdout.splitlines():
            if "Wallet Name:" in line:
                wallet_name = line.split("Wallet Name:")[-1].strip()
                if wallet_name and wallet_name not in wallets:
                    wallets.append(wallet_name)
        return wallets
    except subprocess.CalledProcessError:
        console.print("[error]Failed to fetch wallet list.[/error]")
        return []

def handle_bittensor_registration():
    """Handle Bittensor registration, ensuring wallet name is valid."""
    console.print("\n[info]Fetching available wallets...[/info]")
    
    wallets = get_wallets()
    if not wallets:
        console.print("[error]No wallets found. Please create one using 'btcli wallet new'.[/error]")
        return None

    console.print("\n[info]Available wallets:[/info]")
    for wallet in wallets:
        console.print(f"• {wallet}")

    # Prompt user to select a wallet
    wallet_name = questionary.select(
        "Select your wallet:",
        choices=wallets,
        style=custom_style
    ).ask()

    if not wallet_name:
        console.print("[error]Wallet selection cancelled.[/error]")
        return None

    console.print(f"[success]Selected Wallet: {wallet_name}[/success]")

    # Network selection
    console.print("\n[info]Select Bittensor network:[/info]")
    network = questionary.select(
        "Choose the network:",
        choices=["mainnet (Finney)", "testnet (Local/Test)"],
        style=custom_style
    ).ask()

    network = "finney" if "Finney" in network else "test"
    console.print(f"[success]Using {network} network[/success]")

    # Save the selected network
    network_config_path = os.path.join(POLARIS_HOME, "network_config.json")
    with open(network_config_path, "w") as f:
        json.dump({"network": network}, f, indent=4)

    return wallet_name, network

def start_bittensor_miner(wallet_name):
    """Start the Bittensor miner process."""
    console.print("[info]Starting Bittensor miner process...[/info]")
    
    # Ask for netuid (subnet ID)
    console.print("[input]Enter subnet ID (netuid) for Polaris subnet: [/input]", end="")
    netuid = input().strip()
    if not netuid.isdigit():
        console.print("[error]Invalid subnet ID. Please enter a number.[/error]")
        return
    
    # Get the selected network from config file if available
    network = "finney"  # Default to mainnet
    network_config_path = os.path.join(POLARIS_HOME, "network_config.json")
    if os.path.exists(network_config_path):
        try:
            with open(network_config_path, "r") as f:
                config = json.load(f)
                network = config.get("network", "finney")
        except:
            console.print("[warning]Could not read network configuration. Using mainnet (Finney).[/warning]")
    
    # Create logs and pids directories if they don't exist
    logs_dir = POLARIS_HOME / 'logs'
    pids_dir = POLARIS_HOME / 'pids'
    logs_dir.mkdir(exist_ok=True)
    pids_dir.mkdir(exist_ok=True)
    
    # Set log files for Bittensor miner
    log_file = logs_dir / 'bittensor_miner.log'
    error_log = logs_dir / 'bittensor_miner_error.log'
    
    try:
        # Run as validator using btcli
        console.print("[info]Attempting to start validator with btcli...[/info]")
        process = subprocess.Popen(
            [
                'btcli', 'run', '--netuid', netuid, 
                '--wallet.name', wallet_name, 
                '--subtensor.network', network
            ],
            stdout=open(log_file, 'a'),
            stderr=open(error_log, 'a'),
            preexec_fn=os.setpgrp
        )
        
        # Write PID to file
        pid_file = pids_dir / 'bittensor_miner.pid'
        with open(pid_file, 'w') as f:
            f.write(str(process.pid))
        
        console.print(f"[success]Bittensor miner started successfully with btcli![/success]")
        console.print(f"[info]Process running with PID: {process.pid}[/info]")
        console.print(f"[info]Logs: {log_file} and {error_log}[/info]")
        
    except Exception as e:
        console.print(f"[error]Failed to start Bittensor miner: {str(e)}[/error]")
        return

# ----------------- Interactive Selection Functions -----------------
def select_start_mode():
    """
    Interactive selection for 'polaris start' with two options:
    - Miner (Commune miner process)
    - Validator (Bittensor miner process)
    """
    choices = [
        'Miner',
        'Validator'
    ]
    answer = questionary.select(
        "Select mode:",
        choices=choices,
        style=custom_style,
        qmark="🚀"
    ).ask()
    return answer.lower() if answer else ""

def select_registration_type():
    """
    Interactive selection for 'polaris register' with two options:
    - Commune Miner Node
    - Bittensor Miner Node
    """
    choices = [
        'Commune Miner Node',
        'Bittensor Miner Node'
    ]
    answer = questionary.select(
        "Select registration type:",
        choices=choices,
        style=custom_style,
        qmark="🔑"
    ).ask()
    return answer.lower() if answer else ""

# ----------------- CLI Commands -----------------
@click.group()
def cli():
    """Polaris CLI - Modern Development Workspace Manager for Distributed Compute Resources"""
    setup_directories()
    pass

@cli.command()
def register():
    """Register to become a Polaris Compute Provider."""
    console.print("\n[bold cyan]Register as a Polaris Compute Provider[/bold cyan]")
    
    # Check BT registration
    console.print("\n[title]Bittensor Registration[/title]")
    console.print("\n[title]Bittensor Wallet Configuration[/title]")
    
    # First ask if user already has a wallet
    has_wallet = questionary.confirm(
        "Do you already have a Bittensor wallet?",
        style=custom_style
    ).ask()
    
    wallet_name = None
    network = "finney"  # Default network
    
    if has_wallet:
        # Handle existing wallet
        wallet_response = handle_bittensor_registration()
        if isinstance(wallet_response, tuple) and len(wallet_response) == 2:
            wallet_name, network = wallet_response
        else:
            console.print("[error]Wallet configuration failed.[/error]")
            return
    else:
        # Create a new wallet
        console.print("\n[info]Creating a new Bittensor wallet...[/info]")
        
        # Get wallet name
        wallet_name = questionary.text(
            "Enter a name for your new wallet:",
            style=custom_style
        ).ask()
        
        if not wallet_name or not wallet_name.strip():
            console.print("[error]Wallet name cannot be empty.[/error]")
            return
        
        # Create the wallet
        try:
            subprocess.run(
                ["btcli", "wallet", "new", "--wallet.name", wallet_name],
                check=True
            )
            console.print(f"[success]Wallet '{wallet_name}' created successfully.[/success]")
            
            # Now prompt for network selection
            console.print("\n[info]Select Bittensor network:[/info]")
            network_choice = questionary.select(
                "Choose the network:",
                choices=["mainnet (Finney)", "testnet (Local/Test)"],
                style=custom_style
            ).ask()
            
            network = "finney" if "Finney" in network_choice else "test"
            console.print(f"[success]Using {network} network[/success]")
            
            # Save network selection
            network_config_path = os.path.join(POLARIS_HOME, "network_config.json")
            with open(network_config_path, "w") as f:
                json.dump({"network": network}, f, indent=4)
        except subprocess.CalledProcessError as e:
            console.print(f"[error]Failed to create wallet: {str(e)}[/error]")
            return
    
    if not wallet_name:
        console.print("[error]Wallet configuration failed. Exiting.[/error]")
        return
    
    # Check if wallet is already registered with the subnet
    console.print("\n[info]Checking if wallet is registered with the Bittensor network...[/info]")
    try:
        # Check if the wallet is already registered with the subnet
        result = subprocess.run(
            ['btcli', 'wallet', 'balance', '--wallet.name', wallet_name, '--subtensor.network', network],
            capture_output=True,
            text=True
        )
        
        console.print("[success]Wallet is registered with Bittensor network.[/success]")
        
        # Check if we need to register with the specific subnet
        subnet_registered = False
        try:
            # Ask for Polaris subnet ID
            subnet_id = questionary.text(
                "Enter subnet ID (netuid) for Polaris subnet:",
                default="12",
                style=custom_style
            ).ask()
            
            if not subnet_id.isdigit():
                console.print("[error]Invalid subnet ID. Please enter a number.[/error]")
                return
            
            # Check if already registered on specific subnet
            result = subprocess.run(
                ['btcli', 'subnet', 'list', '--wallet.name', wallet_name, '--subtensor.network', network],
                capture_output=True,
                text=True
            )
            
            if f"Subnet: {subnet_id}" in result.stdout and wallet_name in result.stdout:
                console.print(f"[success]Wallet is already registered on subnet {subnet_id}.[/success]")
                subnet_registered = True
            else:
                # Offer to register on the subnet
                should_register = questionary.confirm(
                    f"Would you like to register on Polaris subnet (netuid {subnet_id})?",
                    style=custom_style
                ).ask()
                
                if should_register:
                    console.print("[info]Registering on Polaris subnet (this may take a few minutes)...[/info]")
                    try:
                        reg_result = subprocess.run(
                            ['btcli', 'subnet', 'register', 
                             '--netuid', subnet_id,
                             '--wallet.name', wallet_name,
                             '--subtensor.network', network],
                            capture_output=True,
                            text=True
                        )
                        
                        if "Successfully registered" in reg_result.stdout:
                            console.print("[success]Successfully registered on Polaris subnet![/success]")
                            subnet_registered = True
                        else:
                            console.print(f"[warning]Registration may not have succeeded. Please check manually.[/warning]")
                    except subprocess.CalledProcessError as e:
                        console.print(f"[error]Failed to register on subnet: {str(e)}[/error]")
        except Exception as e:
            console.print(f"[warning]Could not verify subnet registration: {str(e)}[/warning]")
    
    except Exception as e:
        console.print(f"[warning]Could not verify wallet registration status: {str(e)}[/warning]")
    
    # System Requirements Check
    console.print("\n[title]System Requirements Check[/title]")
    
    # Check CPU
    console.print("[info]Checking CPU...[/info]")
    try:
        if sys.platform == 'darwin':
            # Check if we're on Apple Silicon
            try:
                # Try to get processor brand using sysctl
                processor_brand = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string']).decode().strip()
                if "Apple" in processor_brand:
                    console.print(f"[success]CPU: {processor_brand}[/success]")
                else:
                    # Try alternative method to detect Apple Silicon
                    model = subprocess.check_output(['sysctl', '-n', 'hw.model']).decode().strip()
                    if "Mac" in model:
                        # Try to determine which Apple Silicon chip
                        chip_info = subprocess.check_output(['sysctl', '-n', 'hw.optional.arm64']).decode().strip()
                        if chip_info == "1":
                            # This is definitely Apple Silicon, try to determine which one
                            console.print(f"[success]CPU: Apple Silicon (M-series)[/success]")
                        else:
                            console.print(f"[success]CPU: Apple Silicon Mac[/success]")
                    else:
                        console.print(f"[success]CPU: {processor_brand}[/success]")
            except:
                # Fallback for Apple Silicon detection
                console.print(f"[success]CPU: Apple Silicon Mac[/success]")
        else:
            # Non-macOS CPU detection
            with open('/proc/cpuinfo', 'r') as f:
                cpu_info = [line for line in f if 'model name' in line][0].split(':')[1].strip()
            console.print(f"[success]CPU: {cpu_info}[/success]")
    except:
        console.print("[warning]Could not determine CPU model.[/warning]")
    
    # Check RAM
    console.print("[info]Checking RAM...[/info]")
    try:
        import psutil
        ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
        console.print(f"[success]RAM: {ram_gb} GB[/success]")
        
        if ram_gb < 16:
            console.print("[warning]Recommended minimum RAM is 16GB.[/warning]")
    except:
        console.print("[warning]Could not determine RAM size.[/warning]")
    
    # Check disk space
    console.print("[info]Checking disk space...[/info]")
    try:
        disk_gb = round(psutil.disk_usage('/').total / (1024**3), 2)
        console.print(f"[success]Disk space: {disk_gb} GB[/success]")
        
        if disk_gb < 100:
            console.print("[warning]Recommended minimum disk space is 100GB.[/warning]")
    except:
        console.print("[warning]Could not determine disk space.[/warning]")
    
    # Check GPU(s)
    console.print("[info]Checking GPU(s)...[/info]")
    try:
        # First check if we're on macOS with Apple Silicon
        is_apple_silicon = False
        if sys.platform == 'darwin':
            try:
                # Try to detect Apple Silicon
                platform_info = subprocess.check_output(['sysctl', '-n', 'hw.model']).decode().strip()
                processor_info = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string']).decode().strip()
                
                if "Apple" in processor_info or "Mac" in platform_info:
                    # Check if we can get GPU information
                    try:
                        gpu_info = subprocess.check_output(['system_profiler', 'SPDisplaysDataType']).decode().strip()
                        if "Apple M" in gpu_info:
                            console.print(f"[success]GPU: Apple Integrated GPU (Apple Silicon)[/success]")
                        else:
                            console.print(f"[success]GPU: Apple Integrated GPU[/success]")
                        is_apple_silicon = True
                    except:
                        console.print(f"[success]GPU: Apple Integrated GPU (Apple Silicon)[/success]")
                        is_apple_silicon = True
            except:
                pass
        
        # Fall back to nvidia-smi for NVIDIA GPUs if not Apple Silicon
        if not is_apple_silicon:
            gpu_info = subprocess.check_output(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader']).decode().strip()
            if gpu_info:
                for line in gpu_info.split('\n'):
                    console.print(f"[success]GPU: {line}[/success]")
            else:
                console.print("[warning]No NVIDIA GPU detected.[/warning]")
    except:
        if sys.platform == 'darwin':
            # On macOS, assume integrated GPU
            console.print("[success]GPU: Apple Integrated GPU[/success]")
        else:
            console.print("[warning]Could not detect GPU. NVIDIA tools not installed or GPU not available.[/warning]")
    
    # Print summary
    console.print("\n[title]Registration Summary[/title]")
    console.print(f"[success]Wallet: {wallet_name}[/success]")
    console.print(f"[success]Network: {network}[/success]")
    
    # Confirm registration
    proceed = questionary.confirm(
        "Complete registration as a Polaris Compute Provider?",
        style=custom_style
    ).ask()
    
    if proceed:
        # Start necessary services
        console.print("\n[info]Starting Polaris services...[/info]")
        
        # Start the Bittensor miner with fixed subnet ID
        try:
            # Ask for Polaris subnet ID
            subnet_id = questionary.text(
                "Enter subnet ID (netuid) for Polaris subnet:",
                default="12",
                style=custom_style
            ).ask()
            
            if not subnet_id.isdigit():
                console.print("[error]Invalid subnet ID. Please enter a number.[/error]")
            else:
                # Create logs and pids directories if they don't exist
                logs_dir = POLARIS_HOME / 'logs'
                pids_dir = POLARIS_HOME / 'pids'
                logs_dir.mkdir(exist_ok=True)
                pids_dir.mkdir(exist_ok=True)
                
                # Set log files for Bittensor miner
                log_file = logs_dir / 'bittensor_miner.log'
                error_log = logs_dir / 'bittensor_miner_error.log'
                
                # Run as validator using btcli
                console.print("[info]Starting Bittensor miner...[/info]")
                process = subprocess.Popen(
                    [
                        'btcli', 'run', '--netuid', subnet_id, 
                        '--wallet.name', wallet_name, 
                        '--subtensor.network', network
                    ],
                    stdout=open(log_file, 'a'),
                    stderr=open(error_log, 'a'),
                    preexec_fn=os.setpgrp
                )
                
                # Write PID to file
                pid_file = pids_dir / 'bittensor_miner.pid'
                with open(pid_file, 'w') as f:
                    f.write(str(process.pid))
                
                console.print(f"[success]Bittensor miner started successfully with PID {process.pid}[/success]")
                console.print(f"[info]Logs: {log_file} and {error_log}[/info]")
        except Exception as e:
            console.print(f"[error]Failed to start Bittensor miner: {str(e)}[/error]")
        
        # Start the system and API
        start_system()
        start_polaris()
        
        # Start the heartbeat service
        start_heartbeat()
        
        console.print("\n[success]Registration complete! You are now registered as a Polaris Compute Provider.[/success]")
        console.print("[info]Your node is now running and contributing to the network.[/info]")
        
        # Wait momentarily to allow services to start
        time.sleep(2)
        status()
    else:
        console.print("[info]Registration canceled.[/info]")

@cli.command(name='view-compute')
def view_pod_command():
    """View pod compute resources."""
    from .view_pod import view_pod
    view_pod()

@cli.command()
def start():
    """Start Polaris and selected compute processes."""
    console.print("\n[info]Welcome to Polaris Compute Subnet![/info]")
    mode = select_start_mode()

    if mode == 'validator':
        # Run Bittensor miner process for Validator mode.
        if is_bittensor_running():
            console.print("[warning]Bittensor miner is already running.[/warning]")
            return
        wallet_name = handle_bittensor_registration()
        if wallet_name:
            start_bittensor_miner(wallet_name)
    elif mode == 'miner':
        # Run Commune miner process.
        console.print("\n[info]Starting Commune Miner...[/info]")
        if not start_system():
            console.print("[error]Failed to start system process.[/error]")
            return
        if not start_polaris():
            console.print("[error]Failed to start API process.[/error]")
            stop_system()
            return
        console.print("[success]Commune miner processes started successfully.[/success]")
    else:
        console.print("[error]Unknown mode selected.[/error]")

@cli.command()
def stop():
    """Stop running processes."""
    if is_bittensor_running():
        if stop_bittensor_miner():
            console.print("[success]Bittensor miner stopped successfully.[/success]")
        else:
            console.print("[error]Failed to stop Bittensor miner.[/error]")
    else:
        if stop_polaris():
            console.print("[success]Commune miner processes stopped successfully.[/success]")
        else:
            console.print("[error]Failed to stop miner processes.[/error]")

@cli.command(name='status')
def status():
    """Check process status."""
    if is_bittensor_running():
        if (BITTENSOR_CONFIG_PATH / 'pids' / 'miner.pid').exists():
            console.print("[success]Bittensor miner is running.[/success]")
        else:
            console.print("[warning]Bittensor miner is not running.[/warning]")
    else:
        check_status()

@cli.command(name='monitor')
def monitor():
    """Monitor miner heartbeat signals in real-time."""
    monitor_heartbeat()

@cli.group(name='update')
def update():
    """Update various Polaris components."""
    pass

@update.command(name='subnet')
def update_subnet():
    """Update the Polaris repository."""
    if update_repository():
        console.print("[success]Repository update completed successfully.[/success]")
    else:
        console.print("[error]Failed to update repository.[/error]")
        exit(1)

@cli.command(name='check-main')
def check_main_command():
    """Check if main process is running and view its logs."""
    check_main()

@cli.command(name='logs')
def view_logs():
    """View logs for the running process."""
    if is_bittensor_running():
        log_file = BITTENSOR_CONFIG_PATH / 'logs' / 'miner.log'
        if not log_file.exists():
            console.print("[warning]No Bittensor miner logs found.[/warning]")
            return
        try:
            subprocess.run(['tail', '-f', str(log_file)], check=True)
        except KeyboardInterrupt:
            pass
    else:
        from .log_monitor import monitor_process_and_logs
        monitor_process_and_logs()

def start_heartbeat():
    """Start the heartbeat service to send regular status updates to the network."""
    try:
        console.print("[info]Starting Heartbeat service...[/info]")
        
        # Create necessary directories
        POLARIS_HOME.mkdir(exist_ok=True)
        logs_dir = POLARIS_HOME / 'logs'
        pids_dir = POLARIS_HOME / 'pids'
        logs_dir.mkdir(exist_ok=True)
        pids_dir.mkdir(exist_ok=True)
        
        # Set log file paths
        log_file = logs_dir / 'heartbeat.log'
        error_log = logs_dir / 'heartbeat_error.log'
        
        # Command to run the heartbeat service
        try:
            # Platform-specific process handling
            if sys.platform == 'darwin':  # macOS
                process = subprocess.Popen(
                    ['python', '-m', 'heart_beat.main'],
                    stdout=open(log_file, 'a'),
                    stderr=open(error_log, 'a')
                )
            else:  # Linux and other platforms
                process = subprocess.Popen(
                    ['python', '-m', 'heart_beat.main'],
                    stdout=open(log_file, 'a'),
                    stderr=open(error_log, 'a'),
                    preexec_fn=os.setpgrp
                )
            
            # Store the PID
            pid_file = pids_dir / 'heartbeat.pid'
            with open(pid_file, 'w') as f:
                f.write(str(process.pid))
            
            console.print(f"[success]Heartbeat service running on PID {process.pid}[/success]")
            console.print(f"[info]Heartbeat logs: {log_file} and {error_log}[/info]")
            return True
        except FileNotFoundError:
            # Try alternative method if heartbeat module is not found
            try:
                # Platform-specific process handling
                if sys.platform == 'darwin':  # macOS
                    process = subprocess.Popen(
                        ['python', '-m', 'heartbeat'],
                        stdout=open(log_file, 'a'),
                        stderr=open(error_log, 'a')
                    )
                else:  # Linux and other platforms
                    process = subprocess.Popen(
                        ['python', '-m', 'heartbeat'],
                        stdout=open(log_file, 'a'),
                        stderr=open(error_log, 'a'),
                        preexec_fn=os.setpgrp
                    )
                
                # Store the PID
                pid_file = pids_dir / 'heartbeat.pid'
                with open(pid_file, 'w') as f:
                    f.write(str(process.pid))
                
                console.print(f"[success]Heartbeat service running on PID {process.pid}[/success]")
                console.print(f"[info]Heartbeat logs: {log_file} and {error_log}[/info]")
                return True
            except Exception as e:
                console.print(f"[warning]Started Heartbeat service but couldn't determine its PID.[/warning]")
                console.print(f"[error]Failed to get process group ID for heartbeat: {str(e)}[/error]")
                return False
    except Exception as e:
        console.print(f"[error]Failed to start Heartbeat service: {str(e)}[/error]")
        return False

if __name__ == "__main__":
    cli()
