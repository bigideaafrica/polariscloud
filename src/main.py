import time

import requests

from . import utils
from .ngrok_manager import NgrokManager
from .ssh_manager import SSHManager

logger = utils.configure_logging()

def main():
    try:
        logger.info("Starting Remote Access Setup...")
        
        # Initialize managers
        ngrok = NgrokManager()
        ssh = SSHManager()
        
        # Setup SSH server with default port first
        ssh.setup_server(22)
        
        # Setup SSH user FIRST to get credentials
        logger.info("Setting up SSH user credentials...")
        username, password = ssh.setup_user()
        
        # Start ngrok tunnel
        logger.info("Starting ngrok tunnel...")
        host, port = ngrok.start_tunnel(22)
        
        # Display connection information with CLEAR password
        logger.info("\n" + "="*50)
        logger.info("SSH Connection Details:")
        logger.info(f"Host: {host}")
        logger.info(f"Port: {port}")
        logger.info(f"Username: {username}")
        logger.info(f"Password: {password}  <-- SAVE THIS PASSWORD")
        logger.info(f"\nConnection command:")
        logger.info(f"ssh {username}@{host} -p {port}")
        logger.info("\nIf prompted about host authenticity, type 'yes'")
        logger.info("="*50 + "\n")
        
        logger.info("Setup complete! You can now connect using the details above.")
        logger.info(f"REMEMBER: Your SSH password is: {password}")
        
        # Keep the tunnel running
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