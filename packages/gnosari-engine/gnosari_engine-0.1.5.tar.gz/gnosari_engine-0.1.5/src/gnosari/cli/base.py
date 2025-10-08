"""Base command classes for Gnosari Teams CLI."""

from __future__ import annotations

import argparse
import asyncio
import time
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Dict, Optional

from rich.console import Console

from ..utils.logging import get_logger
from .exceptions import CLIError, ArgumentError
from .schemas import CommandResponse


def monitor_command_execution(func):
    """Decorator to monitor command execution time."""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        start_time = time.time()
        try:
            result = await func(self, *args, **kwargs)
            execution_time = time.time() - start_time
            self.logger.info(f"Command {self.name} completed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Command {self.name} failed after {execution_time:.2f}s: {e}")
            raise
    return wrapper


class BaseCommand(ABC):
    """Base class for all CLI commands."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.logger = get_logger(self.__class__.__name__)
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Command name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Command description."""
        pass
    
    @abstractmethod
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments to parser."""
        pass
    
    @abstractmethod
    async def execute(self, args: argparse.Namespace) -> CommandResponse:
        """Execute the command."""
        pass
    
    def validate_args(self, args: argparse.Namespace) -> bool:
        """Validate command arguments."""
        return True
    
    def handle_error(self, error: Exception) -> CommandResponse:
        """Handle command execution errors."""
        self.logger.error(f"Command {self.name} failed: {error}")
        
        if isinstance(error, CLIError):
            return CommandResponse(
                success=False,
                message=error.message,
                exit_code=error.exit_code
            )
        
        return CommandResponse(
            success=False,
            message=f"Error: {error}",
            exit_code=1
        )


class AsyncCommand(BaseCommand):
    """Base class for async CLI commands."""
    
    @monitor_command_execution
    async def run(self, args: argparse.Namespace) -> CommandResponse:
        """Run the async command with error handling."""
        try:
            if not self.validate_args(args):
                return CommandResponse(
                    success=False,
                    message="Invalid arguments",
                    exit_code=2
                )
            return await self.execute(args)
        except Exception as e:
            return self.handle_error(e)


class SyncCommand(BaseCommand):
    """Base class for sync CLI commands."""
    
    @abstractmethod
    def execute_sync(self, args: argparse.Namespace) -> CommandResponse:
        """Execute the sync command."""
        pass
    
    # Override the async execute method from BaseCommand
    async def execute(self, args: argparse.Namespace) -> CommandResponse:
        """Execute async by calling sync method."""
        return self.execute_sync(args)
    
    def run(self, args: argparse.Namespace) -> CommandResponse:
        """Run the sync command with error handling."""
        try:
            if not self.validate_args(args):
                return CommandResponse(
                    success=False,
                    message="Invalid arguments",
                    exit_code=2
                )
            # Execute synchronously
            return self.execute_sync(args)
        except Exception as e:
            return self.handle_error(e)


class StreamingCommand(AsyncCommand):
    """Base class for commands that support streaming output."""
    
    def __init__(self, console: Optional[Console] = None):
        super().__init__(console)
        self.supports_streaming = True
    
    async def execute_with_streaming(self, args: argparse.Namespace) -> CommandResponse:
        """Execute command with streaming support."""
        # Default implementation falls back to regular execute
        return await self.execute(args)