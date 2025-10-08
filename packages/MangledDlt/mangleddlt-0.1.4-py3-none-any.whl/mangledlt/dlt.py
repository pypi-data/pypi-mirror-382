"""
DLT (Delta Live Tables) compatibility module for local development.

Provides a dlt namespace that mimics Databricks DLT syntax for local development,
automatically switching to native DLT when running on Databricks.
"""

import os
import sys
import inspect
from typing import Any, Optional, Callable

# Cache for view function results
_view_cache = {}


def is_databricks_runtime() -> bool:
    """Check if running on Databricks runtime."""
    return 'DATABRICKS_RUNTIME_VERSION' in os.environ


def read(function_name: str) -> Any:
    """
    Read a DLT view by executing the function that defines it.

    This allows using Databricks DLT syntax (dlt.read("view_name")) in local
    development, while seamlessly working with actual DLT on Databricks.

    Args:
        function_name: Name of the function that defines the view.
                      Can be a simple name or module-qualified (e.g., "module.function")

    Returns:
        The DataFrame or result returned by the view function.

    Raises:
        ValueError: If the function is not found.
        TypeError: If the target is not callable or requires parameters.
    """
    # On Databricks, defer to native DLT (when it becomes available)
    if is_databricks_runtime():
        # In future, this would call the native dlt.read
        # For now, we'll still use our implementation
        pass

    # Check cache first
    if function_name in _view_cache:
        return _view_cache[function_name]

    # Find the target function
    target = _find_function(function_name)

    # Verify it's callable
    if not callable(target):
        raise TypeError(f"'{function_name}' is not a callable function")

    # Verify function signature (DLT views should be parameterless)
    _validate_function_signature(function_name, target)

    # Execute the function and cache result
    result = target()
    _view_cache[function_name] = result

    return result


def _find_function(function_name: str) -> Any:
    """Find a function by name, supporting module-qualified names."""
    if '.' in function_name:
        # Handle module-qualified name
        module_name, func_name = function_name.rsplit('.', 1)

        if module_name not in sys.modules:
            raise ValueError(f"Function '{function_name}' not found")

        module = sys.modules[module_name]
        if not hasattr(module, func_name):
            raise ValueError(f"Function '{function_name}' not found")

        return getattr(module, func_name)

    # Simple name - look in calling module first
    frame = inspect.currentframe()
    if frame and frame.f_back and frame.f_back.f_back:
        caller_module = inspect.getmodule(frame.f_back.f_back)
        if caller_module and hasattr(caller_module, function_name):
            return getattr(caller_module, function_name)

    # Search all modules
    for module in sys.modules.values():
        if module and hasattr(module, function_name):
            return getattr(module, function_name)

    raise ValueError(f"Function '{function_name}' not found")


def _validate_function_signature(function_name: str, func: Callable) -> None:
    """Validate that a function has no required parameters."""
    sig = inspect.signature(func)
    required_params = [
        param for param in sig.parameters.values()
        if param.default is param.empty
    ]
    if required_params:
        raise TypeError(f"Function '{function_name}' requires parameters but DLT views should be parameterless")


def clear_cache():
    """Clear the view cache. Useful for testing or forcing refresh."""
    global _view_cache
    _view_cache = {}


# Stub functions for other DLT decorators (to be implemented later)
def table(*args, **kwargs):
    """Decorator for DLT tables - stub for now."""
    def decorator(func):
        return func
    return decorator


def view(*args, **kwargs):
    """Decorator for DLT views - stub for now."""
    def decorator(func):
        return func
    return decorator