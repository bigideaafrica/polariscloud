# polaris_cli/cli.py

from pathlib import Path

import click
import questionary
from questionary import Style
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

from .heartbeat_monitor import monitor_heartbeat
from .log_monitor import check_main
from .register import register_miner
from .repo_manager import update_repository
from .start import (check_status, start_polaris, start_system, stop_polaris,
                    stop_system)
from .val_start import check_validator_status, start_validator, stop_validator
from .view_pod import view_pod

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

def get_wallet_info():
    """Get commune wallet information from user"""
    console.print(Panel(
        "[cyan]Please enter your Commune wallet name[/cyan]\n"
        "[yellow]Note: This wallet must be registered under the validator subnet[/yellow]",
        box=box.ROUNDED,
        title="Wallet Configuration"
    ))
    
    wallet_name = questionary.text(
        "Enter your wallet name:",
        style=custom_style,
        validate=lambda x: len(x) > 0
    ).ask()

    if not wallet_name:
        console.print("[error]Wallet name cannot be empty.[/error]")
        return None

    return wallet_name

def is_validator_running():
    """Check if validator process is running"""
    validator_pid = Path.home() / '.polaris' / 'validator' / 'pids' / 'validator.pid'
    return validator_pid.exists()

def select_subnet():
    """Interactive selection using arrow keys"""
    choices = [
        '🖥️  Miner',
        '🔐 Validator'
    ]
    
    answer = questionary.select(
        "Select node type:",
        choices=choices,
        style=custom_style,
        qmark="🚀"
    ).ask()
    
    return 'validator' if '🔐 Validator' in answer else 'miner'

@click.group()
def cli():
    """Polaris CLI - Modern Development Workspace Manager for Distributed Compute Resources"""
    pass

@cli.command()
def register():
    """Register a new miner."""
    register_miner()

@cli.command(name='view-compute')
def view_pod_command():
    """View pod compute resources."""
    view_pod()

@cli.command()
def start():
    """Start Polaris and selected compute processes."""
    console.print("\n[info]Welcome to Polaris Compute Subnet![/info]")
    subnet_type = select_subnet()
    
    if subnet_type == 'validator':
        wallet_name = get_wallet_info()
        if wallet_name:
            start_validator(wallet_name)
    else:
        console.print("\n[info]Starting Miner...[/info]")
        # Start the system process first
        if not start_system():
            console.print("[error]Failed to start system process.[/error]")
            return
            
        # Then start the API process
        if not start_polaris():
            console.print("[error]Failed to start API process.[/error]")
            # Stop the system process if API fails
            stop_system()
            return
            
        console.print("[success]Miner processes started successfully.[/success]")

@cli.command()
def stop():
    """Stop running processes."""
    if is_validator_running():
        if stop_validator():
            console.print("[success]Validator stopped successfully.[/success]")
        else:
            console.print("[error]Failed to stop validator.[/error]")
    else:
        if stop_polaris():
            console.print("[success]Miner processes stopped successfully.[/success]")
        else:
            console.print("[error]Failed to stop miner processes.[/error]")

@cli.command(name='status')
def status():
    """Check process status."""
    if is_validator_running():
        check_validator_status()
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
    
@cli.command(name='val-logs')
def monitor_validator():
    """Monitor validator logs and performance in real-time."""
    from .validator_monitor import monitor_validator_logs
    monitor_validator_logs()

@cli.command(name='logs')
def view_logs():
    """View logs for the running process."""
    if is_validator_running():
        log_file = Path.home() / '.polaris' / 'validator' / 'logs' / 'validator.log'
        if not log_file.exists():
            console.print("[warning]No validator logs found.[/warning]")
            return
        try:
            import subprocess
            subprocess.run(['tail', '-f', str(log_file)], check=True)
        except KeyboardInterrupt:
            pass
    else:
        from .log_monitor import monitor_process_and_logs
        monitor_process_and_logs()

if __name__ == "__main__":
    cli()