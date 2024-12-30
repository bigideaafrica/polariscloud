# polaris_cli/start.py

import os
import platform  # Import platform module for OS detection
import signal
import subprocess
import sys

import psutil
from dotenv import load_dotenv  # Ensure you have python-dotenv installed
from pid import PidFile, PidFileAlreadyRunningError, PidFileError
from rich.console import Console

from src.pid_manager import PID_FILE
from src.utils import configure_logging

logger = configure_logging()
console = Console()

def start_polaris():
    """
    Starts the main.py process as a background process.
    """
    # Load .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(dotenv_path=env_path)

    # Retrieve SSH_PASSWORD from environment
    SSH_PASSWORD = os.getenv('SSH_PASSWORD')
    if not SSH_PASSWORD:
        console.print("[red]SSH_PASSWORD not found in .env file.[/red]")
        sys.exit(1)

    try:
        # Attempt to create a PID file; if it exists, the process is already running
        pidfile = PidFile(pidname='polaris-cli-tool', piddir=os.path.dirname(PID_FILE))
    except PidFileAlreadyRunningError:
        console.print("[red]Polaris is already running.[/red]")
        sys.exit(1)
    except PidFileError as e:
        console.print(f"[red]Failed to create PID file: {e}[/red]")
        sys.exit(1)
    
    # Determine the operating system
    current_os = platform.system()
    
    if current_os != 'Windows':
        # Prompt for sudo password on Linux
        console.print("[yellow]Polaris requires elevated privileges to run on Linux.[/yellow]")
        console.print("[yellow]Please enter your sudo password when prompted.[/yellow]")
        try:
            # Execute 'sudo -v' to prompt for password and validate sudo access
            subprocess.run(['sudo', '-v'], check=True)
        except subprocess.CalledProcessError:
            console.print("[red]Failed to authenticate with sudo. Please try again.[/red]")
            sys.exit(1)
    
    # Launch main.py as a separate process
    try:
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'src',
            'main.py'
        )
        
        # Ensure the script path exists
        if not os.path.exists(script_path):
            console.print(f"[red]main.py not found at {script_path}[/red]")
            sys.exit(1)
        
        # Define paths for log files
        log_dir = os.path.join(os.path.dirname(script_path), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        stdout_log = os.path.join(log_dir, 'polaris_stdout.log')
        stderr_log = os.path.join(log_dir, 'polaris_stderr.log')
        
        # Open log files
        stdout_f = open(stdout_log, 'a')
        stderr_f = open(stderr_log, 'a')
        
        # Prepare environment variables for the subprocess
        env = os.environ.copy()
        env['SSH_PASSWORD'] = SSH_PASSWORD  # Pass SSH_PASSWORD to main.py
        
        if current_os == 'Windows':
            # Windows-specific process creation
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=stdout_f,
                stderr=stderr_f,
                creationflags=subprocess.CREATE_NEW_CONSOLE,  # Open in new console window
                env=env
            )
        else:
            # Unix/Linux-specific process creation
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=stdout_f,               # Redirect stdout to log file
                stderr=stderr_f,               # Redirect stderr to log file
                start_new_session=True,        # Detach the process from the parent
                cwd=os.path.dirname(script_path),  # Set working directory
                env=env
            )
        
        # Write the PID to the PID file
        with open(PID_FILE, 'w') as f:
            f.write(str(process.pid))
        
        console.print("[green]Polaris started successfully.[/green]")
        console.print(f"[blue]PID: {process.pid}[/blue]")
        console.print(f"[blue]Logs: stdout -> {stdout_log}, stderr -> {stderr_log}[/blue]")
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
        # Terminate the process gracefully
        os.kill(pid, signal.SIGTERM)
        # Optionally, wait for the process to terminate
        time.sleep(2)
        
        # Check if the process has terminated
        if psutil.pid_exists(pid):
            console.print("[yellow]Polaris did not terminate gracefully. Forcing termination.[/yellow]")
            os.kill(pid, signal.SIGKILL)
            time.sleep(1)
        
        # Remove the PID file
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

def main():
    """
    Entry point for the CLI tool.
    """
    if len(sys.argv) != 2:
        console.print("[red]Usage: polaris [start|stop|status|register|view-pod][/red]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        start_polaris()
    elif command == 'stop':
        stop_polaris()
    elif command == 'status':
        check_status()
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
        console.print("[red]Usage: polaris [start|stop|status|register|view-pod][/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
