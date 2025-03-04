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
from rich.table import Table
from rich.theme import Theme

from .heartbeat_monitor import monitor_heartbeat
from .log_monitor import check_main
from .repo_manager import update_repository
from .start import (check_status, start_polaris, start_system, stop_polaris,
                    stop_system)
from .bittensor_miner import start_bittensor_miner, stop_bittensor_miner, is_bittensor_running
from .register import load_system_info, display_system_info, register_miner as commune_register, register_independent_miner

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red",
    "success": "green"
})

console = Console(theme=custom_theme)

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
SERVER_ENDPOINT = "https://orchestrator-gekh.onrender.com/api/v1/miners"

def setup_directories():
    """Create necessary directories if they don't exist"""
    POLARIS_HOME.mkdir(exist_ok=True)
    BITTENSOR_CONFIG_PATH.mkdir(exist_ok=True)
    (BITTENSOR_CONFIG_PATH / 'pids').mkdir(exist_ok=True)
    (BITTENSOR_CONFIG_PATH / 'logs').mkdir(exist_ok=True)

def display_dashboard():
    """Display the dashboard with fixed-width panels, matching the screenshot as closely as possible."""
    polaris_logo = r"""
      ____        __            _     
     / __ \____  / /___ _______(_)____
    / /_/ / __ \/ / __ `/ ___/ / ___/
   / ____/ /_/ / / /_/ / /  / (__  ) 
  /_/    \____/_/\__,_/_/  /_/____/  
    """
    header_panel = Panel(
        f"[cyan]{polaris_logo}[/cyan]\n"
        "[bold white]♦ The Best Place to List Your GPUs ♦[/bold white]\n\n"
        "[purple]Welcome to the Polaris Compute Subnet![/purple]\n\n"
        "[bold white]♦ Our Mission is to be the Best Place on This Planet to List Your GPUs – We're just getting started! ♦[/bold white]",
        title="[bold cyan]POLARIS SUBNET[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        width=100
    )
    console.print(header_panel, justify="center")
    console.print("[cyan]Powering GPU Computation[/cyan]", justify="center")
    table = Table(show_header=False, show_lines=True, box=box.ROUNDED, width=150)
    table.add_column(justify="left")
    table.add_column(justify="left")
    setup_commands = (
        "[bold cyan]Setup Commands[/bold cyan]\n"
        "• [bold]register[/bold] – Register as a new miner (required before starting)\n"
        "• [bold]update subnet[/bold] – Update the Polaris repository"
    )
    service_management = (
        "[bold cyan]Service Management[/bold cyan]\n"
        "• [bold]start[/bold] – Start Polaris and selected compute processes\n"
        "• [bold]stop[/bold] – Stop running processes\n"
        "• [bold]status[/bold] – Check if services are running"
    )
    monitoring_logs = (
        "[bold cyan]Monitoring & Logs[/bold cyan]\n"
        "• [bold]logs[/bold] – View logs without process monitoring\n"
        "• [bold]monitor[/bold] – Monitor miner heartbeat signals in real-time\n"
        "• [bold]check-main[/bold] – Check if main process is running and view its logs\n"
        "• [bold]view-compute[/bold] – View pod compute resources"
    )
    bittensor_integration = (
        "[bold cyan]Bittensor Integration[/bold cyan]\n"
        "Polaris integrates with Bittensor to provide a decentralized compute subnet\n"
        "• [bold]Wallet Management[/bold] – Create or use existing Bittensor wallets\n"
        "• [bold]Validator Mode[/bold] – Run as a Bittensor subnet validator\n"
        "• [bold]Network Registration[/bold] – Register with Bittensor network (netuid 12)\n"
        "• [bold]Heartbeat Service[/bold] – Maintain connection with the Bittensor network"
    )
    table.add_row(setup_commands, service_management)
    table.add_row(monitoring_logs, bittensor_integration)
    combined_panel = Panel(table, border_style="cyan", box=box.ROUNDED, width=150)
    console.print(combined_panel, justify="center")
    bottom_panel = Panel(
    "1. First register as a miner\n"
    "2. Then start your preferred service type\n"
    "3. Check status to verify everything is running\n"
    "4. Use logs to monitor operation\n"
    "5. Use stop when you want to shut down services\n\n"
    "[bold white]Examples:[/bold white]\n"
    "$ [magenta]polaris register[/magenta] – Register as a new miner\n"
    "$ [magenta]polaris start[/magenta] – Start the Polaris services\n"
    "$ [magenta]polaris status[/magenta] – Check which services are running\n"
    "$ [magenta]polaris stop[/magenta] – Stop running services\n"
    "$ [magenta]polaris logs[/magenta] – View service logs",
    border_style="cyan",
    box=box.ROUNDED,
    width=150,
    title="[bold cyan]Quick Start Guide[/bold cyan]",
    title_align="center"
    )
    console.print(bottom_panel, justify="start")

def setup_directories():
    POLARIS_HOME.mkdir(exist_ok=True)
    BITTENSOR_CONFIG_PATH.mkdir(exist_ok=True)
    (BITTENSOR_CONFIG_PATH / 'pids').mkdir(exist_ok=True)
    (BITTENSOR_CONFIG_PATH / 'logs').mkdir(exist_ok=True)

def display_registration_summary(wallet_name, hotkey, network_name, netuid):
    console.print(Panel(
        f"[cyan]Registration Summary[/cyan]\n\n"
        f"Wallet: [bold green]{wallet_name}[/bold green]\n"
        f"Hotkey: [bold green]{hotkey}[/bold green]\n"
        f"Network: [bold green]{network_name} (netuid {netuid})[/bold green]\n\n"
        "[yellow]Proceeding to start Polaris services...[/yellow]",
        title="✅ Registration Complete",
        border_style="green"
    ))

def select_registration_type():
    choices = [
        'Commune Miner Node',
        'Bittensor Miner Node',
        'Polaris Miner Node (Coming Soon)',
        'Independent Miner'
    ]
    answer = questionary.select(
        "Select registration type:",
        choices=choices,
        style=custom_style,
        qmark="🔑"
    ).ask()
    return answer.lower() if answer else ""

@click.group()
def cli():
    setup_directories()
    pass

@cli.command()
def register():
    from src.user_manager import UserManager
    user_manager = UserManager()
    skip_registration, user_info = user_manager.check_existing_registration(show_prompt=True)
    if skip_registration:
        console.print("[yellow]Using existing registration.[/yellow]")
        return
    reg_type = select_registration_type()
    if "bittensor" in reg_type:
        handle_bittensor_registration()
    elif "commune" in reg_type:
        commune_register(skip_existing_check=True)
    elif "polaris" in reg_type:
        console.print(Panel(
            "[yellow]Polaris Miner Node is coming soon![/yellow]",
            title="🚧 Coming Soon",
            border_style="yellow"
        ))
    elif "independent" in reg_type:
        register_independent_miner(skip_existing_check=True)
    else:
        console.print("[error]Invalid registration type selected.[/error]")

def handle_bittensor_registration():
    console.print(Panel(
        "[cyan]Bittensor Wallet Configuration[/cyan]\n"
        "[yellow]You'll need a wallet to participate in the Bittensor subnet[/yellow]",
        box=box.ROUNDED,
        title="Bittensor Setup"
    ))

    # Check if user already has a wallet
    has_wallet = questionary.confirm(
        "Do you already have a Bittensor wallet?",
        style=custom_style
    ).ask()

    if has_wallet:
        try:
            result = subprocess.run(
                ['btcli', 'wallet', 'list'],
                capture_output=True,
                text=True,
                check=True
            )
            wallets = parse_wallet_list(result.stdout)
            
            if not wallets:
                console.print("[error]No wallets found. Please create a new wallet.[/error]")
                selected_wallet_name = create_new_wallet()
                if not selected_wallet_name:
                    return  # Stop execution
            
            else:
                wallet_names = list(wallets.keys())
                selected_wallet_name = questionary.select(
                    "Select your wallet (cold key):",
                    choices=wallet_names,
                    style=custom_style
                ).ask()
                
                if not selected_wallet_name:
                    console.print("[error]No wallet selected. Exiting.[/error]")
                    return  # Stop execution
                
                hotkeys = wallets[selected_wallet_name]
                selected_hotkey = questionary.select(
                    "Select a hotkey:",
                    choices=hotkeys,
                    style=custom_style
                ).ask()
                
                if not selected_hotkey:
                    console.print("[error]No hotkey selected. Exiting.[/error]")
                    return  # Stop execution
                
        except subprocess.CalledProcessError as e:
            console.print(f"[error]Error listing wallets: {str(e)}[/error]")
            return  # Stop execution

    else:
        selected_wallet_name = create_new_wallet()
        if not selected_wallet_name:
            return  # Stop execution
        selected_hotkey = "default"

    # Select the network
    network_choice = questionary.select(
        "Select the network to register on:",
        choices=["Mainnet (netuid 100)", "Testnet (netuid 12)"],
        style=custom_style
    ).ask()
    
    if not network_choice:
        console.print("[error]No network selected. Exiting.[/error]")
        return  # Stop execution

    netuid = 100 if "Mainnet" in network_choice else 12
    network_name = "Mainnet" if netuid == 100 else "Testnet"

    console.print(Panel(
        f"[cyan]Registering on {network_name} (netuid {netuid})[/cyan]\n"
        "[yellow]This may take a few minutes...[/yellow]",
        box=box.ROUNDED,
        title="Network Registration"
    ))

    # Attempt registration
    wallet, message = register_wallet(selected_wallet_name, selected_hotkey, netuid)

    if not wallet:
        console.print(f"[error]Registration failed: {message}[/error]")
        console.print("[red]Stopping execution.[/red]")
        return  # Stop execution immediately

    # Load system info only if registration was successful
    system_info = load_system_info()
    if system_info:
        display_system_info(system_info)
        display_registration_summary(selected_wallet_name, selected_hotkey, network_name, netuid)

        # Start Polaris only if registration succeeded
        if start_polaris():
            console.print("[success]Polaris services started successfully![/success]")
        else:
            console.print("[error]Failed to start Polaris services.[/error]")

def parse_wallet_list(wallet_list_output):
    wallets = {}
    current_wallet = None
    for line in wallet_list_output.splitlines():
        line = line.strip()
        if not line or line == "Wallets":
            continue
        if "Coldkey" in line:
            parts = line.split("Coldkey")
            if len(parts) > 1:
                parts = parts[1].strip().split()
                if parts:
                    wallet_name = parts[0]
                    current_wallet = wallet_name
                    wallets[current_wallet] = []
        elif "Hotkey" in line and current_wallet:
            parts = line.split("Hotkey")
            if len(parts) > 1:
                parts = parts[1].strip().split()
                if parts:
                    hotkey_name = parts[0]
                    wallets[current_wallet].append(hotkey_name)
    return wallets

def create_new_wallet():
    console.print(Panel(
        "[cyan]Creating a New Bittensor Wallet[/cyan]\n"
        "[yellow]You will need to provide a name for your new wallet.[/yellow]",
        box=box.ROUNDED,
        title="Wallet Creation"
    ))
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
            subprocess.run([
                'btcli', 'wallet', 'new_coldkey',
                '--wallet.name', wallet_name
            ], check=True)
            console.print("[info]Creating new hotkey...[/info]")
            subprocess.run([
                'btcli', 'wallet', 'new_hotkey',
                '--wallet.name', wallet_name,
                '--wallet.hotkey', 'default'
            ], check=True)
            console.print("[success]Wallet created successfully![/success]")
            return wallet_name
        except subprocess.CalledProcessError as e:
            console.print(f"[error]Failed to create wallet: {str(e)}[/error]")
            return None

def register_wallet(wallet_name, hotkey, netuid):
    network = "finney" if netuid == 100 else "local"
    network_name = "Mainnet" if netuid == 100 else "Testnet"

    console.print(f"\n[info]Registering on {network_name} subnet (netuid={netuid}) (this may take a few minutes)...[/info]")

    try:
        registration_result = subprocess.run(
            [
                'btcli', 'subnet', 'register',
                '--netuid', str(netuid),
                '--subtensor.network', network,
                '--wallet.name', wallet_name,
                '--wallet.hotkey', hotkey
            ],
            capture_output=True,
            text=True
        )

        if "Insufficient balance" in registration_result.stdout:
            console.print("[error]Insufficient balance to register neuron.[/error]")
            return None, "Insufficient balance"

        if registration_result.returncode != 0:
            console.print(f"[error]Registration failed: {registration_result.stdout}[/error]")
            return None, registration_result.stdout  # STOP HERE

        if "Successfully registered" not in registration_result.stdout:
            console.print("[error]Registration was not successful.[/error]")
            return None, registration_result.stdout  # STOP HERE

        console.print("[success]Successfully registered on subnet![/success]")
        return wallet_name, "Success"

    except subprocess.CalledProcessError as e:
        console.print(f"[error]Failed to register on subnet: {str(e)}[/error]")
        return None, str(e)  # STOP HERE

def select_start_mode():
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

@cli.command()
def start():
    mode = select_start_mode()
    if mode == 'validator':
        if is_bittensor_running():
            console.print("[warning]Bittensor miner is already running.[/warning]")
            return
        wallet_name = handle_bittensor_registration()
        if wallet_name:
            if start_bittensor_miner(wallet_name):
                console.print("[success]Bittensor miner started successfully![/success]")
                display_dashboard()
            else:
                console.print("[error]Failed to start Bittensor miner.[/error]")
    elif mode == 'miner':
        console.print("\n[info]Starting Commune Miner...[/info]")
        if not start_system():
            console.print("[error]Failed to start system process.[/error]")
            return
        if not start_polaris():
            console.print("[error]Failed to start API process.[/error]")
            stop_system()
            return
        console.print("[success]Commune miner processes started successfully![/success]")
        display_dashboard()
    else:
        console.print("[error]Unknown mode selected.[/error]")

@cli.command()
def stop():
    if is_bittensor_running():
        if stop_bittensor_miner():
            console.print("[success]Bittensor miner stopped successfully.[/success]")
        else:
            console.print("[error]Failed to stop Bittensor miner.[/error]")
    else:
        if stop_polaris():
            console.print("[success]Commune miner processes stopped successfully![/success]")
        else:
            console.print("[error]Failed to stop miner processes.[/error]")

@cli.command(name='status')
def status():
    if is_bittensor_running():
        if (BITTENSOR_CONFIG_PATH / 'pids' / 'miner.pid').exists():
            console.print("[success]Bittensor miner is running.[/success]")
        else:
            console.print("[warning]Bittensor miner is not running.[/warning]")
    else:
        check_status()

@cli.command(name='monitor')
def monitor():
    monitor_heartbeat()

@cli.group(name='update')
def update():
    pass

@update.command(name='subnet')
def update_subnet():
    if update_repository():
        console.print("[success]Repository update completed successfully.[/success]")
    else:
        console.print("[error]Failed to update repository.[/error]")
        exit(1)

@cli.command(name='check-main')
def check_main_command():
    check_main()

@cli.command(name='logs')
def view_logs():
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
