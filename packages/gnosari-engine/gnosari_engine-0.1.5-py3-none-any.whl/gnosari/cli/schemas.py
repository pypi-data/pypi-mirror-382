"""CLI schemas for Gnosari Teams CLI application."""

from __future__ import annotations

from typing import Any, Dict, Optional
from pathlib import Path
from pydantic import Field

from ..schemas.base import BaseIOSchema


class CLIConfig(BaseIOSchema):
    """Configuration schema for CLI operations."""
    
    log_level: str = Field(default="INFO", description="Logging level")
    output_format: str = Field(default="rich", description="Output format")
    debug: bool = Field(default=False, description="Enable debug mode")
    

class CommandRequest(BaseIOSchema):
    """Base request schema for CLI commands."""
    
    command_name: str = Field(description="Name of the command")
    args: Dict[str, Any] = Field(default_factory=dict, description="Command arguments")
    

class CommandResponse(BaseIOSchema):
    """Base response schema for CLI commands."""
    
    success: bool = Field(description="Command execution success")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    exit_code: int = Field(default=0, description="Exit code")


class CLIContext(BaseIOSchema):
    """CLI execution context."""
    
    debug: bool = Field(default=False, description="Debug mode enabled")
    log_level: str = Field(default="INFO", description="Logging level")
    output_format: str = Field(default="rich", description="Output format")
    session_id: Optional[str] = Field(None, description="Session ID")
    working_directory: Path = Field(default_factory=Path.cwd, description="Working directory")
    environment: Dict[str, str] = Field(default_factory=dict, description="Environment variables")