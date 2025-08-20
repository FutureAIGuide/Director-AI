"""
plugin_system.py

Provides a basic plugin loader for Director-AI.
Allows users to add custom Python plugins for new features and extensions.
"""

import importlib.util
import os
from typing import List, Any

class PluginSystem:
    def __init__(self, plugins_dir: str = 'plugins'):
        self.plugins_dir = plugins_dir
        self.plugins: List[Any] = []
        self.load_plugins()

    def load_plugins(self):
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith('.py'):
                plugin_path = os.path.join(self.plugins_dir, filename)
                spec = importlib.util.spec_from_file_location(filename[:-3], plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.plugins.append(module)

    def run_all(self, *args, **kwargs):
        for plugin in self.plugins:
            if hasattr(plugin, 'run'):
                plugin.run(*args, **kwargs)

# Example usage:
# plugin_system = PluginSystem()
# plugin_system.run_all()
