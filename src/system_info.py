# system_info.py
import json
import logging
import os
import platform
import re
import subprocess
import time
import uuid

import psutil
import requests

logger = logging.getLogger('remote_access')

def is_windows():
    return platform.system().lower() == "windows"

def is_linux():
    return platform.system().lower() == "linux"

def is_macos():
    return platform.system().lower() == "darwin"

def get_location():
    try:
        r = requests.get("http://ipinfo.io/json", timeout=5)
        j = r.json()
        loc_str = f'{j.get("city","")}, {j.get("region","")}, {j.get("country","")}'
        return loc_str
    except Exception as e:
        logger.error(f"Failed to get location: {e}")
        return None

def get_cpu_info_windows():
    try:
        ps_cmd = ["powershell", "-Command", """
            $cpu = Get-CimInstance Win32_Processor | Select-Object *;
            $sys = Get-ComputerInfo | Select-Object CsProcessors,OsArchitecture,CsPhyicallyInstalledMemory;
            $props = @{
                'Name' = $cpu.Name;
                'Manufacturer' = $cpu.Manufacturer;
                'MaxClockSpeed' = $cpu.MaxClockSpeed;
                'CurrentClockSpeed' = $cpu.CurrentClockSpeed;
                'NumberOfCores' = $cpu.NumberOfCores;
                'ThreadCount' = $cpu.NumberOfLogicalProcessors;
                'Family' = $cpu.Family;
                'ProcessorId' = $cpu.ProcessorId;
                'AddressWidth' = $cpu.AddressWidth;
                'DataWidth' = $cpu.DataWidth;
                'Architecture' = $cpu.Architecture;
                'Stepping' = $cpu.Stepping;
                'OsArchitecture' = $sys.OsArchitecture;
            };
            ConvertTo-Json -InputObject $props
        """]
        r = subprocess.run(ps_cmd, capture_output=True, text=True, check=True)
        cpu_info = json.loads(r.stdout)
        
        return {
            "op_modes": f"32-bit, 64-bit" if cpu_info.get("DataWidth") == 64 else "32-bit",
            "address_sizes": f"{cpu_info.get('AddressWidth')} bits",
            "byte_order": "Little Endian",
            "total_cpus": int(cpu_info.get("ThreadCount", 0)),
            "online_cpus": f"0-{int(cpu_info.get('ThreadCount', 0))-1}" if int(cpu_info.get('ThreadCount', 0)) > 0 else "",
            "vendor_id": cpu_info.get("Manufacturer"),
            "cpu_name": cpu_info.get("Name"),
            "cpu_family": int(cpu_info.get("Family", 0)),
            "model": int(cpu_info.get("ProcessorId", "0")[9:10], 16) if cpu_info.get("ProcessorId") else 0,
            "threads_per_core": int(cpu_info.get("ThreadCount", 0)) // int(cpu_info.get("NumberOfCores", 1)),
            "cores_per_socket": int(cpu_info.get("NumberOfCores", 0)),
            "sockets": 1,
            "stepping": int(cpu_info.get("Stepping", 0)) if cpu_info.get("Stepping") else None,
            "cpu_max_mhz": float(cpu_info.get("MaxClockSpeed", 0)),
            "cpu_min_mhz": float(cpu_info.get("CurrentClockSpeed", 0))
        }
    except Exception as e:
        logger.error(f"Failed to get Windows CPU info: {e}")
        return None

def get_cpu_info_linux():
    try:
        r = subprocess.run(["lscpu"], capture_output=True, text=True, check=True)
        lines = r.stdout.splitlines()
        info = {}
        
        for line in lines:
            parts = line.split(":", 1)
            if len(parts) == 2:
                info[parts[0].strip()] = parts[1].strip()

        return {
            "op_modes": info.get("CPU op-mode(s)"),
            "address_sizes": info.get("Address sizes"),
            "byte_order": info.get("Byte Order"),
            "total_cpus": int(info.get("CPU(s)", 0)),
            "online_cpus": info.get("On-line CPU(s) list", ""),
            "vendor_id": info.get("Vendor ID"),
            "cpu_name": info.get("Model name"),
            "cpu_family": int(info.get("CPU family", 0)),
            "model": int(info.get("Model", 0)),
            "threads_per_core": int(info.get("Thread(s) per core", 1)),
            "cores_per_socket": int(info.get("Core(s) per socket", 1)),
            "sockets": int(info.get("Socket(s)", 1)),
            "stepping": int(info.get("Stepping", 0)) if info.get("Stepping") else None,
            "cpu_max_mhz": float(info.get("CPU max MHz", 0)),
            "cpu_min_mhz": float(info.get("CPU min MHz", 0))
        }
    except Exception as e:
        logger.error(f"Failed to get Linux CPU info: {e}")
        return None

def get_cpu_info_macos():
    try:
        # Get CPU details using sysctl
        cpu_model = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string']).decode().strip()
        cores = int(subprocess.check_output(['sysctl', '-n', 'hw.physicalcpu']).decode().strip())
        threads = int(subprocess.check_output(['sysctl', '-n', 'hw.logicalcpu']).decode().strip())
        family = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.family']).decode().strip()
        stepping = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.stepping']).decode().strip()
        model = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.model']).decode().strip()
        
        # Get CPU architecture
        arch_raw = subprocess.check_output(['uname', '-m']).decode().strip()
        if arch_raw == 'x86_64':
            architecture = '64-bit'
            address_sizes = '48 bits physical, 64 bits virtual'
            byte_order = 'Little Endian'
        elif arch_raw == 'arm64':
            architecture = 'ARM64'
            address_sizes = '48 bits physical, 64 bits virtual'
            byte_order = 'Little Endian'
        else:
            architecture = arch_raw
            address_sizes = 'Unknown'
            byte_order = 'Unknown'
            
        # Get CPU manufacturer
        if 'Intel' in cpu_model:
            manufacturer = 'Intel'
        elif 'AMD' in cpu_model:
            manufacturer = 'AMD'
        elif arch_raw == 'arm64':
            manufacturer = 'Apple'
        else:
            manufacturer = 'Unknown'
            
        # Get CPU speed
        try:
            speed_mhz = float(subprocess.check_output(['sysctl', '-n', 'hw.cpufrequency']).decode().strip()) / 1000000
        except:
            # Some older versions don't have this sysctl
            speed_mhz = 0
            
        # Format in the same structure as Linux/Windows functions
        cpu_list = list(range(threads))
        return {
            "op_modes": f"32-bit, 64-bit" if architecture == '64-bit' or architecture == 'ARM64' else architecture,
            "address_sizes": address_sizes,
            "byte_order": byte_order,
            "total_cpus": threads,
            "online_cpus": f"0-{threads-1}" if threads > 0 else "",  # Format as "0-7" for 8 cores, as a string
            "vendor_id": manufacturer,
            "cpu_name": cpu_model,
            "cpu_family": int(family) if family.isdigit() else 0,
            "model": int(model) if model.isdigit() else 0,
            "threads_per_core": threads // cores if cores > 0 else 0,
            "cores_per_socket": cores,
            "sockets": 1,
            "stepping": int(stepping) if stepping.isdigit() else 0,
            "cpu_max_mhz": speed_mhz,
            "cpu_min_mhz": speed_mhz * 0.8 if speed_mhz > 0 else 0  # Estimate min frequency as 80% of max
        }
    except Exception as e:
        logger.error(f"Failed to get macOS CPU info: {e}")
        return {
            "op_modes": "Unknown",
            "address_sizes": "Unknown",
            "byte_order": "Unknown",
            "total_cpus": 0,
            "online_cpus": "",  # Empty string instead of empty string
            "vendor_id": "Unknown",
            "cpu_name": "Unknown",
            "cpu_family": 0,
            "model": 0,
            "threads_per_core": 0,
            "cores_per_socket": 0,
            "sockets": 0,
            "stepping": 0,
            "cpu_max_mhz": 0.0,
            "cpu_min_mhz": 0.0
        }

def get_gpu_info_windows():
    try:
        ps_cmd = ["powershell", "-Command", """
            $gpu = Get-CimInstance win32_VideoController | Select-Object *;
            ConvertTo-Json -InputObject $gpu -Depth 10
        """]
        r = subprocess.run(ps_cmd, capture_output=True, text=True, check=True)
        gpu_info = json.loads(r.stdout)
        
        if not isinstance(gpu_info, list):
            gpu_info = [gpu_info]
            
        primary_gpu = gpu_info[0]
        memory_bytes = int(primary_gpu.get('AdapterRAM', 0))
        memory_gb = memory_bytes / (1024**3) if memory_bytes > 0 else 0
        
        return {
            "gpu_name": primary_gpu.get('Name'),
            "memory_size": f"{memory_gb:.2f}GB",
            "cuda_cores": None,
            "clock_speed": f"{primary_gpu.get('MaxRefreshRate', 0)}Hz",
            "power_consumption": None
        }
    except Exception as e:
        logger.error(f"Failed to get GPU info: {e}")
        return None

def get_gpu_info_linux():
    try:
        try:
            nvidia_cmd = ["nvidia-smi", "--query-gpu=name,memory.total,clocks.max.graphics,power.limit", "--format=csv,noheader,nounits"]
            r = subprocess.run(nvidia_cmd, capture_output=True, text=True, check=True)
            gpu_data = r.stdout.strip().split(',')
            
            return {
                "gpu_name": gpu_data[0].strip(),
                "memory_size": f"{float(gpu_data[1].strip())/1024:.2f}GB",
                "cuda_cores": None,
                "clock_speed": f"{gpu_data[2].strip()}MHz",
                "power_consumption": f"{gpu_data[3].strip()}W"
            }
        except:
            cmd = ["lspci", "-v", "-nn", "|", "grep", "VGA"]
            r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            return {
                "gpu_name": r.stdout.strip(),
                "memory_size": "Unknown",
                "cuda_cores": None,
                "clock_speed": None,
                "power_consumption": None
            }
    except Exception as e:
        logger.error(f"Failed to get Linux GPU info: {e}")
        return None

def get_gpu_info_macos():
    try:
        # Run system_profiler to get GPU info
        output = subprocess.check_output(['system_profiler', 'SPDisplaysDataType'], text=True)
        
        # Parse output to extract GPU info
        gpu_name = "Unknown"
        gpu_memory = "Unknown"
        
        # Try to find the GPU name
        gpu_name_match = re.search(r'Chipset Model: (.+)', output)
        if gpu_name_match:
            gpu_name = gpu_name_match.group(1).strip()
            
        # Try to get VRAM
        vram_match = re.search(r'VRAM \(.*\): (\d+).*MB', output)
        if vram_match:
            vram_mb = int(vram_match.group(1))
            gpu_memory = f"{vram_mb / 1024:.2f}GB" if vram_mb >= 1024 else f"{vram_mb}MB"
        
        # Format exactly like Windows/Linux versions
        return {
            "gpu_name": gpu_name,
            "memory_size": gpu_memory,
            "cuda_cores": None,
            "clock_speed": None,
            "power_consumption": None
        }
    except Exception as e:
        logger.error(f"Failed to get macOS GPU info: {e}")
        return {
            "gpu_name": "Unknown",
            "memory_size": "Unknown",
            "cuda_cores": None,
            "clock_speed": None,
            "power_consumption": None
        }

def get_system_ram_gb():
    try:
        info = psutil.virtual_memory()
        gb = info.total / (1024**3)
        return f"{gb:.2f}GB"
    except Exception as e:
        logger.error(f"Failed to get RAM info: {e}")
        return None

def get_storage_info():
    storage_info = {
        "type": "Unknown",
        "capacity": "0GB",
        "read_speed": None,
        "write_speed": None
    }
    
    try:
        if is_windows():
            ps_cmd = ["powershell", "-Command", """
                $disk = Get-PhysicalDisk | Select-Object MediaType,Size,Model,FriendlyName;
                ConvertTo-Json -InputObject $disk -Depth 10
            """]
            r = subprocess.run(ps_cmd, capture_output=True, text=True, check=True)
            disk_info = json.loads(r.stdout)
            
            if not isinstance(disk_info, list):
                disk_info = [disk_info]
                
            primary_disk = disk_info[0]
            media_type = primary_disk.get('MediaType', '').lower()
            
            if 'ssd' in media_type or 'solid' in media_type:
                storage_info["type"] = "SSD"
                storage_info["read_speed"] = "550MB/s"
                storage_info["write_speed"] = "520MB/s"
            elif 'nvme' in media_type.lower() or 'nvme' in primary_disk.get('Model', '').lower():
                storage_info["type"] = "NVME"
                storage_info["read_speed"] = "3500MB/s"
                storage_info["write_speed"] = "3000MB/s"
            elif 'hdd' in media_type or 'hard' in media_type:
                storage_info["type"] = "HDD"
                storage_info["read_speed"] = "150MB/s"
                storage_info["write_speed"] = "100MB/s"
            
            total_bytes = psutil.disk_usage('/').total
            storage_info["capacity"] = f"{(total_bytes / (1024**3)):.2f}GB"
            
        elif is_macos():
            # For macOS, use diskutil to get storage info
            try:
                # Get the boot volume identifier
                diskutil_list = subprocess.check_output(['diskutil', 'list'], text=True)
                boot_disk = None
                for line in diskutil_list.splitlines():
                    if "disk" in line and "internal" in line.lower():
                        boot_disk = line.split()[0]
                        break
                
                if boot_disk:
                    # Get info for the primary disk
                    disk_info = subprocess.check_output(['diskutil', 'info', boot_disk], text=True)
                    
                    # Try to determine storage type
                    if 'Solid State' in disk_info or 'SSD' in disk_info:
                        if 'NVMe' in disk_info:
                            storage_info["type"] = "NVME"
                            storage_info["read_speed"] = "3500MB/s"
                            storage_info["write_speed"] = "3000MB/s"
                        else:
                            storage_info["type"] = "SSD"
                            storage_info["read_speed"] = "550MB/s"
                            storage_info["write_speed"] = "520MB/s"
                    else:
                        storage_info["type"] = "HDD"
                        storage_info["read_speed"] = "150MB/s"
                        storage_info["write_speed"] = "100MB/s"
                
                # Use psutil to get total capacity
                total_bytes = psutil.disk_usage('/').total
                storage_info["capacity"] = f"{(total_bytes / (1024**3)):.2f}GB"
            except Exception as e:
                logger.warning(f"Failed to get detailed macOS storage info: {e}. Falling back to psutil.")
                total_bytes = psutil.disk_usage('/').total
                storage_info["capacity"] = f"{(total_bytes / (1024**3)):.2f}GB"
                storage_info["type"] = "SSD"  # Default to SSD for modern Macs
                storage_info["read_speed"] = "550MB/s"
                storage_info["write_speed"] = "520MB/s"
                
        elif is_linux():
            cmd = ["lsblk", "-d", "-o", "NAME,SIZE,ROTA,TRAN"]
            r = subprocess.run(cmd, capture_output=True, text=True, check=True)
            lines = r.stdout.splitlines()[1:]  # Skip header
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    is_rotational = parts[2] == "1"
                    transport = parts[3] if len(parts) > 3 else ""
                    
                    if "nvme" in transport.lower():
                        storage_info["type"] = "NVME"
                        storage_info["read_speed"] = "3500MB/s"
                        storage_info["write_speed"] = "3000MB/s"
                    elif not is_rotational:
                        storage_info["type"] = "SSD"
                        storage_info["read_speed"] = "550MB/s"
                        storage_info["write_speed"] = "520MB/s"
                    else:
                        storage_info["type"] = "HDD"
                        storage_info["read_speed"] = "150MB/s"
                        storage_info["write_speed"] = "100MB/s"
                    
                    total_bytes = psutil.disk_usage('/').total
                    storage_info["capacity"] = f"{(total_bytes / (1024**3)):.2f}GB"
                    break
                    
    except Exception as e:
        logger.error(f"Failed to get storage info: {e}")
        
    return storage_info

def get_system_info(resource_type=None):
    """Gather all system information according to the models."""
    try:
        # Auto-detect resource type if not specified
        if resource_type is None:
            resource_type = "GPU" if has_gpu() else "CPU"
            logger.info(f"Detected resource type: {resource_type}")

        location = get_location()
        resource_id = str(uuid.uuid4())
        ram = get_system_ram_gb()
        storage = get_storage_info()

        # Base resource without cpu_specs or gpu_specs
        resource = {
            "id": resource_id,
            "resource_type": resource_type.upper(),
            "location": location,
            "hourly_price": 0.0,
            "ram": ram,
            "storage": storage,
            "is_active": True
        }

        # Add the appropriate specs based on resource type
        if resource_type.upper() == "CPU":
            if is_windows():
                resource["cpu_specs"] = get_cpu_info_windows()
            elif is_macos():
                resource["cpu_specs"] = get_cpu_info_macos()
            else:
                resource["cpu_specs"] = get_cpu_info_linux()
        elif resource_type.upper() == "GPU":
            if is_windows():
                resource["gpu_specs"] = get_gpu_info_windows()
            elif is_macos():
                resource["gpu_specs"] = get_gpu_info_macos()
            else:
                resource["gpu_specs"] = get_gpu_info_linux()

        return {
            "location": location,
            "compute_resources": [resource]
        }
    except Exception as e:
        logger.error(f"Failed to gather system info: {e}")
        return None

def has_gpu():
    """Detect if system has a GPU."""
    try:
        if is_windows():
            ps_cmd = ["powershell", "-Command", """
                $gpu = Get-CimInstance win32_VideoController | Where-Object { $_.AdapterRAM -ne $null };
                if ($gpu) { ConvertTo-Json $true } else { ConvertTo-Json $false }
            """]
            r = subprocess.run(ps_cmd, capture_output=True, text=True, check=True)
            return json.loads(r.stdout)
        elif is_macos():
            # For macOS, check system_profiler output
            try:
                gpu_info = subprocess.check_output(['system_profiler', 'SPDisplaysDataType'], text=True)
                # If we found a dedicated GPU, it's typically mentioned as such
                if 'Chipset Model' in gpu_info:
                    return True
                return False
            except:
                return False
        else:
            # Try nvidia-smi first
            try:
                subprocess.run(["nvidia-smi"], capture_output=True, check=True)
                return True
            except:
                # Check for any graphics card using lspci
                r = subprocess.run(["lspci"], capture_output=True, text=True, check=True)
                return any("VGA" in line or "3D" in line for line in r.stdout.splitlines())
    except Exception as e:
        logger.error(f"Failed to detect GPU: {e}")
        return False