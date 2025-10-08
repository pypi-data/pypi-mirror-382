"""Team push command for Gnosari Teams CLI."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
import yaml

from ...base import AsyncCommand
from ...exceptions import ValidationError, NetworkError, ConfigurationError
from ...registry import register_command
from ...schemas import CommandResponse
from ....engine.config.configuration_manager import ConfigurationManager


@register_command("team")
class PushCommand(AsyncCommand):
    """Push team configuration to Gnosari API."""
    
    name = "push"
    description = "Push team configuration to Gnosari API"
    
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            'team_path',
            help='Team identifier (looks in teams/{identifier}) or direct path to team configuration file/directory'
        )
        parser.add_argument(
            '--api-url',
            help='Gnosari API URL (default: https://api.gnosari.com or GNOSARI_API_URL env var)'
        )
    
    def validate_args(self, args: argparse.Namespace) -> bool:
        """Validate command arguments."""
        # Resolve the actual config path
        resolved_path = self._resolve_team_path(args.team_path)
        if not resolved_path or not resolved_path.exists():
            self.console.print(f"[red]Error: Team configuration not found for '{args.team_path}'[/red]")
            if not resolved_path:
                self.console.print("[red]Tried: teams/{identifier} and direct path[/red]")
            return False
        
        # Store resolved path for use in execute
        args._resolved_path = resolved_path
        return True
    
    async def execute(self, args: argparse.Namespace) -> CommandResponse:
        """Execute the push command."""
        try:
            # Default API URL if not provided
            api_url = args.api_url or os.getenv("GNOSARI_API_URL", "https://api.gnosari.com")
            
            # Ensure the API URL ends with the correct endpoint
            if not api_url.endswith("/api/v1/teams/push"):
                # Only add endpoint if it's a base URL (no path after domain)
                parsed = urlparse(api_url)
                if parsed.path in ['', '/']:
                    api_url = api_url.rstrip("/") + "/api/v1/teams/push"
            
            # Load team configuration (handle both file and directory)
            config_path = args._resolved_path
            yaml_content = await self._load_team_configuration(config_path)
            
            # Validate required fields
            if not yaml_content.get('name'):
                raise ValidationError("'name' field is required in the team configuration")
            
            if not yaml_content.get('id'):
                raise ValidationError("'id' field is required in the team configuration")
            
            self.console.print(f"[blue]Loading team configuration from:[/blue] {config_path}")
            self.console.print(f"[blue]Team name:[/blue] {yaml_content.get('name')}")
            self.console.print(f"[blue]Team ID:[/blue] {yaml_content.get('id')}")
            self.console.print(f"[blue]Pushing to API:[/blue] {api_url}")
            
            # Convert to JSON for API
            json_payload = json.dumps(yaml_content, indent=2)
            
            # Make HTTP request
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
                
                # Add authentication header if API key is available
                api_key = os.getenv("GNOSARI_API_KEY")
                if api_key:
                    headers['X-Auth-Token'] = api_key
                else:
                    self.console.print("[yellow]Warning: GNOSARI_API_KEY not found in environment variables[/yellow]")
                
                self.console.print("🚀 [yellow]Pushing team configuration...[/yellow]")
                
                # Debug logging of the request
                self.logger.debug(f"Making HTTP POST request to: {api_url}")
                self.logger.debug(f"Request headers: {dict(headers)}")
                self.logger.debug(f"Request payload: {json_payload}")
                
                try:
                    async with session.post(api_url, data=json_payload, headers=headers) as response:
                        response_text = await response.text()
                        
                        self.logger.debug(f"Response status: {response.status}")
                        self.logger.debug(f"Response headers: {dict(response.headers)}")
                        self.logger.debug(f"Response body: {response_text}")
                        
                        if response.status == 200:
                            try:
                                response_data = await response.json()
                                self.console.print("✅ [green]Team configuration pushed successfully![/green]")
                                
                                if 'team_url' in response_data:
                                    self.console.print(f"[green]Team URL:[/green] {response_data['team_url']}")
                                if 'message' in response_data:
                                    self.console.print(f"[green]API Message:[/green] {response_data['message']}")
                                
                                return CommandResponse(
                                    success=True,
                                    message="Team configuration pushed successfully",
                                    data=response_data
                                )
                            except json.JSONDecodeError:
                                # Response is not JSON, but status is 200
                                self.console.print("✅ [green]Team configuration pushed successfully![/green]")
                                return CommandResponse(
                                    success=True,
                                    message="Team configuration pushed successfully",
                                    data={"response": response_text}
                                )
                        
                        elif response.status == 401:
                            raise NetworkError(
                                "Authentication failed. Please check your GNOSARI_API_KEY environment variable.",
                                exit_code=1
                            )
                        
                        elif response.status == 400:
                            try:
                                error_data = await response.json()
                                error_message = error_data.get('message', 'Bad request')
                            except json.JSONDecodeError:
                                error_message = response_text
                            raise ValidationError(f"Invalid team configuration: {error_message}")
                        
                        else:
                            try:
                                error_data = await response.json()
                                error_message = error_data.get('message', f'HTTP {response.status}')
                            except json.JSONDecodeError:
                                error_message = f"HTTP {response.status}: {response_text}"
                            
                            raise NetworkError(f"Failed to push team configuration: {error_message}")
                
                except aiohttp.ClientError as e:
                    raise NetworkError(f"Network error while pushing team configuration: {e}")
        
        except ValidationError:
            raise
        except NetworkError:
            raise
        except Exception as e:
            self.logger.error(f"Push command failed: {e}")
            raise ConfigurationError(f"Failed to push team configuration: {e}")
    
    async def _load_team_configuration(self, config_path: Path) -> dict:
        """
        Load team configuration from either a YAML file or modular directory.
        
        Args:
            config_path: Path to configuration file or directory
            
        Returns:
            Dictionary containing the complete team configuration
        """
        if config_path.is_file():
            # Single YAML file - load directly
            self.console.print(f"[blue]Loading monolithic team configuration...[/blue]")
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        elif config_path.is_dir():
            # Directory - load as modular configuration
            self.console.print(f"[blue]Loading modular team configuration...[/blue]")
            config_manager = ConfigurationManager()
            
            # Load modular configuration
            modular_config = await config_manager.load_team_from_directory(config_path)
            
            # Convert to dict format for API with arrays
            team_dict = {
                "name": modular_config.main.name,
                "id": modular_config.main.id or self._infer_team_id_from_path(config_path),
                "description": modular_config.main.description,
                "version": modular_config.main.version,
                "tags": modular_config.main.tags or [],
                "config": modular_config.main.config or {},
                "agents": [{"id": agent_id, **agent.model_dump()} for agent_id, agent in modular_config.agents.items()],
                "tools": [{"id": tool_id, **tool.model_dump()} for tool_id, tool in modular_config.tools.items()],
                "knowledge": [{"id": kb_id, **kb.model_dump()} for kb_id, kb in modular_config.knowledge.items()],
                "traits": [{"id": trait_id, **trait.model_dump()} for trait_id, trait in modular_config.traits.items()]
            }
            
            return team_dict
        
        else:
            raise ValidationError(f"Configuration path must be a file or directory: {config_path}")
    
    def _resolve_team_path(self, team_path: str) -> Path:
        """
        Resolve team path - try as team identifier first, then as direct path.
        
        Args:
            team_path: Team identifier or direct path
            
        Returns:
            Path object to the resolved team configuration, or None if not found
        """
        # Try as direct path first
        direct_path = Path(team_path)
        if direct_path.exists():
            return direct_path
        
        # Try as team identifier in teams/ directory
        teams_path = Path("teams") / team_path
        if teams_path.exists():
            return teams_path
        
        # Return None if neither worked
        return None
    
    def _infer_team_id_from_path(self, config_path: Path) -> str:
        """
        Infer team ID from directory path structure.
        
        Args:
            config_path: Path to team configuration directory
            
        Returns:
            Inferred team identifier
        """
        # If path is teams/some-team, use "some-team"
        if config_path.parent.name == "teams":
            return config_path.name
        
        # Otherwise use the directory name
        return config_path.name