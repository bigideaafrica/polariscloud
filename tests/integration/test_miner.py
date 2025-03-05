"""
Integration tests for the miner module.
"""

import os
import tempfile
import time
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

from polaris.miner.bittensor_miner import (
    start_bittensor_miner,
    stop_bittensor_miner,
    is_bittensor_running,
    check_miner_status
)


class TestMinerIntegration(unittest.TestCase):
    """Integration tests for the miner module"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.bittensor_dir = Path(self.temp_dir.name) / 'bittensor'
        self.pids_dir = self.bittensor_dir / 'pids'
        self.logs_dir = self.bittensor_dir / 'logs'
        
        # Create directories
        self.pids_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Patch constants
        self.patchers = [
            patch('polaris.miner.bittensor_miner.BITTENSOR_CONFIG_PATH', self.bittensor_dir),
            patch('polaris.miner.bittensor_miner.PID_FILE', self.pids_dir / 'miner.pid'),
            patch('polaris.miner.bittensor_miner.LOG_FILE', self.logs_dir / 'miner.log')
        ]
        for patcher in self.patchers:
            patcher.start()
    
    def tearDown(self):
        """Clean up test environment"""
        # Stop all patchers
        for patcher in self.patchers:
            patcher.stop()
        
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    @patch('polaris.miner.bittensor_miner.subprocess.Popen')
    def test_start_stop_miner_simulation(self, mock_popen):
        """Test starting and stopping the miner in simulation mode"""
        # Mock the subprocess.Popen to return a process with a PID
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        # Start the miner in simulation mode
        result = start_bittensor_miner('test_wallet', simulation_mode=True)
        self.assertTrue(result)
        
        # Check that the PID file was created
        pid_file = self.pids_dir / 'miner.pid'
        self.assertTrue(pid_file.exists())
        
        # Check that the PID was written correctly
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        self.assertEqual(pid, 12345)
        
        # Check that the miner is reported as running
        self.assertTrue(is_bittensor_running())
        
        # Check the miner status
        status = check_miner_status()
        self.assertTrue(status['running'])
        self.assertEqual(status['pid'], 12345)
        
        # Mock os.kill to simulate process existence
        with patch('os.kill', return_value=None):
            # Stop the miner
            result = stop_bittensor_miner()
            self.assertTrue(result)
            
            # Check that the PID file was removed
            self.assertFalse(pid_file.exists())
            
            # Check that the miner is reported as not running
            self.assertFalse(is_bittensor_running())


if __name__ == '__main__':
    unittest.main() 