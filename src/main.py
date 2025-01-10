import json
import logging
import os
import signal
import subprocess
import sys
import time
import platform
import requests

from src.ngrok_manager import NgrokManager
from src.pid_manager import PID_FILE, create_pid_file, remove_pid_file
from src.ssh_manager import SSHManager
from src.sync_manager import SyncManager
from src.system_info import get_system_info
from src.user_manager import UserManager
from src.utils import configure_logging, get_local_ip, get_project_root

logger = configure_logging()

def is_admin():
    """Check if the script is running with administrative privileges."""
    if platform.system().lower() == 'windows':
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except AttributeError:
            return False
    else:
        # For Linux/Unix systems
        return os.geteuid() == 0

def run_as_admin():
    """
    Relaunch the current script with administrative privileges.
    """
    if platform.system().lower() == 'windows':
        try:
            script_path = os.path.abspath(__file__)
            params = f'"{script_path}"'
            
            import ctypes
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
    else:
        # For Linux/Unix systems
        if os.geteuid() != 0:
            try:
                # Read password from .env file
                env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
                if os.path.exists(env_path):
                    with open(env_path, 'r') as f:
                        for line in f:
                            if line.startswith('SSH_PASSWORD='):
                                password = line.split('=')[1].strip()
                                logger.info("Restarting with sudo using password from .env...")
                                
                                # Construct the sudo command
                                cmd = ['sudo', '-S'] + [sys.executable] + sys.argv
                                
                                # Use subprocess to pipe the password
                                process = subprocess.Popen(
                                    cmd,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True
                                )
                                
                                # Send password to stdin
                                stdout, stderr = process.communicate(input=password + '\n')
                                
                                if process.returncode != 0:
                                    logger.error(f"Sudo failed: {stderr}")
                                    return False
                                return True
                
                logger.error("No .env file found or SSH_PASSWORD not set")
                return False
                
            except Exception as e:
                logger.exception(f"Failed to restart with sudo: {e}")
                return False
        return True

def configure_ssh():
    """Configure SSH server for the current platform."""
    if platform.system().lower() == 'windows':
        return configure_ssh_windows()
    else:
        return configure_ssh_linux()

def configure_ssh_linux():
    """Configure SSH server on Linux."""
    try:
        # Check if SSH server is installed
        result = subprocess.run(['systemctl', 'status', 'ssh'], capture_output=True, text=True)
        if result.returncode != 0:
            # Install SSH server if not present
            logger.info("Installing SSH server...")
            subprocess.run(['apt-get', 'update'], check=True)
            subprocess.run(['apt-get', 'install', '-y', 'openssh-server'], check=True)
        
        # Start and enable SSH service
        subprocess.run(['systemctl', 'start', 'ssh'], check=True)
        subprocess.run(['systemctl', 'enable', 'ssh'], check=True)
        
        logger.info("SSH server configured successfully on Linux.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to configure SSH server on Linux: {e}")
        return False
    except Exception as e:
        logger.error(f"Error configuring SSH server: {e}")
        return False

def configure_ssh_windows():
    """Configure SSH server on Windows."""
    if not create_ssh_directory_windows():
        logger.error("Failed to create SSH directory.")
        return False
    
    commands = [
        'powershell "Get-WindowsCapability -Online | Where-Object Name -like \'OpenSSH.Server*\'"',
        'powershell "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0"',
        'powershell "Start-Service sshd"',
        'powershell "Set-Service -Name sshd -StartupType Automatic"'
    ]
    
    success = True
    for cmd in commands:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0 and not "already installed" in result.stdout:
                logger.error(f"Failed to execute SSH command: {cmd}\nError: {result.stderr}")
                success = False
                break
        except Exception as e:
            logger.error(f"Error executing SSH command: {cmd}\nError: {e}")
            success = False
            break

    if success:
        logger.info("SSH server configured successfully.")
        return True
    else:
        logger.error("SSH server configuration failed.")
        return False

def create_ssh_directory_windows():
    """Create SSH directory on Windows with administrative privileges."""
    ssh_dir = r'C:\ProgramData\ssh'
    
    # Try using PowerShell commands first
    try:
        ps_command = f'powershell -Command "New-Item -ItemType Directory -Force -Path \'{ssh_dir}\'"'
        subprocess.run(ps_command, check=True, shell=True, capture_output=True)
        logger.info(f"SSH directory created at {ssh_dir} using PowerShell")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"PowerShell directory creation failed: {e}")
    
    # Try using cmd.exe as fallback
    try:
        cmd_command = f'cmd /c mkdir "{ssh_dir}" 2>nul'
        subprocess.run(cmd_command, check=True, shell=True, capture_output=True)
        logger.info(f"SSH directory created at {ssh_dir} using cmd")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"CMD directory creation failed: {e}")
    
    # Try using os.makedirs as final fallback
    try:
        os.makedirs(ssh_dir, exist_ok=True)
        logger.info(f"SSH directory created at {ssh_dir} using os.makedirs")
        return True
    except Exception as e:
        logger.error(f"Failed to create SSH directory: {e}")
        return False

def setup_firewall():
    """Configure firewall based on platform."""
    if platform.system().lower() == 'windows':
        return setup_firewall_windows()
    else:
        return setup_firewall_linux()

def setup_firewall_linux():
    """Configure Linux firewall (ufw) to allow SSH connections."""
    try:
        # Check if ufw is installed
        result = subprocess.run(['which', 'ufw'], capture_output=True)
        if result.returncode != 0:
            logger.info("Installing ufw...")
            subprocess.run(['apt-get', 'update'], check=True)
            subprocess.run(['apt-get', 'install', '-y', 'ufw'], check=True)
        
        # Configure ufw
        subprocess.run(['ufw', 'allow', 'ssh'], check=True)
        subprocess.run(['ufw', '--force', 'enable'], check=True)
        
        logger.info("Linux firewall configured to allow SSH connections.")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to configure Linux firewall: {e}")
        return False
    except Exception as e:
        logger.warning(f"Error configuring firewall: {e}")
        return False

def setup_firewall_windows():
    """Configure Windows Firewall to allow SSH connections."""
    firewall_cmd = 'netsh advfirewall firewall add rule name="OpenSSH" dir=in action=allow protocol=TCP localport=22'
    try:
        subprocess.run(firewall_cmd, shell=True, check=True, capture_output=True)
        logger.info("Windows Firewall configured to allow SSH connections on port 22.")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to configure Windows Firewall: {e}")
        return False
    except Exception as e:
        logger.warning(f"Error configuring firewall: {e}")
        return False

def format_network_info(username: str, password: str, host: str, port: int) -> dict:
    """Format network information according to API requirements."""
    return {
        "internal_ip": str(get_local_ip()),
        "ssh": f"ssh://{username}@{host}:{port}",
        "open_ports": ["22"],
        "password": str(password),
        "username": str(username)
    }

def save_and_sync_info(system_info, filename='system_info.json'):
    """Save system info and sync network details."""
    try:
        root_dir = get_project_root()
        abs_path = os.path.join(root_dir, filename)
        with open(abs_path, 'w') as f:
            json.dump([system_info], f, indent=4)
        logger.debug(f"System information saved to {abs_path}")

        user_manager = UserManager()
        has_registration, user_info = user_manager.check_existing_registration(show_prompt=False)
        
        if has_registration and user_info:
            sync_manager = SyncManager()
            if sync_manager.sync_network_info():
                logger.info("Network information synchronized successfully")
                
                overall_status, component_status = sync_manager.verify_sync_status()
                if not overall_status:
                    logger.warning("Sync verification failed:")
                    for component, status in component_status.items():
                        logger.warning(f"- {component}: {'Success' if status else 'Failed'}")
            else:
                logger.warning("Failed to synchronize network information")

        return abs_path
    except Exception as e:
        logger.exception(f"Failed to save and sync system info: {e}")
        return None

def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal. Cleaning up...")
    sys.exit(0)

def main():
    logger.debug("Starting Polaris main function.")
    
    # Ensure admin rights
    if not is_admin():
        logger.warning("Restarting script with administrative privileges...")
        if run_as_admin():
            logger.info("Relaunching Polaris with administrative privileges.")
            sys.exit(0)
        else:
            logger.error("Unable to obtain administrative privileges.")
            sys.exit(1)

    # Create PID file
    if not create_pid_file():
        logger.error("Polaris is already running or failed to create PID file.")
        sys.exit(1)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    ngrok = None
    try:
        # Configure SSH based on platform
        if not configure_ssh():
            logger.error("Failed to configure SSH.")
            sys.exit(1)
        
        # Setup firewall based on platform
        if not setup_firewall():
            logger.warning("Could not configure firewall. SSH access might be blocked.")
        
        while True:
            # Get system information
            system_info = get_system_info("CPU")
            
            # Initialize managers
            ngrok = NgrokManager()
            ssh = SSHManager()
            
            # Setup SSH user
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
                break

            # Create network info
            network_info = format_network_info(
                username=username,
                password=password,
                host=host,
                port=port
            )
            
            if system_info and "compute_resources" in system_info:
                system_info["compute_resources"][0]["network"] = network_info
            
            # Save and sync system information
            file_path = save_and_sync_info(system_info)
            
            if file_path:
                logger.info("\n" + "="*50)
                logger.info(f"System information saved to: {file_path}")
                
                user_manager = UserManager()
                user_info = user_manager.get_user_info()
                if user_info and 'network_info' in user_info:
                    network = user_info['network_info']
                    logger.info(f"SSH Command: {network.get('ssh', 'N/A')}")
                    logger.info(f"Password: {network.get('password', 'N/A')}")
                logger.info("="*50 + "\n")
            else:
                logger.error("Failed to save and sync system information")
            
            # Monitor ngrok tunnel
            while True:
                try:
                    r = requests.get("http://localhost:4040/api/tunnels", timeout=5)
                    tunnels = r.json().get("tunnels", [])
                    if not tunnels:
                        logger.warning("No active tunnels found. Restarting ngrok...")
                        host, port = ngrok.start_tunnel(22)
                        if not host or not port:
                            logger.error("Failed to restart ngrok tunnel.")
                            break
                        network_info = format_network_info(
                            username=username,
                            password=password,
                            host=host,
                            port=port
                        )
                        system_info["compute_resources"][0]["network"] = network_info
                        save_and_sync_info(system_info)
                    time.sleep(10)
                except Exception as e:
                    logger.warning(f"Tunnel check failed: {e}. Restarting...")
                    try:
                        host, port = ngrok.start_tunnel(22)
                        if not host or not port:
                            logger.error("Failed to restart ngrok tunnel.")
                            break
                        network_info = format_network_info(
                            username=username,
                            password=password,
                            host=host,
                            port=port
                        )
                        system_info["compute_resources"][0]["network"] = network_info
                        save_and_sync_info(system_info)
                    except Exception as restart_error:
                        logger.error(f"Failed to restart tunnel: {restart_error}")
                    time.sleep(15)
                
    except KeyboardInterrupt:
        logger.info("\nShutdown requested. Cleaning up...")
    except Exception as e:
        logger.exception(f"Error during setup: {e}")
    finally:
        if ngrok:
            logger.info("Stopping ngrok tunnel...")
            ngrok.kill_existing()
        remove_pid_file()
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    main()
