"""CLI utilities for Gnosari Teams."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, Set, Optional, Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..utils.logging import setup_logging as setup_base_logging


def setup_cli_logging(level: str = "INFO", debug: bool = False) -> None:
    """Setup CLI-specific logging."""
    if debug:
        level = "DEBUG"
    # Ensure level is uppercase
    level = level.upper()
    setup_base_logging(level)


def load_environment_variables() -> Dict[str, str]:
    """Load environment variables from .env file if present."""
    from dotenv import load_dotenv
    
    env_files = ['.env', '.env.local']
    loaded_vars = {}
    
    for env_file in env_files:
        if Path(env_file).exists():
            load_dotenv(env_file, override=False)  # Don't override existing env vars
            
    # Return relevant environment variables
    relevant_vars = [
        'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'DEEPSEEK_API_KEY',
        'GNOSARI_API_KEY', 'GNOSARI_API_URL',
        'OPENAI_MODEL', 'OPENAI_TEMPERATURE',
        'GNOSARI_CLI_DEBUG', 'GNOSARI_CLI_LOG_LEVEL', 'GNOSARI_CLI_OUTPUT_FORMAT'
    ]
    
    for var in relevant_vars:
        if var in os.environ:
            loaded_vars[var] = os.environ[var]
    
    return loaded_vars


def detect_env_variables(config: Dict[str, Any]) -> Set[str]:
    """Detect required environment variables from configuration."""
    env_vars = set()
    
    def _recursive_search(obj: Any, path: str = "") -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                _recursive_search(value, new_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]"
                _recursive_search(item, new_path)
        elif isinstance(obj, str):
            # Look for environment variable patterns
            import re
            env_pattern = r'\$\{([^}]+)\}'
            matches = re.findall(env_pattern, obj)
            env_vars.update(matches)
    
    _recursive_search(config)
    return env_vars


def generate_env_example(env_vars: Set[str]) -> str:
    """Generate example .env file content."""
    if not env_vars:
        return ""
    
    lines = ["# Environment variables for Gnosari Teams", ""]
    
    for var in sorted(env_vars):
        if var.endswith('_API_KEY'):
            lines.append(f"{var}=your-api-key-here")
        elif var.endswith('_URL'):
            lines.append(f"{var}=https://api.example.com")
        elif var.endswith('_MODEL'):
            lines.append(f"{var}=gpt-4o")
        elif var.endswith('_TEMPERATURE'):
            lines.append(f"{var}=1.0")
        else:
            lines.append(f"{var}=your-value-here")
    
    return "\n".join(lines)


def validate_file_path(path: str, must_exist: bool = True) -> Path:
    """Validate and return a Path object."""
    file_path = Path(path)
    
    if must_exist and not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    return file_path


def format_success_message(message: str) -> Text:
    """Format a success message for rich console."""
    return Text.assemble(("✅ ", "green"), (message, "green"))


def format_error_message(message: str) -> Text:
    """Format an error message for rich console."""
    return Text.assemble(("❌ ", "red"), (message, "red"))


def format_warning_message(message: str) -> Text:
    """Format a warning message for rich console."""
    return Text.assemble(("⚠️  ", "yellow"), (message, "yellow"))


def format_info_message(message: str) -> Text:
    """Format an info message for rich console."""
    return Text.assemble(("ℹ️  ", "blue"), (message, "blue"))


def create_progress_panel(title: str, content: str) -> Panel:
    """Create a progress panel for CLI operations."""
    return Panel(
        content,
        title=title,
        border_style="blue",
        padding=(1, 2)
    )


def handle_keyboard_interrupt() -> None:
    """Handle keyboard interrupt gracefully."""
    console = Console()
    console.print("\n[yellow]Operation cancelled by user[/yellow]")
    sys.exit(130)


def ensure_directory_exists(path: Path) -> None:
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe file system usage."""
    import re
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    return sanitized


def parse_key_value_args(args: list) -> Dict[str, str]:
    """Parse key=value arguments from command line."""
    result = {}
    for arg in args:
        if '=' in arg:
            key, value = arg.split('=', 1)
            result[key] = value
    return result