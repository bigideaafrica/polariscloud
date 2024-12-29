# utils.py
import logging
import platform
import random
import subprocess
from pathlib import Path

from . import config


def configure_logging():
    logger = logging.getLogger('remote_access')
    logger.setLevel(logging.DEBUG)
    
    config.LOG_DIR.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(config.LOG_DIR / 'remote-access.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        "%(message)s"
    ))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
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

def generate_password(length=5):
    return ''.join(random.choices(config.PASSWORD_CHARS, k=length))