"""MCP resources for procedure access"""

import logging
from pathlib import Path
from typing import Callable

from ..config.settings import settings
from ..utils.errors import ProjectNotFoundError
from ..utils.parser import ProcedureParser

logger = logging.getLogger(__name__)


def register_resources(mcp: any) -> None:
    """Register procedure resources with MCP server

    Args:
        mcp: FastMCP server instance
    """

    @mcp.resource("engmanager://procedures/{project}")
    async def get_procedure(project: str) -> str:
        """Get the full procedure file for a project

        Args:
            project: Project name

        Returns:
            Complete procedure content with variables substituted

        Examples:
            engmanager://procedures/trowel
            engmanager://procedures/utility-blue
        """
        try:
            # Load project configuration
            try:
                config = settings.load_project_config(project)
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

            # Substitute variables and return
            try:
                return parser.substitute_variables()
            except Exception as e:
                # If substitution fails, return raw content with warning
                logger.warning(f"Variable substitution failed: {e}")
                return f"⚠️  Variable substitution incomplete\n\n{content}"

        except Exception as e:
            logger.error(f"Error in get_procedure resource: {e}")
            return f"❌ Error loading procedure: {str(e)}"

    @mcp.resource("engmanager://config/{project}")
    async def get_config(project: str) -> str:
        """Get the configuration for a project

        Args:
            project: Project name

        Returns:
            Project configuration as formatted text

        Examples:
            engmanager://config/trowel
            engmanager://config/utility-blue
        """
        try:
            # Load project configuration
            try:
                config = settings.load_project_config(project)
            except ProjectNotFoundError as e:
                return f"❌ {str(e)}"

            result = f"# Configuration: {project}\n\n"
            result += f"**Procedure file:** {config['procedure_file']}\n\n"

            if config.get('variables'):
                result += "## Template Variables\n\n"
                result += "```json\n"
                import json
                result += json.dumps(config['variables'], indent=2)
                result += "\n```\n"

            return result

        except Exception as e:
            logger.error(f"Error in get_config resource: {e}")
            return f"❌ Error loading config: {str(e)}"

    @mcp.resource("engmanager://templates")
    async def get_templates() -> str:
        """Get information about available template variables

        Returns:
            Documentation of template variable syntax and examples
        """
        return """# Template Variables

Engineering Manager MCP supports template variables in procedure files.

## Syntax

Use curly braces with UPPERCASE variable names:

```markdown
## Branch Creation

Create a branch for {PROJECT_NAME}:
```bash
git checkout -b feature/my-feature-{ISSUE_NUMBER}
git push -u origin feature/my-feature-{ISSUE_NUMBER}
```
```

## Common Variables

- `{PROJECT_NAME}` - Name of the project
- `{REPO_OWNER}` - GitHub repository owner
- `{REPO_NAME}` - GitHub repository name
- `{ISSUE_NUMBER}` - Current issue number
- `{BRANCH_PREFIX}` - Branch prefix (feature/fix/refactor)
- `{DEFAULT_BRANCH}` - Default branch name (usually main)

## Custom Variables

Define custom variables in your project's config file:

```json
{
  "project_name": "myproject",
  "procedure_file": "myproject-workflow.md",
  "variables": {
    "PROJECT_NAME": "myproject",
    "REPO_OWNER": "username",
    "REPO_NAME": "repository",
    "DEFAULT_BRANCH": "main",
    "CUSTOM_VAR": "custom_value"
  }
}
```

## Configuration Files

Place project configuration files in:
- `./procedures/<project>-config.json`
- `~/.config/engmanager-mcp/<project>-config.json`
- `/etc/engmanager-mcp/<project>-config.json`

The first matching file will be used.
"""

    @mcp.resource("engmanager://projects")
    async def list_projects() -> str:
        """List all available projects

        Returns:
            List of configured projects
        """
        try:
            projects = settings.list_available_projects()

            if not projects:
                return (
                    "# No Projects Configured\n\n"
                    "Add project configurations to one of these directories:\n\n"
                    + "\n".join(f"- `{path}`" for path in settings.config_paths)
                    + "\n\nConfiguration files should be named: `<project>-config.json`"
                )

            result = "# Available Projects\n\n"
            for project in projects:
                try:
                    config = settings.load_project_config(project)
                    result += f"## {project}\n\n"
                    result += f"- **Procedure:** {config['procedure_file']}\n"

                    # Check if procedure file exists
                    procedure_file = settings.find_procedure_file(config['procedure_file'])
                    if procedure_file:
                        result += f"- **Status:** ✅ Ready\n"
                    else:
                        result += f"- **Status:** ❌ Procedure file missing\n"

                    result += "\n"
                except Exception as e:
                    result += f"## {project}\n\n"
                    result += f"- **Status:** ❌ Configuration error: {e}\n\n"

            if settings.default_project:
                result += f"\n**Default project:** {settings.default_project}\n"

            return result

        except Exception as e:
            logger.error(f"Error in list_projects resource: {e}")
            return f"❌ Error listing projects: {str(e)}"

    logger.info("Procedure resources registered")
