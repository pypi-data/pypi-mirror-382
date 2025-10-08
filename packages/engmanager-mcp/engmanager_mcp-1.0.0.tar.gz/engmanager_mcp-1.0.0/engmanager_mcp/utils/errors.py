"""Custom exception classes for Engineering Manager MCP"""


class EngManagerError(Exception):
    """Base exception for Engineering Manager MCP"""
    pass


class ConfigurationError(EngManagerError):
    """Raised when configuration is invalid or missing"""
    pass


class ProcedureNotFoundError(EngManagerError):
    """Raised when requested procedure file cannot be found"""
    pass


class TemplateParsingError(EngManagerError):
    """Raised when template parsing fails"""
    pass


class ProjectNotFoundError(EngManagerError):
    """Raised when specified project configuration is not found"""
    pass


class InvalidStepError(EngManagerError):
    """Raised when requesting an invalid workflow step"""
    pass
