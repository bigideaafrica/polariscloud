import json  # Added for JSON formatting in logs
import logging
import platform
import sys
from enum import Enum
from time import sleep
from typing import Optional, Tuple

import requests
from communex.client import CommuneClient
from communex.compat.key import classic_load_key
from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.emoji import Emoji
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import (BarColumn, Progress, SpinnerColumn,
                           TaskProgressColumn, TextColumn)
from rich.prompt import Confirm, Prompt
from rich.spinner import Spinner
from rich.style import Style
from rich.table import Table
from rich.text import Text

if platform.system() == "Windows":
    import msvcrt
else:
    import termios
    import tty

console = Console()
logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all logs; adjust as needed
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("polaris_cli.log")  # Logs will be written to polaris_cli.log
    ]
)


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

            # Display title in a panel
            title_panel = Panel(
                Text(self.title, justify="center", style="bold cyan"),
                box=box.ROUNDED,
                border_style="blue",
                padding=(1, 2)
            )
            console.print(Align.center(title_panel))
            console.print()

            # Display options with enhanced styling
            options_panel = Panel(
                Group(
                    *[
                        Text(
                            f"{'➜ ' if i == self.selected else '  '}{option}",
                            style="bold blue" if i == self.selected else "white"
                        )
                        for i, option in enumerate(self.options)
                    ]
                ),
                box=box.ROUNDED,
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(Align.center(options_panel))

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
        self.api_test_url = 'http://localhost:8000/api/v1'
        self.api_base_url = 'https://orchestrator-gekh.onrender.com/api/v1'
        self.created_miner_id = None

    def set_miner_id(self, miner_id: str):
        """Store the miner ID after successful compute registration."""
        if not miner_id:
            raise ValueError("Miner ID cannot be empty")
        self.created_miner_id = miner_id
        logger.info(f"Set miner ID to: {miner_id}")

    def select_network(self):
        """Display enhanced network options with cross-platform arrow key selection."""
        welcome_panel = Panel(
            Group(
                Text("🌟 Welcome to", style="cyan"),
                Text("POLARIS COMPUTE NETWORK",
                     style="bold white", justify="center"),
                Text("Choose your registration network", style="cyan"),
            ),
            box=box.HEAVY,
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(Align.center(welcome_panel))
        self.console.print()

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
            self.console.print(Panel(
                "[yellow]Registration cancelled.[/yellow]",
                border_style="yellow"
            ))
            sys.exit(0)

    def handle_commune_registration(self):
        """Handle Commune network registration process with enhanced UI."""
        # Step 1: Confirm Registration as Commune Miner
        registration_panel = Panel(
            Group(
                # Registration Header
                Text.assemble(
                    ("You are about to register as a ", "bright_blue"),
                    ("POLARIS COMMUNE MINER", "bold white")
                ),
                Text(""),
                Text("This will:", style="cyan"),
                # Benefits
                Text("• Connect you to our Polaris Commune Network", style="white"),
                Text("• Enable you to earn rewards", style="white"),
                Text("• Join the decentralized compute ecosystem", style="white"),
                Text(""),
                Text("────────────────────────────────────", style="dim"),
                Text(""),
                # Key Requirements
                Text("Requirements:", style="cyan"),
                Text("• Must have registered Commune key", style="white"),
                Text(
                    "• Key must be registered under our Polaris subnet on Commune", style="white"
                ),
                Text(""),
                # Information for those without key
                Text("If you don't have a registered Commune key, visit:",
                     style="yellow"),
                Text("https://communeai.org/docs/working-with-keys/key-basics",
                     style="blue underline"),
                Text(""),
                Text("Please enter your Commune wallet name below", style="cyan"),
                Text(""),
                Text.assemble(
                    ("Note: This wallet must be registered under ", "yellow"),
                    ("polaris miner subnet (subnet 30) ", "yellow"),
                    ("on commune", "yellow")
                ),
                Text("If your key is not yet registered under our subnet, follow instructions under: ",
                     style="yellow"),
                Text("https://github.com/bigideainc/polaris-subnet",
                     style="blue underline"),
                Text("")
            ),
            box=box.HEAVY,
            border_style="green",
            padding=(1, 3),
            title="[bold green]🔒 Commune Miner Registration[/bold green]",
            subtitle="[dim]Please confirm your action[/dim]"
        )
        self.console.print(Align.left(registration_panel))

        # Get Wallet Name
        wallet_name = Prompt.ask(
            "\n[bold cyan]Enter your wallet name[/bold cyan]")

        if not wallet_name.strip():
            self.console.print(
                Panel("[red]Wallet name cannot be empty.[/red]", border_style="red")
            )
            sys.exit(1)

        # Step 4: Retrieve Commune UID and SS58 Address
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                expand=True
            ) as progress:
                task = progress.add_task(
                    "[cyan]Retrieving Commune UID...", total=100
                )

                key = classic_load_key(wallet_name)
                ss58_address = key.ss58_address
                commune_uid = self._get_commune_uid(wallet_name)

                while not progress.finished:
                    progress.update(task, advance=1)
                    sleep(0.01)

            if not commune_uid or commune_uid == "Miner not found":
                self.console.print(Panel(
                    "[red]Failed to retrieve Commune UID[/red]\n"
                    "Please ensure your key is registered to mine Polaris subnet.",
                    title="❌ Error",
                    border_style="red"
                ))
                sys.exit(1)

            success_panel = Panel(
                Group(
                    Text("✅ Successfully retrieved wallet information!",
                         style="green"),
                    Text(f"\nCommune UID: {commune_uid}", style="cyan"),
                    Text(
                        f"Wallet Address: {ss58_address[:10]}...{ss58_address[-8:]}", style="cyan"
                    ),
                ),
                box=box.ROUNDED,
                border_style="green",
                title="[bold green]Wallet Verified[/bold green]"
            )
            self.console.print(Align.center(success_panel))
            return wallet_name, commune_uid, ss58_address

        except Exception as e:
            self.console.print(Panel(
                f"[red]Error during Commune registration: {str(e)}[/red]",
                title="❌ Error",
                border_style="red"
            ))
            logger.error(f"Error during Commune registration: {e}")
            sys.exit(1)

    def _get_commune_uid(self, wallet_name, netuid=13):
        """Retrieve Commune UID for the given wallet.

        This is a dummy implementation that returns a random UID for testing purposes.

        Args:
            wallet_name (str): Name of the wallet
            netuid (int): Network UID (default: 13)

        Returns:
            int: A random miner UID between 0 and 255
        """
        try:
            import random

            # Generate a random UID between 0 and 255 (typical range for subnet UIDs)
            random_uid = random.randint(0, 255)
            logger.info(f"Retrieved random miner UID: {random_uid} for wallet: {wallet_name}")
            return random_uid
        except Exception as e:
            logger.error(f"Error retrieving miner UID: {e}")
            return None

    def get_created_miner_id(self) -> str:
        """Get the miner ID that was created during the compute registration process."""
        # This is where you would get the miner ID that was created earlier
        # For now, we'll return it from a class variable that should be set during miner creation
        if self.created_miner_id:
            return self.created_miner_id
        raise ValueError("Miner ID not found. Please ensure miner was created successfully.")

    def display_success_message(self, miner_id: str, commune_uid: str, wallet_name: str):
        """Display a beautiful success message indicating the node is live."""
        # Optional: Add a brief animation
        with Live(console=self.console, refresh_per_second=10) as live:
            for i in range(3, 0, -1):
                countdown = f"[bold green]Launching your node in {i}...[/bold green] 🚀"
                live.update(Align.center(Text(countdown, justify="center")))
                sleep(1)

        success_message = f"""
## 🎉 **Congratulations!**

Your node is now **live** on the **Polaris Commune Network**.

---

**Miner ID:** `{miner_id}`

**Commune UID:** `{commune_uid}`

**Wallet Name:** `{wallet_name}`

You are now part of a decentralized compute ecosystem. 🚀

**What's Next?**
- **Monitor your node's status:** Use `polaris status` to check if Polaris and Compute Subnet are running.
- **View your compute resources:** Use `polaris view-compute` to see your pod compute resources.
- **Monitor miner heartbeat:** Use `polaris monitor` to keep an eye on your miner's heartbeat signals in real-time.

Thank you for joining us! 🌟
"""

        panel = Panel(
            Align.center(Markdown(success_message)),
            box=box.ROUNDED,
            border_style="bold green",
            padding=(2, 4),
            title="[bold green]🚀 Node Live on Polaris Commune Network[/bold green]",
            subtitle="[dim]Your node is now active and contributing to the network[/dim]"
        )

        self.console.print(panel)

    def register_commune_miner(self, wallet_name: str, commune_uid: str, wallet_address: str):
        """Register miner with Commune network."""
        try:
            miner_id = self.get_created_miner_id()
            api_url = f'{self.api_test_url}/commune/register'

            payload = {
                'miner_id': miner_id,
                'commune_uid': str(commune_uid),
                'wallet_name': wallet_name,
                'wallet_address': wallet_address,
                'netuid': 13
            }

            # Mask sensitive information before logging
            masked_wallet_address = f"{wallet_address[:10]}...{wallet_address[-8:]}"
            masked_payload = {**payload, 'wallet_address': masked_wallet_address}

            # Log the payload (excluding sensitive info)
            # logger.info(f"Register Commune Miner payload: {json.dumps(masked_payload, indent=2)}")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                expand=True
            ) as progress:
                task = progress.add_task(
                    "[cyan]Registering with Commune network...", total=100
                )

                response = requests.post(api_url, json=payload)
                response.raise_for_status()

                while not progress.finished:
                    progress.update(task, advance=1)
                    sleep(0.01)

                result = response.json()

            if result['status'] == 'success':
                # Display the beautiful success message
                self.display_success_message(miner_id, commune_uid, wallet_name)
                return result
            else:
                # Display server-provided error message
                error_message = result.get('message', 'Unknown error')
                self.console.print(Panel(
                    f"[red]Registration failed: {error_message}[/red]",
                    title="❌ Error",
                    border_style="red"
                ))
                logger.error(f"Registration failed: {error_message}")
                return None

        except requests.HTTPError as http_err:
            # Attempt to extract error details from response
            try:
                error_details = http_err.response.json()
                error_message = error_details.get('message', str(http_err))
            except (json.JSONDecodeError, AttributeError):
                error_message = str(http_err)

            # Log the error
            logger.error(f"HTTPError during Commune registration: {error_message}")

            self.console.print(Panel(
                f"[red]Failed to register with Commune network: {error_message}[/red]",
                title="❌ Error",
                border_style="red"
            ))
            return None

        except Exception as e:
            # Log the unexpected error
            logger.error(f"Unexpected error during Commune registration: {e}")

            self.console.print(Panel(
                f"[red]Failed to register with Commune network: {str(e)}[/red]",
                title="❌ Error",
                border_style="red"
            ))
            return None

    def verify_commune_status(self, miner_id: str):
        """Verify Commune registration status."""
        try:
            api_url = f'{self.api_test_url}/commune/miner/{miner_id}/verify'

            # Log the verification URL
            logger.debug(f"Verifying Commune status with URL: {api_url}")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                expand=True
            ) as progress:
                task = progress.add_task(
                    "[cyan]Verifying Commune registration...", total=100
                )

                response = requests.get(api_url)
                response.raise_for_status()
                result = response.json()

                while not progress.finished:
                    progress.update(task, advance=1)
                    sleep(0.01)

            if result['status'] == 'ok':
                verification_panel = Panel(
                    Group(
                        Text("✅ Verification Complete!", style="bold green"),
                        Text(""),
                        Text(
                            f"Status: {result.get('miner_status', 'Unknown')}", style="cyan"),
                        Text(
                            f"Commune UID: {result.get('commune_uid', 'Unknown')}", style="cyan"),
                        Text(
                            f"Last Updated: {result.get('last_updated', 'Unknown')}", style="cyan"),
                    ),
                    box=box.ROUNDED,
                    border_style="green",
                    title="[bold green]✅ Verification Status[/bold green]"
                )
                self.console.print(Align.center(verification_panel))
                return True
            else:
                self.console.print(Panel(
                    f"[yellow]Verification failed: {result.get('message', 'Unknown error')}[/yellow]",
                    title="⚠️ Warning",
                    border_style="yellow"
                ))
                logger.warning(f"Verification failed: {result.get('message', 'Unknown error')}")
                return False

        except Exception as e:
            # Log the verification failure
            logger.error(f"Failed to verify Commune status: {e}")

            self.console.print(Panel(
                f"[red]Failed to verify Commune status: {str(e)}[/red]",
                title="❌ Error",
                border_style="red"
            ))
            return False

    def handle_bittensor_registration(self):
        """Handle Bittensor network registration."""
        panel = Panel(
            Group(
                Text("Bittensor Network registration coming soon!",
                     style="bold yellow"),
                Text(
                    "We're working hard to bring you Bittensor integration.", style="italic"),
            ),
            box=box.ROUNDED,
            border_style="yellow",
            title="[bold yellow]🚧 Coming Soon[/bold yellow]"
        )
        self.console.print(Align.center(panel))
        logger.info("Bittensor registration is not yet implemented.")
        return None

    def run_registration_flow(self):
        """Run the complete registration flow with enhanced UI."""
        try:
            # Show welcome banner
            welcome_panel = Panel(
                Group(
                    Text("🌟 Welcome to", style="cyan"),
                    Text("POLARIS COMPUTE NETWORK",
                         style="bold white", justify="center"),
                    Text("\nPlease select your registration network", style="cyan"),
                ),
                box=box.HEAVY,
                border_style="blue",
                padding=(1, 2)
            )
            self.console.print(Align.center(welcome_panel))
            self.console.print()

            network = self.select_network()

            if network == NetworkType.COMMUNE:
                registration_details = self.handle_commune_registration()
                if registration_details:
                    wallet_name, commune_uid, ss58_address = registration_details
                    # miner_id should be set externally via set_miner_id
                    if not self.created_miner_id:
                        self.console.print(Panel(
                            "[red]Miner ID not set. Please ensure compute registration is completed before Commune registration.[/red]",
                            title="❌ Error",
                            border_style="red"
                        ))
                        logger.error("Miner ID not set before Commune registration.")
                        sys.exit(1)
                    self.register_commune_miner(wallet_name, commune_uid, ss58_address)
            elif network == NetworkType.BITTENSOR:
                self.handle_bittensor_registration()
            elif network == NetworkType.NORMAL:
                self.console.print(Panel(
                    "[bold green]Normal Provider registration is not implemented yet.[/bold green]",
                    border_style="green"
                ))
                logger.info("Normal Provider registration is not implemented.")
            else:
                self.console.print(Panel(
                    "[yellow]Unknown network selected. Exiting.[/yellow]",
                    border_style="yellow"
                ))
                logger.warning("Unknown network selected.")
                sys.exit(0)

        except KeyboardInterrupt:
            self.console.print("\n")
            self.console.print(Panel(
                "[yellow]Registration process cancelled by user.[/yellow]",
                title="ℹ️ Cancelled",
                border_style="yellow"
            ))
            logger.info("Registration process cancelled by user.")
        except Exception as e:
            self.console.print(Panel(
                f"[red]An unexpected error occurred: {str(e)}[/red]",
                title="❌ Error",
                border_style="red"
            ))
            logger.error(f"Unexpected error in registration flow: {e}")


# Example usage:
# if __name__ == "__main__":
#     handler = NetworkSelectionHandler()
#     # Example of setting miner ID; in real usage, this should come from compute registration
#     handler.set_miner_id("miner12345")
#     handler.run_registration_flow()
