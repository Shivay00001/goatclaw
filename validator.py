"""
DevOS Security Module
Provides command validation and sandboxing
"""

import re
import os
from typing import List, Dict, Tuple
from enum import Enum


class RiskLevel(Enum):
    """Risk levels for commands"""
    SAFE = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


class SecurityValidator:
    """Validates commands for security risks"""
    
    # Critical commands that should never be allowed
    BLOCKED_COMMANDS = [
        r'rm\s+-rf\s+/',
        r'rm\s+-fr\s+/',
        r'mkfs',
        r'dd\s+if=.*of=/dev/',
        r'format\s+[a-zA-Z]:',
        r':\(\)\{:\|:&\};:',  # Fork bomb
        r'>(.*)/dev/(sd|hd|nvme)',
        r'curl.*\|\s*(bash|sh)',
        r'wget.*\|\s*(bash|sh)',
    ]
    
    # High-risk patterns that need confirmation
    HIGH_RISK_PATTERNS = [
        r'rm\s+-[rf]',
        r'del\s+/[sS]',
        r'Remove-Item.*-Recurse',
        r'drop\s+database',
        r'truncate\s+table',
        r'delete\s+from\s+\w+\s+where',
        r'>/dev/',
    ]
    
    # Medium-risk patterns
    MEDIUM_RISK_PATTERNS = [
        r'sudo',
        r'chmod\s+777',
        r'chown',
        r'kill\s+-9',
        r'reboot',
        r'shutdown',
        r'systemctl',
    ]
    
    # File system manipulation
    FS_MANIPULATION = [
        r'mv\s+.*\s+/',
        r'cp\s+.*\s+/',
        r'rsync.*--delete',
    ]
    
    def __init__(self):
        # Compile patterns for efficiency
        self.blocked_patterns = [re.compile(p, re.IGNORECASE) for p in self.BLOCKED_COMMANDS]
        self.high_risk_patterns = [re.compile(p, re.IGNORECASE) for p in self.HIGH_RISK_PATTERNS]
        self.medium_risk_patterns = [re.compile(p, re.IGNORECASE) for p in self.MEDIUM_RISK_PATTERNS]
        self.fs_patterns = [re.compile(p, re.IGNORECASE) for p in self.FS_MANIPULATION]
    
    def validate_command(self, command: str) -> Tuple[bool, RiskLevel, str]:
        """
        Validate a single command
        
        Args:
            command: Command string to validate
        
        Returns:
            Tuple of (is_allowed, risk_level, reason)
        """
        # Check for blocked commands
        for pattern in self.blocked_patterns:
            if pattern.search(command):
                return False, RiskLevel.CRITICAL, f"Blocked command pattern detected: {pattern.pattern}"
        
        # Check for high-risk patterns
        for pattern in self.high_risk_patterns:
            if pattern.search(command):
                return True, RiskLevel.HIGH, f"High-risk operation: {pattern.pattern}"
        
        # Check for medium-risk patterns
        for pattern in self.medium_risk_patterns:
            if pattern.search(command):
                return True, RiskLevel.MEDIUM, f"Elevated privileges required: {pattern.pattern}"
        
        # Check for file system manipulation
        for pattern in self.fs_patterns:
            if pattern.search(command):
                return True, RiskLevel.MEDIUM, f"File system modification: {pattern.pattern}"
        
        # Check for shell redirections that could be dangerous
        if self._has_dangerous_redirection(command):
            return True, RiskLevel.HIGH, "Dangerous I/O redirection detected"
        
        # Command is safe
        return True, RiskLevel.SAFE, "Command appears safe"
    
    def validate_commands(self, commands: List[str]) -> Dict[str, any]:
        """
        Validate multiple commands
        
        Args:
            commands: List of command strings
        
        Returns:
            Dictionary with validation results
        """
        results = {
            'all_allowed': True,
            'needs_confirmation': False,
            'max_risk_level': RiskLevel.SAFE,
            'blocked': [],
            'warnings': [],
            'details': []
        }
        
        for cmd in commands:
            is_allowed, risk_level, reason = self.validate_command(cmd)
            
            detail = {
                'command': cmd,
                'allowed': is_allowed,
                'risk_level': risk_level.name,
                'reason': reason
            }
            results['details'].append(detail)
            
            if not is_allowed:
                results['all_allowed'] = False
                results['blocked'].append(cmd)
            
            if risk_level.value >= RiskLevel.MEDIUM.value:
                results['needs_confirmation'] = True
                results['warnings'].append(f"{cmd}: {reason}")
            
            if risk_level.value > results['max_risk_level'].value:
                results['max_risk_level'] = risk_level
        
        return results
    
    def _has_dangerous_redirection(self, command: str) -> bool:
        """Check for dangerous I/O redirections"""
        dangerous_redirects = [
            r'>.*/(etc|usr|bin|sbin|boot|sys)',
            r'>>.*/(etc|usr|bin|sbin|boot|sys)',
            r'<.*/(etc|shadow|passwd)',
        ]
        
        for pattern in dangerous_redirects:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        
        return False
    
    def sanitize_command(self, command: str) -> str:
        """
        Sanitize command by removing potentially dangerous elements
        
        Args:
            command: Raw command string
        
        Returns:
            Sanitized command string
        """
        # Remove comments
        command = re.sub(r'#.*$', '', command)
        
        # Remove trailing semicolons and ampersands
        command = command.strip().rstrip(';').rstrip('&')
        
        # Remove multiple spaces
        command = re.sub(r'\s+', ' ', command)
        
        return command.strip()


class CommandSandbox:
    """Provides sandboxed command execution environment"""
    
    def __init__(self, work_dir: str = None):
        self.work_dir = work_dir or os.getcwd()
        self.validator = SecurityValidator()
    
    def can_execute(self, command: str) -> Tuple[bool, str]:
        """
        Check if command can be executed in sandbox
        
        Args:
            command: Command to check
        
        Returns:
            Tuple of (can_execute, reason)
        """
        is_allowed, risk_level, reason = self.validator.validate_command(command)
        
        if not is_allowed:
            return False, f"Command blocked: {reason}"
        
        if risk_level.value >= RiskLevel.HIGH.value:
            return False, f"Risk too high: {reason}"
        
        return True, "Command allowed in sandbox"
    
    def prepare_environment(self) -> Dict[str, str]:
        """
        Prepare sandboxed environment variables
        
        Returns:
            Dictionary of environment variables
        """
        # Create isolated environment
        env = os.environ.copy()
        
        # Restrict PATH to safe directories
        safe_paths = [
            '/usr/local/bin',
            '/usr/bin',
            '/bin',
        ]
        env['PATH'] = ':'.join(safe_paths)
        
        # Set working directory
        env['PWD'] = self.work_dir
        
        # Remove potentially dangerous variables
        dangerous_vars = ['LD_PRELOAD', 'LD_LIBRARY_PATH', 'DYLD_INSERT_LIBRARIES']
        for var in dangerous_vars:
            env.pop(var, None)
        
        return env
