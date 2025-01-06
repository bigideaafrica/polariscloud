import json
import os
import signal
import sys
import time
from pathlib import Path
from typing import Optional

import typer
from communex.compat.key import classic_load_key
from loguru import logger
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from substrateinterface import Keypair

from validator.src.validator_node._config import ValidatorSettings
from validator.src.validator_node.base.utils import get_netuid
from validator.src.validator_node.validator_ import ValidatorNode

app = typer.Typer()
console = Console()

# Constants for status tracking
STATUS_FILE = Path.home() / '.polaris' / 'validator' / 'status.json'

def setup_logging():
    """Setup validator logging"""
    log_dir = os.path.join(os.path.expanduser('~'), '.polaris', 'validator', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'validator.log')
    
    logger.remove()  # Remove default handler
    logger.add(sys.stdout, level="INFO")
    logger.add(log_file, rotation="500 MB", level="DEBUG")
    return log_file

def update_status(status: str, error: str = None):
    """Update validator status file
    
    Args:
        status (str): Current status of the validator
        error (str, optional): Error message if any. Defaults to None.
    """
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    status_data = {
        "status": status,
        "timestamp": time.time(),
        "error": error
    }
    STATUS_FILE.write_text(json.dumps(status_data))

def cleanup(signal, frame):
    """Cleanup handler for graceful shutdown"""
    logger.info("Initiating cleanup process...")
    update_status("stopped")
    sys.exit(0)

def initialize_client(settings: ValidatorSettings):
    """Initialize the substrate client based on settings
    
    Args:
        settings (ValidatorSettings): Validator settings
        
    Returns:
        SubstrateInterface: Initialized substrate client
    """
    # This is a placeholder - implement actual client initialization
    # based on your specific needs
    return None

@app.command()
def main(
    wallet: str = typer.Option(..., help="Commune wallet name"),
    testnet: bool = typer.Option(False, help="Use testnet endpoints"),
    log_level: str = typer.Option("INFO", help="Logging level"),
    host: str = typer.Option("0.0.0.0", help="Host address to bind to"),
    port: int = typer.Option(8000, help="Port to listen on"),
    iteration_interval: int = typer.Option(800, help="Interval between validation iterations")
):
    """Main validator process
    
    This is the entry point for the validator node. It handles:
    - Logging setup
    - Key management
    - Validator initialization
    - Main validation loop
    - Graceful shutdown
    """
    # Setup signal handlers
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Initialize logging
    log_file = setup_logging()
    logger.info(f"Initialized logging to {log_file}")
    update_status("starting")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
        transient=False
    ) as progress:
        try:
            # Task for key loading
            key_task = progress.add_task("[cyan]Loading commune key...", total=1)
            
            # Load commune key
            try:
                key = classic_load_key(wallet)
                logger.info(f"Loaded key for wallet: {wallet}")
                progress.update(key_task, completed=1)
            except Exception as e:
                error_msg = f"Failed to load wallet key: {str(e)}"
                logger.error(error_msg)
                update_status("failed", error_msg)
                console.print(Panel(
                    f"[red]{error_msg}[/red]", 
                    title="Error", 
                    border_style="red",
                    box=box.HEAVY
                ))
                return

            # Task for validator initialization
            init_task = progress.add_task("[cyan]Initializing validator node...", total=1)
            
            try:
                # Initialize settings with command line parameters
                settings = ValidatorSettings(
                    use_testnet=testnet,
                    logging_level=log_level,
                    host=host,
                    port=port,
                    iteration_interval=iteration_interval
                )
                
                # Initialize the client
                client = initialize_client(settings)
                
                netuid = get_netuid(client)
                
                # Initialize validator node
                validator = ValidatorNode(
                    key=key,
                    netuid=netuid,  # Default netuid
                    client=client,
                    max_allowed_weights=settings.max_allowed_weights
                )
                progress.update(init_task, completed=1)
                
            except Exception as e:
                error_msg = f"Failed to initialize validator: {str(e)}"
                logger.error(error_msg)
                update_status("failed", error_msg)
                console.print(Panel(
                    f"[red]{error_msg}[/red]", 
                    title="Error", 
                    border_style="red",
                    box=box.HEAVY
                ))
                return

            # Task for startup
            startup_task = progress.add_task("[cyan]Starting validator process...", total=1)
            
            try:
                # Update status and show success message
                update_status("running")
                progress.update(startup_task, completed=1)
                
                console.print(Panel(
                    "[green]Validator successfully started![/green]\n"
                    f"[blue]Wallet: [white]{wallet}[/white][/blue]\n"
                    f"[blue]Network: [white]{'Testnet' if testnet else 'Mainnet'}[/white][/blue]\n"
                    f"[blue]Host: [white]{host}[/white][/blue]\n"
                    f"[blue]Port: [white]{port}[/white][/blue]",
                    title="Success",
                    border_style="green",
                    box=box.HEAVY
                ))

                # Main validation loop
                logger.info("Starting validation process...")
                while True:
                    validator.track_miner_containers()
                    time.sleep(settings.iteration_interval)

            except Exception as e:
                error_msg = f"Error in validation process: {str(e)}"
                logger.error(error_msg)
                update_status("failed", error_msg)
                console.print(Panel(
                    f"[red]{error_msg}[/red]", 
                    title="Error", 
                    border_style="red",
                    box=box.HEAVY
                ))
                return

        except KeyboardInterrupt:
            logger.info("Validator shutting down...")
            update_status("stopped")
            console.print("\n[yellow]Validator shutdown initiated by user[/yellow]")
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            update_status("failed", error_msg)
            console.print(Panel(
                f"[red]{error_msg}[/red]", 
                title="Error", 
                border_style="red",
                box=box.HEAVY
            ))
            raise

if __name__ == "__main__":
    app()
