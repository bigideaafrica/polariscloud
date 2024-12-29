# utils.py
import logging
import os
import platform
import random
import socket  # Add this import
import subprocess
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from . import config


def configure_logging():
    """
    Configures the logging settings.
    """
    logger = logging.getLogger('polaris_cli')
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # File handler
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'polaris.log')
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    return logger

def run_elevated(cmd):
    if platform.system().lower() == "windows":
        cmd = cmd.replace('"', '""')
        vbs_content = (
            'Set UAC = CreateObject("Shell.Application")\n'
            f'UAC.ShellExecute "cmd.exe", "/c {cmd}", "", "runas", 1'
        )
        
        vbs_path = config.HOME_DIR / 'temp_elevate.vbs'
        with open(vbs_path, 'w', encoding='utf-8') as f:
            f.write(vbs_content)
        
        subprocess.run(['cscript', '//Nologo', str(vbs_path)], check=True)
        vbs_path.unlink(missing_ok=True)
    else:
        subprocess.run(['sudo', cmd], shell=True, check=True)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            # Fallback method
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception:
            return '127.0.0.1'