# polaris_cli/register.py

import ast
import copy
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict

import requests
from click_spinner import spinner
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from polaris_cli.network_handler import NetworkSelectionHandler, NetworkType
from src.pid_manager import PID_FILE
from src.user_manager import UserManager
from src.utils import configure_logging

logger = configure_logging()
console = Console()

def load_system_info(json_path='system_info.json') -> Dict[str, Any]:
    """
    Load system information from JSON file.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    system_info_full_path = os.path.join(project_root, json_path)

    if not os.path.exists(system_info_full_path):
        console.print(Panel(
            "[red]System information file not found.[/red]\n"
            "Please ensure that 'polaris start' is running.",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)

    try:
        with open(system_info_full_path, 'r') as f:
            data = json.load(f)
        logger.info("System information loaded successfully.")
        return data[0]
    except json.JSONDecodeError as e:
        console.print(Panel(
            f"[red]Failed to parse the system information file: {e}[/red]",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)
    except Exception as e:
        console.print(Panel(
            f"[red]Error reading system information: {e}[/red]",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)

def display_system_info(system_info: Dict[str, Any]) -> None:
    """
    Display system information in a formatted table.
    """
    table = Table(title="System Information", box=box.ROUNDED)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    def flatten_dict(d: Dict[str, Any], parent_key: str = '') -> list:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key))
            elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                for i, item in enumerate(v):
                    items.extend(flatten_dict(item, f"{new_key}[{i}]"))
            else:
                items.append((new_key, v))
        return items

    # Flatten and display system info
    flattened = flatten_dict(system_info)
    for key, value in flattened:
        if isinstance(value, list):
            value = ', '.join(map(str, value))
        # Mask sensitive information
        if 'password' in key.lower():
            value = '*' * 8
        table.add_row(key, str(value))

    console.print(table)

def submit_registration(submission: Dict[str, Any]) -> Dict[str, Any]:
    """
    Submit registration to the API.
    """
    try:
        with spinner():
            api_url = 'https://orchestrator-gekh.onrender.com/api/v1/miners/'
            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, json=submission, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
    except requests.HTTPError as http_err:
        try:
            error_details = response.json()
            console.print(Panel(
                f"[red]Registration failed: {error_details}[/red]",
                title="Error",
                border_style="red"
            ))
            logger.error(f"Registration failed: {json.dumps(error_details, indent=2)}")
        except json.JSONDecodeError:
            console.print(Panel(
                f"[red]Registration failed: {http_err}[/red]",
                title="Error",
                border_style="red"
            ))
        sys.exit(1)
    except requests.Timeout:
        console.print(Panel(
            "[red]Request timed out while submitting registration.[/red]",
            title="Timeout Error",
            border_style="red"
        ))
        sys.exit(1)
    except Exception as err:
        console.print(Panel(
            f"[red]An error occurred during registration: {err}[/red]",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)

def display_registration_success(result: Dict[str, Any]) -> None:
    """
    Display successful registration details.
    """
    miner_id = result.get('miner_id', 'N/A')
    message = result.get('message', 'Registration successful')
    added_resources = result.get('added_resources', [])

    console.print(Panel(
        f"[green]{message}[/green]\n\n"
        f"Miner ID: [bold cyan]{miner_id}[/bold cyan]\n"
        f"Added Resources: [cyan]{', '.join(added_resources) if added_resources else 'None'}[/cyan]\n\n"
        "[yellow]Important: Save your Miner ID - you'll need it to manage your compute resources.[/yellow]",
        title="✅ Registration Complete",
        border_style="green"
    ))

def process_compute_resource(resource: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process and validate a compute resource.
    """
    return {
        "id": resource.get("id"),
        "resource_type": resource.get("resource_type"),
        "location": resource.get("location"),
        "hourly_price": resource.get("hourly_price"),
        "ram": resource.get("ram"),
        "storage": {
            "type": resource.get("storage", {}).get("type"),
            "capacity": resource.get("storage", {}).get("capacity"),
            "read_speed": resource.get("storage", {}).get("read_speed"),
            "write_speed": resource.get("storage", {}).get("write_speed")
        },
        "cpu_specs": {
            "op_modes": resource.get("cpu_specs", {}).get("op_modes"),
            "address_sizes": resource.get("cpu_specs", {}).get("address_sizes"),
            "byte_order": resource.get("cpu_specs", {}).get("byte_order"),
            "total_cpus": resource.get("cpu_specs", {}).get("total_cpus"),
            "online_cpus": process_online_cpus(
                resource.get("cpu_specs", {}).get("online_cpus"),
                resource.get("id")
            ),
            "vendor_id": resource.get("cpu_specs", {}).get("vendor_id"),
            "cpu_name": resource.get("cpu_specs", {}).get("cpu_name"),
            "cpu_family": resource.get("cpu_specs", {}).get("cpu_family"),
            "model": resource.get("cpu_specs", {}).get("model"),
            "threads_per_core": resource.get("cpu_specs", {}).get("threads_per_core"),
            "cores_per_socket": resource.get("cpu_specs", {}).get("cores_per_socket"),
            "sockets": resource.get("cpu_specs", {}).get("sockets"),
            "stepping": process_stepping(
                resource.get("cpu_specs", {}).get("stepping"),
                resource.get("id")
            ),
            "cpu_max_mhz": resource.get("cpu_specs", {}).get("cpu_max_mhz"),
            "cpu_min_mhz": resource.get("cpu_specs", {}).get("cpu_min_mhz")
        },
        "network": {
            "internal_ip": resource.get("network", {}).get("internal_ip"),
            "ssh": process_ssh(resource.get("network", {}).get("ssh")),
            "password": resource.get("network", {}).get("password"),
            "username": resource.get("network", {}).get("username"),
            "open_ports": resource.get("network", {}).get("open_ports", ["22"])
        }
    }

def process_stepping(stepping: Any, resource_id: str) -> int:
    """Process and validate CPU stepping value."""
    if stepping is None:
        return 1
    if not isinstance(stepping, int):
        console.print(Panel(
            f"[red]Invalid 'stepping' value for resource {resource_id}.[/red]\n"
            "It must be an integer.",
            title="Validation Error",
            border_style="red"
        ))
        sys.exit(1)
    return stepping

def process_online_cpus(online_cpus: Any, resource_id: str) -> str:
    """Process and validate online CPUs configuration."""
    if isinstance(online_cpus, list):
        if not all(isinstance(cpu, int) for cpu in online_cpus):
            console.print(Panel(
                f"[red]Invalid CPU identifiers in 'online_cpus' for resource {resource_id}.[/red]\n"
                "All CPU identifiers must be integers.",
                title="Validation Error",
                border_style="red"
            ))
            sys.exit(1)
        if not online_cpus:
            console.print(Panel(
                f"[red]Empty 'online_cpus' list for resource {resource_id}.[/red]",
                title="Validation Error",
                border_style="red"
            ))
            sys.exit(1)
        return f"{min(online_cpus)}-{max(online_cpus)}"
    
    if isinstance(online_cpus, str):
        # Handle string representation of list
        if online_cpus.startswith('[') and online_cpus.endswith(']'):
            try:
                cpu_list = ast.literal_eval(online_cpus)
                if isinstance(cpu_list, list) and all(isinstance(cpu, int) for cpu in cpu_list):
                    return f"{min(cpu_list)}-{max(cpu_list)}"
            except:
                pass
        
        # Handle range format
        if '-' in online_cpus:
            try:
                start, end = map(int, online_cpus.split('-'))
                if start <= end:
                    return f"{start}-{end}"
            except:
                pass
    
    console.print(Panel(
        f"[red]Invalid 'online_cpus' format for resource {resource_id}.[/red]\n"
        "Expected format: '0-15' or a list of integers.",
        title="Validation Error",
        border_style="red"
    ))
    sys.exit(1)

def process_ssh(ssh_str: str) -> str:
    """Process and validate SSH connection string."""
    if not ssh_str:
        return ""
        
    ssh_str = ssh_str.strip()
    if ssh_str.startswith('ssh://'):
        return ssh_str
    
    # Parse traditional SSH command format
    pattern = r'^ssh\s+([^@]+)@([\w\.-]+)\s+-p\s+(\d+)$'
    match = re.match(pattern, ssh_str)
    if match:
        user, host, port = match.groups()
        return f"ssh://{user}@{host}:{port}"
    
    raise ValueError(f"Invalid SSH format: {ssh_str}")

def register_miner():
    """
    Main registration function.
    """
    user_manager = UserManager()
    
    # Check for existing registration
    skip_registration, user_info = user_manager.check_existing_registration()
    if skip_registration:
        console.print("[yellow]Using existing registration.[/yellow]")
        return
    
    # Load and validate system info
    system_info = load_system_info()
    display_system_info(system_info)

    if not Confirm.ask("Do you want to proceed with this registration?", default=True):
        console.print("[yellow]Registration cancelled.[/yellow]")
        sys.exit(0)

    # Get username
    username = Prompt.ask("Enter your desired username", default="")
    if not username:
        console.print(Panel(
            "[red]Username is required for registration.[/red]",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)

    # Handle network selection
    network_handler = NetworkSelectionHandler()
    network_type = network_handler.select_network()

    if network_type == NetworkType.BITTENSOR:
        network_handler.handle_bittensor_registration()
        return

    # Handle Commune network registration
    wallet_name = None
    commune_uid = None
    if network_type == NetworkType.COMMUNE:
        result = network_handler.handle_commune_registration()
        if not result:
            console.print(Panel(
                "[red]Commune registration failed.[/red]",
                title="Error",
                border_style="red"
            ))
            sys.exit(1)
        wallet_name, commune_uid = result

    # Prepare submission
    submission = {
        "name": username,
        "location": system_info.get("location", "N/A"),
        "description": "Registered via Polaris CLI tool",
        "compute_resources": []
    }

    # Process compute resources
    compute_resources = system_info.get("compute_resources", [])
    if isinstance(compute_resources, dict):
        compute_resources = [compute_resources]
    
    for resource in compute_resources:
        try:
            processed_resource = process_compute_resource(resource)
            submission["compute_resources"].append(processed_resource)
        except Exception as e:
            console.print(Panel(
                f"[red]Error processing compute resource:[/red]\n{str(e)}",
                title="Error",
                border_style="red"
            ))
            sys.exit(1)

    # Submit registration
    result = submit_registration(submission)

    # Save user information
    if result.get('miner_id'):
        network_info = submission['compute_resources'][0]['network']
        user_manager.save_user_info(result['miner_id'], username, network_info)
        
        # Display results
        display_registration_success(result)

        # Handle Commune network post-registration
        if network_type == NetworkType.COMMUNE and commune_uid:
            commune_result = network_handler.register_commune_miner(
                result['miner_id'],
                commune_uid
            )
            if commune_result:
                console.print(Panel(
                    "[green]Successfully registered with Commune network![/green]\n"
                    f"Wallet Name: [cyan]{wallet_name}[/cyan]\n"
                    f"Commune UID: [cyan]{commune_uid}[/cyan]",
                    title="🌐 Commune Registration Status",
                    border_style="green"
                ))
            else:
                console.print(Panel(
                    "[yellow]Warning: Compute network registration successful, but Commune network registration failed.[/yellow]\n"
                    "You can try registering with Commune network later using your miner ID.",
                    title="⚠️ Partial Registration",
                    border_style="yellow"
                ))

def validate_compute_resources(compute_resources) -> None:
    """
    Validate compute resources structure and required fields.
    
    Args:
        compute_resources: List or dict of compute resources
    
    Raises:
        SystemExit: If validation fails
    """
    if not compute_resources:
        console.print(Panel(
            "[red]No compute resources found in system info.[/red]",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)

    required_fields = [
        "id", "resource_type", "location", "hourly_price",
        "ram", "storage.type", "storage.capacity",
        "storage.read_speed", "storage.write_speed",
        "cpu_specs.op_modes", "cpu_specs.total_cpus",
        "cpu_specs.online_cpus", "cpu_specs.vendor_id",
        "cpu_specs.cpu_name", "network.internal_ip",
        "network.ssh", "network.password",
        "network.username"
    ]

    def check_field(resource, field):
        path = field.split('.')
        value = resource
        for key in path:
            if not isinstance(value, dict) or key not in value:
                return False
            value = value[key]
        return value is not None

    for resource in (compute_resources if isinstance(compute_resources, list) else [compute_resources]):
        missing_fields = [field for field in required_fields if not check_field(resource, field)]
        
        if missing_fields:
            console.print(Panel(
                f"[red]Missing required fields for resource {resource.get('id', 'unknown')}:[/red]\n"
                f"{', '.join(missing_fields)}",
                title="Validation Error",
                border_style="red"
            ))
            sys.exit(1)

def validate_ram_format(ram_value: str, resource_id: str) -> None:
    """
    Validate RAM format.
    
    Args:
        ram_value: RAM value to validate
        resource_id: ID of the resource for error reporting
    
    Raises:
        SystemExit: If validation fails
    """
    if not isinstance(ram_value, str) or not ram_value.endswith("GB"):
        console.print(Panel(
            f"[red]Invalid RAM format for resource {resource_id}.[/red]\n"
            "Expected format: '16.0GB' or similar",
            title="Validation Error",
            border_style="red"
        ))
        sys.exit(1)
    
    try:
        float(ram_value[:-2])
    except ValueError:
        console.print(Panel(
            f"[red]Invalid RAM value for resource {resource_id}.[/red]\n"
            "RAM value must be a number followed by 'GB'",
            title="Validation Error",
            border_style="red"
        ))
        sys.exit(1)

if __name__ == "__main__":
    register_miner()