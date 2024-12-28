import string
from pathlib import Path

NGROK_AUTH_TOKEN = "2lwekoAUktCc51onS7imUocGHak_3nVjaNFUzSuCcK6t2jzU7"
SSH_CONFIG_PATH = "C:\\ProgramData\\ssh\\sshd_config"
PASSWORD_CHARS = string.ascii_letters + string.digits
HOME_DIR = Path.home()
NGROK_CONFIG_DIR = HOME_DIR / '.ngrok2'
LOG_DIR = HOME_DIR / '.remote-access'