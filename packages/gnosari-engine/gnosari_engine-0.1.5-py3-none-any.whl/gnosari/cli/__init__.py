"""Gnosari Teams CLI package."""

from typing import NoReturn

from .base import BaseCommand, AsyncCommand, SyncCommand, StreamingCommand
from .exceptions import CLIError, ValidationError, NetworkError, ConfigurationError
from .registry import registry, register_command, get_registry
from .router import CLIRouter, create_cli_app
from .schemas import CLIConfig, CommandRequest, CommandResponse, CLIContext


def main(argv=None) -> NoReturn:
    """Main entry point for the gnosari CLI with new architecture."""
    # Import and register all commands BEFORE creating the CLI router
    try:
        from .commands import team, modular, worker, prompts
        # Auto-discover any additional commands
        registry.auto_discover_commands('gnosari.cli.commands')
    except ImportError as e:
        print(f"Warning: Could not import some command modules: {e}")
    
    # Create and run CLI app
    app = create_cli_app()
    app.run(argv)

__all__ = [
    # Base classes
    'BaseCommand',
    'AsyncCommand', 
    'SyncCommand',
    'StreamingCommand',
    
    # Exceptions
    'CLIError',
    'ValidationError',
    'NetworkError',
    'ConfigurationError',
    
    # Registry
    'registry',
    'register_command',
    'get_registry',
    
    # Router
    'CLIRouter',
    'create_cli_app',
    'main',
    
    # Schemas
    'CLIConfig',
    'CommandRequest',
    'CommandResponse',
    'CLIContext',
]