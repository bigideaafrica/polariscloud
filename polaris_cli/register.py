import ast
import copy
import json
import os
import re
import sys

import requests
from click_spinner import spinner
from rich import box
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from src.pid_manager import PID_FILE
from src.utils import configure_logging

logger = configure_logging()
console = Console()

def load_system_info(json_path='system_info.json'):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    system_info_full_path = os.path.join(project_root, json_path)

    if not os.path.exists(system_info_full_path):
        logger.error("system_info.json not found. Ensure that 'polaris start' is running.")
        console.print("[red]System information file not found. Ensure that 'polaris start' is running.[/red]")
        sys.exit(1)
    
    try:
        with open(system_info_full_path, 'r') as f:
            data = json.load(f)
        logger.info("System information loaded successfully.")
        return data[0]
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {e}")
        console.print("[red]Failed to parse the system information file.[/red]")
        sys.exit(1)

def display_system_info(system_info):
    table = Table(title="System Information", box=box.ROUNDED)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    
    def flatten(obj, parent_key=''):
        items = []
        for k, v in obj.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten(v, new_key))
            else:
                items.append((new_key, v))
        return items

    flattened = flatten(system_info)
    
    for key, value in flattened:
        if isinstance(value, list):
            value = ', '.join(map(str, value))
        table.add_row(key, str(value))
    
    console.print(table)

def confirm_registration():
    return Confirm.ask("Do you want to proceed with this registration?", default=True)

def get_username():
    return Prompt.ask("Enter your desired username", default="")

def submit_registration(submission):
    try:
        with spinner():
            api_url = 'https://orchestrator-gekh.onrender.com/api/v1/miners/'
            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, json=submission, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            return result
    except requests.HTTPError as http_err:
        try:
            error_details = response.json()
            console.print(f"[red]Registration failed: {error_details}[/red]")
            logger.error(f"Registration failed: {json.dumps(error_details, indent=2)}")
        except json.JSONDecodeError:
            console.print(f"[red]Registration failed: {http_err}[/red]")
            logger.error(f"Registration failed: {http_err}")
        sys.exit(1)
    except requests.Timeout:
        console.print("[red]Request timed out while submitting registration.[/red]")
        logger.error("Request timed out while submitting registration.")
        sys.exit(1)
    except Exception as err:
        console.print(f"[red]An error occurred during registration: {err}[/red]")
        logger.error(f"An error occurred during registration: {err}")
        sys.exit(1)

def display_registration_status(result):
    miner_id = result.get('miner_id', 'N/A')
    message = result.get('message', 'No message provided.')
    added_resources = result.get('added_resources', [])
    
    table = Table(title="Registration Status", box=box.ROUNDED)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Details", style="magenta")
    
    table.add_row("Message", message)
    table.add_row("Miner ID", miner_id)
    table.add_row("Added Resources", "\n".join(added_resources) if added_resources else "N/A")
    
    console.print(table)
    console.print("\n[bold yellow]🔑 Important: Save your Miner ID[/bold yellow]")
    console.print(f"Your Miner ID is: [bold cyan]{miner_id}[/bold cyan]")
    console.print("You will need this ID to manage your compute resources.")
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    system_info_path = os.path.join(project_root, 'system_info.json')
    if os.path.exists(system_info_path):
        try:
            os.remove(system_info_path)
            logger.info(f"Removed {system_info_path} after registration.")
        except Exception as e:
            logger.warning(f"Failed to remove system_info.json: {e}")

def reformat_ssh(ssh_str):
    ssh_str = ssh_str.strip()
    if ssh_str.startswith('ssh://'):
        return ssh_str
    else:
        pattern = r'^ssh\s+([^@]+)@([\w\.-]+)\s+-p\s+(\d+)$'
        match = re.match(pattern, ssh_str)
        if match:
            user = match.group(1)
            host = match.group(2)
            port = match.group(3)
            return f"ssh://{user}@{host}:{port}"
        else:
            raise ValueError(f"SSH string '{ssh_str}' is not in the expected format.")

def register_miner():
    system_info = load_system_info()
    display_system_info(system_info)
    
    if not confirm_registration():
        console.print("[yellow]Registration cancelled.[/yellow]")
        sys.exit(0)
    
    username = get_username()
    
    if not username:
        console.print("[red]Username is required for registration.[/red]")
        sys.exit(1)
    
    submission = {
        "name": username,
        "location": system_info.get("location", "N/A"),
        "description": "Registered via Polaris CLI tool",
        "compute_resources": []
    }
    
    compute_resources = system_info.get("compute_resources", [])
    
    if isinstance(compute_resources, dict):
        compute_resources = [compute_resources]
    elif not isinstance(compute_resources, list):
        console.print("[red]'compute_resources' must be a list or a dictionary in system_info.json.[/red]")
        logger.error("'compute_resources' must be a list or a dictionary in system_info.json.")
        sys.exit(1)
    
    for resource in compute_resources:
        resource_submission = {
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
                "online_cpus": resource.get("cpu_specs", {}).get("online_cpus"),
                "vendor_id": resource.get("cpu_specs", {}).get("vendor_id"),
                "cpu_name": resource.get("cpu_specs", {}).get("cpu_name"),
                "cpu_family": resource.get("cpu_specs", {}).get("cpu_family"),
                "model": resource.get("cpu_specs", {}).get("model"),
                "threads_per_core": resource.get("cpu_specs", {}).get("threads_per_core"),
                "cores_per_socket": resource.get("cpu_specs", {}).get("cores_per_socket"),
                "sockets": resource.get("cpu_specs", {}).get("sockets"),
                "stepping": resource.get("cpu_specs", {}).get("stepping"),
                "cpu_max_mhz": resource.get("cpu_specs", {}).get("cpu_max_mhz"),
                "cpu_min_mhz": resource.get("cpu_specs", {}).get("cpu_min_mhz")
            },
            "network": {
                "internal_ip": resource.get("network", {}).get("internal_ip"),
                "ssh": resource.get("network", {}).get("ssh"),
                "password": resource.get("network", {}).get("password"),
                "username": resource.get("network", {}).get("username"),
                "open_ports": resource.get("network", {}).get("open_ports")
            }
        }
        
        resource_submission.pop("is_active", None)
        
        try:
            stepping = resource_submission["cpu_specs"]["stepping"]
            if stepping is None:
                stepping = 1
                resource_submission["cpu_specs"]["stepping"] = stepping
                logger.info(f"'stepping' was None for resource {resource_submission['id']}. Set to 1.")
            
            if not isinstance(stepping, int):
                console.print(f"[red]Invalid 'stepping' value for resource {resource_submission['id']}. It must be an integer.[/red]")
                logger.error(f"Invalid 'stepping' value for resource {resource_submission['id']}. It must be an integer.")
                sys.exit(1)
            
            ram = resource_submission["ram"]
            if isinstance(ram, str) and ram.endswith("GB"):
                try:
                    float(ram[:-2])
                except ValueError:
                    console.print(f"[red]Invalid RAM format for resource {resource_submission['id']}. Expected a numerical value like '15.68GB'.[/red]")
                    logger.error(f"Invalid RAM format for resource {resource_submission['id']}. Expected a numerical value like '15.68GB'.")
                    sys.exit(1)
            else:
                console.print(f"[red]Invalid RAM format for resource {resource_submission['id']}. Expected a string ending with 'GB'.[/red]")
                logger.error(f"Invalid RAM format for resource {resource_submission['id']}. Expected a string ending with 'GB'.")
                sys.exit(1)
            
            online_cpus = resource_submission["cpu_specs"]["online_cpus"]
            
            if isinstance(online_cpus, list):
                if all(isinstance(cpu, int) for cpu in online_cpus):
                    if online_cpus:
                        cpu_range = f"{online_cpus[0]}-{online_cpus[-1]}"
                        resource_submission["cpu_specs"]["online_cpus"] = cpu_range
                        logger.info(f"Converted 'online_cpus' list to range string '{cpu_range}' for resource {resource_submission['id']}.")
                    else:
                        console.print(f"[red]'online_cpus' list is empty for resource {resource_submission['id']}.[/red]")
                        logger.error(f"'online_cpus' list is empty for resource {resource_submission['id']}.")
                        sys.exit(1)
                else:
                    console.print(f"[red]Invalid CPU identifiers in 'online_cpus' for resource {resource_submission['id']}. Must be integers.[/red]")
                    logger.error(f"Invalid CPU identifiers in 'online_cpus' for resource {resource_submission['id']}. Must be integers.")
                    sys.exit(1)
            elif isinstance(online_cpus, str):
                ssh_original = resource_submission["network"]["ssh"]
                try:
                    ssh_reformatted = reformat_ssh(ssh_original)
                    resource_submission["network"]["ssh"] = ssh_reformatted
                    logger.info(f"Reformatted 'ssh' for resource {resource_submission['id']}: {ssh_reformatted}")
                except ValueError as ve:
                    console.print(f"[red]{ve}[/red]")
                    logger.error(str(ve))
                    sys.exit(1)
                
                if online_cpus.startswith('[') and online_cpus.endswith(']'):
                    try:
                        online_cpus_list = ast.literal_eval(online_cpus)
                        if isinstance(online_cpus_list, list) and all(isinstance(cpu, int) for cpu in online_cpus_list):
                            if online_cpus_list:
                                cpu_range = f"{online_cpus_list[0]}-{online_cpus_list[-1]}"
                                resource_submission["cpu_specs"]["online_cpus"] = cpu_range
                                logger.info(f"Parsed and converted 'online_cpus' to range string '{cpu_range}' for resource {resource_submission['id']}.")
                            else:
                                console.print(f"[red]'online_cpus' list is empty for resource {resource_submission['id']}.[/red]")
                                logger.error(f"'online_cpus' list is empty for resource {resource_submission['id']}.")
                                sys.exit(1)
                        else:
                            console.print(f"[red]Invalid 'online_cpus' list format for resource {resource_submission['id']}.[/red]")
                            logger.error(f"Invalid 'online_cpus' list format for resource {resource_submission['id']}.")
                            sys.exit(1)
                    except (ValueError, SyntaxError):
                        console.print(f"[red]Failed to parse 'online_cpus' for resource {resource_submission['id']}.[/red]")
                        logger.error(f"Failed to parse 'online_cpus' for resource {resource_submission['id']}.")
                        sys.exit(1)
                elif "-" in online_cpus:
                    parts = online_cpus.split('-')
                    if len(parts) != 2:
                        console.print(f"[red]Invalid 'online_cpus' format for resource {resource_submission['id']}. Expected format like '0-15'.[/red]")
                        logger.error(f"Invalid 'online_cpus' format for resource {resource_submission['id']}. Expected format like '0-15'.")
                        sys.exit(1)
                    try:
                        start, end = parts
                        start = int(start.strip())
                        end = int(end.strip())
                        if start > end:
                            raise ValueError
                        resource_submission["cpu_specs"]["online_cpus"] = f"{start}-{end}"
                        logger.info(f"Validated and set 'online_cpus' to '{start}-{end}' for resource {resource_submission['id']}.")
                    except ValueError:
                        console.print(f"[red]Invalid 'online_cpus' numbers in range for resource {resource_submission['id']}.[/red]")
                        logger.error(f"Invalid 'online_cpus' numbers in range for resource {resource_submission['id']}.")
                        sys.exit(1)
                else:
                    console.print(f"[red]Invalid 'online_cpus' format for resource {resource_submission['id']}. Expected format like '0-15' or a list string.[/red]")
                    logger.error(f"Invalid 'online_cpus' format for resource {resource_submission['id']}. Expected format like '0-15' or a list string.")
                    sys.exit(1)
            else:
                console.print(f"[red]Invalid 'online_cpus' format for resource {resource_submission['id']}. Expected format like '0-15' or a list string.[/red]")
                logger.error(f"Invalid 'online_cpus' format for resource {resource_submission['id']}. Expected format like '0-15' or a list string.")
                sys.exit(1)
            
            open_ports = resource_submission["network"]["open_ports"]
            if isinstance(open_ports, list):
                if all(isinstance(port, str) for port in open_ports):
                    port_pattern = re.compile(r'^(\d{1,5})(-\d{1,5})?$')
                    for port in open_ports:
                        if not port_pattern.match(port):
                            console.print(f"[red]Invalid port format '{port}' in 'open_ports' for resource {resource_submission['id']}.[/red]")
                            logger.error(f"Invalid port format '{port}' in 'open_ports' for resource {resource_submission['id']}.")
                            sys.exit(1)
                else:
                    console.print(f"[red]All 'open_ports' must be strings for resource {resource_submission['id']}.[/red]")
                    logger.error(f"All 'open_ports' must be strings for resource {resource_submission['id']}.")
                    sys.exit(1)
            else:
                console.print(f"[red]'open_ports' must be a list for resource {resource_submission['id']}.[/red]")
                logger.error(f"'open_ports' must be a list for resource {resource_submission['id']}.")
                sys.exit(1)
            
            password = resource_submission["network"]["password"]
            username_net = resource_submission["network"]["username"]
            if not isinstance(password, str) or not password.strip():
                console.print(f"[red]Invalid 'password' for resource {resource_submission['id']}. It must be a non-empty string.[/red]")
                logger.error(f"Invalid 'password' for resource {resource_submission['id']}. It must be a non-empty string.")
                sys.exit(1)
            if not isinstance(username_net, str) or not username_net.strip():
                console.print(f"[red]Invalid 'username' in network for resource {resource_submission['id']}. It must be a non-empty string.[/red]")
                logger.error(f"Invalid 'username' in network for resource {resource_submission['id']}. It must be a non-empty string.")
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error processing compute resource data: {e}[/red]")
            logger.error(f"Error processing compute resource data: {e}")
            sys.exit(1)
        
        required_fields = [
            "id", "resource_type", "location", "hourly_price",
            "ram", "storage.type", "storage.capacity",
            "storage.read_speed", "storage.write_speed",
            "cpu_specs.op_modes", "cpu_specs.address_sizes",
            "cpu_specs.byte_order", "cpu_specs.total_cpus",
            "cpu_specs.online_cpus", "cpu_specs.vendor_id",
            "cpu_specs.cpu_name", "cpu_specs.cpu_family",
            "cpu_specs.model", "cpu_specs.threads_per_core",
            "cpu_specs.cores_per_socket", "cpu_specs.sockets",
            "cpu_specs.stepping", "cpu_specs.cpu_max_mhz",
            "cpu_specs.cpu_min_mhz", "network.internal_ip",
            "network.ssh", "network.password",
            "network.username", "network.open_ports"
        ]
        
        def check_fields(data, fields):
            missing = []
            for field in fields:
                keys = field.split('.')
                value = data
                for key in keys:
                    value = value.get(key)
                    if value is None:
                        missing.append(field)
                        break
            return missing
        
        missing_fields = check_fields(resource_submission, required_fields)
        if missing_fields:
            console.print(f"[red]Compute resource missing fields: {', '.join(missing_fields)}[/red]")
            logger.error(f"Compute resource missing fields: {', '.join(missing_fields)}")
            sys.exit(1)
        
        submission["compute_resources"].append(resource_submission)
    
    safe_submission = copy.deepcopy(submission)
    for resource in safe_submission.get("compute_resources", []):
        if "network" in resource:
            resource["network"]["password"] = "*****"
    logger.info(f"Submitting registration with data: {json.dumps(safe_submission, indent=2)}")
    
    console.print("[bold green]Final Submission Payload:[/bold green]")
    safe_console_submission = copy.deepcopy(submission)
    for resource in safe_console_submission.get("compute_resources", []):
        if "network" in resource:
            resource["network"]["password"] = "*****"
    console.print(json.dumps(safe_console_submission, indent=2))
    
    result = submit_registration(submission)
    
    display_registration_status(result)

if __name__ == "__main__":
    register_miner()
