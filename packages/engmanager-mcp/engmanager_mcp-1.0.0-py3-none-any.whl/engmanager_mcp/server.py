"""Main Engineering Manager MCP server entry point"""

import asyncio
import logging

from mcp.server.fastmcp import FastMCP

from .config.settings import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.mcp_log_level.upper()))
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name=settings.mcp_server_name,
)


def register_components() -> None:
    """Register all tools and resources"""

    # Register workflow tools
    try:
        from .tools import workflow as workflow_tools
        workflow_tools.register_tools(mcp)
        logger.info("Workflow tools registered")
    except ImportError as e:
        logger.error(f"Failed to register workflow tools: {e}")
        raise

    # Register procedure resources
    try:
        from .resources import procedures as procedure_resources
        procedure_resources.register_resources(mcp)
        logger.info("Procedure resources registered")
    except ImportError as e:
        logger.error(f"Failed to register procedure resources: {e}")
        raise


def main() -> None:
    """Main entry point"""
    try:
        logger.info(f"Starting {settings.mcp_server_name} v{settings.mcp_server_version}")
        logger.info(f"Transport: {settings.mcp_transport}")
        logger.info(f"Log level: {settings.mcp_log_level}")

        # Log configuration
        if settings.default_project:
            logger.info(f"Default project: {settings.default_project}")

        available_projects = settings.list_available_projects()
        if available_projects:
            logger.info(f"Available projects: {', '.join(available_projects)}")
        else:
            logger.warning("No projects configured - add project configs to use the server")

        # Register all components
        register_components()

        # Start server based on transport
        if settings.mcp_transport == "stdio":
            logger.info("Starting with stdio transport")
            mcp.run()
        elif settings.mcp_transport == "http":
            logger.info("Starting with HTTP transport on localhost:8000")
            mcp.run_server(host="localhost", port=8000)
        else:
            raise ValueError(f"Unsupported transport: {settings.mcp_transport}")

    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        raise


if __name__ == "__main__":
    main()
