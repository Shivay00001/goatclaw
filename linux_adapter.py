"""
DevOS Linux Adapter
Provides Linux-specific command execution and utilities
"""

import subprocess
import os
import platform
from typing import Dict, List, Tuple


class LinuxAdapter:
    """Adapter for Linux-specific operations"""
    
    def __init__(self):
        self.os_name = "linux"
        self.shell = "bash"
    
    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """
        Execute a command on Linux
        
        Args:
            command: Command to execute
        
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                executable="/bin/bash"
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    def get_system_info(self) -> Dict[str, str]:
        """Get Linux system information"""
        info = {
            'os': 'Linux',
            'distribution': self._get_distribution(),
            'kernel': platform.release(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'user': os.environ.get('USER', 'unknown')
        }
        return info
    
    def _get_distribution(self) -> str:
        """Get Linux distribution name"""
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME='):
                        return line.split('=')[1].strip().strip('"')
        except:
            pass
        return "Unknown"
    
    def create_directory(self, path: str) -> bool:
        """Create directory on Linux"""
        code, _, _ = self.execute_command(f'mkdir -p "{path}"')
        return code == 0
    
    def create_file(self, path: str, content: str = "") -> bool:
        """Create file on Linux"""
        code, _, _ = self.execute_command(f'touch "{path}"')
        if code == 0 and content:
            # Write content
            escaped_content = content.replace('"', '\\"').replace('$', '\\$')
            code, _, _ = self.execute_command(f'echo "{escaped_content}" > "{path}"')
        return code == 0
    
    def list_directory(self, path: str = ".") -> List[str]:
        """List directory contents"""
        code, stdout, _ = self.execute_command(f'ls -1 "{path}"')
        if code == 0:
            return [line.strip() for line in stdout.split('\n') if line.strip()]
        return []
    
    def get_environment_variable(self, name: str) -> str:
        """Get environment variable"""
        return os.environ.get(name, "")
    
    def set_environment_variable(self, name: str, value: str, persistent: bool = False) -> bool:
        """Set environment variable"""
        if persistent:
            # Add to .bashrc
            home = os.path.expanduser("~")
            bashrc = os.path.join(home, ".bashrc")
            code, _, _ = self.execute_command(f'echo \'export {name}="{value}"\' >> {bashrc}')
            return code == 0
        else:
            os.environ[name] = value
            return True
    
    def get_cpu_usage(self) -> str:
        """Get CPU usage"""
        code, stdout, _ = self.execute_command('top -bn1 | grep "Cpu(s)"')
        return stdout if code == 0 else "Unable to get CPU usage"
    
    def get_memory_usage(self) -> str:
        """Get memory usage"""
        code, stdout, _ = self.execute_command('free -h')
        return stdout if code == 0 else "Unable to get memory usage"
    
    def get_disk_usage(self) -> str:
        """Get disk usage"""
        code, stdout, _ = self.execute_command('df -h')
        return stdout if code == 0 else "Unable to get disk usage"
    
    def find_executable(self, name: str) -> str:
        """Find executable in PATH"""
        code, stdout, _ = self.execute_command(f'which {name}')
        return stdout.strip() if code == 0 else ""
    
    def kill_process(self, pid: int) -> bool:
        """Kill process by PID"""
        code, _, _ = self.execute_command(f'kill -9 {pid}')
        return code == 0
    
    def get_running_processes(self) -> List[Dict[str, str]]:
        """Get list of running processes"""
        code, stdout, _ = self.execute_command('ps aux')
        
        processes = []
        if code == 0:
            lines = stdout.split('\n')[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 11:
                        processes.append({
                            'user': parts[0],
                            'pid': parts[1],
                            'cpu': parts[2],
                            'mem': parts[3],
                            'command': ' '.join(parts[10:])
                        })
        
        return processes
    
    def get_package_manager(self) -> str:
        """Detect package manager"""
        managers = {
            'apt-get': 'apt',
            'dnf': 'dnf',
            'yum': 'yum',
            'pacman': 'pacman',
            'zypper': 'zypper'
        }
        
        for cmd, name in managers.items():
            if self.find_executable(cmd):
                return name
        
        return "unknown"
    
    def install_package(self, package: str) -> bool:
        """Install package using detected package manager"""
        pm = self.get_package_manager()
        
        commands = {
            'apt': f'sudo apt-get install -y {package}',
            'dnf': f'sudo dnf install -y {package}',
            'yum': f'sudo yum install -y {package}',
            'pacman': f'sudo pacman -S --noconfirm {package}',
            'zypper': f'sudo zypper install -y {package}'
        }
        
        if pm in commands:
            code, _, _ = self.execute_command(commands[pm])
            return code == 0
        
        return False
    
    def update_system(self) -> bool:
        """Update system packages"""
        pm = self.get_package_manager()
        
        commands = {
            'apt': 'sudo apt-get update && sudo apt-get upgrade -y',
            'dnf': 'sudo dnf upgrade -y',
            'yum': 'sudo yum update -y',
            'pacman': 'sudo pacman -Syu --noconfirm',
            'zypper': 'sudo zypper update -y'
        }
        
        if pm in commands:
            code, _, _ = self.execute_command(commands[pm])
            return code == 0
        
        return False
    
    def get_systemd_services(self) -> List[Dict[str, str]]:
        """Get list of systemd services"""
        code, stdout, _ = self.execute_command('systemctl list-units --type=service --all --no-pager')
        
        services = []
        if code == 0:
            lines = stdout.split('\n')[1:]  # Skip header
            for line in lines:
                if '.service' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        services.append({
                            'name': parts[0],
                            'load': parts[1],
                            'active': parts[2],
                            'sub': parts[3]
                        })
        
        return services
    
    def start_service(self, service: str) -> bool:
        """Start systemd service"""
        code, _, _ = self.execute_command(f'sudo systemctl start {service}')
        return code == 0
    
    def stop_service(self, service: str) -> bool:
        """Stop systemd service"""
        code, _, _ = self.execute_command(f'sudo systemctl stop {service}')
        return code == 0
    
    def get_network_interfaces(self) -> str:
        """Get network interfaces"""
        code, stdout, _ = self.execute_command('ip addr show')
        return stdout if code == 0 else "Unable to get network interfaces"
