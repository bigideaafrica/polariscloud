# src/start.py

import os
import platform
import subprocess
import sys
import time

import psutil
from dotenv import load_dotenv
from rich.console import Console

from polaris_cli.repo_manager import ensure_repository_exists
from src.pid_manager import create_pid_file, create_pid_file_for_process
from src.pid_manager import read_pid
from src.pid_manager import read_pid as read_pid_specific
from src.pid_manager import remove_pid_file, remove_pid_file_for_process
from src.utils import configure_logging, get_project_root

# Initialize logging and console
logger = configure_logging()
console = Console()

# Define DETACHED_PROCESS flag for Windows
DETACHED_PROCESS = 0x00000008


def start_polaris():
    """
    Starts both main.py processes as background processes.
    """
    # Ensure the compute_subnet repository exists and get the path to compute_subnet/main.py
    success, compute_main_py = ensure_repository_exists()
    if not success:
        console.print("[red]Failed to ensure the compute_subnet repository is available.[/red]")
        sys.exit(1)
    
    # Load .env file
    env_path = os.path.join(get_project_root(), '.env')
    load_dotenv(dotenv_path=env_path)

    # Retrieve SSH_PASSWORD from environment
    SSH_PASSWORD = os.getenv('SSH_PASSWORD')
    if not SSH_PASSWORD:
        console.print("[red]SSH_PASSWORD not found in .env file.[/red]")
        sys.exit(1)

    # Start src/main.py
    start_process(
        process_name='polaris',
        script_path=os.path.join(get_project_root(), 'src', 'main.py'),
        env={'SSH_PASSWORD': SSH_PASSWORD},
        log_files=('polaris_stdout.log', 'polaris_stderr.log')
    )

    # Start compute_subnet/main.py
    start_process(
        process_name='compute_subnet',
        script_path=compute_main_py,
        env={'SSH_PASSWORD': SSH_PASSWORD},
        log_files=('compute_subnet_stdout.log', 'compute_subnet_stderr.log')
    )


def start_process(process_name, script_path, env, log_files):
    """
    Starts a single process with the given parameters.
    
    Args:
        process_name (str): Identifier for the process ('polaris' or 'compute_subnet').
        script_path (str): Absolute path to the main.py script to execute.
        env (dict): Environment variables to pass to the subprocess.
        log_files (tuple): Tuple containing paths for stdout and stderr logs.
    """
    # Check if the process is already running
    pid = read_pid_specific(process_name)
    if pid and psutil.pid_exists(pid):
        console.print(f"[red]{process_name} is already running with PID {pid}.[/red]")
        return

    # Define paths for log files
    log_dir = os.path.join(get_project_root(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    stdout_log = os.path.join(get_project_root(), 'logs', log_files[0])
    stderr_log = os.path.join(get_project_root(), 'logs', log_files[1])

    # Open log files
    try:
        stdout_f = open(stdout_log, 'a')
        stderr_f = open(stderr_log, 'a')
    except Exception as e:
        console.print(f"[red]Failed to open log files for {process_name}: {e}[/red]")
        logger.exception(f"Failed to open log files for {process_name}: {e}")
        sys.exit(1)

    # Prepare environment variables for the subprocess
    subprocess_env = os.environ.copy()
    subprocess_env.update(env)

    try:
        if platform.system() == 'Windows':
            # Windows-specific process creation with DETACHED_PROCESS
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=stdout_f,
                stderr=stderr_f,
                creationflags=DETACHED_PROCESS,
                env=subprocess_env,
                close_fds=True
            )
        else:
            # Unix/Linux-specific process creation
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=stdout_f,               # Redirect stdout to log file
                stderr=stderr_f,               # Redirect stderr to log file
                start_new_session=True,        # Detach the process from the parent
                cwd=os.path.dirname(script_path),  # Set working directory
                env=subprocess_env,
                close_fds=True
            )

        # Create PID file for the specific process
        if create_pid_file_for_process(process_name, process.pid):
            logger.info(f"Started {process_name} with PID: {process.pid}")
            console.print(f"[green]{process_name} started successfully with PID {process.pid}.[/green]")
            console.print(f"[blue]Logs: stdout -> {stdout_log}, stderr -> {stderr_log}[/blue]")
        else:
            console.print(f"[red]Failed to create PID file for {process_name}.[/red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Failed to start {process_name}: {e}[/red]")
        logger.exception(f"Failed to start {process_name}: {e}")
        sys.exit(1)


def stop_polaris():
    """
    Stops both running main.py processes using their PID files.
    """
    for process_name in ['polaris', 'compute_subnet']:
        pid = read_pid_specific(process_name)
        if not pid:
            console.print(f"[yellow]{process_name} is not running.[/yellow]")
            continue

        try:
            process = psutil.Process(pid)
            console.print(f"[yellow]Terminating {process_name} (PID {pid})...[/yellow]")
            process.terminate()

            try:
                process.wait(timeout=10)
                console.print(f"[green]{process_name} (PID {pid}) stopped successfully.[/green]")
            except psutil.TimeoutExpired:
                console.print(f"[yellow]{process_name} did not terminate gracefully. Forcing termination.[/yellow]")
                process.kill()
                process.wait()
                console.print(f"[green]{process_name} forcefully stopped.[/green]")
        except psutil.NoSuchProcess:
            console.print(f"[yellow]{process_name} process not found. Removing stale PID file.[/yellow]")
        except Exception as e:
            console.print(f"[red]Failed to stop {process_name}: {e}[/red]")
            logger.exception(f"Failed to stop {process_name}: {e}")
            continue

        # Remove PID file
        if remove_pid_file_for_process(process_name):
            logger.info(f"Removed PID file for {process_name}.")
        else:
            console.print(f"[red]Failed to remove PID file for {process_name}.[/red]")


def check_status():
    """
    Checks if both Polaris processes are running.
    """
    all_running = True
    for process_name in ['polaris', 'compute_subnet']:
        pid = read_pid_specific(process_name)
        if pid and psutil.pid_exists(pid):
            console.print(f"[green]{process_name} is running with PID {pid}.[/green]")
        else:
            console.print(f"[yellow]{process_name} is not running.[/yellow]")
            all_running = False
            # Optionally, remove stale PID files
            if pid:
                if remove_pid_file_for_process(process_name):
                    logger.info(f"Removed stale PID file for {process_name}.")
        # Short delay to prevent overwhelming the console
        time.sleep(0.1)

    if all_running:
        sys.exit(0)
    else:
        sys.exit(1)


def main():
    """
    Entry point for the CLI tool.
    """
    if len(sys.argv) != 2:
        console.print("[red]Usage: polaris [start|stop|status][/red]")
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
        console.print("[red]Usage: polaris [start|stop|status][/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
