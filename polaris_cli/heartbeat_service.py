# polaris_cli/heartbeat_service.py

import asyncio
import json
import logging
import os
import platform
import signal
import socket
import sys
import time
from datetime import datetime
from pathlib import Path

import aiohttp
import psutil

from src.user_manager import UserManager
from src.utils import configure_logging

# Configure detailed logging
logger = logging.getLogger(__name__)

class HeartbeatService:
    def __init__(self, 
                 server_url: str = "https://orchestrator-gekh.onrender.com/api/v1",
                 heartbeat_interval: int = 30):
        """Initialize HeartbeatService with configuration"""
        self.server_url = server_url.rstrip('/')
        self.heartbeat_interval = heartbeat_interval
        self.session = None
        self.is_running = False
        self.user_manager = UserManager()
        self.miner_id = None
        self.last_heartbeat = None
        
        logger.info("HeartbeatService initialized with:")
        logger.info(f"  Server URL: {self.server_url}")
        logger.info(f"  Heartbeat interval: {self.heartbeat_interval} seconds")

    def _get_miner_id(self) -> str:
        """Get miner ID from config file"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_info.json')
            logger.debug(f"Looking for config file at: {config_path}")
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    miner_id = config.get('miner_id')
                    if miner_id:
                        logger.info(f"Loaded miner_id from config: {miner_id}")
                        return miner_id
                    else:
                        logger.error("No miner_id found in config file")
            else:
                logger.error(f"Config file not found at {config_path}")
        except Exception as e:
            logger.error(f"Error reading miner_id from config: {str(e)}", exc_info=True)
        return None

    def _get_system_metrics(self):
        """Get current system metrics"""
        try:
            logger.debug("Collecting system metrics...")
            
            # CPU metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            logger.debug(f"CPU Usage: {cpu_usage}%")
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            logger.debug(f"Memory Usage: {memory_usage}%")
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            logger.debug(f"Disk Usage: {disk_usage}%")
            
            # System info
            boot_time_timestamp = psutil.boot_time()
            boot_time = datetime.fromtimestamp(boot_time_timestamp).isoformat()
            uptime = time.time() - boot_time_timestamp
            logger.debug(f"System Uptime: {uptime:.2f} seconds")

            # Network interfaces
            net_info = psutil.net_if_addrs()
            ip_address = "0.0.0.0"
            
            logger.debug("Scanning network interfaces...")
            for interface, addresses in net_info.items():
                logger.debug(f"Checking interface: {interface}")
                for addr in addresses:
                    if hasattr(addr, 'family') and addr.family == socket.AF_INET and not interface.startswith(('lo', 'docker', 'veth')):
                        ip_address = addr.address
                        logger.debug(f"Found usable IP address: {ip_address} on interface {interface}")
                        break

            metrics = {
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "disk_usage": disk_usage,
                "network_latency": 0,
                "temperature": None
            }

            system_info = {
                "hostname": platform.node(),
                "ip_address": ip_address,
                "os_version": f"{platform.system()} {platform.release()}",
                "uptime": uptime,
                "last_boot": boot_time
            }

            logger.debug("System metrics collected successfully")
            logger.debug(f"System Info: {json.dumps(system_info, indent=2)}")
            logger.debug(f"Metrics: {json.dumps(metrics, indent=2)}")

            return metrics, system_info
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}", exc_info=True)
            return {}, {}

    async def initialize(self) -> bool:
        """Initialize the heartbeat service"""
        try:
            logger.info("Starting heartbeat service initialization")
            
            # Get miner ID
            self.miner_id = self._get_miner_id()
            if not self.miner_id:
                logger.error("No miner_id available. Please configure miner_id in config.json")
                return False
            
            # Initialize HTTP session
            logger.info("Creating aiohttp ClientSession with 10s timeout")
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )
            
            logger.info("Heartbeat service initialization completed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize heartbeat service: {str(e)}", exc_info=True)
            return False

    async def send_heartbeat(self) -> bool:
        """Send a heartbeat signal to the server"""
        if not self.session:
            logger.error("Cannot send heartbeat: session not initialized")
            return False

        try:
            logger.debug("Preparing heartbeat data...")
            metrics, system_info = self._get_system_metrics()
            current_time = datetime.utcnow()
            
            heartbeat_data = {
                "timestamp": current_time.isoformat(),
                "status": "online",  # Changed from "ONLINE" to "online"
                "version": "1.0.0",
                "metrics": {
                    "miner_id": self.miner_id,
                    "system_info": system_info,
                    "metrics": metrics,
                    "resource_usage": {},
                    "active_jobs": []
                }
            }
            
            endpoint = f"{self.server_url}/heart_beat"
            logger.info(f"Sending heartbeat to: {endpoint}")
            logger.debug(f"Request payload: {json.dumps(heartbeat_data, indent=2)}")

            start_time = time.time()
            logger.debug("Making POST request...")
            
            async with self.session.post(
                endpoint,
                json=heartbeat_data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": f"PolarisHeartbeat/{platform.python_version()}"
                }
            ) as response:
                response_time = time.time() - start_time
                logger.info(f"Response received in {response_time:.3f} seconds with status {response.status}")
                
                response_body = await response.text()
                logger.debug(f"Response headers: {dict(response.headers)}")
                logger.debug(f"Response body: {response_body}")
                
                if response.status == 200:
                    self.last_heartbeat = time.time()
                    logger.info("Heartbeat sent successfully")
                    return True
                elif response.status == 422:
                    logger.error(f"Data validation error. Response: {response_body}")
                    return False
                else:
                    logger.warning(f"Heartbeat failed with status {response.status}. Response: {response_body}")
                    return False

        except aiohttp.ClientError as e:
            logger.error(f"Network error sending heartbeat: {str(e)}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending heartbeat: {str(e)}", exc_info=True)
            return False

    async def run(self):
        """Main service loop"""
        if not await self.initialize():
            logger.error("Failed to initialize heartbeat service, exiting")
            return

        self.is_running = True
        logger.info(f"Heartbeat service started with interval of {self.heartbeat_interval} seconds")

        retry_interval = self.heartbeat_interval
        cycle_count = 0
        
        while self.is_running:
            try:
                cycle_count += 1
                logger.info(f"Starting heartbeat cycle #{cycle_count}")
                
                success = await self.send_heartbeat()
                
                if success:
                    logger.info(f"Heartbeat cycle #{cycle_count} completed successfully")
                    retry_interval = self.heartbeat_interval
                else:
                    logger.warning(f"Heartbeat cycle #{cycle_count} failed")
                    retry_interval = min(retry_interval * 2, 300)
                    logger.info(f"Increasing retry interval to {retry_interval} seconds")
                
                logger.debug(f"Sleeping for {retry_interval} seconds until next cycle")
                await asyncio.sleep(retry_interval)
                
            except Exception as e:
                logger.error(f"Error in heartbeat cycle #{cycle_count}: {str(e)}", exc_info=True)
                await asyncio.sleep(retry_interval)

    async def stop(self):
        """Stop the heartbeat service"""
        logger.info("Stopping heartbeat service...")
        self.is_running = False
        
        if self.session:
            logger.debug("Closing aiohttp session")
            await self.session.close()
            
        logger.info("Heartbeat service stopped successfully")

async def main():
    """Main entry point for the heartbeat service"""
    try:
        # Configure logging with more detailed format
        logging.basicConfig(
            level=logging.DEBUG,  # Set to DEBUG for maximum verbosity
            format='%(asctime)s.%(msecs)03d %(levelname)s [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler('heartbeat.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        logger.info("=" * 60)
        logger.info("Starting Polaris Heartbeat Service")
        logger.info(f"Python Version: {platform.python_version()}")
        logger.info(f"Platform: {platform.platform()}")
        logger.info(f"Working Directory: {os.getcwd()}")
        logger.info("=" * 60)

        service = HeartbeatService()

        def signal_handler(sig, frame):
            sig_name = signal.Signals(sig).name
            logger.info(f"Received signal {sig_name} ({sig})")
            asyncio.create_task(service.stop())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        await service.run()
        
    except Exception as e:
        logger.critical(f"Fatal error in heartbeat service: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        await service.stop()

if __name__ == "__main__":
    asyncio.run(main())