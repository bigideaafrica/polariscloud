# system_info.py
import json
import logging
import os
import platform
import re
import socket
import subprocess
import time

import psutil
import requests

logger = logging.getLogger('remote_access')

def is_windows():
    return platform.system().lower() == "windows"

def is_linux():
    return platform.system().lower() == "linux"

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
    c = {
        "op_modes": None,
        "address_sizes": None,
        "byte_order": None,
        "total_cpus": None,
        "online_cpus": None,
        "vendor_id": None,
        "cpu_name": None,
        "cpu_family": None,
        "model": None,
        "threads_per_core": None,
        "cores_per_socket": None,
        "sockets": None,
        "stepping": None,
        "cpu_max_mhz": None,
        "cpu_min_mhz": None
    }
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
        
        c["op_modes"] = f"32-bit, 64-bit" if cpu_info.get("DataWidth") == 64 else "32-bit"
        c["address_sizes"] = f"{cpu_info.get('AddressWidth')} bits"
        c["byte_order"] = "Little Endian"
        c["total_cpus"] = int(cpu_info.get("ThreadCount", 0))
        c["vendor_id"] = cpu_info.get("Manufacturer")
        c["cpu_name"] = cpu_info.get("Name")
        c["cpu_family"] = int(cpu_info.get("Family", 0))
        c["cores_per_socket"] = int(cpu_info.get("NumberOfCores", 0))
        c["threads_per_core"] = int(cpu_info.get("ThreadCount", 0)) // int(cpu_info.get("NumberOfCores", 1))
        c["sockets"] = 1
        c["stepping"] = int(cpu_info.get("Stepping", 0)) if cpu_info.get("Stepping") else None
        c["cpu_max_mhz"] = float(cpu_info.get("MaxClockSpeed", 0))
        c["cpu_min_mhz"] = float(cpu_info.get("CurrentClockSpeed", 0))

    except Exception as e:
        logger.error(f"Failed to get Windows CPU info: {e}")
    return c

def get_cpu_info_linux():
    c = {
        "op_modes": None,
        "address_sizes": None,
        "byte_order": None,
        "total_cpus": None,
        "online_cpus": None,
        "vendor_id": None,
        "cpu_name": None,
        "cpu_family": None,
        "model": None,
        "threads_per_core": None,
        "cores_per_socket": None,
        "sockets": None,
        "stepping": None,
        "cpu_max_mhz": None,
        "cpu_min_mhz": None
    }
    try:
        r = subprocess.run(["lscpu"], capture_output=True, text=True, check=True)
        for line in r.stdout.splitlines():
            parts = line.split(":", 1)
            if len(parts) != 2:
                continue
            k = parts[0].strip()
            v = parts[1].strip()
            
            if k == "CPU op-mode(s)":
                c["op_modes"] = v
            elif k == "Address sizes":
                c["address_sizes"] = v
            elif k == "Byte Order":
                c["byte_order"] = v
            elif k == "CPU(s)":
                c["total_cpus"] = int(v)
            elif k == "On-line CPU(s) list":
                c["online_cpus"] = v
            elif k == "Vendor ID":
                c["vendor_id"] = v
            elif k == "Model name":
                c["cpu_name"] = v
            elif k == "CPU family":
                c["cpu_family"] = int(v)
            elif k == "Model":
                c["model"] = int(v)
            elif k == "Thread(s) per core":
                c["threads_per_core"] = int(v)
            elif k == "Core(s) per socket":
                c["cores_per_socket"] = int(v)
            elif k == "Socket(s)":
                c["sockets"] = int(v)
            elif k == "Stepping":
                c["stepping"] = int(v)
            elif k == "CPU max MHz":
                c["cpu_max_mhz"] = float(v)
            elif k == "CPU min MHz":
                c["cpu_min_mhz"] = float(v)
    except Exception as e:
        logger.error(f"Failed to get Linux CPU info: {e}")
    return c

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
        "read_speed": "Unknown",
        "write_speed": "Unknown"
    }
    
    try:
        if is_windows():
            ps_cmd = ["powershell", "-Command", """
                $disk = Get-PhysicalDisk | Select-Object MediaType,Size,Model,FriendlyName;
                ConvertTo-Json -InputObject $disk -Depth 10
            """]
            r = subprocess.run(ps_cmd, capture_output=True, text=True, check=True)
            disk_info = json.loads(r.stdout)
            
            # Handle both single disk and array response
            if not isinstance(disk_info, list):
                disk_info = [disk_info]
                
            # Get primary disk info
            primary_disk = disk_info[0]
            media_type = primary_disk.get('MediaType', '').lower()
            
            # Determine storage type and speeds
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
            
            # Get capacity
            total_bytes = psutil.disk_usage('/').total
            storage_info["capacity"] = f"{(total_bytes / (1024**3)):.2f}GB"

        elif is_linux():
            r = subprocess.run(["lsblk", "-d", "-o", "NAME,SIZE,ROTA,TRAN"], capture_output=True, text=True, check=True)
            lines = r.stdout.splitlines()[1:]  # Skip header
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    is_rotational = parts[2] == "1"
                    transport = parts[3] if len(parts) > 3 else ""
                    
                    if "nvme" in transport:
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

def get_system_info():
    """Gather all system information."""
    try:
        location = get_location()
        
        if is_linux():
            cpu_info = get_cpu_info_linux()
        else:
            cpu_info = get_cpu_info_windows()
            
        ram = get_system_ram_gb()
        storage = get_storage_info()
        
        return {
            "location": location,
            "compute_resources": [{
                "resource_type": "CPU",
                "ram": ram,
                "cpu_specs": cpu_info,
                "storage": storage
            }]
        }
    except Exception as e:
        logger.error(f"Failed to gather system info: {e}")
        return None