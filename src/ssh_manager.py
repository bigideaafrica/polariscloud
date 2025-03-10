import getpass
import logging
import os
import platform
import subprocess
import time
from pathlib import Path

from . import config, utils


class SSHManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_windows = platform.system().lower() == 'windows'
        # Check if systemd is available
        if not self.is_windows:
            try:
                subprocess.run(['systemctl', '--version'], capture_output=True, check=True)
                self.has_systemd = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.has_systemd = False
                self.logger.info("systemd not available, will use alternative service management methods")
        else:
            self.has_systemd = False
        
    def _check_linux_ssh_installed(self):
        """Check if OpenSSH is already installed on Linux"""
        try:
            result = subprocess.run(
                ['dpkg', '-s', 'openssh-server'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def _install_linux_ssh(self):
        """Install OpenSSH on Linux with error handling"""
        try:
            # Try installing without update first
            self.logger.info("Attempting to install OpenSSH server...")
            subprocess.run(
                ['sudo', 'apt-get', 'install', '-y', 'openssh-server'],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError:
            self.logger.warning("Direct installation failed, attempting with apt update...")
            try:
                # If that fails, try updating apt (but handle errors gracefully)
                update_result = subprocess.run(
                    ['sudo', 'apt-get', 'update'],
                    capture_output=True,
                    text=True
                )
                if update_result.returncode != 0:
                    self.logger.warning(f"Apt update had issues but continuing: {update_result.stderr}")
                
                # Attempt installation again
                subprocess.run(
                    ['sudo', 'apt-get', 'install', '-y', 'openssh-server'],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to install OpenSSH: {e}")
                raise RuntimeError("Failed to install OpenSSH server") from e

    def create_sshd_config(self, port):
        if self.is_windows:
            config_content = f"""
# SSH Server Configuration
Port {port}
PermitRootLogin yes
AuthorizedKeysFile .ssh/authorized_keys
PasswordAuthentication yes
PermitEmptyPasswords no
ChallengeResponseAuthentication no
UsePAM yes
Subsystem sftp sftp-server.exe
"""
        else:
            config_content = f"""
# SSH Server Configuration
Port {port}
PermitRootLogin yes
AuthorizedKeysFile .ssh/authorized_keys
PasswordAuthentication yes
PermitEmptyPasswords no
ChallengeResponseAuthentication no
UsePAM yes
Subsystem sftp /usr/lib/openssh/sftp-server
"""
        try:
            # Write to temp file first
            temp_config = config.HOME_DIR / 'sshd_config_temp'
            with open(temp_config, 'w', encoding='utf-8') as f:
                f.write(config_content.strip())
            
            if self.is_windows:
                utils.run_elevated(f'copy /Y "{temp_config}" "{config.SSH_CONFIG_PATH}"')
            else:
                subprocess.run(['sudo', 'cp', str(temp_config), '/etc/ssh/sshd_config'], check=True)
                subprocess.run(['sudo', 'chmod', '644', '/etc/ssh/sshd_config'], check=True)
            
            temp_config.unlink(missing_ok=True)
        except Exception as e:
            self.logger.error(f"Failed to create SSH config: {e}")
            raise

    def setup_server(self, port):
        """Setup SSH server with the specified port"""
        try:
            # Create sshd_config with the port
            self.create_sshd_config(port)
            
            # Start the service
            self.start_server()
            
            if self.is_windows:
                utils.run_elevated('powershell -Command "Set-Service -Name sshd -StartupType Automatic"')
            else:
                if self.has_systemd:
                    subprocess.run(['sudo', 'systemctl', 'enable', 'ssh'], check=True)
                else:
                    # Alternative to enable SSH at startup
                    rc_local = Path('/etc/rc.local')
                    if rc_local.exists():
                        content = rc_local.read_text()
                        if '/usr/sbin/sshd' not in content:
                            with open('/etc/rc.local', 'a') as f:
                                f.write('\n# Start SSH server\n/usr/sbin/sshd\n')
                            subprocess.run(['chmod', '+x', '/etc/rc.local'], check=True)
                
        except Exception as e:
            self.logger.error(f"Failed to setup SSH server: {e}")
            raise

    def setup_user(self):
        username = getpass.getuser()
        password = config.SSH_PASSWORD
        
        self.logger.info(f"Configuring user {username} for SSH access...")
        
        try:
            if self.is_windows:
                enable_cmd = f'wmic UserAccount where Name="{username}" set PasswordExpires=false'
                utils.run_elevated(enable_cmd)
                
                commands = [
                    f'net user {username} "{password}"',
                    f'powershell -Command "$password = ConvertTo-SecureString \'{password}\' -AsPlainText -Force; Set-LocalUser -Name \'{username}\' -Password $password"',
                    f'net user {username} /active:yes',
                    'powershell -Command "Set-ItemProperty -Path HKLM:\\SOFTWARE\\OpenSSH -Name DefaultShell -Value C:\\Windows\\System32\\cmd.exe -Force"'
                ]
                
                for cmd in commands:
                    utils.run_elevated(cmd)
                    time.sleep(1)
            else:
                # Set password using chpasswd
                chpasswd_proc = subprocess.Popen(
                    ['sudo', 'chpasswd'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                chpasswd_proc.communicate(input=f'{username}:{password}\n')
                
                # Ensure .ssh directory exists with correct permissions
                ssh_dir = Path.home() / '.ssh'
                ssh_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
                
                # Set ownership
                subprocess.run(['sudo', 'chown', '-R', f'{username}:{username}', str(ssh_dir)], check=True)
            
            self.logger.info("User configured successfully")
            return username, password
            
        except Exception as e:
            self.logger.error(f"Failed to configure user: {e}")
            raise

    def stop_server(self):
        """Stop the SSH server"""
        try:
            if self.is_windows:
                stop_cmd = subprocess.Popen(
                    ['net', 'stop', 'sshd'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stop_cmd.communicate(input='y\n')
            else:
                if self.has_systemd:
                    subprocess.run(['sudo', 'systemctl', 'stop', 'ssh'], check=True)
                else:
                    # Try service command first
                    try:
                        subprocess.run(['sudo', 'service', 'ssh', 'stop'], check=True)
                    except subprocess.CalledProcessError:
                        # Alternative method - find and kill sshd process
                        try:
                            # Get the PID of the sshd process
                            ps_result = subprocess.run(['ps', '-ef', '|', 'grep', 'sshd', '|', 'grep', '-v', 'grep'], 
                                                      shell=True, capture_output=True, text=True)
                            if ps_result.stdout:
                                # Extract the PID and kill the process
                                lines = ps_result.stdout.strip().split('\n')
                                for line in lines:
                                    parts = line.split()
                                    if len(parts) > 1:
                                        pid = parts[1]
                                        subprocess.run(['sudo', 'kill', pid], check=True)
                        except subprocess.CalledProcessError as e:
                            self.logger.warning(f"Could not kill SSH process: {e}")
            time.sleep(2)
        except subprocess.CalledProcessError:
            self.logger.warning("SSH service was not running or could not be stopped")

    def start_server(self):
        """Start the SSH server"""
        try:
            if self.is_windows:
                start_cmd = subprocess.Popen(
                    ['net', 'start', 'sshd'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                start_cmd.communicate(input='y\n')
            else:
                if self.has_systemd:
                    subprocess.run(['sudo', 'systemctl', 'start', 'ssh'], check=True)
                else:
                    # Try service command first
                    try:
                        subprocess.run(['sudo', 'service', 'ssh', 'start'], check=True)
                    except subprocess.CalledProcessError:
                        # Try to start sshd directly
                        try:
                            subprocess.run(['sudo', '/usr/sbin/sshd'], check=True)
                        except subprocess.CalledProcessError as e:
                            self.logger.error(f"Failed to start SSH server using direct method: {e}")
                            raise
            time.sleep(2)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to start SSH server: {e}")
            raise