# src/cli.py

import click

from .log_monitor import check_main
from .register import register_miner
from .repo_manager import update_repository
from .start import check_status, start_polaris, stop_polaris
from .view_pod import view_pod


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
    """Start Polaris and Compute Subnet as background processes."""
    start_polaris()

@cli.command()
def stop():
    """Stop Polaris and Compute Subnet background processes."""
    stop_polaris()

@cli.command(name='status')
def status():
    """Check if Polaris and Compute Subnet are running."""
    check_status()

@cli.group(name='update')
def update():
    """Update various Polaris components."""
    pass

@update.command(name='subnet')
def update_subnet():
    """Update the Polaris subnet repository."""
    if update_repository():
        click.echo("Subnet repository update completed successfully.")
    else:
        click.echo("Failed to update subnet repository.", err=True)
        exit(1)

@cli.command(name='check-main')
def check_main_command():
    """Check if main process is running and view its logs."""
    check_main()

@cli.command(name='logs')
def view_logs():
    """View logs without process monitoring."""
    from .log_monitor import monitor_process_and_logs
    monitor_process_and_logs()

if __name__ == "__main__":
    cli()
