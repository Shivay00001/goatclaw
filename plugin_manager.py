"""
DevOS Plugin System
Provides dynamic plugin loading and execution
"""

import os
import json
import importlib.util
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from pathlib import Path


class PluginInterface(ABC):
    """Base interface for DevOS plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description"""
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]):
        """
        Initialize plugin with configuration
        
        Args:
            config: Plugin configuration
        """
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute plugin functionality
        
        Args:
            context: Execution context
        
        Returns:
            Execution result
        """
        pass
    
    @abstractmethod
    def get_commands(self) -> List[str]:
        """
        Get list of commands this plugin handles
        
        Returns:
            List of command patterns
        """
        pass


class PluginManifest:
    """Plugin manifest parser"""
    
    def __init__(self, manifest_path: str):
        with open(manifest_path, 'r') as f:
            data = json.load(f)
        
        self.name = data['name']
        self.version = data['version']
        self.description = data.get('description', '')
        self.author = data.get('author', '')
        self.entry_point = data['entry_point']
        self.permissions = data.get('permissions', [])
        self.dependencies = data.get('dependencies', [])
        self.config = data.get('config', {})


class PluginManager:
    """Manages plugin lifecycle"""
    
    def __init__(self, plugin_dir: str = None):
        """
        Initialize plugin manager
        
        Args:
            plugin_dir: Directory containing plugins
        """
        if plugin_dir is None:
            config_dir = self._get_config_dir()
            plugin_dir = os.path.join(config_dir, 'plugins')
        
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, PluginInterface] = {}
        self.manifests: Dict[str, PluginManifest] = {}
        
        # Ensure plugin directory exists
        os.makedirs(self.plugin_dir, exist_ok=True)
    
    def _get_config_dir(self) -> str:
        """Get platform-specific config directory"""
        if os.name == 'nt':  # Windows
            base_dir = os.getenv('APPDATA')
        elif os.uname().sysname == 'Darwin':  # macOS
            base_dir = os.path.join(Path.home(), 'Library', 'Application Support')
        else:  # Linux
            base_dir = os.getenv('XDG_CONFIG_HOME', os.path.join(Path.home(), '.config'))
        
        return os.path.join(base_dir, 'devos')
    
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins
        
        Returns:
            List of plugin names
        """
        plugins = []
        
        for item in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, item)
            if os.path.isdir(plugin_path):
                manifest_path = os.path.join(plugin_path, 'manifest.json')
                if os.path.exists(manifest_path):
                    plugins.append(item)
        
        return plugins
    
    def load_plugin(self, plugin_name: str) -> bool:
        """
        Load a plugin
        
        Args:
            plugin_name: Name of plugin to load
        
        Returns:
            True if loaded successfully
        """
        try:
            plugin_path = os.path.join(self.plugin_dir, plugin_name)
            manifest_path = os.path.join(plugin_path, 'manifest.json')
            
            # Load manifest
            manifest = PluginManifest(manifest_path)
            self.manifests[plugin_name] = manifest
            
            # Load plugin module
            entry_point_path = os.path.join(plugin_path, manifest.entry_point)
            spec = importlib.util.spec_from_file_location(plugin_name, entry_point_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get plugin class (should be named 'Plugin')
            plugin_class = getattr(module, 'Plugin')
            plugin_instance = plugin_class()
            
            # Validate plugin implements interface
            if not isinstance(plugin_instance, PluginInterface):
                raise TypeError(f"Plugin {plugin_name} does not implement PluginInterface")
            
            # Initialize plugin
            plugin_instance.initialize(manifest.config)
            
            # Store plugin
            self.plugins[plugin_name] = plugin_instance
            
            return True
            
        except Exception as e:
            print(f"Failed to load plugin {plugin_name}: {str(e)}")
            return False
    
    def load_all_plugins(self):
        """Load all discovered plugins"""
        plugins = self.discover_plugins()
        for plugin_name in plugins:
            self.load_plugin(plugin_name)
    
    def unload_plugin(self, plugin_name: str):
        """
        Unload a plugin
        
        Args:
            plugin_name: Name of plugin to unload
        """
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
        if plugin_name in self.manifests:
            del self.manifests[plugin_name]
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """
        Get a loaded plugin
        
        Args:
            plugin_name: Name of plugin
        
        Returns:
            Plugin instance or None
        """
        return self.plugins.get(plugin_name)
    
    def execute_plugin(self, plugin_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a plugin
        
        Args:
            plugin_name: Name of plugin to execute
            context: Execution context
        
        Returns:
            Execution result
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin not found: {plugin_name}")
        
        return plugin.execute(context)
    
    def find_plugin_for_command(self, command: str) -> Optional[str]:
        """
        Find plugin that handles a command
        
        Args:
            command: Command string
        
        Returns:
            Plugin name or None
        """
        for plugin_name, plugin in self.plugins.items():
            for cmd_pattern in plugin.get_commands():
                if cmd_pattern.lower() in command.lower():
                    return plugin_name
        
        return None
    
    def list_plugins(self) -> List[Dict[str, str]]:
        """
        List all loaded plugins
        
        Returns:
            List of plugin information
        """
        result = []
        for plugin_name, plugin in self.plugins.items():
            manifest = self.manifests.get(plugin_name)
            result.append({
                'name': plugin.name,
                'version': plugin.version,
                'description': plugin.description,
                'author': manifest.author if manifest else 'Unknown',
                'commands': plugin.get_commands()
            })
        
        return result
