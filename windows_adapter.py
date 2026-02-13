"""
DevOS Windows Adapter
Provides Windows-specific command execution and utilities
"""

import subprocess
import os
from typing import Dict, List, Tuple


class WindowsAdapter:
    """Adapter for Windows-specific operations"""
    
    def __init__(self):
        self.os_name = "windows"
        self.shell = "powershell"
    
    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """
        Execute a command on Windows
        
        Args:
            command: Command to execute
        
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    def get_system_info(self) -> Dict[str, str]:
        """Get Windows system information"""
        info = {
            'os': 'Windows',
            'version': self._get_windows_version(),
            'architecture': self._get_architecture(),
            'hostname': os.environ.get('COMPUTERNAME', 'unknown'),
            'user': os.environ.get('USERNAME', 'unknown')
        }
        return info
    
    def _get_windows_version(self) -> str:
        """Get Windows version"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", "(Get-WmiObject -Class Win32_OperatingSystem).Caption"],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except:
            return "Unknown"
    
    def _get_architecture(self) -> str:
        """Get system architecture"""
        return os.environ.get('PROCESSOR_ARCHITECTURE', 'unknown')
    
    def create_directory(self, path: str) -> bool:
        """Create directory on Windows"""
        code, _, _ = self.execute_command(f'New-Item -ItemType Directory -Path "{path}" -Force')
        return code == 0
    
    def create_file(self, path: str, content: str = "") -> bool:
        """Create file on Windows"""
        code, _, _ = self.execute_command(f'New-Item -ItemType File -Path "{path}" -Force')
        if code == 0 and content:
            # Write content
            escaped_content = content.replace('"', '`"')
            code, _, _ = self.execute_command(f'Set-Content -Path "{path}" -Value "{escaped_content}"')
        return code == 0
    
    def list_directory(self, path: str = ".") -> List[str]:
        """List directory contents"""
        code, stdout, _ = self.execute_command(f'Get-ChildItem -Path "{path}" | Select-Object Name')
        if code == 0:
            return [line.strip() for line in stdout.split('\n') if line.strip() and line.strip() != 'Name' and line.strip() != '----']
        return []
    
    def get_environment_variable(self, name: str) -> str:
        """Get environment variable"""
        return os.environ.get(name, "")
    
    def set_environment_variable(self, name: str, value: str, persistent: bool = False) -> bool:
        """Set environment variable"""
        if persistent:
            cmd = f'[Environment]::SetEnvironmentVariable("{name}", "{value}", "User")'
        else:
            cmd = f'$env:{name}="{value}"'
        
        code, _, _ = self.execute_command(cmd)
        return code == 0
    
    def get_cpu_usage(self) -> str:
        """Get CPU usage"""
        code, stdout, _ = self.execute_command(
            'Get-WmiObject -Class Win32_Processor | Select-Object LoadPercentage | Format-List'
        )
        return stdout if code == 0 else "Unable to get CPU usage"
    
    def get_memory_usage(self) -> str:
        """Get memory usage"""
        code, stdout, _ = self.execute_command(
            'Get-WmiObject -Class Win32_OperatingSystem | Select-Object @{Name="FreeGB";Expression={[math]::Round($_.FreePhysicalMemory/1MB,2)}}, @{Name="TotalGB";Expression={[math]::Round($_.TotalVisibleMemorySize/1MB,2)}} | Format-List'
        )
        return stdout if code == 0 else "Unable to get memory usage"
    
    def get_disk_usage(self) -> str:
        """Get disk usage"""
        code, stdout, _ = self.execute_command(
            'Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{Name="UsedGB";Expression={[math]::Round($_.Used/1GB,2)}}, @{Name="FreeGB";Expression={[math]::Round($_.Free/1GB,2)}} | Format-Table'
        )
        return stdout if code == 0 else "Unable to get disk usage"
    
    def find_executable(self, name: str) -> str:
        """Find executable in PATH"""
        code, stdout, _ = self.execute_command(f'(Get-Command {name} -ErrorAction SilentlyContinue).Source')
        return stdout.strip() if code == 0 else ""
    
    def kill_process(self, pid: int) -> bool:
        """Kill process by PID"""
        code, _, _ = self.execute_command(f'Stop-Process -Id {pid} -Force')
        return code == 0
    
    def get_running_processes(self) -> List[Dict[str, str]]:
        """Get list of running processes"""
        code, stdout, _ = self.execute_command(
            'Get-Process | Select-Object Id, ProcessName, CPU | ConvertTo-Json'
        )
        
        if code == 0:
            try:
                import json
                return json.loads(stdout)
            except:
                pass
        
        return []
