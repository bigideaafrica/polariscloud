# polaris_cli/log_monitor.py

import os
import subprocess
import sys
import time
from queue import Queue
from threading import Thread

import psutil
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.utils import configure_logging

logger = configure_logging()
console = Console()

class LogReader:
    def __init__(self, log_path, log_type, queue):
        self.log_path = log_path
        self.log_type = log_type
        self.queue = queue
        self.running = True
        self.thread = Thread(target=self._read_log, daemon=True)
    
    def start(self):
        # First read existing content
        self._read_existing_content()
        # Then start monitoring for new content
        self.thread.start()
    
    def _read_existing_content(self):
        """Read all existing content from the log file."""
        try:
            with open(self.log_path, 'r') as f:
                existing_lines = f.readlines()
                for line in existing_lines:
                    self.queue.put((self.log_type, line.strip(), False))  # False indicates existing content
        except Exception as e:
            self.queue.put((self.log_type, f"[red]Error reading existing log content: {e}[/red]", False))
    
    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
    
    def _read_log(self):
        """Monitor for new content."""
        try:
            with open(self.log_path, 'r') as f:
                # Go to end of file
                f.seek(0, 2)
                while self.running:
                    line = f.readline()
                    if line:
                        self.queue.put((self.log_type, line.strip(), True))  # True indicates new content
                    else:
                        time.sleep(0.1)  # Short sleep when no new data
        except Exception as e:
            self.queue.put((self.log_type, f"[red]Error reading log: {e}[/red]", True))

class ProcessMonitor:
    def __init__(self, pid):
        self.pid = pid
        self.process = psutil.Process(pid)
    
    def get_status(self):
        try:
            with self.process.oneshot():
                cpu_percent = self.process.cpu_percent()
                memory_info = self.process.memory_info()
                status = self.process.status()
                
            return Panel(
                f"[bold green]Process Status[/bold green]\n"
                f"PID: {self.pid}\n"
                f"CPU Usage: {cpu_percent}%\n"
                f"Memory Usage: {memory_info.rss / 1024 / 1024:.2f} MB\n"
                f"Status: {status}",
                border_style="green"
            )
        except psutil.NoSuchProcess:
            return Panel("[red]Process has terminated[/red]", border_style="red")
        except Exception as e:
            return Panel(f"[red]Error monitoring process: {e}[/red]", border_style="red")

def format_logs(stdout_lines, stderr_lines, max_lines=1000):
    """Format logs for display with line limiting."""
    table = Table(show_header=True, header_style="bold magenta", box=None)
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("Content", style="white")
    table.add_column("Status", style="green", width=8)

    # Keep only the last max_lines
    stdout_lines = stdout_lines[-max_lines:]
    stderr_lines = stderr_lines[-max_lines:]

    # Add stdout lines
    for line, is_new in stdout_lines:
        status = "NEW" if is_new else ""
        table.add_row("OUT", line, status)

    # Add stderr lines
    for line, is_new in stderr_lines:
        status = "NEW" if is_new else ""
        table.add_row("ERR", Text(line, style="red"), status)

    return table

def create_display(process_status, log_table):
    """Create the combined display layout."""
    layout = Layout()
    
    if process_status:
        layout.split(
            Layout(process_status, size=6),
            Layout(log_table)
        )
    else:
        layout.update(log_table)
    
    return layout

def monitor_process_and_logs(process_pid=None):
    """Monitor process and its logs in real-time using threads."""
    stdout_log, stderr_log = get_log_paths()
    
    if not os.path.exists(stdout_log) or not os.path.exists(stderr_log):
        console.print("[red]Log files not found. Please ensure Polaris is running.[/red]")
        return False

    try:
        # Initialize log storage - now storing tuples of (line, is_new)
        stdout_lines = []
        stderr_lines = []
        
        # Create queue for log lines
        log_queue = Queue()
        
        # Create and start log readers
        stdout_reader = LogReader(stdout_log, "stdout", log_queue)
        stderr_reader = LogReader(stderr_log, "stderr", log_queue)
        
        process_monitor = None
        if process_pid:
            try:
                process_monitor = ProcessMonitor(process_pid)
            except psutil.NoSuchProcess:
                console.print("[red]Main process not found.[/red]")
                return False

        # Start log readers
        stdout_reader.start()
        stderr_reader.start()

        with Live(auto_refresh=True, refresh_per_second=10) as live:
            try:
                while True:
                    # Process all available log lines
                    while not log_queue.empty():
                        log_type, line, is_new = log_queue.get_nowait()
                        if log_type == "stdout":
                            stdout_lines.append((line, is_new))
                        else:
                            stderr_lines.append((line, is_new))

                    # Get process status if monitoring a process
                    process_status = process_monitor.get_status() if process_monitor else None
                    
                    # Create and update display
                    log_table = format_logs(stdout_lines, stderr_lines)
                    display = create_display(process_status, log_table)
                    live.update(display)
                    
                    time.sleep(0.1)  # Small delay between updates

            except KeyboardInterrupt:
                console.print("\n[yellow]Log monitoring stopped.[/yellow]")
            finally:
                # Clean up
                stdout_reader.stop()
                stderr_reader.stop()

    except Exception as e:
        console.print(f"[red]Failed to monitor logs: {e}[/red]")
        return False

def get_log_paths():
    """Get paths to log files."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(project_root, 'logs')
    stdout_log = os.path.join(log_dir, 'polaris_stdout.log')
    stderr_log = os.path.join(log_dir, 'polaris_stderr.log')
    return stdout_log, stderr_log

def get_main_process_pid():
    """Get the PID of the main process."""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.cmdline()
                if len(cmdline) > 1 and 'main.py' in cmdline[1]:
                    return proc.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    except Exception as e:
        console.print(f"[red]Error finding main process: {e}[/red]")
        return None

def check_main():
    """Check if main process is running and show its logs."""
    pid = get_main_process_pid()
    if pid:
        console.print(f"[green]Main process is running (PID: {pid})[/green]")
        console.print("[yellow]Starting log monitor (Press Ctrl+C to stop)...[/yellow]")
        monitor_process_and_logs(pid)
    else:
        console.print("[red]Main process is not running.[/red]")