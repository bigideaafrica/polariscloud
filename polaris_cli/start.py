# polaris_cli/start.py
import ctypes
import logging
import os
import platform
import signal
import subprocess
import sys
import time
from pathlib import Path

import psutil
from dotenv import load_dotenv
from rich.console import Console

from polaris_cli.repo_manager import (ensure_repository_exists, get_repo_path,
                                      start_server, update_repository)

# Initialize logging and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('polaris.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
console = Console()

# Constants
DETACHED_PROCESS = 0x00000008 if platform.system() == 'Windows' else 0
PID_DIR = os.path.join(os.path.expanduser('~'), '.polaris', 'pids')

def is_admin():
    """Check if the current process has admin privileges"""
    try:
        if platform.system() == 'Windows':
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except:
        return False

def elevate_privileges():
    """Restart the current script with elevated privileges"""
    if platform.system() == 'Windows':
        script = os.path.abspath(sys.argv[0])
        params = ' '.join(sys.argv[1:])
        
        try:
            if not is_admin():
                ctypes.windll.shell32.ShellExecuteW(
                    None, 
                    "runas",
                    sys.executable,
                    f'"{script}" {params}',
                    None,
                    1
                )
                sys.exit()
        except Exception as e:
            logger.error(f"Failed to elevate privileges: {e}")
            return False
    else:
        if not is_admin():
            script = os.path.abspath(sys.argv[0])
            params = ' '.join(sys.argv[1:])
            
            try:
                cmd = ['sudo', sys.executable, script]
                if params:
                    cmd.extend(params.split())
                subprocess.run(cmd, check=True)
                sys.exit()
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to elevate privileges: {e}")
                return False
    return True

def get_project_root():
    """Get the project root directory"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ensure_pid_directory():
    """Ensure PID directory exists"""
    os.makedirs(PID_DIR, exist_ok=True)

def get_pid_file(process_name):
    """Get path to PID file for given process"""
    return os.path.join(PID_DIR, f"{process_name}.pid")

def create_pid_file(process_name, pid):
    """Create PID file for a process"""
    try:
        with open(get_pid_file(process_name), 'w') as f:
            f.write(str(pid))
        logger.info(f"PID file for '{process_name}' created with PID: {pid}")
        return True
    except Exception as e:
        logger.error(f"Failed to create PID file for {process_name}: {e}")
        return False

def read_pid(process_name):
    """Read PID from PID file"""
    try:
        with open(get_pid_file(process_name), 'r') as f:
            return int(f.read().strip())
    except:
        return None

def remove_pid_file(process_name):
    """Remove PID file for a process"""
    try:
        os.remove(get_pid_file(process_name))
        return True
    except FileNotFoundError:
        logger.warning(f"PID file for '{process_name}' does not exist. Nothing to remove.")
        return False
    except Exception as e:
        logger.error(f"Failed to remove PID file for {process_name}: {e}")
        return False

def start_process(process_name, script_path, env_vars=None):
    """Start a single process with privilege handling"""
    pid = read_pid(process_name)
    if pid and psutil.pid_exists(pid):
        console.print(f"[yellow]{process_name} is already running with PID {pid}.[/yellow]")
        return False

    # Define log file paths
    log_dir = os.path.join(get_project_root(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    stdout_log = os.path.join(log_dir, f'{process_name}_stdout.log')
    stderr_log = os.path.join(log_dir, f'{process_name}_stderr.log')

    # Prepare environment
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)

    try:
        with open(stdout_log, 'a') as stdout_f, open(stderr_log, 'a') as stderr_f:
            if platform.system() == 'Windows':
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=stdout_f,
                    stderr=stderr_f,
                    creationflags=DETACHED_PROCESS,
                    env=env,
                    close_fds=True
                )
            else:
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=stdout_f,
                    stderr=stderr_f,
                    start_new_session=True,
                    env=env,
                    close_fds=True
                )

            if create_pid_file(process_name, process.pid):
                console.print(f"[green]{process_name} started successfully with PID {process.pid}.[/green]")
                console.print(f"[blue]Logs: stdout -> {stdout_log}, stderr -> {stderr_log}[/blue]")
                return True
            else:
                process.kill()
                return False

    except Exception as e:
        logger.error(f"Failed to start {process_name}: {e}")
        return False

def start_polaris():
    ensure_pid_directory()
    env_path = os.path.join(get_project_root(), '.env')
    load_dotenv(dotenv_path=env_path)
    ensure_repository_exists()
    
    repo_path = get_repo_path()
    main_py_path = os.path.join(repo_path, "src", "main.py")
    
    log_dir = os.path.join(repo_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    stdout_log = os.path.join(log_dir, 'server.log')
    stderr_log = os.path.join(log_dir, 'server_error.log')
    
    # env = os.environ.copy()
    # env.update({
    #     'HOST': os.getenv('HOST'),
    #     'API_PORT': os.getenv('API_PORT'),
    #     'BASE_SSH_PORT': os.getenv('BASE_SSH_PORT'),
    #     'SSH_USER': os.getenv('SSH_USER', 'devuser'),
    #     'SSH_HOST': os.getenv('SSH_HOST', '24.83.13.62')
    # })

    with open(stdout_log, 'a') as stdout_f, open(stderr_log, 'a') as stderr_f:
        cmd = [
    'python3',
    '-m',
    'uvicorn',
    'src.main:app',
    '--reload',
    '--host', '0.0.0.0',
    '--port', '8000'
     ]

        process = subprocess.Popen(
            cmd,
            cwd=repo_path,
            # env=env,
            stdout=stdout_f,
            stderr=stderr_f,
            start_new_session=True
        )

        if create_pid_file('compute_subnet', process.pid):
            console.print(f"[green]Server started on PID {process.pid}[/green]")
            console.print(f"[blue]Logs: {stdout_log} and {stderr_log}[/blue]")
            return True
        else:
            process.kill()
            return False 

def stop_process(pid, process_name, force=False):
    """Stop a single process with privilege handling"""
    try:
        process = psutil.Process(pid)
        console.print(f"[yellow]Terminating {process_name} (PID {pid})...[/yellow]")

        try:
            # Try normal termination first
            process.terminate()
            try:
                process.wait(timeout=10)
                console.print(f"[green]{process_name} (PID {pid}) stopped successfully.[/green]")
                return True
            except psutil.TimeoutExpired:
                if force:
                    if platform.system() == 'Windows':
                        subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
                    else:
                        os.kill(pid, signal.SIGKILL)
                    console.print(f"[green]{process_name} forcefully stopped.[/green]")
                    return True
                return False
                
        except psutil.AccessDenied:
            if not is_admin():
                console.print("[yellow]Requesting elevated privileges...[/yellow]")
                if elevate_privileges():
                    return stop_process(pid, process_name, force)
            return False

    except psutil.NoSuchProcess:
        console.print(f"[yellow]Process {pid} not found.[/yellow]")
        return True
    except Exception as e:
        logger.error(f"Failed to stop {process_name}: {e}")
        return False

def stop_polaris():
    """Stop all Polaris processes"""
    success = True
    
    # Stop processes in reverse order
    for process_name in ['heartbeat', 'compute_subnet', 'local_polaris']:
        pid = read_pid(process_name)
        if not pid:
            console.print(f"[yellow]{process_name} is not running.[/yellow]")
            continue

        # Try graceful shutdown first
        if not stop_process(pid, process_name, force=False):
            # If graceful shutdown fails, try forced shutdown
            console.print(f"[yellow]Attempting forced shutdown of {process_name}...[/yellow]")
            if not stop_process(pid, process_name, force=True):
                console.print(f"[red]Failed to stop {process_name}.[/red]")
                success = False
                continue

        # Remove PID file
        remove_pid_file(process_name)

    return success

def check_status():
    """Check if processes are running"""
    processes = ['local_polaris', 'compute_subnet', 'heartbeat']
    all_running = True

    for process_name in processes:
        pid = read_pid(process_name)
        if pid and psutil.pid_exists(pid):
            try:
                process = psutil.Process(pid)
                if process.is_running():
                    console.print(f"[green]{process_name} is running with PID {pid}.[/green]")
                    continue
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        console.print(f"[yellow]{process_name} is not running.[/yellow]")
        all_running = False
        remove_pid_file(process_name)

    return all_running

def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        console.print("[red]Usage: polaris [start|stop|status][/red]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'start':
        start_polaris()
    elif command == 'stop':
        if not stop_polaris():
            sys.exit(1)
    elif command == 'status':
        if not check_status():
            sys.exit(1)
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
        console.print("[red]Usage: polaris [start|stop|status][/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()