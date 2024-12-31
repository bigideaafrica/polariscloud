import os
import platform
import sys
import time
from queue import Queue
from threading import Event, Thread

import psutil
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

class BaseLogReader:
    def __init__(self, log_path, log_type, queue):
        self.log_path = log_path
        self.log_type = log_type
        self.queue = queue
        self.running = Event()
        self.thread = Thread(target=self._read_log, daemon=True)
        self.last_position = 0
        
    def _read_existing_content(self):
        """Read existing content using efficient buffered reading."""
        try:
            with open(self.log_path, 'r', buffering=1) as f:
                chunk_size = 8192
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    lines = chunk.splitlines()
                    for line in lines:
                        if line:  # Skip empty lines
                            self.queue.put((self.log_type, line, False))
                self.last_position = f.tell()
        except Exception as e:
            self.queue.put((self.log_type, f"[red]Error reading existing log: {e}[/red]", False))

    def start(self):
        self._read_existing_content()
        self.running.set()
        self.thread.start()

    def stop(self):
        self.running.clear()
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def _read_log(self):
        raise NotImplementedError("Subclasses must implement _read_log")

class UnixLogReader(BaseLogReader):
    def _read_log(self):
        """Monitor log file using select.poll() for Unix systems."""
        try:
            import select
            with open(self.log_path, 'r') as f:
                fd = f.fileno()
                poll_obj = select.poll()
                poll_obj.register(fd, select.POLLIN)

                while self.running.is_set():
                    events = poll_obj.poll(100)  # 100ms timeout
                    if events:
                        f.seek(self.last_position)
                        new_content = f.read()
                        self.last_position = f.tell()
                        
                        if new_content:
                            lines = new_content.splitlines()
                            for line in lines:
                                if line:
                                    self.queue.put((self.log_type, line, True))
                    
        except Exception as e:
            self.queue.put((self.log_type, f"[red]Error monitoring log: {e}[/red]", True))

class WindowsLogReader(BaseLogReader):
    def _read_log(self):
        """Monitor log file using Windows API."""
        try:
            import win32con
            import win32file
            
            directory = os.path.dirname(self.log_path)
            file_name = os.path.basename(self.log_path)
            
            handle = win32file.CreateFile(
                directory,
                win32con.GENERIC_READ,
                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
                None,
                win32con.OPEN_EXISTING,
                win32con.FILE_FLAG_BACKUP_SEMANTICS,
                None
            )
            
            while self.running.is_set():
                try:
                    results = win32file.ReadDirectoryChangesW(
                        handle,
                        1024,
                        False,
                        win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
                        None,
                        None
                    )
                    
                    for action, file in results:
                        if file == file_name and action == win32con.FILE_ACTION_MODIFIED:
                            with open(self.log_path, 'r') as f:
                                f.seek(self.last_position)
                                new_content = f.read()
                                self.last_position = f.tell()
                                
                                if new_content:
                                    lines = new_content.splitlines()
                                    for line in lines:
                                        if line:
                                            self.queue.put((self.log_type, line, True))
                    
                    time.sleep(0.05)
                    
                except Exception as e:
                    # Handle temporary file system issues
                    time.sleep(0.1)
                    continue
                    
        except Exception as e:
            self.queue.put((self.log_type, f"[red]Error monitoring log: {e}[/red]", True))
        finally:
            try:
                win32file.CloseHandle(handle)
            except:
                pass

class FallbackLogReader(BaseLogReader):
    def _read_log(self):
        """Fallback monitoring method using basic file reading."""
        try:
            while self.running.is_set():
                with open(self.log_path, 'r') as f:
                    f.seek(self.last_position)
                    new_content = f.read()
                    if new_content:
                        self.last_position = f.tell()
                        lines = new_content.splitlines()
                        for line in lines:
                            if line:
                                self.queue.put((self.log_type, line, True))
                time.sleep(0.1)
        except Exception as e:
            self.queue.put((self.log_type, f"[red]Error monitoring log: {e}[/red]", True))

def get_log_reader_class():
    """Get the appropriate log reader class for the current platform."""
    system = platform.system().lower()
    
    if system == 'windows':
        try:
            import win32file
            return WindowsLogReader
        except ImportError:
            console.print("[yellow]pywin32 not found, using fallback monitor[/yellow]")
            return FallbackLogReader
    elif system in ('linux', 'darwin', 'freebsd', 'openbsd', 'netbsd'):
        try:
            import select
            return UnixLogReader
        except ImportError:
            return FallbackLogReader
    else:
        return FallbackLogReader

class RealTimeProcessMonitor:
    def __init__(self, pid):
        self.pid = pid
        self.process = psutil.Process(pid)
        self.last_cpu_time = None
        self.last_check_time = None
        
    def get_status(self):
        try:
            with self.process.oneshot():
                current_time = time.time()
                current_cpu_time = sum(self.process.cpu_times())
                
                if self.last_cpu_time is not None:
                    time_diff = current_time - self.last_check_time
                    if time_diff > 0:  # Avoid division by zero
                        cpu_percent = (current_cpu_time - self.last_cpu_time) / time_diff * 100
                    else:
                        cpu_percent = 0.0
                else:
                    cpu_percent = 0.0
                
                self.last_cpu_time = current_cpu_time
                self.last_check_time = current_time
                
                memory_info = self.process.memory_info()
                status = self.process.status()
                
                try:
                    io_counters = self.process.io_counters()
                    io_info = (
                        f"IO Read: {io_counters.read_bytes / 1024 / 1024:.1f} MB\n"
                        f"IO Write: {io_counters.write_bytes / 1024 / 1024:.1f} MB"
                    )
                except (psutil.AccessDenied, AttributeError):
                    io_info = "IO Stats: Not available"
                
                return Panel(
                    f"[bold green]Process Status[/bold green]\n"
                    f"PID: {self.pid}\n"
                    f"CPU Usage: {cpu_percent:.1f}%\n"
                    f"Memory: {memory_info.rss / 1024 / 1024:.1f} MB\n"
                    f"Status: {status}\n"
                    f"{io_info}",
                    border_style="green"
                )
        except psutil.NoSuchProcess:
            return Panel("[red]Process terminated[/red]", border_style="red")
        except Exception as e:
            return Panel(f"[red]Monitor error: {e}[/red]", border_style="red")

def format_logs(stdout_lines, stderr_lines, max_lines=1000):
    table = Table(show_header=True, header_style="bold magenta", box=None, expand=True)
    table.add_column("Type", style="cyan", no_wrap=True, width=8)
    table.add_column("Content", style="white", ratio=1)
    table.add_column("Status", style="green", width=8)

    stdout_lines = stdout_lines[-max_lines:]
    stderr_lines = stderr_lines[-max_lines:]

    rows = []
    for line, is_new in stdout_lines:
        rows.append(("OUT", line, "NEW" if is_new else ""))
    for line, is_new in stderr_lines:
        rows.append(("ERR", Text(line, style="red"), "NEW" if is_new else ""))
    
    for row in rows:
        table.add_row(*row)

    return table

def monitor_process_and_logs(process_pid=None):
    stdout_log, stderr_log = get_log_paths()
    
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(stdout_log)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        
    # Create empty log files if they don't exist
    for log_file in [stdout_log, stderr_log]:
        if not os.path.exists(log_file):
            with open(log_file, 'w') as f:
                pass  # Create empty file

    try:
        stdout_lines = []
        stderr_lines = []
        log_queue = Queue()
        
        LogReader = get_log_reader_class()
        stdout_reader = LogReader(stdout_log, "stdout", log_queue)
        stderr_reader = LogReader(stderr_log, "stderr", log_queue)
        
        process_monitor = None
        if process_pid:
            try:
                process_monitor = RealTimeProcessMonitor(process_pid)
            except psutil.NoSuchProcess:
                console.print("[red]Process not found.[/red]")
                return False

        stdout_reader.start()
        stderr_reader.start()

        with Live(auto_refresh=True, refresh_per_second=30) as live:
            try:
                while True:
                    while not log_queue.empty():
                        log_type, line, is_new = log_queue.get_nowait()
                        if log_type == "stdout":
                            stdout_lines.append((line, is_new))
                        else:
                            stderr_lines.append((line, is_new))

                    process_status = process_monitor.get_status() if process_monitor else None
                    log_table = format_logs(stdout_lines, stderr_lines)
                    
                    layout = Layout()
                    if process_status:
                        layout.split(
                            Layout(process_status, size=8),
                            Layout(log_table)
                        )
                    else:
                        layout.update(log_table)
                    
                    live.update(layout)

            except KeyboardInterrupt:
                console.print("\n[yellow]Monitoring stopped.[/yellow]")
            finally:
                stdout_reader.stop()
                stderr_reader.stop()

    except Exception as e:
        console.print(f"[red]Monitor failed: {e}[/red]")
        return False

def get_log_paths():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(project_root, 'logs')
    return (
        os.path.join(log_dir, 'polaris_stdout.log'),
        os.path.join(log_dir, 'polaris_stderr.log')
    )

def get_main_process_pid():
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
        console.print(f"[red]Error finding process: {e}[/red]")
        return None

def check_main():
    pid = get_main_process_pid()
    if pid:
        console.print(f"[green]Process running (PID: {pid})[/green]")
        console.print("[yellow]Starting monitor (Ctrl+C to stop)...[/yellow]")
        monitor_process_and_logs(pid)
    else:
        console.print("[red]Process not running.[/red]")