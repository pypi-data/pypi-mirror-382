"""CLI commands package for Gnosari Teams."""

# Import all command modules to ensure registration
from .run import UnifiedRunCommand
from . import team
from . import modular
from . import worker
from . import prompts

__all__ = [
    'UnifiedRunCommand',
    'team',
    'modular', 
    'worker',
    'prompts',
]