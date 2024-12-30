# src/main.py

import json
import os
import sys
import time

import requests

from src import utils
from src.ngrok_manager import NgrokManager
from src.pid_manager import create_pid_file, remove_pid_file
from src.ssh_manager import SSHManager
from src.system_info import get_system_info

logger = utils.configure_logging()

def save_system_info(data, filename='system_info.json'):
    try:
        # Save the JSON file in the same directory as main.py
        script_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(script_dir, filename)
        with open(abs_path, 'w') as f:
            json.dump(data, f, indent=4)
        return abs_path
    except Exception as e:
        logger.error(f"Failed to save system info: {e}")
        return None

def main():
    # Create PID file to ensure only one instance runs
    pidfile = create_pid_file()
    
    ngrok = None  # Initialize outside try block for cleanup
    try:
        while True:
            # Get system information
            system_info = get_system_info("CPU")  # or "GPU" based on your needs
            
            # Initialize managers
            ngrok = NgrokManager()
            ssh = SSHManager()
            
            # Setup SSH server
            ssh.setup_server(22)
            
            # Get SSH credentials
            username, password = ssh.setup_user()
            
            # Start ngrok tunnel
            logger.info("Starting ngrok tunnel...")
            host, port = ngrok.start_tunnel(22)
            
            # Add network info
            network_info = {
                "internal_ip": utils.get_local_ip(),
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
                        network_info["ssh"] = f"ssh {username}@{host} -p {port}"
                        system_info["compute_resources"][0]["network"] = network_info
                        save_system_info([system_info])
                    time.sleep(10)  # Check every 10 seconds
                except Exception as e:
                    logger.warning(f"Tunnel check failed: {e}. Restarting...")
                    try:
                        host, port = ngrok.start_tunnel(22)
                        network_info["ssh"] = f"ssh {username}@{host} -p {port}"
                        system_info["compute_resources"][0]["network"] = network_info
                        save_system_info([system_info])
                    except Exception as restart_error:
                        logger.error(f"Failed to restart tunnel: {restart_error}")
                    time.sleep(15)  # Wait before retrying
                        
    except KeyboardInterrupt:
        logger.info("\nShutdown requested. Cleaning up...")
    except Exception as e:
        logger.error(f"Error during setup: {e}")
    finally:
        # Clean shutdown
        if ngrok:
            logger.info("Stopping ngrok tunnel...")
            ngrok.kill_existing()
        remove_pid_file()
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    main()
