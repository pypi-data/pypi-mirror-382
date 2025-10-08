"""Error handler for connection and operation failures."""

import time
from typing import Callable, Any, Optional
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Handles errors with retry logic and helpful messages."""

    @staticmethod
    def with_retry(max_retries: int = 3, backoff_factor: float = 2.0):
        """Decorator for retrying operations with exponential backoff."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                last_exception = None

                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_retries - 1:
                            wait_time = backoff_factor ** attempt
                            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds...")
                            time.sleep(wait_time)
                        else:
                            logger.error(f"All {max_retries} attempts failed: {e}")

                # All retries exhausted
                if last_exception:
                    raise last_exception

            return wrapper
        return decorator

    @staticmethod
    def handle_connection_error(error: Exception) -> str:
        """Generate helpful error message for connection failures."""
        error_str = str(error).lower()

        if "authentication" in error_str or "unauthorized" in error_str:
            return (
                "Authentication failed. Please check:\n"
                "1. Your Databricks token is valid\n"
                "2. The token has not expired\n"
                "3. You have the necessary permissions\n"
                "Run 'databricks configure --token' to update credentials"
            )

        if "connection" in error_str or "timeout" in error_str:
            return (
                "Connection failed. Please check:\n"
                "1. Your network connection\n"
                "2. The Databricks workspace URL is correct\n"
                "3. Any VPN or firewall settings\n"
                "4. The workspace is accessible from your location"
            )

        if "not found" in error_str:
            return (
                "Resource not found. Please check:\n"
                "1. The table/schema/catalog name is correct\n"
                "2. You have access to the resource\n"
                "3. The resource exists in the specified workspace"
            )

        if "permission" in error_str or "denied" in error_str:
            return (
                "Permission denied. Please check:\n"
                "1. You have the necessary Unity Catalog permissions\n"
                "2. The table is accessible with your credentials\n"
                "3. Your workspace has Unity Catalog enabled"
            )

        return f"Operation failed: {error}\nPlease check your configuration and try again."

    @staticmethod
    def safe_execute(func: Callable, *args, **kwargs) -> tuple[bool, Any, Optional[str]]:
        """Safely execute a function and return success status, result, and error message."""
        try:
            result = func(*args, **kwargs)
            return True, result, None
        except Exception as e:
            error_msg = ErrorHandler.handle_connection_error(e)
            logger.error(error_msg)
            return False, None, error_msg