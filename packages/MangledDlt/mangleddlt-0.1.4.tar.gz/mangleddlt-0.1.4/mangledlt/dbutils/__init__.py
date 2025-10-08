"""DBUtils compatibility module for MangledDLT."""

import sys


def __getattr__(name):
    """Lazy attribute access for dbutils properties."""
    if name in ('fs', 'secrets'):
        from .dbutils_wrapper import get_dbutils
        dbutils_instance = get_dbutils()
        return getattr(dbutils_instance, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = ['fs', 'secrets']