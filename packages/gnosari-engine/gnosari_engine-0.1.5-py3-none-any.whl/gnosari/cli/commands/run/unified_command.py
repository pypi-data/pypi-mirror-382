"""Unified run command following SOLID principles and DRY principle."""

import argparse
import os
import uuid
from pathlib import Path

from ...base import StreamingCommand
from ...exceptions import ValidationError, ConfigurationError
from ...registry import register_command
from ...schemas import CommandResponse
from ....engine.builder import TeamBuilder
from ....engine.runner import TeamRunner

from .detectors import ConfigurationDetectorFactory
from .loaders import ConfigurationLoaderFactory
from .executors import TeamExecutorFactory
from .validators import RunCommandValidatorFactory


@register_command()
class UnifiedRunCommand(StreamingCommand):
    """Unified run command that auto-detects configuration type and handles both monolithic and modular teams."""
    
    name = "run"
    description = "Run team from YAML file or modular directory (auto-detects configuration type)"
    
    def __init__(self, console=None):
        super().__init__(console)
        self._detector_factory = ConfigurationDetectorFactory()
        self._loader_factory = ConfigurationLoaderFactory()
        self._executor_factory = TeamExecutorFactory()
        self._validator_factory = RunCommandValidatorFactory()
    
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            'team_path',
            help='Path to team YAML file or modular directory'
        )
        parser.add_argument(
            '--message', '-m',
            required=True,
            help='Message to send to the team'
        )
        parser.add_argument(
            '--agent', '-a',
            help='Run only a specific agent from the team (by name)'
        )
        parser.add_argument(
            '--session-id', '-s',
            help='Session ID for conversation persistence'
        )
        parser.add_argument(
            '--api-key',
            help='OpenAI API key (or set OPENAI_API_KEY env var)'
        )
        parser.add_argument(
            '--model',
            default=os.getenv("OPENAI_MODEL", "gpt-4o"),
            help='Model to use (default: gpt-4o)'
        )
        parser.add_argument(
            '--temperature',
            type=float,
            default=float(os.getenv("OPENAI_TEMPERATURE", "1")),
            help='Model temperature (default: 1.0)'
        )
        parser.add_argument(
            '--stream',
            action='store_true',
            help='Enable streaming output'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Show debug information with raw JSON output'
        )
    
    def validate_args(self, args: argparse.Namespace) -> bool:
        """Validate command arguments using the validator factory."""
        validator = self._validator_factory.create_validator()
        
        if not validator.validate(args):
            self.console.print(f"[red]{validator.get_error_message()}[/red]")
            return False
        
        return True
    
    async def execute(self, args: argparse.Namespace) -> CommandResponse:
        """Execute the unified run command."""
        try:
            team_path = Path(args.team_path)
            
            # Detect configuration type
            detector = self._detector_factory.detect_configuration_type(team_path)
            config_type = detector.get_config_type()
            
            self.console.print(f"[blue]Detected {config_type} team configuration:[/blue] {team_path}")
            
            # Load configuration
            loader = self._loader_factory.create_loader(config_type)
            config = await loader.load_configuration(team_path)
            team_identifier = loader.get_team_identifier(team_path)
            
            # Build team
            team_builder = self._create_team_builder(args, team_identifier)
            team = await self._build_team(team_builder, config, team_path, args.debug)
            runner = TeamRunner(team)
            
            # Execute team
            executor = self._executor_factory.create_executor(args.stream)
            session_context = self._create_session_context(team_identifier, args.session_id)
            
            await executor.execute_team(
                runner=runner,
                message=args.message,
                agent_name=args.agent,
                stream=args.stream,
                debug=args.debug,
                session_id=args.session_id,
                session_context=session_context,
                console=self.console
            )
            
            return CommandResponse(
                success=True,
                message=f"{config_type.title()} team execution completed successfully"
            )
        
        except Exception as e:
            self.logger.error(f"Run command failed: {e}")
            if args.debug:
                import traceback
                self.console.print(traceback.format_exc())
            raise ConfigurationError(f"Team execution failed: {e}")
    
    def _create_team_builder(self, args: argparse.Namespace, team_identifier: str) -> TeamBuilder:
        """Create a team builder with the provided arguments."""
        api_key = args.api_key or os.getenv("OPENAI_API_KEY")
        session_id = args.session_id or f"session-{uuid.uuid4().hex[:8]}"
        
        return TeamBuilder(
            api_key=api_key,
            model=args.model,
            temperature=args.temperature,
            session_id=session_id,
            team_identifier=team_identifier
        )
    
    async def _build_team(self, builder: TeamBuilder, config: dict, team_path: Path, debug: bool):
        """Build the team from configuration."""
        if isinstance(config, dict):
            # For modular configs that are already dictionaries
            import tempfile
            import yaml
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2)
                temp_config_path = f.name
            
            try:
                return await builder.build_team(temp_config_path, debug=debug)
            finally:
                os.unlink(temp_config_path)
        else:
            # For monolithic configs that are file paths
            return await builder.build_team(str(team_path), debug=debug)
    
    def _create_session_context(self, team_identifier: str, session_id: str) -> dict:
        """Create session context for the team execution."""
        actual_session_id = session_id or f"session-{uuid.uuid4().hex[:8]}"
        
        return {
            'team_identifier': team_identifier,
            'session_id': actual_session_id
        }