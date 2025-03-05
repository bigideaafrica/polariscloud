import ast
import copy
import json
import os
import re
import sys
import inspect
import subprocess
import questionary
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
from communex.client import CommuneClient
from communex.compat.key import classic_load_key

logger = configure_logging()
console = Console()
server_url_ = "https://api.polaris.com"

logger = configure_logging()
console = Console()
server_url_ = os.getenv('SERVER_URL')

def load_system_info(json_path='system_info.json') -> Dict[str, Any]:
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

    flattened = flatten_dict(system_info)
    for key, value in flattened:
        if isinstance(value, list):
            value = ', '.join(map(str, value))
        if 'password' in key.lower():
            value = '*' * 8
        table.add_row(key, str(value))
    console.print(table)

def submit_registration(submission: Dict[str, Any]) -> Dict[str, Any]:
    try:
        with spinner():
            api_url = f'{server_url_}/miners/'
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

def check_commune_balance(key_name: str, required: float = 10.0):
    from subprocess import run
    import re
    result = run(["comx", "key", "balance", key_name], capture_output=True, text=True)
    balance = 0.0
    if result.returncode == 0:
        match = re.search(r"([\d\.]+)", result.stdout)
        if match:
            balance = float(match.group(1))
    return (balance, balance >= required)

def process_compute_resource(resource: Dict[str, Any]) -> Dict[str, Any]:
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
        if online_cpus.startswith('[') and online_cpus.endswith(']'):
            try:
                cpu_list = ast.literal_eval(online_cpus)
                if isinstance(cpu_list, list) and all(isinstance(cpu, int) for cpu in cpu_list):
                    return f"{min(cpu_list)}-{max(cpu_list)}"
            except:
                pass
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
    if not ssh_str:
        return ""
    ssh_str = ssh_str.strip()
    if ssh_str.startswith('ssh://'):
        return ssh_str
    pattern = r'^ssh\s+([^@]+)@([\w\.-]+)\s+-p\s+(\d+)$'
    match = re.match(pattern, ssh_str)
    if match:
        user, host, port = match.groups()
        return f"ssh://{user}@{host}:{port}"
    raise ValueError(f"Invalid SSH format: {ssh_str}")

def register_miner(skip_existing_check=False):
    user_manager = UserManager()
    if not skip_existing_check:
        skip_registration, user_info = user_manager.check_existing_registration()
        if skip_registration:
            console.print("[yellow]Using existing registration.[/yellow]")
            return

    # Check if the user has an existing Commune key
    has_commune_key = questionary.confirm("Do you have an existing Commune key?", default=True).ask()
    if has_commune_key:
        result_keys = subprocess.run(["comx", "key", "list"], capture_output=True, text=True)
        if result_keys.returncode != 0 or not result_keys.stdout.strip():
            console.print("[yellow]No existing keys found. You will need to create one.[/yellow]")
            has_commune_key = False
        else:
            console.print(Panel(
                f"Available keys:\n\n{result_keys.stdout}",
                title="Your Commune Keys",
                border_style="cyan"
            ))
            selected_key = Prompt.ask("Enter the name of the key you want to use")
            if not selected_key:
                console.print("[yellow]No key provided. You will need to create a new key.[/yellow]")
                has_commune_key = False

    # Create a new Commune key if needed
    if not has_commune_key:
        selected_key = Prompt.ask("Enter a name for your new Commune key")
        create_result = subprocess.run(["comx", "key", "create", selected_key], capture_output=True, text=True)
        if create_result.returncode != 0:
            console.print(Panel(f"[red]Failed to create key: {create_result.stderr}[/red]", border_style="red"))
            return
        console.print(f"[green]Key {selected_key} created successfully.[/green]")

    # Check Commune balance
    balance, is_sufficient = check_commune_balance(selected_key, 10)
    if not is_sufficient:
        console.print(Panel(
            f"[yellow]WARNING: Your current balance is {balance} COMAI.[/yellow]\n"
            "[yellow]A minimum of 10 COMAI is recommended for registration.[/yellow]\n"
            "[yellow]You may proceed, but some network features might be limited.[/yellow]",
            title="⚠️ Low Balance Warning",
            border_style="yellow"
        ))

    # Select network
    console.print(Panel(
        "Available networks:\n1. Mainnet (netuid=33)\n2. Testnet (netuid=12)",
        title="Network Selection",
        border_style="cyan"
    ))
    network_choice = Prompt.ask(
        "Select network (enter 1 for Mainnet or 2 for Testnet)",
        choices=["1", "2"],
        default="1"
    )
    netuid = 33 if network_choice == "1" else 12
    network_name = "Mainnet" if network_choice == "1" else "Testnet"
    console.print(f"[green]Selected network: {network_name} (netuid={netuid})[/green]")

    # Attempt Commune subnet registration
    try:
        from communex.client import CommuneClient
        from communex.compat.key import classic_load_key
        key = classic_load_key(selected_key)
        ss58_address = key.ss58_address
        commune_node_url = "wss://api.communeai.net/"
        client = CommuneClient(commune_node_url)
        modules_keys = client.query_map_key(netuid)
        commune_uid = next((uid for uid, address in modules_keys.items() if address == ss58_address), None)

        if not commune_uid:
            console.print(Panel(
                f"[red]Failed to retrieve Commune UID for key '{selected_key}' on network {network_name} (netuid={netuid}).[/red]\n"
                "[red]Key may not be registered on the Polaris subnet.[/red]\n\n"
                "Registration process stopped.",
                title="❌ Commune Registration Failed",
                border_style="red"
            ))
            return  # Stop the process if Commune subnet registration fails

        # Only proceed with username and system info if subnet registration is successful
        username = Prompt.ask("Enter your desired username", default="")
        if not username:
            console.print(Panel(
                "[red]Username is required for registration.[/red]",
                title="Error",
                border_style="red"
            ))
            return

        # Load and display system info
        system_info = load_system_info()
        display_system_info(system_info)

        # Prepare submission data
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
                return

        # Submit registration to your server
        result = submit_registration(submission)
        if not result.get('miner_id'):
            console.print(Panel(
                "[red]Compute registration failed. Unable to proceed with Commune registration.[/red]",
                title="❌ Registration Error",
                border_style="red"
            ))
            return

        miner_id = result['miner_id']
        console.print(f"[green]Miner ID: {miner_id}[/green]")

        # Register with Commune network
        commune_result = network_handler.register_commune_miner(
            wallet_name=selected_key,
            commune_uid=commune_uid,
            wallet_address=ss58_address
        )
        if commune_result and commune_result.get('status') == 'success':
            network_handler.verify_commune_status(miner_id)
            console.print(Panel(
                "[green]Successfully registered with Commune network![/green]",
                title="🌐 Commune Registration Status",
                border_style="green"
            ))
        else:
            console.print(Panel(
                "[yellow]Warning: Compute network registration successful, but Commune network registration failed.[/yellow]",
                title="⚠️ Partial Registration",
                border_style="yellow"
            ))
    except Exception as e:
        console.print(Panel(
            f"[red]An error occurred during Commune subnet registration: {str(e)}[/red]",
            title="❌ Commune Registration Error",
            border_style="red"
        ))

def register_independent_miner(skip_existing_check=False):
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm
    import questionary
    from .start import start_polaris
    import socket
    import requests
    console = Console()
    from src.user_manager import UserManager
    user_manager = UserManager()
    if not skip_existing_check:
        skip_registration, user_info = user_manager.check_existing_registration()
        if skip_registration:
            miner_id = user_info.get('miner_id', 'Unknown')
            username = user_info.get('username', 'Unknown')
            console.print(Panel(
                f"[yellow]Existing registration found:[/yellow]\n"
                f"Miner ID: [bold cyan]{miner_id}[/bold cyan]\n"
                f"Username: [bold cyan]{username}[/bold cyan]",
                title="⚠️ Existing Registration",
                border_style="yellow"
            ))
            if not Confirm.ask("Do you want to proceed with a new registration?", default=False):
                console.print("[yellow]Using existing registration.[/yellow]")
                return
    console.print(Panel(
        "[cyan]Independent Miner Registration[/cyan]\n"
        "[yellow]You will register your miner and compute resources without joining any network.[/yellow]",
        title="Independent Miner",
        border_style="cyan"
    ))
    system_info = load_system_info()
    if system_info:
        display_system_info(system_info)
        if Confirm.ask("Do you want to proceed with registration?", default=True):
            username = questionary.text("Enter your desired username:").ask()
            if not username:
                console.print("[error]Username is required for registration.[/error]")
                return
            location = system_info.get("location")
            if not location:
                try:
                    response = requests.get('https://ipinfo.io/json', timeout=3)
                    if response.status_code == 200:
                        ip_data = response.json()
                        if 'country' in ip_data and 'region' in ip_data:
                            location = f"{ip_data['region']}, {ip_data['country']}"
                        elif 'country' in ip_data:
                            location = ip_data['country']
                except:
                    try:
                        hostname = socket.gethostname()
                        if hostname:
                            location = f"Host: {hostname}"
                    except:
                        pass
            if not location:
                location = "Polaris HQ"
            submission = {
                "name": username,
                "location": location,
                "description": "Independent Miner registered via Polaris CLI tool",
                "compute_resources": [],
                "registration_type": "independent"
            }
            compute_resources = system_info.get("compute_resources", [])
            if isinstance(compute_resources, dict):
                compute_resources = [compute_resources]
            if not compute_resources:
                console.print("[error]No compute resources found.[/error]")
                return
            for resource in compute_resources:
                try:
                    resource_copy = resource.copy() if isinstance(resource, dict) else {}
                    if not resource_copy.get("location"):
                        resource_copy["location"] = location
                    processed_resource = process_compute_resource(resource_copy)
                    submission["compute_resources"].append(processed_resource)
                except Exception as e:
                    console.print(Panel(
                        f"[red]Error processing compute resource:[/red]\n{str(e)}",
                        title="Error",
                        border_style="red"
                    ))
                    return
            try:
                result = submit_registration(submission)
                if not result or not result.get('miner_id'):
                    console.print("[error]Failed to register with server.[/error]")
                    return
                miner_id = result.get('miner_id')
                network_info = submission['compute_resources'][0]['network']
                user_manager.save_user_info(miner_id, username, network_info)
                console.print(Panel(
                    "[green]Independent miner registered successfully![/green]\n\n"
                    f"Miner ID: [bold cyan]{miner_id}[/bold cyan]\n"
                    f"Username: [bold cyan]{username}[/bold cyan]\n\n"
                    "[yellow]Important: Save your Miner ID - you'll need it to manage your compute resources.[/yellow]\n"
                    "[yellow]Note: As an independent miner, you are not connected to any network.[/yellow]",
                    title="✅ Registration Complete",
                    border_style="green"
                ))
                from .start import start_polaris
                if start_polaris():
                    console.print("[success]Polaris services started successfully![/success]")
                else:
                    console.print("[error]Failed to start Polaris services.[/error]")
            except Exception as e:
                console.print(Panel(
                    f"[red]Error during registration: {str(e)}[/red]",
                    title="Error",
                    border_style="red"
                ))
        else:
            console.print("[yellow]Registration cancelled.[/yellow]")

def validate_compute_resources(compute_resources) -> None:
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
