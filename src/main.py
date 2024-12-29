import json
import os
import socket
import time

import requests

from . import utils
from .ngrok_manager import NgrokManager
from .ssh_manager import SSHManager
from .system_info import get_system_info

logger = utils.configure_logging()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
        s.close()
        return IP
    except Exception as e:
        logger.error(f"Failed to get local IP: {e}")
        return None

def save_system_info(data, filename='system_info.json'):
    try:
        abs_path = os.path.abspath(filename)
        json_str = json.dumps(data, indent=4)
        with open(filename, 'w') as f:
            f.write(json_str)
        return abs_path
    except Exception as e:
        logger.error(f"Failed to save system info: {e}")
        return None

def main():
    try:
        # Get system information
        system_info = get_system_info()
        
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
        
        # Get local IP
        local_ip = get_local_ip()
        
        # Add network info
        network_info = {
            "internal_ip": local_ip,
            "ssh": f"ssh {username}@{host} -p {port}",
            "local_ssh": f"ssh {username}@{local_ip}" if local_ip else "",
            "password": password,
            "open_ports": ["22"]
        }
        
        if system_info and "compute_resources" in system_info:
            system_info["compute_resources"][0]["network"] = network_info
            
        final_data = [system_info]
        
        # Save and get path
        file_path = save_system_info(final_data)
        
        # Only show the file path
        logger.info("\n" + "="*50)
        logger.info(f"System information saved to: {file_path}")
        logger.info("="*50 + "\n")
        
        # Keep tunnel running
        while True:
            time.sleep(5)
            try:
                r = requests.get("http://localhost:4040/api/tunnels", timeout=5)
                if r.status_code != 200:
                    logger.warning("Tunnel appears to be down. Restarting...")
                    host, port = ngrok.start_tunnel(22)
            except requests.exceptions.RequestException:
                logger.warning("Tunnel check failed. Restarting...")
                host, port = ngrok.start_tunnel(22)
                
    except KeyboardInterrupt:
        logger.info("Stopping services...")
        ngrok.kill_existing()
    except Exception as e:
        logger.error(f"Error during setup: {e}")
        ngrok.kill_existing()

if __name__ == "__main__":
    main()