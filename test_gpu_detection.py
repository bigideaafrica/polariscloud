#!/usr/bin/env python3
"""
Test script to check if the GPU detection is working properly.
This will run the has_gpu() function from system_info.py and show detailed output.
"""

import sys
import os
import logging

# Configure logging to see all output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger()
logger.info("Starting GPU detection test...")

# Add the current directory to the Python path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the has_gpu function
try:
    # Try relative import first (when in a package)
    from src.system_info import has_gpu, get_gpu_info_linux, get_gpu_info_windows
    logger.info("Imported GPU functions from src.system_info")
except ImportError:
    try:
        # Try direct import (when in same directory)
        from system_info import has_gpu, get_gpu_info_linux, get_gpu_info_windows
        logger.info("Imported GPU functions from system_info")
    except ImportError:
        logger.error("Could not import has_gpu function. Make sure you're running this script from the correct directory.")
        sys.exit(1)

# Get platform
import platform
logger.info(f"Platform: {platform.system()}")

# Run the detection function
logger.info("Running has_gpu() function...")
result = has_gpu()
logger.info(f"has_gpu() result: {result}")

# Get detailed GPU info based on platform
try:
    if platform.system().lower() == 'windows':
        logger.info("Getting detailed Windows GPU info...")
        gpu_info = get_gpu_info_windows()
    else:
        logger.info("Getting detailed Linux GPU info...")
        gpu_info = get_gpu_info_linux()
    
    logger.info(f"Detailed GPU info: {gpu_info}")
except Exception as e:
    logger.error(f"Error getting detailed GPU info: {e}")

logger.info("GPU detection test complete.") 