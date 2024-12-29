# polaris_cli/cli.py

import click

from .register import register_miner
from .start import check_status, start_polaris, stop_polaris
from .view_pod import view_pod


@click.group()
def cli():
    """
    Polaris CLI - Modern Development Workspace Manager for Distributed Compute Resources
    """
    pass

@cli.command()
def register():
    """Register a new miner."""
    register_miner()

@cli.command(name='view-pod')
def view_pod_command():
    """View pod compute resources."""
    view_pod()

@cli.command()
def start():
    """Start Polaris as a background process."""
    start_polaris()

@cli.command()
def stop():
    """Stop the running Polaris background process."""
    stop_polaris()

@cli.command(name='status')
def status():
    """Check if Polaris is running."""
    check_status()

if __name__ == "__main__":
    cli()
