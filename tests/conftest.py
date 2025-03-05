"""
Pytest configuration file.

This file contains fixtures and configuration for pytest.
"""

import os
import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def config_dir(temp_dir):
    """Create a temporary config directory for testing"""
    config_dir = temp_dir / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


@pytest.fixture
def logs_dir(temp_dir):
    """Create a temporary logs directory for testing"""
    logs_dir = temp_dir / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


@pytest.fixture
def pids_dir(temp_dir):
    """Create a temporary pids directory for testing"""
    pids_dir = temp_dir / 'pids'
    pids_dir.mkdir(parents=True, exist_ok=True)
    return pids_dir 