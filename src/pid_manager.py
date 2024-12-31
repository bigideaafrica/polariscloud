# src/pid_manager.py

import logging
import os

from src.utils import get_project_root

logger = logging.getLogger("polaris_cli.pid_manager")

# Define the path to the PID file using the project root
PID_FILE = os.path.join(get_project_root(), 'polaris.pid')

def create_pid_file():
    """
    Creates a PID file to ensure only one instance runs.

    Returns:
        bool: True if the PID file was created successfully, False otherwise.
    """
    try:
        pid = os.getpid()
        with open(PID_FILE, 'w') as f:
            f.write(str(pid))
        logger.debug(f"Attempting to create PID file at: {PID_FILE}")
        logger.info(f"PID file created with PID: {pid}")
        return True
    except Exception as e:
        logger.exception(f"Failed to create PID file at {PID_FILE}: {e}")
        return False

def remove_pid_file():
    """
    Removes the PID file if it exists.
    """
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
            logger.debug(f"Attempting to remove PID file at: {PID_FILE}")
            logger.info("PID file removed.")
        else:
            logger.debug(f"No PID file found at: {PID_FILE} to remove.")
    except Exception as e:
        logger.exception(f"Failed to remove PID file at {PID_FILE}: {e}")
