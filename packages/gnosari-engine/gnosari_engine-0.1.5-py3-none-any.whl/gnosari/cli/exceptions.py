"""CLI-specific exceptions for Gnosari Teams."""

from __future__ import annotations

from typing import Optional


class CLIError(Exception):
    """Base exception for CLI errors."""
    
    def __init__(self, message: str, exit_code: int = 1, suggestion: Optional[str] = None):
        self.message = message
        self.exit_code = exit_code
        self.suggestion = suggestion
        super().__init__(self.message)


class ValidationError(CLIError):
    """Configuration validation error."""
    pass


class NetworkError(CLIError):
    """Network-related error."""
    pass


class ConfigurationError(CLIError):
    """Configuration file error."""
    pass


class CommandNotFoundError(CLIError):
    """Command not found error."""
    pass


class ArgumentError(CLIError):
    """Invalid command arguments error."""
    pass