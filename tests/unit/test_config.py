"""
Unit tests for the config module.
"""

import json
import os
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

from polaris.core.config import PolarisConfig


class TestPolarisConfig(unittest.TestCase):
    """Test cases for PolarisConfig class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name) / 'config'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Patch the CONFIG_DIR constant
        self.patcher = patch('polaris.core.config.CONFIG_DIR', self.config_dir)
        self.patcher.start()
    
    def tearDown(self):
        """Clean up test environment"""
        self.patcher.stop()
        self.temp_dir.cleanup()
    
    def test_init_creates_config_dir(self):
        """Test that initialization creates the config directory"""
        # Remove the config directory
        os.rmdir(self.config_dir)
        
        # Initialize config
        config = PolarisConfig()
        
        # Check that the directory was created
        self.assertTrue(self.config_dir.exists())
    
    def test_get_default_value(self):
        """Test getting a value with a default"""
        config = PolarisConfig()
        value = config.get('nonexistent_key', 'default_value')
        self.assertEqual(value, 'default_value')
    
    def test_set_and_get_value(self):
        """Test setting and getting a value"""
        # Mock the save method to avoid file operations
        with patch.object(PolarisConfig, 'save', return_value=True):
            config = PolarisConfig()
            config.set('test_key', 'test_value')
            value = config.get('test_key')
            self.assertEqual(value, 'test_value')
    
    def test_delete_value(self):
        """Test deleting a value"""
        # Mock the save method to avoid file operations
        with patch.object(PolarisConfig, 'save', return_value=True):
            config = PolarisConfig()
            config.config['test_key'] = 'test_value'
            config.delete('test_key')
            self.assertNotIn('test_key', config.config)
    
    def test_component_config(self):
        """Test component-specific configuration"""
        # Create a component config file
        component_config = {'miner.key': 'value'}
        component_file = self.config_dir / 'miner.json'
        with open(component_file, 'w') as f:
            json.dump(component_config, f)
        
        # Initialize component config
        config = PolarisConfig('miner')
        
        # Check that the component config was loaded
        self.assertEqual(config.get('miner.key'), 'value')


if __name__ == '__main__':
    unittest.main() 