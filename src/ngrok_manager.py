import logging
import platform
import subprocess
import time
from pathlib import Path

import requests
import yaml

from . import config, utils

logger = logging.getLogger('remote_access')

class NgrokManager:
    def __init__(self):
        self.logger = logging.getLogger('remote_access')
    
    def kill_existing(self):
        try:
            if platform.system().lower() == "windows":
                subprocess.run("taskkill /F /IM ngrok.exe 2>nul", shell=True, check=False)
            else:
                subprocess.run("pkill ngrok", shell=True, check=False)
            time.sleep(2)
        except Exception as e:
            self.logger.error(f"Error killing ngrok: {e}")

    def create_config(self, port):
        config.NGROK_CONFIG_DIR.mkdir(exist_ok=True)
        config_path = config.NGROK_CONFIG_DIR / 'ngrok.yml'
        
        ngrok_config = {
            'version': '2',
            'authtoken': config.NGROK_AUTH_TOKEN,
            'tunnels': {
                'ssh': {
                    'proto': 'tcp',
                    'addr': port
                }
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(ngrok_config, f)

    def start_tunnel(self, port):
        self.kill_existing()
        self.create_config(port)
        
        cmd = ["ngrok", "start", "--all"]
        if platform.system().lower() == "windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(cmd, startupinfo=startupinfo)
        else:
            subprocess.Popen(cmd)
        
        time.sleep(3)
        
        for _ in range(30):
            try:
                r = requests.get("http://localhost:4040/api/tunnels", timeout=5)
                if r.status_code == 200:
                    tunnels = r.json().get("tunnels", [])
                    if tunnels:
                        tunnel = tunnels[0]
                        url = tunnel["public_url"]
                        raw_url = url.replace("tcp://", "")
                        host, port = raw_url.split(":")
                        return host, port
            except requests.exceptions.RequestException:
                time.sleep(1)
                continue
        
        raise Exception("Failed to establish tunnel after 30 seconds")