"""Custom exceptions for MangledDLT."""


class MangledDLTError(Exception):
    """Base exception for all MangledDLT errors."""
    pass


class ConfigError(MangledDLTError):
    """Raised when configuration is invalid or missing."""
    pass


class AuthError(MangledDLTError):
    """Raised when authentication fails."""
    pass


class ConnectionError(MangledDLTError):
    """Raised when connection to Databricks fails."""
    pass


class TableNotFoundError(MangledDLTError):
    """Raised when a table is not found in Unity Catalog."""
    pass


class PermissionError(MangledDLTError):
    """Raised when user lacks permissions for an operation."""
    pass


class InvalidReferenceError(MangledDLTError):
    """Raised when a table reference is invalid."""
    pass