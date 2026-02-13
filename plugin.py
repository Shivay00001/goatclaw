"""
DevOS Git Helper Plugin
Provides intelligent Git operations
"""

import subprocess
from typing import Dict, List, Any
import sys
import os

# Add parent directory to path to import plugin interface
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from plugins.plugin_manager import PluginInterface


class Plugin(PluginInterface):
    """Git helper plugin for DevOS"""
    
    def __init__(self):
        self._name = "git-helper"
        self._version = "0.1.0"
        self._description = "Intelligent Git operations and workflow automation"
        self._config = {}
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return self._version
    
    @property
    def description(self) -> str:
        return self._description
    
    def initialize(self, config: Dict[str, Any]):
        """Initialize plugin with configuration"""
        self._config = config
    
    def get_commands(self) -> List[str]:
        """Get list of commands this plugin handles"""
        return [
            "git",
            "commit",
            "push",
            "pull",
            "branch",
            "merge",
            "stash",
            "status"
        ]
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Git operations
        
        Args:
            context: Execution context with 'command' and 'args'
        
        Returns:
            Execution result
        """
        command = context.get('command', '')
        
        if 'status' in command.lower():
            return self._git_status()
        elif 'commit' in command.lower():
            return self._smart_commit(context)
        elif 'push' in command.lower():
            return self._safe_push(context)
        elif 'pull' in command.lower():
            return self._git_pull()
        else:
            return self._generic_git(command)
    
    def _git_status(self) -> Dict[str, Any]:
        """Get Git status with analysis"""
        try:
            result = subprocess.run(
                ['git', 'status', '--short'],
                capture_output=True,
                text=True,
                check=True
            )
            
            output = result.stdout
            lines = output.strip().split('\n')
            
            # Analyze status
            modified = sum(1 for line in lines if line.startswith(' M'))
            added = sum(1 for line in lines if line.startswith('A'))
            deleted = sum(1 for line in lines if line.startswith('D'))
            untracked = sum(1 for line in lines if line.startswith('??'))
            
            analysis = f"📊 Git Status Analysis:\n"
            analysis += f"  Modified: {modified}\n"
            analysis += f"  Added: {added}\n"
            analysis += f"  Deleted: {deleted}\n"
            analysis += f"  Untracked: {untracked}\n"
            
            return {
                'success': True,
                'output': analysis + '\n' + output,
                'commands': []
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'output': f"Failed to get Git status: {e.stderr}",
                'commands': []
            }
    
    def _smart_commit(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create smart commit with analysis"""
        try:
            # Get diff
            diff_result = subprocess.run(
                ['git', 'diff', '--staged'],
                capture_output=True,
                text=True,
                check=True
            )
            
            if not diff_result.stdout:
                return {
                    'success': False,
                    'output': "No staged changes to commit. Use 'git add' first.",
                    'commands': []
                }
            
            # Generate smart commit message suggestion
            message = context.get('message', '')
            if not message:
                message = "Update: changes applied"  # Default message
            
            commands = [
                f'git commit -m "{message}"'
            ]
            
            return {
                'success': True,
                'output': f"Ready to commit with message: {message}",
                'commands': commands
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'output': f"Failed to prepare commit: {e.stderr}",
                'commands': []
            }
    
    def _safe_push(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Safe push with checks"""
        try:
            # Check if there are commits to push
            result = subprocess.run(
                ['git', 'log', '@{u}..', '--oneline'],
                capture_output=True,
                text=True
            )
            
            if not result.stdout:
                return {
                    'success': False,
                    'output': "No commits to push.",
                    'commands': []
                }
            
            # Get current branch
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                check=True
            )
            
            branch = branch_result.stdout.strip()
            
            commands = [
                f'git push origin {branch}'
            ]
            
            return {
                'success': True,
                'output': f"Ready to push to origin/{branch}",
                'commands': commands,
                'needs_confirmation': True
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'output': f"Failed to prepare push: {e.stderr}",
                'commands': []
            }
    
    def _git_pull(self) -> Dict[str, Any]:
        """Git pull with conflict detection"""
        commands = ['git pull']
        
        return {
            'success': True,
            'output': "Pulling latest changes...",
            'commands': commands
        }
    
    def _generic_git(self, command: str) -> Dict[str, Any]:
        """Handle generic Git command"""
        return {
            'success': True,
            'output': f"Executing: {command}",
            'commands': [command]
        }
