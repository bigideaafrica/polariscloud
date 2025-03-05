"""
Command-line interface for Polaris.

This module provides the CLI commands for interacting with Polaris.
"""

import os
import sys
from pathlib import Path

import click
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

from polaris.miner.bittensor_miner import (
    start_bittensor_miner,
    stop_bittensor_miner,
    check_miner_status,
    is_bittensor_running
)
from polaris.utils.logging import get_logger

# Initialize console for rich output
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red",
    "success": "green"
})
console = Console(theme=custom_theme)

# Initialize logger
logger = get_logger('cli')


@click.group()
@click.version_option(package_name='polaris-subnet')
def cli():
    """
    Polaris - Modern Development Workspace Manager for Distributed Compute Resources
    
    This CLI tool helps you manage compute resources, monitor their status,
    and automate key tasks in a distributed environment.
    """
    pass


@cli.group()
def miner():
    """Manage Bittensor miners"""
    pass


@miner.command(name='start')
@click.option('--wallet', '-w', help='Wallet name to use for mining')
@click.option('--simulation', '-s', is_flag=True, help='Run in simulation mode without network connection')
def start_miner(wallet, simulation):
    """Start the Bittensor miner"""
    if not wallet:
        wallet = questionary.text("Enter wallet name:").ask()
        if not wallet:
            console.print("[error]Wallet name is required[/error]")
            return
    
    result = start_bittensor_miner(wallet, simulation_mode=simulation)
    if result:
        console.print(f"[success]Bittensor miner started with wallet '{wallet}'[/success]")
        if simulation:
            console.print("[info]Running in simulation mode - no actual mining will occur[/info]")
    else:
        console.print("[error]Failed to start Bittensor miner[/error]")


@miner.command(name='stop')
def stop_miner():
    """Stop the Bittensor miner"""
    result = stop_bittensor_miner()
    if result:
        console.print("[success]Bittensor miner stopped[/success]")
    else:
        console.print("[error]Failed to stop Bittensor miner[/error]")


@miner.command(name='status')
def miner_status():
    """Check the status of the Bittensor miner"""
    status = check_miner_status()
    
    table = Table(title="Bittensor Miner Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Running", "Yes" if status["running"] else "No")
    if status["running"]:
        table.add_row("PID", str(status["pid"]))
        if status["uptime"]:
            table.add_row("Uptime", status["uptime"])
    
    console.print(table)


@cli.group()
def validator():
    """Manage Bittensor validators"""
    pass


@validator.command(name='start')
@click.option('--wallet', '-w', help='Wallet name to use for validation')
def start_validator(wallet):
    """Start the Bittensor validator"""
    if not wallet:
        wallet = questionary.text("Enter wallet name:").ask()
        if not wallet:
            console.print("[error]Wallet name is required[/error]")
            return
    
    # Placeholder for validator start
    console.print("[info]Validator start not yet implemented[/info]")


@validator.command(name='stop')
def stop_validator():
    """Stop the Bittensor validator"""
    # Placeholder for validator stop
    console.print("[info]Validator stop not yet implemented[/info]")


@validator.command(name='status')
def validator_status():
    """Check the status of the Bittensor validator"""
    # Placeholder for validator status
    console.print("[info]Validator status not yet implemented[/info]")


@cli.group()
def wallet():
    """Manage Bittensor wallets"""
    pass


@wallet.command(name='list')
def list_wallets():
    """List available Bittensor wallets"""
    try:
        # Run bittensor CLI to list wallets
        import subprocess
        result = subprocess.run(
            ["btcli", "wallet", "list"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            console.print(result.stdout)
        else:
            console.print(f"[error]Failed to list wallets: {result.stderr}[/error]")
            
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/error]")


@wallet.command(name='create')
@click.option('--name', '-n', help='Wallet name')
def create_wallet(name):
    """Create a new Bittensor wallet"""
    if not name:
        name = questionary.text("Enter wallet name:").ask()
        if not name:
            console.print("[error]Wallet name is required[/error]")
            return
    
    try:
        # Run bittensor CLI to create wallet
        import subprocess
        result = subprocess.run(
            ["btcli", "wallet", "new", "--wallet.name", name], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            console.print(f"[success]Wallet '{name}' created successfully[/success]")
            console.print(result.stdout)
        else:
            console.print(f"[error]Failed to create wallet: {result.stderr}[/error]")
            
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/error]")


@cli.group()
def subnet():
    """Manage Bittensor subnets"""
    pass


@subnet.command(name='register')
@click.option('--wallet', '-w', help='Wallet name to register')
@click.option('--netuid', '-n', type=int, default=12, help='Subnet UID to register with')
@click.option('--pow', is_flag=True, help='Use proof of work for registration')
def register_subnet(wallet, netuid, pow):
    """Register a wallet with a Bittensor subnet"""
    if not wallet:
        wallet = questionary.text("Enter wallet name:").ask()
        if not wallet:
            console.print("[error]Wallet name is required[/error]")
            return
    
    try:
        # Prepare command
        cmd = ["btcli", "subnet", "register", "--wallet.name", wallet, "--netuid", str(netuid)]
        if pow:
            cmd.append("--pow")
        
        # Run bittensor CLI to register with subnet
        import subprocess
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            console.print(f"[success]Wallet '{wallet}' registered with subnet {netuid}[/success]")
            console.print(result.stdout)
        else:
            console.print(f"[error]Failed to register with subnet: {result.stderr}[/error]")
            
    except Exception as e:
        console.print(f"[error]Error: {str(e)}[/error]")


@cli.command()
def status():
    """Show overall system status"""
    # Miner status
    miner_running = is_bittensor_running()
    
    # Create status display
    table = Table(title="Polaris System Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    
    table.add_row("Bittensor Miner", "Running" if miner_running else "Stopped")
    table.add_row("Validator", "Status not available")
    
    console.print(table)


if __name__ == '__main__':
    cli() 