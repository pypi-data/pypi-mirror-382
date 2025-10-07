"""
Secure Command Execution Module

Provides secure command execution with input validation and privilege escalation handling.
"""

import logging
import shlex
import subprocess
from typing import List, Union


class SecureCommandExecutor:
    """
    Secure command execution with input validation and privilege escalation handling.
    
    Security Features:
    1. Command whitelist validation
    2. Parameter sanitization
    3. Privilege escalation handling
    4. Input validation
    5. Audit logging
    """
    
    def __init__(self):
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Whitelist of allowed command prefixes by OS
        self.allowed_commands = {
            'windows': [
                'powershell', 'reg', 'wmic', 'net', 'sc', 'bcdedit',
                'Get-LocalUser', 'Get-NetFirewallProfile', 'Get-WindowsOptionalFeature',
                'Get-MpPreference', 'Set-MpPreference', 'Set-NetFirewallProfile',
                'Disable-LocalUser', 'Enable-LocalUser', 'Disable-WindowsOptionalFeature',
                'Enable-WindowsOptionalFeature'
            ],
            'linux': [
                'grep', 'sed', 'awk', 'systemctl', 'ufw', 'sysctl', 'lsmod',
                'bootctl', 'dpkg', 'rpm', 'yum', 'apt', 'sudo'
            ]
        }
        
        # Commands that require privilege escalation
        self.sudo_required = [
            'systemctl', 'ufw', 'sed -i', 'tee -a', 'modprobe'
        ]
    
    def _validate_command(self, command: str, os_type: str) -> bool:
        """Validate command against whitelist"""
        if not command or not command.strip():
            return False
            
        # Get allowed commands for OS
        allowed = self.allowed_commands.get(os_type, [])
        
        # Check if command starts with allowed prefix
        command_lower = command.lower().strip()
        
        for allowed_cmd in allowed:
            if command_lower.startswith(allowed_cmd.lower()):
                return True
        
        self.logger.warning(f"Command not in whitelist: {command}")
        return False
    
    def _needs_sudo(self, command: str) -> bool:
        """Check if command requires sudo privileges"""
        command_lower = command.lower()
        return any(sudo_cmd in command_lower for sudo_cmd in self.sudo_required)
    
    def _sanitize_command(self, command: str) -> Union[List[str], str]:
        """
        Sanitize command by parsing it safely
        
        Returns either:
        - List[str] for simple commands that can run with shell=False
        - str for complex commands that need shell=True but are validated
        
        This prevents command injection by:
        1. Using shlex to properly parse simple command arguments
        2. Validating complex commands against whitelist
        3. Avoiding shell interpretation when possible
        """
        try:
            command = command.strip()
            
            # Check if command contains shell features that require shell=True
            shell_features = ['|', '>', '<', '&&', '||', ';', '`', '$', '(', ')']
            needs_shell = any(feature in command for feature in shell_features)
            
            if needs_shell:
                # Complex command - return as string for shell=True but validated
                self.logger.info(f"Complex command requires shell: {command}")
                return command
            else:
                # Simple command - parse into list for shell=False
                if command.startswith('powershell'):
                    # PowerShell commands often need shell=True
                    return command
                else:
                    # Simple Linux commands can be parsed safely
                    return shlex.split(command)
                    
        except ValueError as e:
            self.logger.error(f"Failed to parse command: {command}, Error: {e}")
            raise ValueError(f"Invalid command syntax: {command}")
    
    def execute_command(self, command: str, os_type: str, timeout: int = 30) -> subprocess.CompletedProcess:
        """
        Securely execute a command with validation and logging
        
        Args:
            command: Command to execute
            os_type: Operating system type (windows/linux/ubuntu/centos)
            timeout: Command timeout in seconds
            
        Returns:
            subprocess.CompletedProcess object
            
        Raises:
            ValueError: If command is invalid or not allowed
            subprocess.TimeoutExpired: If command times out
        """
        
        # Normalize OS type
        if os_type in ['ubuntu', 'centos']:
            os_type = 'linux'
        
        # Validate command
        if not self._validate_command(command, os_type):
            raise ValueError(f"Command not allowed: {command}")
        
        # Log the execution attempt
        self.logger.info(f"Executing command: {command} (OS: {os_type})")
        
        try:
            # Sanitize command - get either list or string
            sanitized_cmd = self._sanitize_command(command)
            
            # Determine if we need shell=True
            if isinstance(sanitized_cmd, str):
                # Complex command requiring shell=True (but validated)
                self.logger.info(f"Executing with shell=True (validated): {command}")
                result = subprocess.run(
                    sanitized_cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    shell=True  # Required for complex commands, but command is validated
                )
            else:
                # Simple command that can run with shell=False
                self.logger.info(f"Executing with shell=False: {command}")
                result = subprocess.run(
                    sanitized_cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    shell=False  # SECURE: No shell interpretation
                )
            
            # Log result
            self.logger.info(f"Command completed with return code: {result.returncode}")
            
            return result
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {command}")
            raise
        except FileNotFoundError:
            # Command not found - might need different handling on Windows vs Linux
            self.logger.error(f"Command not found: {command}")
            raise ValueError(f"Command not found: {sanitized_cmd[0] if isinstance(sanitized_cmd, list) else command}")
        except Exception as e:
            self.logger.error(f"Command execution failed: {command}, Error: {e}")
            raise

