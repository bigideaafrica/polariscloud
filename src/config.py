import os
import string
from pathlib import Path

from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get NGROK token from environment
NGROK_AUTH_TOKEN = os.getenv('NGROK_AUTH_TOKEN')

# Directory configurations
HOME_DIR = Path.home()
NGROK_CONFIG_DIR = HOME_DIR / '.ngrok2'
LOG_DIR = HOME_DIR / '.remote-access'

# Create required directories if they don't exist
NGROK_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)