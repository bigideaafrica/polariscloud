import logging
import platform
import sys
from enum import Enum

import requests
from communex.client import CommuneClient
from communex.compat.key import classic_load_key
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.text import Text

if platform.system() == "Windows":
    import msvcrt
else:
    import termios
    import tty

console = Console()
logger = logging.getLogger(__name__)

class NetworkType(Enum):
    COMMUNE = "commune"
    BITTENSOR = "bittensor"
    NORMAL = "normal"

class CrossPlatformMenu:
    def __init__(self, options, title="Select an option"):
        self.options = options
        self.title = title
        self.selected = 0

    def _get_char_windows(self):
        """Get character input for Windows."""
        char = msvcrt.getch()
        if char in [b'\xe0', b'\x00']:  # Arrow keys prefix
            char = msvcrt.getch()
            return {
                b'H': 'up',
                b'P': 'down',
                b'\r': 'enter'
            }.get(char, None)
        elif char == b'\r':
            return 'enter'
        return None

    def _get_char_unix(self):
        """Get character input for Unix-like systems."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                sys.stdin.read(1)  # skip '['
                ch = sys.stdin.read(1)
                return {
                    'A': 'up',
                    'B': 'down'
                }.get(ch, None)
            elif ch == '\r':
                return 'enter'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None

    def _get_char(self):
        """Get character input in a cross-platform way."""
        if platform.system() == "Windows":
            return self._get_char_windows()
        return self._get_char_unix()

    def _clear_screen(self):
        """Clear the screen in a cross-platform way."""
        console.clear()

    def show(self):
        """Display the menu and handle user input."""
        while True:
            self._clear_screen()
            console.print(f"\n[bold cyan]{self.title}[/bold cyan]\n")

            for i, option in enumerate(self.options):
                if i == self.selected:
                    console.print(f"[bold blue]➜ {option}[/bold blue]")
                else:
                    console.print(f"  {option}")

            key = self._get_char()
            
            if key == 'up':
                self.selected = (self.selected - 1) % len(self.options)
            elif key == 'down':
                self.selected = (self.selected + 1) % len(self.options)
            elif key == 'enter':
                return self.selected

class NetworkSelectionHandler:
    def __init__(self):
        self.console = Console()
        self.api_base_url = 'https://orchestrator-gekh.onrender.com/api/v1'  # Update with your actual API URL
        
    def select_network(self):
        """Display network options with cross-platform arrow key selection."""
        options = [
            "🌐 Commune Network",
            "🔗 Bittensor Network",
            "📡 Normal Provider"
        ]
        
        menu = CrossPlatformMenu(
            options,
            title="Select Registration Network"
        )
        
        selected_index = menu.show()
        
        if selected_index == 0:
            return NetworkType.COMMUNE
        elif selected_index == 1:
            return NetworkType.BITTENSOR
        elif selected_index == 2:
            return NetworkType.NORMAL
        else:
            self.console.print("[yellow]Registration cancelled.[/yellow]")
            sys.exit(0)
            
    def handle_commune_registration(self):
        """Handle Commune network registration process."""
        # Create a custom prompt with styled text
        prompt_text = Text()
        prompt_text.append("Enter your Commune wallet name", style="bold cyan")
        console.print(Panel(prompt_text))
        
        wallet_name = input("➜ ").strip()
        
        if not wallet_name:
            console.print("[red]Wallet name cannot be empty[/red]")
            return None
            
        try:
            with console.status("[bold cyan]Retrieving Commune UID..."):
                # Get wallet key and SS58 address
                key = classic_load_key(wallet_name)
                ss58_address = key.ss58_address
                commune_uid = self._get_commune_uid(wallet_name)
                
            if not commune_uid or commune_uid == "Miner not found":
                console.print("[red]Failed to retrieve Commune UID[/red]")
                return None
                
            console.print(f"[green]Successfully retrieved Commune UID: {commune_uid}[/green]")
            return wallet_name, commune_uid, ss58_address
            
        except Exception as e:
            console.print(f"[red]Error in Commune registration: {e}[/red]")
            return None

    def _get_commune_uid(self, wallet_name, netuid=13):
        """Retrieve Commune UID for the given wallet."""
        try:
            key = classic_load_key(wallet_name)
            commune_node_url = "wss://testnet-commune-api-node-0.communeai.net/"
            client = CommuneClient(commune_node_url)
            modules_keys = client.query_map_key(netuid)
            val_ss58 = key.ss58_address
            miner_uid = next(uid for uid, address in modules_keys.items() 
                           if address == val_ss58)
            logger.info(f"Retrieved miner UID: {miner_uid} for wallet: {wallet_name}")
            return miner_uid
            
        except StopIteration:
            logger.error("Miner's SS58 address not found in the network.")
            return None
        except Exception as e:
            logger.error(f"Error retrieving miner UID: {e}")
            return None

    def register_commune_miner(self, miner_id: str, wallet_name: str, commune_uid: str, wallet_address: str):
        """Register miner with Commune network."""
        try:
            api_url = f'{self.api_base_url}/commune/register'
            
            payload = {
                'miner_id': miner_id,
                'commune_uid': commune_uid,
                'wallet_name': wallet_name,
                'wallet_address': wallet_address,
                'netuid': 13  # Default netuid for Commune
            }
            
            with console.status("[bold cyan]Registering with Commune network..."):
                response = requests.post(api_url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                if result['status'] == 'success':
                    console.print("[green]Successfully registered with Commune network![/green]")
                    console.print(Panel(
                        f"[cyan]Registration Details:[/cyan]\n"
                        f"Miner ID: {miner_id}\n"
                        f"Commune UID: {commune_uid}\n"
                        f"Wallet: {wallet_name}",
                        title="✅ Registration Complete"
                    ))
                    return result
                else:
                    console.print(f"[red]Registration failed: {result.get('message', 'Unknown error')}[/red]")
                    return None
                
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Failed to connect to registration service: {e}[/red]")
            return None
        except Exception as e:
            console.print(f"[red]Failed to register with Commune network: {e}[/red]")
            return None

    async def verify_commune_status(self, miner_id: str):
        """Verify Commune registration status."""
        try:
            api_url = f'{self.api_base_url}/commune/miner/{miner_id}/verify'
            
            with console.status("[bold cyan]Verifying Commune registration..."):
                response = requests.get(api_url)
                response.raise_for_status()
                
                result = response.json()
                if result['status'] == 'ok':
                    console.print(Panel(
                        f"[cyan]Commune Status:[/cyan]\n"
                        f"Status: {result.get('miner_status', 'Unknown')}\n"
                        f"Commune UID: {result.get('commune_uid', 'Unknown')}\n"
                        f"Last Updated: {result.get('last_updated', 'Unknown')}",
                        title="✅ Verification Complete"
                    ))
                    return True
                else:
                    console.print(f"[yellow]Verification failed: {result.get('message', 'Unknown error')}[/yellow]")
                    return False
                    
        except Exception as e:
            console.print(f"[red]Failed to verify Commune status: {e}[/red]")
            return False

    def handle_bittensor_registration(self):
        """Handle Bittensor network registration."""
        panel = Panel(
            "[bold yellow]Bittensor Network registration coming soon![/bold yellow]\n" +
            "[italic]We're working hard to bring you Bittensor integration.[/italic]",
            title="🚧 Coming Soon",
            border_style="yellow"
        )
        self.console.print(panel)
        return None