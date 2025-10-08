"""Configuration settings for Engineering Manager MCP"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..utils.errors import ConfigurationError, ProjectNotFoundError

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Main settings for Engineering Manager MCP"""

    model_config = SettingsConfigDict(
        env_prefix="ENGMANAGER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server configuration
    mcp_server_name: str = Field(
        default="engmanager-mcp",
        description="MCP server name"
    )
    mcp_server_version: str = Field(
        default="1.0.0",
        description="MCP server version"
    )
    mcp_transport: str = Field(
        default="stdio",
        description="MCP transport (stdio or http)"
    )
    mcp_log_level: str = Field(
        default="INFO",
        description="Logging level"
    )

    # Project configuration
    default_project: Optional[str] = Field(
        default=None,
        description="Default project to use when none specified"
    )
    procedures_dir: str = Field(
        default="procedures",
        description="Directory containing procedure files"
    )
    config_paths: List[str] = Field(
        default_factory=lambda: [
            "./procedures",
            "~/.config/engmanager-mcp",
            "/etc/engmanager-mcp",
        ],
        description="Paths to search for project configurations"
    )

    @property
    def expanded_config_paths(self) -> List[Path]:
        """Get expanded configuration paths"""
        paths = []
        for path_str in self.config_paths:
            expanded = Path(path_str).expanduser().resolve()
            if expanded.exists():
                paths.append(expanded)
        return paths

    def find_project_config(self, project_name: str) -> Optional[Path]:
        """Find configuration file for a project

        Args:
            project_name: Name of the project

        Returns:
            Path to config file or None if not found
        """
        config_filename = f"{project_name}-config.json"

        for config_path in self.expanded_config_paths:
            config_file = config_path / config_filename
            if config_file.exists():
                logger.info(f"Found project config: {config_file}")
                return config_file

        logger.warning(f"No config found for project: {project_name}")
        return None

    def load_project_config(self, project_name: str) -> Dict:
        """Load project configuration

        Args:
            project_name: Name of the project

        Returns:
            Project configuration dictionary

        Raises:
            ProjectNotFoundError: If project config not found
            ConfigurationError: If config is invalid
        """
        config_file = self.find_project_config(project_name)
        if not config_file:
            raise ProjectNotFoundError(
                f"Project configuration not found: {project_name}. "
                f"Searched in: {', '.join(str(p) for p in self.expanded_config_paths)}"
            )

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Validate required fields
            if 'project_name' not in config:
                config['project_name'] = project_name

            if 'procedure_file' not in config:
                raise ConfigurationError(
                    f"Project config missing 'procedure_file': {config_file}"
                )

            # Set defaults
            config.setdefault('variables', {})

            logger.info(f"Loaded project config for: {project_name}")
            return config

        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in config file {config_file}: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load project config {config_file}: {e}")

    def find_procedure_file(self, filename: str) -> Optional[Path]:
        """Find a procedure file

        Args:
            filename: Name of the procedure file

        Returns:
            Path to procedure file or None if not found
        """
        # Check in procedures directory first
        procedures_path = Path(self.procedures_dir).expanduser().resolve()
        if procedures_path.exists():
            procedure_file = procedures_path / filename
            if procedure_file.exists():
                return procedure_file

        # Check in config paths
        for config_path in self.expanded_config_paths:
            procedure_file = config_path / filename
            if procedure_file.exists():
                return procedure_file

        return None

    def list_available_projects(self) -> List[str]:
        """List all available project configurations

        Returns:
            List of project names
        """
        projects = set()

        for config_path in self.expanded_config_paths:
            if not config_path.exists():
                continue

            for config_file in config_path.glob("*-config.json"):
                # Extract project name from filename (remove -config.json suffix)
                project_name = config_file.stem.replace("-config", "")
                projects.add(project_name)

        return sorted(list(projects))


# Global settings instance
settings = Settings()
