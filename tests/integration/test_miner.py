"""
Integration tests for the miner module.
"""

import os
import tempfile
import time
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock
import shutil

from polaris.miner.bittensor_miner import (
    start_bittensor_miner,
    stop_bittensor_miner,
    is_bittensor_running,
    check_miner_status,
    PID_FILE,
    BITTENSOR_CONFIG_PATH,
    LOG_FILE
)


class TestMinerIntegration(unittest.TestCase):
    """Integration tests for the miner module"""
    
    def setUp(self):
        """Set up the test environment"""
        # Create temporary directories for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        self.bittensor_dir = self.temp_dir / 'bittensor'
        self.pids_dir = self.bittensor_dir / 'pids'
        self.logs_dir = self.bittensor_dir / 'logs'
        
        # Create the directories
        self.pids_dir.mkdir(parents=True)
        self.logs_dir.mkdir(parents=True)
        
        # Patch the constants
        self.config_patcher = patch('polaris.miner.bittensor_miner.BITTENSOR_CONFIG_PATH', self.bittensor_dir)
        self.pid_file_patcher = patch('polaris.miner.bittensor_miner.PID_FILE', self.pids_dir / 'miner.pid')
        self.log_file_patcher = patch('polaris.miner.bittensor_miner.LOG_FILE', self.logs_dir / 'miner.log')
        
        # Start the patchers
        self.config_patcher.start()
        self.pid_file_patcher.start()
        self.log_file_patcher.start()
    
    def tearDown(self):
        """Clean up after the test"""
        # Stop the patchers
        self.config_patcher.stop()
        self.pid_file_patcher.stop()
        self.log_file_patcher.stop()
        
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    @patch('polaris.miner.bittensor_miner.subprocess.Popen')
    @patch('polaris.miner.bittensor_miner.os.kill')
    def test_start_stop_miner_simulation(self, mock_kill, mock_popen):
        """Test starting and stopping the miner in simulation mode"""
        # Mock the subprocess.Popen to return a process with a PID
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        # Mock os.kill to not raise an exception (indicating process is running)
        mock_kill.return_value = None
        
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
        
        # Stop the miner
        stop_bittensor_miner()
        
        # Check that the PID file was removed
        self.assertFalse(pid_file.exists())
        
        # Check that the miner is reported as not running
        self.assertFalse(is_bittensor_running())


if __name__ == '__main__':
    unittest.main() 