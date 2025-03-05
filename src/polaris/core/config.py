"""
Configuration management for Polaris.

This module provides utilities for loading, saving, and managing configuration
for Polaris components.
"""

import json
import os
from pathlib import Path

from polaris.utils.logging import get_logger

# Initialize logger
logger = get_logger('config')

# Constants
POLARIS_HOME = Path.home() / '.polaris'
CONFIG_DIR = POLARIS_HOME / 'config'


class PolarisConfig:
    """
    Configuration manager for Polaris
    
    This class handles loading, saving, and accessing configuration values
    for all Polaris components.
    """
    
    def __init__(self, component=None):
        """
        Initialize configuration manager
        
        Args:
            component (str, optional): Component-specific configuration
        """
        self.component = component
        self.config = {}
        
        # Create config directory if it doesn't exist
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load default config
        self.config_file = CONFIG_DIR / 'polaris.json'
        if component:
            self.component_config_file = CONFIG_DIR / f"{component}.json"
        
        # Load configurations
        self._load_config()
    
    def _load_config(self):
        """Load configuration from files"""
        # Load main config
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load main configuration: {str(e)}")
        
        # Load component config if applicable
        if self.component and hasattr(self, 'component_config_file') and self.component_config_file.exists():
            try:
                with open(self.component_config_file, 'r') as f:
                    component_config = json.load(f)
                    # Merge component config with main config (component takes precedence)
                    self.config.update(component_config)
            except Exception as e:
                logger.error(f"Failed to load {self.component} configuration: {str(e)}")
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            # Save component-specific config if applicable
            if self.component:
                component_config = {k: v for k, v in self.config.items() if k.startswith(f"{self.component}.")}
                if component_config:
                    with open(self.component_config_file, 'w') as f:
                        json.dump(component_config, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            return False
    
    def get(self, key, default=None):
        """
        Get a configuration value
        
        Args:
            key (str): Configuration key
            default: Default value if key is not found
            
        Returns:
            The configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        Set a configuration value
        
        Args:
            key (str): Configuration key
            value: Value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.config[key] = value
        return self.save()
    
    def delete(self, key):
        """
        Delete a configuration value
        
        Args:
            key (str): Configuration key
            
        Returns:
            bool: True if successful, False otherwise
        """
        if key in self.config:
            del self.config[key]
            return self.save()
        return False


# Initialize global config
global_config = PolarisConfig()


def get_config(component=None):
    """
    Get a configuration instance
    
    Args:
        component (str, optional): Component-specific configuration
        
    Returns:
        PolarisConfig: Configuration instance
    """
    if component:
        return PolarisConfig(component)
    return global_config 