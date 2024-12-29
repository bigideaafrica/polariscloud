# polaris_cli/start.py

import os
import signal
import subprocess
import sys
import time

import psutil
from pid import PidFile, PidFileAlreadyRunningError, PidFileError
from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel

from src.pid_manager import PID_FILE
from src.utils import configure_logging

logger = configure_logging()
console = Console()

def start_polaris():
    """
    Starts the main.py process as a background process.
    """
    try:
        # Attempt to create a PID file; if it exists, the process is already running
        pidfile = PidFile(pidname='polaris-cli-tool', piddir=os.path.dirname(PID_FILE))
    except PidFileAlreadyRunningError:
        console.print("[red]Polaris is already running.[/red]")
        sys.exit(1)
    except PidFileError as e:
        console.print(f"[red]Failed to create PID file: {e}[/red]")
        sys.exit(1)
    
    # Launch main.py as a separate process
    try:
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'main.py')
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE  # For Windows to open in new console
        )
        # Write the PID to the PID file
        with open(PID_FILE, 'w') as f:
            f.write(str(process.pid))
        console.print("[green]Polaris started successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Failed to start Polaris: {e}[/red]")
        sys.exit(1)

def stop_polaris():
    """
    Stops the running main.py process using the PID file.
    """
    if not os.path.exists(PID_FILE):
        console.print("[yellow]Polaris is not running.[/yellow]")
        sys.exit(0)
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read())
    except Exception as e:
        console.print(f"[red]Failed to read PID file: {e}[/red]")
        sys.exit(1)
    
    try:
        # Terminate the process
        os.kill(pid, signal.SIGTERM)
        # Optionally, wait for the process to terminate
        time.sleep(2)
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        console.print("[green]Polaris stopped successfully.[/green]")
    except ProcessLookupError:
        console.print("[yellow]Polaris process not found. Removing stale PID file.[/yellow]")
        os.remove(PID_FILE)
    except Exception as e:
        console.print(f"[red]Failed to stop Polaris: {e}[/red]")
        sys.exit(1)

def check_status():
    """
    Checks if the Polaris background process is running.
    """
    if not os.path.exists(PID_FILE):
        console.print("[yellow]Polaris is not running.[/yellow]")
        sys.exit(0)
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read())
    except Exception as e:
        console.print(f"[red]Failed to read PID file: {e}[/red]")
        sys.exit(1)
    
    try:
        process = psutil.Process(pid)
        if process.is_running() and process.status() != psutil.STATUS_ZOMBIE:
            console.print("[green]Polaris is currently running.[/green]")
        else:
            console.print("[yellow]Polaris process is not running. Removing stale PID file.[/yellow]")
            os.remove(PID_FILE)
            sys.exit(0)
    except psutil.NoSuchProcess:
        console.print("[yellow]Polaris process not found. Removing stale PID file.[/yellow]")
        os.remove(PID_FILE)
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error checking Polaris status: {e}[/red]")
        sys.exit(1)
