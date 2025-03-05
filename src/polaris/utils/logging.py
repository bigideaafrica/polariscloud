"""
Logging utilities for Polaris projects.

This module provides consistent logging setup across all Polaris components.
"""

import logging
import os
import sys
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

# Constants
POLARIS_HOME = Path.home() / '.polaris'
LOG_DIR = POLARIS_HOME / 'logs'


def setup_logger(name, level=logging.INFO):
    """
    Set up a logger with consistent formatting
    
    Args:
        name (str): Name of the logger
        level (int): Logging level (default: logging.INFO)
        
    Returns:
        logging.Logger: Configured logger
    """
    # Create log directory if it doesn't exist
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create log file path
    log_file = LOG_DIR / f"{name}.log"
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers if any
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler with rich formatting
    console_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=True,
        show_level=True,
    )
    console_handler.setLevel(level)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name):
    """
    Get an existing logger or create a new one
    
    Args:
        name (str): Name of the logger
        
    Returns:
        logging.Logger: Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger 