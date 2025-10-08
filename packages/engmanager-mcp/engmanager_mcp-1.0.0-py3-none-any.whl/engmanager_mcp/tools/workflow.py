"""MCP tools for workflow guidance"""

import logging
from pathlib import Path
from typing import Callable, Dict, List, Optional

from ..config.settings import settings
from ..utils.errors import InvalidStepError, ProcedureNotFoundError, ProjectNotFoundError
from ..utils.parser import ProcedureParser

logger = logging.getLogger(__name__)


def register_tools(mcp: any) -> None:
    """Register workflow tools with MCP server

    Args:
        mcp: FastMCP server instance
    """

    @mcp.tool()
    async def get_next_step(
        project: Optional[str] = None,
        current_step: Optional[int] = None
    ) -> str:
        """Get the next step in the workflow

        Retrieves the next step in the development workflow for the specified project.
        If current_step is provided, returns the step immediately following it.
        If current_step is not provided, returns step 1 (start of workflow).

        Args:
            project: Project name (uses default if not specified)
            current_step: Current step number (optional, defaults to 0 to get step 1)

        Returns:
            Formatted next step instructions

        Examples:
            get_next_step(project="trowel")
            get_next_step(project="trowel", current_step=3)
        """
        try:
            # Determine project
            project_name = project or settings.default_project
            if not project_name:
                return (
                    "❌ No project specified and no default project configured.\n\n"
                    "Please specify a project name or set ENGMANAGER_DEFAULT_PROJECT.\n\n"
                    f"Available projects: {', '.join(settings.list_available_projects())}"
                )

            # Load project configuration
            try:
                config = settings.load_project_config(project_name)
            except ProjectNotFoundError as e:
                return f"❌ {str(e)}"

            # Find procedure file
            procedure_file = settings.find_procedure_file(config['procedure_file'])
            if not procedure_file:
                return (
                    f"❌ Procedure file not found: {config['procedure_file']}\n\n"
                    f"Searched in: {settings.procedures_dir} and config paths"
                )

            # Load and parse procedure
            with open(procedure_file, 'r') as f:
                content = f.read()

            parser = ProcedureParser(content, config.get('variables', {}))

            # Get next step
            if current_step is None:
                current_step = 0

            if current_step == 0:
                # Get first step
                step = parser.get_step(1)
                if not step:
                    return "❌ No steps found in procedure file"
                title, content = step
                return parser.format_step(1, title, content)
            else:
                # Get next step
                next_step = parser.get_next_step(current_step)
                if not next_step:
                    return (
                        f"✅ Workflow complete! You've finished step {current_step}.\n\n"
                        "No more steps in this procedure."
                    )
                num, title, content = next_step
                return parser.format_step(num, title, content)

        except Exception as e:
            logger.error(f"Error in get_next_step: {e}")
            return f"❌ Error retrieving next step: {str(e)}"

    @mcp.tool()
    async def get_workflow_section(
        section: str,
        project: Optional[str] = None
    ) -> str:
        """Get a specific section from the workflow

        Retrieves a named section from the project's workflow procedure.
        Useful for jumping to specific parts of the workflow or getting
        reference information.

        Args:
            section: Section title to retrieve
            project: Project name (uses default if not specified)

        Returns:
            Section content

        Examples:
            get_workflow_section(section="Error Recovery Protocols", project="trowel")
            get_workflow_section(section="Quality Gates")
        """
        try:
            # Determine project
            project_name = project or settings.default_project
            if not project_name:
                return (
                    "❌ No project specified and no default project configured.\n\n"
                    f"Available projects: {', '.join(settings.list_available_projects())}"
                )

            # Load project configuration
            try:
                config = settings.load_project_config(project_name)
            except ProjectNotFoundError as e:
                return f"❌ {str(e)}"

            # Find procedure file
            procedure_file = settings.find_procedure_file(config['procedure_file'])
            if not procedure_file:
                return f"❌ Procedure file not found: {config['procedure_file']}"

            # Load and parse procedure
            with open(procedure_file, 'r') as f:
                content = f.read()

            parser = ProcedureParser(content, config.get('variables', {}))

            # Get section
            section_content = parser.get_section(section)
            if section_content is None:
                # Try to find similar sections
                matches = parser.find_section_by_keyword(section)
                if matches:
                    suggestions = "\n".join([f"- {title}" for title, _ in matches[:5]])
                    return (
                        f"❌ Section not found: {section}\n\n"
                        f"Did you mean one of these?\n{suggestions}"
                    )
                return f"❌ Section not found: {section}"

            return f"## {section}\n\n{section_content}"

        except Exception as e:
            logger.error(f"Error in get_workflow_section: {e}")
            return f"❌ Error retrieving section: {str(e)}"

    @mcp.tool()
    async def list_workflow_steps(project: Optional[str] = None) -> str:
        """List all steps in the workflow

        Provides an overview of all numbered steps in the project's workflow.

        Args:
            project: Project name (uses default if not specified)

        Returns:
            List of all workflow steps

        Examples:
            list_workflow_steps(project="trowel")
            list_workflow_steps()
        """
        try:
            # Determine project
            project_name = project or settings.default_project
            if not project_name:
                return (
                    "❌ No project specified and no default project configured.\n\n"
                    f"Available projects: {', '.join(settings.list_available_projects())}"
                )

            # Load project configuration
            try:
                config = settings.load_project_config(project_name)
            except ProjectNotFoundError as e:
                return f"❌ {str(e)}"

            # Find procedure file
            procedure_file = settings.find_procedure_file(config['procedure_file'])
            if not procedure_file:
                return f"❌ Procedure file not found: {config['procedure_file']}"

            # Load and parse procedure
            with open(procedure_file, 'r') as f:
                content = f.read()

            parser = ProcedureParser(content, config.get('variables', {}))

            # Get all steps summary
            return parser.get_all_steps_summary()

        except Exception as e:
            logger.error(f"Error in list_workflow_steps: {e}")
            return f"❌ Error listing steps: {str(e)}"

    @mcp.tool()
    async def list_available_projects() -> str:
        """List all configured projects

        Shows all projects that have configuration files available.

        Returns:
            List of available project names

        Examples:
            list_available_projects()
        """
        try:
            projects = settings.list_available_projects()

            if not projects:
                return (
                    "❌ No projects configured.\n\n"
                    f"Add project configurations to one of these directories:\n"
                    + "\n".join(f"- {path}" for path in settings.config_paths)
                    + "\n\nConfiguration files should be named: <project>-config.json"
                )

            result = "# Available Projects\n\n"
            for project in projects:
                result += f"- **{project}**\n"

            if settings.default_project:
                result += f"\nDefault project: **{settings.default_project}**"

            return result

        except Exception as e:
            logger.error(f"Error in list_available_projects: {e}")
            return f"❌ Error listing projects: {str(e)}"

    @mcp.tool()
    async def get_project_info(project: str) -> str:
        """Get information about a specific project

        Shows configuration and available procedures for a project.

        Args:
            project: Project name

        Returns:
            Project information including variables and procedure file

        Examples:
            get_project_info(project="trowel")
        """
        try:
            # Load project configuration
            try:
                config = settings.load_project_config(project)
            except ProjectNotFoundError as e:
                return f"❌ {str(e)}"

            result = f"# Project: {config['project_name']}\n\n"
            result += f"**Procedure file:** {config['procedure_file']}\n\n"

            if config.get('variables'):
                result += "## Template Variables\n\n"
                for key, value in config['variables'].items():
                    result += f"- `{key}` = {value}\n"

            # Check if procedure file exists
            procedure_file = settings.find_procedure_file(config['procedure_file'])
            if procedure_file:
                result += f"\n✅ Procedure file found: {procedure_file}"
            else:
                result += f"\n❌ Procedure file not found: {config['procedure_file']}"

            return result

        except Exception as e:
            logger.error(f"Error in get_project_info: {e}")
            return f"❌ Error getting project info: {str(e)}"

    logger.info("Workflow tools registered")
