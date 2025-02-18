import getpass
import logging
import platform
import subprocess
import time
import os
import sys

if sys.platform != "win32":
    import pwd
    import grp

from pathlib import Path

from . import config, utils


class SSHManager:
    def __init__(self):
        self.logger = logging.getLogger('remote_access')
        self.is_windows = platform.system().lower() == 'windows'
        self.is_macos = platform.system().lower() == 'darwin'  # Check for macOS

        
    def _check_ssh_installed(self):
        """Check if OpenSSH is already installed on the current platform."""
        if self.is_linux:
            try:
                result = subprocess.run(
                    ['dpkg', '-s', 'openssh-server'],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            except Exception:
                return False
        elif self.is_macos:
            # On macOS, check if sshd is available
            result = subprocess.run(
                ['which', 'sshd'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        else:
            return False

    def _install_ssh(self):
        """Install OpenSSH on the current platform with error handling."""
        if self.is_linux:
            try:
                # Try installing without update first
                self.logger.info("Attempting to install OpenSSH server on Linux...")
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
        elif self.is_macos:
            # On macOS, use Homebrew to install OpenSSH if it's missing
            try:
                self.logger.info("Attempting to install OpenSSH on macOS...")
                subprocess.run(
                    ['brew', 'install', 'openssh'],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to install OpenSSH on macOS: {e}")
                raise RuntimeError("Failed to install OpenSSH on macOS") from e

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
        self.logger.info("Installing and configuring OpenSSH Server...")
        
        try:
            if self.is_windows:
                utils.run_elevated('powershell -Command "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0"')
                utils.run_elevated('mkdir "C:\\ProgramData\\ssh" 2>NUL')
            else:
                if not self._check_linux_ssh_installed():
                    self._install_linux_ssh()
                subprocess.run(['sudo', 'mkdir', '-p', '/etc/ssh'], check=True)
            
            # Stop the service
            self.stop_server()
            
            # Create and copy new config
            self.create_sshd_config(port)
            
            # Start the service
            self.start_server()
            
            if self.is_windows:
                utils.run_elevated('powershell -Command "Set-Service -Name sshd -StartupType Automatic"')
            else:
                subprocess.run(['sudo', 'systemctl', 'enable', 'ssh'], check=True)
                
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
                
                if self.is_macos:  # macOS-specific logic
                    user_info = pwd.getpwnam(username)  # Get user info based on username
                    group_info = grp.getgrgid(user_info.pw_gid)  # Get group info using group ID
                    group_name = group_info.gr_name  # Get the group name
                    subprocess.run(['sudo', 'chown', '-R', f'{username}:{group_name}', str(ssh_dir)], check=True)
                else:
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
                subprocess.run(['sudo', 'systemctl', 'stop', 'ssh'], check=True)
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
                subprocess.run(['sudo', 'systemctl', 'start', 'ssh'], check=True)
            time.sleep(2)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to start SSH server: {e}")
            raise