"""
DevOS macOS Adapter
Provides macOS-specific command execution and utilities
"""

import subprocess
import os
import platform
from typing import Dict, List, Tuple


class MacAdapter:
    """Adapter for macOS-specific operations"""
    
    def __init__(self):
        self.os_name = "darwin"
        self.shell = "zsh"
    
    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """
        Execute a command on macOS
        
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
                executable="/bin/zsh"
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    def get_system_info(self) -> Dict[str, str]:
        """Get macOS system information"""
        info = {
            'os': 'macOS',
            'version': platform.mac_ver()[0],
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'user': os.environ.get('USER', 'unknown')
        }
        return info
    
    def create_directory(self, path: str) -> bool:
        """Create directory on macOS"""
        code, _, _ = self.execute_command(f'mkdir -p "{path}"')
        return code == 0
    
    def create_file(self, path: str, content: str = "") -> bool:
        """Create file on macOS"""
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
            # Add to .zshrc
            home = os.path.expanduser("~")
            zshrc = os.path.join(home, ".zshrc")
            code, _, _ = self.execute_command(f'echo \'export {name}="{value}"\' >> {zshrc}')
            return code == 0
        else:
            os.environ[name] = value
            return True
    
    def get_cpu_usage(self) -> str:
        """Get CPU usage"""
        code, stdout, _ = self.execute_command('top -l 1 | grep "CPU usage"')
        return stdout if code == 0 else "Unable to get CPU usage"
    
    def get_memory_usage(self) -> str:
        """Get memory usage"""
        code, stdout, _ = self.execute_command('vm_stat')
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
    
    def get_homebrew_packages(self) -> List[str]:
        """Get list of installed Homebrew packages"""
        code, stdout, _ = self.execute_command('brew list')
        if code == 0:
            return [line.strip() for line in stdout.split('\n') if line.strip()]
        return []
    
    def install_homebrew_package(self, package: str) -> bool:
        """Install Homebrew package"""
        code, _, _ = self.execute_command(f'brew install {package}')
        return code == 0
    
    def get_system_profiler_info(self, data_type: str = "SPHardwareDataType") -> str:
        """Get system profiler information"""
        code, stdout, _ = self.execute_command(f'system_profiler {data_type}')
        return stdout if code == 0 else ""
