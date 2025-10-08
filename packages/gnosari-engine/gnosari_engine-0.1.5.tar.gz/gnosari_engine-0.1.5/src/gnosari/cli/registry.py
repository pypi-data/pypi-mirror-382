"""Command registry for Gnosari Teams CLI."""

from __future__ import annotations

from typing import Dict, Type, List, Optional, Any
import importlib
import pkgutil

from .base import BaseCommand
from .exceptions import CommandNotFoundError


class CommandRegistry:
    """Registry for CLI commands."""
    
    def __init__(self):
        self._commands: Dict[str, Type[BaseCommand]] = {}
        self._command_groups: Dict[str, List[str]] = {}
        self._command_instances: Dict[str, BaseCommand] = {}
    
    def register(self, command_cls: Type[BaseCommand], group: str = "main") -> None:
        """Register a command class."""
        # Skip abstract classes
        import inspect
        if inspect.isabstract(command_cls):
            return
            
        # Get command name from class
        try:
            # Try to access the name property - if it's abstract, this will fail
            command_name = command_cls.name
            if isinstance(command_name, property):
                # This is still the abstract property, skip registration
                return
        except (AttributeError, TypeError, NotImplementedError):
            # Fallback to class name conversion
            command_name = self._class_name_to_command_name(command_cls.__name__)
        
        # Check if command already exists (avoid conflicts)
        if command_name in self._commands:
            print(f"Warning: Command '{command_name}' already registered, skipping duplicate")
            return
        
        self._commands[command_name] = command_cls
        
        if group not in self._command_groups:
            self._command_groups[group] = []
        
        if command_name not in self._command_groups[group]:
            self._command_groups[group].append(command_name)
    
    def get_command(self, name: str) -> Optional[Type[BaseCommand]]:
        """Get command class by name."""
        return self._commands.get(name)
    
    def get_command_instance(self, name: str, **kwargs) -> Optional[BaseCommand]:
        """Get or create command instance by name."""
        if name not in self._command_instances:
            command_cls = self.get_command(name)
            if command_cls:
                self._command_instances[name] = command_cls(**kwargs)
            else:
                return None
        return self._command_instances[name]
    
    def get_commands_by_group(self, group: str) -> List[Type[BaseCommand]]:
        """Get all commands in a group."""
        command_names = self._command_groups.get(group, [])
        return [self._commands[name] for name in command_names if name in self._commands]
    
    def list_commands(self) -> Dict[str, List[str]]:
        """List all registered commands by group."""
        return self._command_groups.copy()
    
    def list_all_commands(self) -> List[str]:
        """List all registered command names."""
        return list(self._commands.keys())
    
    def auto_discover_commands(self, package_path: str) -> None:
        """Auto-discover and register commands from a package."""
        try:
            package = importlib.import_module(package_path)
            
            # Walk through all modules in the package
            for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
                if not is_pkg:  # Only process modules, not sub-packages
                    full_module_name = f"{package_path}.{module_name}"
                    try:
                        module = importlib.import_module(full_module_name)
                        self._register_commands_from_module(module)
                    except Exception as e:
                        # Log but don't fail on import errors
                        print(f"Warning: Could not import {full_module_name}: {e}")
                        
        except ImportError as e:
            print(f"Warning: Could not import package {package_path}: {e}")
    
    def _register_commands_from_module(self, module: Any) -> None:
        """Register commands from a module."""
        import inspect
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, BaseCommand) and 
                attr != BaseCommand and
                not inspect.isabstract(attr)):
                
                # Determine group from module path
                module_parts = module.__name__.split('.')
                group = module_parts[-2] if len(module_parts) > 1 else "main"
                
                self.register(attr, group)
    
    def _class_name_to_command_name(self, class_name: str) -> str:
        """Convert class name to command name."""
        # Remove 'Command' suffix if present
        if class_name.endswith('Command'):
            class_name = class_name[:-7]
        
        # Convert CamelCase to kebab-case
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', class_name)
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()


# Global registry instance
registry = CommandRegistry()


def register_command(group: str = "main"):
    """Decorator to register commands."""
    def decorator(command_cls: Type[BaseCommand]):
        registry.register(command_cls, group)
        return command_cls
    return decorator


def get_registry() -> CommandRegistry:
    """Get the global command registry."""
    return registry