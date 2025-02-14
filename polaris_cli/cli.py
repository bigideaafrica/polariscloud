# polaris_cli/cli.py
import json
import os
import subprocess
import sys
from pathlib import Path
import requests

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

# ----------------- Bittensor Registration Flow -----------------
def handle_bittensor_registration():
    """
    Handle the Bittensor wallet creation and registration process.
    Properly validates registration success and balance requirements.
    """
    console.print(Panel(
        "[cyan]Bittensor Wallet Configuration[/cyan]\n"
        "[yellow]You'll need a wallet to participate in the Bittensor subnet[/yellow]",
        box=box.ROUNDED,
        title="Bittensor Setup"
    ))
    
    has_wallet = questionary.confirm(
        "Do you already have a Bittensor wallet?",
        style=custom_style
    ).ask()
    
    if has_wallet:
        while True:
            wallet_name = questionary.text(
                "Enter your existing wallet name:",
                style=custom_style
            ).ask()
            
            if not wallet_name or not wallet_name.strip():
                console.print("[error]Wallet name cannot be empty. Please enter a valid name.[/error]")
                continue
                
            # Verify wallet exists
            try:
                result = subprocess.run(
                    ['btcli', 'wallet', 'list'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                if wallet_name in result.stdout:
                    break
                else:
                    console.print("[error]Wallet not found. Please check the name and try again.[/error]")
            except subprocess.CalledProcessError as e:
                console.print(f"[error]Error checking wallet: {str(e)}[/error]")
                return None
    else:
        while True:
            wallet_name = questionary.text(
                "Enter a name for your new wallet:",
                style=custom_style
            ).ask()
            
            if not wallet_name or not wallet_name.strip():
                console.print("[error]Wallet name cannot be empty. Please enter a valid name.[/error]")
                continue
            
            console.print("\n[info]Creating new coldkey...[/info]")
            try:
                # Create coldkey
                subprocess.run([
                    'btcli', 'wallet', 'new_coldkey',
                    '--wallet.name', wallet_name
                ], check=True)
                
                console.print("[info]Creating new hotkey...[/info]")
                # Create hotkey
                subprocess.run([
                    'btcli', 'wallet', 'new_hotkey',
                    '--wallet.name', wallet_name,
                    '--wallet.hotkey', 'default'
                ], check=True)
                
                console.print("[success]Wallet created successfully![/success]")
                break
            except subprocess.CalledProcessError as e:
                console.print(f"[error]Failed to create wallet: {str(e)}[/error]")
                return None
    
    # Check balance before attempting registration
    try:
        balance_result = subprocess.run(
            [
                'btcli', 'wallet', 'balance',
                '--wallet.name', wallet_name,
                '--subtensor.network', 'finney'
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse balance from output
        if "Insufficient balance" in balance_result.stdout or "0.0000" in balance_result.stdout:
            console.print("[error]Insufficient balance to register neuron.[/error]")
            console.print("[info]Please ensure your wallet has enough TAO tokens before registering.[/info]")
            return None
            
    except subprocess.CalledProcessError as e:
        console.print(f"[error]Error checking wallet balance: {str(e)}[/error]")
        return None
    
    # Register on subnet
    console.print("\n[info]Registering on subnet (this may take a few minutes)...[/info]")
    try:
        registration_result = subprocess.run(
            [
                'btcli', 'subnet', 'register',
                '--netuid', '12',
                '--subtensor.network', 'finney',
                '--wallet.name', wallet_name,
                '--wallet.hotkey', 'default'
            ],
            capture_output=True,
            text=True
        )
        
        # Check for specific error conditions in the output
        if "Insufficient balance" in registration_result.stdout:
            console.print("[error]Insufficient balance to register neuron.[/error]")
            console.print("[info]Please ensure your wallet has enough TAO tokens before registering.[/info]")
            return None
            
        if registration_result.returncode != 0:
            console.print(f"[error]Registration failed: {registration_result.stdout}[/error]")
            return None
            
        if "Successfully registered" not in registration_result.stdout:
            console.print("[error]Registration was not successful.[/error]")
            return None
            
        console.print("[success]Successfully registered on subnet![/success]")
        
    except subprocess.CalledProcessError as e:
        console.print(f"[error]Failed to register on subnet: {str(e)}[/error]")
        return None
    
    # Only proceed with server registration and config if Bittensor registration succeeded
    try:
        response = requests.post(SERVER_ENDPOINT, json={
            'wallet_name': wallet_name,
            'netuid': 12,
            'status': 'registered'
        })
        if response.status_code == 200:
            console.print("[success]Successfully registered with server![/success]")
        else:
            console.print("[warning]Failed to register with server. Continuing anyway...[/warning]")
    except requests.RequestException:
        console.print("[warning]Failed to register with server. Continuing anyway...[/warning]")
    
    # Save wallet configuration
    config = {
        'wallet_name': wallet_name,
        'netuid': 12,
        'network': 'finney'
    }
    with open(BITTENSOR_CONFIG_PATH / 'config.json', 'w') as f:
        json.dump(config, f)
    console.print("[success]Configuration saved successfully![/success]")
    
    return wallet_name

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
    """Register a new miner."""
    reg_type = select_registration_type()
    if "bittensor" in reg_type:
        # For Bittensor registration, run the Bittensor registration flow.
        wallet_name = handle_bittensor_registration()
        if wallet_name:
            console.print("[success]Bittensor miner registration complete.[/success]")
    else:
        # For Commune registration, call the existing commune registration.
        commune_register()

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

if __name__ == "__main__":
    cli()
