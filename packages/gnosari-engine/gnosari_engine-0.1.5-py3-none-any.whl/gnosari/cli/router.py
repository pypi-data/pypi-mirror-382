"""Main CLI router and application controller for Gnosari Teams."""

from __future__ import annotations

import argparse
import asyncio
import sys
from typing import Dict, List, NoReturn, Optional

from rich.console import Console

from .exceptions import CLIError, CommandNotFoundError
from .registry import registry
from .schemas import CommandResponse
from .utils import (
    setup_cli_logging, 
    load_environment_variables, 
    handle_keyboard_interrupt,
    format_error_message,
    format_success_message
)


class CLIRouter:
    """Main CLI router and application controller."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        # Build parser after command registration in main CLI
        self.parser = self._build_parser()
    
    def _build_parser(self) -> argparse.ArgumentParser:
        """Build the main argument parser."""
        parser = argparse.ArgumentParser(
            description="Gnosari Teams - Multi-Agent AI Team Runner",
            epilog="Use 'gnosari <command> --help' for more information."
        )
        
        # Global options
        parser.add_argument(
            '--debug', 
            action='store_true', 
            help='Enable debug mode'
        )
        parser.add_argument(
            '--log-level', 
            default=None,  # No default so environment variables can be used
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            help='Set logging level'
        )
        parser.add_argument(
            '--output-format', 
            default='rich', 
            choices=['rich', 'json', 'yaml'],
            help='Output format'
        )
        
        # Create subparsers for commands
        subparsers = parser.add_subparsers(
            dest='command',
            help='Available commands',
            metavar='COMMAND'
        )
        
        # Register all commands from registry
        self._register_commands_with_parser(subparsers)
        
        # Legacy support - add backward compatibility arguments
        self._add_legacy_arguments(parser)
        
        return parser
    
    def _register_commands_with_parser(self, subparsers) -> None:
        """Register all commands from registry with argument parser."""
        command_groups = registry.list_commands()
        
        for group, command_names in command_groups.items():
            for command_name in command_names:
                command_cls = registry.get_command(command_name)
                if command_cls:
                    try:
                        # Create subparser for this command
                        cmd_parser = subparsers.add_parser(
                            command_name,
                            help=command_cls.description if hasattr(command_cls, 'description') else f"{command_name} command"
                        )
                        
                        # Let command add its own arguments
                        if hasattr(command_cls, 'add_arguments'):
                            # Create a temporary instance to call add_arguments
                            temp_instance = command_cls(self.console)
                            temp_instance.add_arguments(cmd_parser)
                    except Exception as e:
                        self.console.print(f"Warning: Could not register command {command_name}: {e}")
    
    def _add_legacy_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add legacy arguments for backward compatibility."""
        # Backward compatibility arguments for direct team running
        parser.add_argument(
            "--config", "-c", 
            help="Path to team configuration YAML file (legacy mode)"
        )
        parser.add_argument(
            "--message", "-m", 
            help="Message to send to the team (legacy mode)"
        )
        parser.add_argument(
            "--agent", "-a", 
            help="Run only a specific agent from the team (legacy mode)"
        )
        parser.add_argument(
            "--session-id", "-s", 
            help="Session ID for conversation persistence (legacy mode)"
        )
        parser.add_argument(
            "--api-key", 
            help="OpenAI API key (legacy mode)"
        )
        parser.add_argument(
            "--model", 
            help="Model to use (legacy mode)"
        )
        parser.add_argument(
            "--temperature", 
            type=float, 
            help="Model temperature (legacy mode)"
        )
        parser.add_argument(
            "--stream", 
            action="store_true", 
            help="Stream the response in real-time (legacy mode)"
        )
        parser.add_argument(
            "--show-prompts", 
            action="store_true", 
            help="Display the generated system prompts (legacy mode)"
        )
    
    async def route(self, args: argparse.Namespace) -> CommandResponse:
        """Route command to appropriate handler."""
        # Handle legacy mode (no command specified but config provided)
        if not args.command and args.config:
            return await self._handle_legacy_mode(args)
        
        # Handle case where no command is specified
        if not args.command:
            self.parser.print_help()
            return CommandResponse(
                success=False, 
                message="No command specified",
                exit_code=1
            )
        
        # Get command class from registry
        command_cls = registry.get_command(args.command)
        if not command_cls:
            available_commands = ", ".join(registry.list_all_commands())
            error_msg = f"Unknown command: {args.command}. Available commands: {available_commands}"
            self.console.print(format_error_message(error_msg))
            return CommandResponse(
                success=False, 
                message=error_msg,
                exit_code=1
            )
        
        # Create command instance and run it
        try:
            command_instance = command_cls(self.console)
            return await command_instance.run(args)
        except Exception as e:
            error_msg = f"Failed to execute command {args.command}: {e}"
            self.console.print(format_error_message(error_msg))
            return CommandResponse(
                success=False,
                message=error_msg,
                exit_code=1
            )
    
    async def _handle_legacy_mode(self, args: argparse.Namespace) -> CommandResponse:
        """Handle legacy mode for backward compatibility."""
        # Import and delegate to legacy run command
        try:
            from .commands.team.run import RunCommand
            
            # Create a run command instance
            run_command = RunCommand(self.console)
            
            # Convert legacy args to new format
            setattr(args, 'command', 'run')
            
            return await run_command.run(args)
        except ImportError:
            return CommandResponse(
                success=False,
                message="Legacy mode not available - run command not found",
                exit_code=1
            )
        except Exception as e:
            return CommandResponse(
                success=False,
                message=f"Legacy mode failed: {e}",
                exit_code=1
            )
    
    def run(self, argv: Optional[List[str]] = None) -> NoReturn:
        """Main entry point for CLI."""
        try:
            # Load environment variables
            load_environment_variables()
            
            # Parse arguments - handle unknown args for variable substitution
            args, unknown_args = self.parser.parse_known_args(argv)
            
            # Parse variable arguments for prompts commands
            if getattr(args, 'command', None) == 'prompts':
                variables = self._parse_variable_args(unknown_args)
                setattr(args, 'variables', variables)
            
            # Setup logging based on arguments and environment variables
            # Priority: command line arg > environment variable > default
            import os
            env_log_level = os.getenv('LOG_LEVEL', os.getenv('GNOSARI_CLI_LOG_LEVEL', 'INFO')).upper()
            # If --log-level was provided, use it; otherwise use environment variable
            log_level = args.log_level if args.log_level is not None else env_log_level
            setup_cli_logging(
                level=log_level,
                debug=getattr(args, 'debug', False)
            )
            
            # Route and execute command
            response = asyncio.run(self.route(args))
            
            # Handle response
            if response.success:
                if response.message:
                    self.console.print(format_success_message(response.message))
            else:
                if response.message:
                    self.console.print(format_error_message(response.message))
            
            sys.exit(response.exit_code)
            
        except KeyboardInterrupt:
            handle_keyboard_interrupt()
        except CLIError as e:
            self.console.print(format_error_message(e.message))
            if e.suggestion:
                self.console.print(f"[dim]Suggestion: {e.suggestion}[/dim]")
            sys.exit(e.exit_code)
        except Exception as e:
            self.console.print(format_error_message(f"Unexpected error: {e}"))
            if hasattr(args, 'debug') and getattr(args, 'debug', False):
                import traceback
                self.console.print(traceback.format_exc())
            sys.exit(1)
    
    def _parse_variable_args(self, unknown_args: List[str]) -> Dict[str, str]:
        """Parse --variable_name value arguments from unknown args."""
        variables = {}
        i = 0
        while i < len(unknown_args):
            if unknown_args[i].startswith('--'):
                var_name = unknown_args[i][2:]  # Remove --
                if i + 1 < len(unknown_args) and not unknown_args[i + 1].startswith('--'):
                    variables[var_name] = unknown_args[i + 1]
                    i += 2
                else:
                    # Variable without value - treat as flag or empty string
                    variables[var_name] = ""
                    i += 1
            else:
                i += 1
        return variables


def create_cli_app() -> CLIRouter:
    """Create and configure the CLI application."""
    return CLIRouter()


def main(argv=None) -> NoReturn:
    """Main entry point for the CLI application."""
    # Create and run CLI app
    app = create_cli_app()
    app.run(argv)