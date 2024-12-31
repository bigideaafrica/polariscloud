# src/main.py

import ctypes
import json
import logging
import os
import signal
import subprocess
import sys
import time

import requests

from src.ngrok_manager import NgrokManager
from src.pid_manager import PID_FILE, create_pid_file, remove_pid_file
from src.ssh_manager import SSHManager
from src.system_info import get_system_info
from src.utils import configure_logging, get_local_ip, get_project_root

logger = configure_logging()

def is_admin():
    """Check if the script is running with administrative privileges on Windows."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        return False

def run_as_admin():
    """
    Relaunch the current script with administrative privileges on Windows.
    
    Returns:
        bool: True if the script was successfully relaunched, False otherwise.
    """
    try:
        script_path = os.path.abspath(__file__)
        params = f'"{script_path}"'  # Ensure the script path is quoted
        
        # Relaunch the script with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            params,
            None,
            1
        )
        logger.info("Script relaunched with administrative privileges.")
        return True
    except Exception as e:
        logger.exception(f"Failed to get admin rights: {e}")
        return False

def create_ssh_directory_windows():
    """
    Create SSH directory on Windows with administrative privileges.
    
    Attempts multiple methods to ensure directory creation:
    1. Using subprocess with admin rights
    2. Using os.makedirs with elevated privileges
    """
    ssh_dir = r'C:\ProgramData\ssh'
    
    # Method 1: Use subprocess with admin rights
    if run_as_admin_command(['mkdir', ssh_dir]):
        logger.info(f"SSH directory created at {ssh_dir} using admin command.")
        return True
    
    # Method 2: Try os.makedirs with error handling
    try:
        os.makedirs(ssh_dir, exist_ok=True)
        logger.info(f"SSH directory created at {ssh_dir} using os.makedirs.")
        return True
    except PermissionError:
        logger.warning("Permission denied when creating SSH directory.")
        return False
    except Exception as e:
        logger.exception(f"Failed to create SSH directory: {e}")
        return False

def run_as_admin_command(command):
    """
    Run a command with administrative privileges on Windows.
    
    Args:
        command (list): Command to run with arguments
    
    Returns:
        bool: True if command was successful, False otherwise
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=True
        )
        
        if result.returncode != 0:
            logger.error(f"Command '{' '.join(command)}' failed with error: {result.stderr.strip()}")
            return False
        
        logger.debug(f"Command '{' '.join(command)}' executed successfully with output: {result.stdout.strip()}")
        return True
    except Exception as e:
        logger.exception(f"Error running command '{' '.join(command)}': {e}")
        return False

def configure_ssh_windows():
    """
    Configure SSH server on Windows.
    
    This involves:
    1. Ensuring SSH directory exists
    2. Configuring SSH service
    3. Potentially creating SSH configuration files
    """
    # Create SSH directory
    if not create_ssh_directory_windows():
        logger.error("Failed to create SSH directory.")
        return False
    
    # Configure SSH service
    commands = [
        'powershell "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0"',
        'powershell "Start-Service sshd"',
        'powershell "Set-Service -Name sshd -StartupType Automatic"'
    ]
    
    for cmd in commands:
        if not run_as_admin_command(cmd.split()):
            logger.error(f"Failed to execute SSH configuration command: {cmd}")
            return False
    
    logger.info("SSH server configured successfully.")
    return True

def setup_firewall_windows():
    """
    Configure Windows Firewall to allow SSH connections.
    """
    firewall_cmd = 'netsh advfirewall firewall add rule name="OpenSSH" dir=in action=allow protocol=TCP localport=22'
    if run_as_admin_command(firewall_cmd.split()):
        logger.info("Windows Firewall configured to allow SSH connections on port 22.")
        return True
    else:
        logger.warning("Failed to configure Windows Firewall for SSH. SSH access might be blocked.")
        return False

def save_system_info(data, filename='system_info.json'):
    try:
        # Always save in project root directory
        root_dir = get_project_root()
        abs_path = os.path.join(root_dir, filename)
        with open(abs_path, 'w') as f:
            json.dump(data, f, indent=4)
        logger.debug(f"System information saved to {abs_path}")
        return abs_path
    except Exception as e:
        logger.exception(f"Failed to save system info: {e}")
        return None

def handle_shutdown(signum, frame):
    logger.info("Received shutdown signal. Cleaning up...")
    sys.exit(0)

def main():
    logger.debug("Starting Polaris main function.")
    
    # Ensure admin rights
    logger.debug("Checking for administrative privileges.")
    if not is_admin():
        logger.warning("Restarting script with administrative privileges...")
        if run_as_admin():
            logger.info("Relaunching Polaris with administrative privileges.")
            sys.exit(0)  # Exit the non-admin process
        else:
            logger.error("Unable to obtain administrative privileges.")
            sys.exit(1)

    # Create PID file to ensure only one instance runs
    logger.debug(f"Creating PID file at {PID_FILE}.")
    if not create_pid_file():
        logger.error("Polaris is already running or failed to create PID file.")
        sys.exit(1)
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    ngrok = None  # Initialize outside try block for cleanup
    try:
        # Windows-specific SSH setup
        logger.debug("Configuring SSH on Windows.")
        if not configure_ssh_windows():
            logger.error("Failed to configure SSH on Windows.")
            sys.exit(1)
        
        # Setup firewall
        logger.debug("Setting up Windows Firewall for SSH.")
        if not setup_firewall_windows():
            logger.warning("Could not configure firewall. SSH access might be blocked.")
        
        while True:
            # Get system information
            system_info = get_system_info("CPU")  # or "GPU" based on your needs
            
            # Initialize managers
            ngrok = NgrokManager()
            ssh = SSHManager()
            
            # Get SSH credentials
            logger.debug("Setting up SSH user.")
            username, password = ssh.setup_user()
            if not username or not password:
                logger.error("Failed to set up SSH user.")
                sys.exit(1)
            
            # Start ngrok tunnel
            logger.info("Starting ngrok tunnel...")
            host, port = ngrok.start_tunnel(22)
            if not host or not port:
                logger.error("Failed to start ngrok tunnel.")
                break  # Exit the loop if ngrok fails to start
            
            # Add network info
            network_info = {
                "internal_ip": get_local_ip(),
                "ssh": f"ssh {username}@{host} -p {port}",
                "open_ports": ["22"],
                "password": password,
                "username": username
            }
            
            if system_info and "compute_resources" in system_info:
                system_info["compute_resources"][0]["network"] = network_info
            
            # Save system information
            file_path = save_system_info([system_info])
            
            if file_path:
                logger.info("\n" + "="*50)
                logger.info(f"System information saved to: {file_path}")
                logger.info(f"SSH Command: ssh {username}@{host} -p {port}")
                logger.info(f"Password: {password}")
                logger.info("="*50 + "\n")
            else:
                logger.error("Failed to save system information.")
            
            # Monitor ngrok tunnel status
            while True:
                try:
                    r = requests.get("http://localhost:4040/api/tunnels", timeout=5)
                    tunnels = r.json().get("tunnels", [])
                    if not tunnels:
                        logger.warning("No active tunnels found. Restarting ngrok...")
                        host, port = ngrok.start_tunnel(22)
                        if not host or not port:
                            logger.error("Failed to restart ngrok tunnel.")
                            break  # Exit the inner loop to restart the outer loop
                        network_info["ssh"] = f"ssh {username}@{host} -p {port}"
                        system_info["compute_resources"][0]["network"] = network_info
                        save_system_info([system_info])
                    time.sleep(10)  # Check every 10 seconds
                except Exception as e:
                    logger.warning(f"Tunnel check failed: {e}. Restarting...")
                    try:
                        host, port = ngrok.start_tunnel(22)
                        if not host or not port:
                            logger.error("Failed to restart ngrok tunnel.")
                            break  # Exit the inner loop to restart the outer loop
                        network_info["ssh"] = f"ssh {username}@{host} -p {port}"
                        system_info["compute_resources"][0]["network"] = network_info
                        save_system_info([system_info])
                    except Exception as restart_error:
                        logger.error(f"Failed to restart tunnel: {restart_error}")
                    time.sleep(15)  # Wait before retrying
                
    except KeyboardInterrupt:
        logger.info("\nShutdown requested. Cleaning up...")
    except Exception as e:
        logger.exception(f"Error during setup: {e}")
    finally:
        # Clean shutdown
        if ngrok:
            logger.info("Stopping ngrok tunnel...")
            ngrok.kill_existing()
        remove_pid_file()
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    main()
