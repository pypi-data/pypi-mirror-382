"""MangledDLT - Local Databricks Development Bridge."""

from typing import Optional, Dict, Any
import logging
from .config import Config
from .models.databricks_config import DatabricksConfig
from .models.unity_catalog_connection import UnityCatalogConnection
from .core.interceptor import SparkInterceptor
from .core.session import SparkSessionWrapper
from .connectors.unity_catalog import UnityCatalogConnector
from .utils.error_handler import ErrorHandler
from .exceptions import (
    ConfigError,
    AuthError,
    ConnectionError,
    TableNotFoundError,
    PermissionError,
    InvalidReferenceError
)

# Import display module to auto-patch DataFrame
from .core import display

# Import dlt module for DLT compatibility
from . import dlt

# Import dbutils module for dbutils compatibility
from . import dbutils

__version__ = "0.1.4"
__all__ = [
    "MangledDLT",
    "Config",
    "ConfigError",
    "AuthError",
    "ConnectionError",
    "TableNotFoundError",
    "PermissionError",
    "InvalidReferenceError",
    "dlt",
    "dbutils"
]

logger = logging.getLogger(__name__)


class MangledDLT:
    """Main class for MangledDLT - enables local Databricks development."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize MangledDLT with optional configuration."""
        # Load configuration
        if config:
            self.config = Config(config)
        else:
            self.config = Config.auto_detect()

        # Initialize components
        self.interceptor = SparkInterceptor()
        self.session_wrapper = SparkSessionWrapper()
        self.connection: Optional[UnityCatalogConnection] = None
        self.connector: Optional[UnityCatalogConnector] = None
        self._enabled = False

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging for MangledDLT."""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    def enable(self) -> bool:
        """Enable Spark operation interception."""
        try:
            # Check if running on Databricks
            if self.session_wrapper.is_databricks_runtime():
                logger.info("Running on Databricks cluster - MangledDLT not enabled")
                return False

            # Get Databricks configuration
            db_config = self.config.get_databricks_config()
            if not db_config:
                db_config = DatabricksConfig.from_env() if hasattr(DatabricksConfig, 'from_env') else None

            if not db_config:
                # Try to create from environment
                from .auth.databricks_cli import DatabricksCLIAuth
                db_config = DatabricksCLIAuth.load_config()

            if not db_config:
                raise ConfigError("No valid configuration found. Please configure Databricks CLI or set environment variables.")

            # Create Unity Catalog connection
            self.connection = UnityCatalogConnection(db_config)
            self.connector = UnityCatalogConnector(self.connection)

            # Test connection
            success, _, error_msg = ErrorHandler.safe_execute(self.connection.connect)
            if not success:
                raise ConnectionError(f"Failed to connect to Unity Catalog: {error_msg}")

            # Configure cache
            if self.config.cache_enabled:
                self.interceptor.cache.max_size = self.config.cache_max_size
                self.interceptor.cache.ttl_seconds = self.config.cache_ttl

            # Enable interception
            self.interceptor.enable(self.connection)
            self.session_wrapper.enable_interception(self.interceptor)
            self._enabled = True

            logger.info(f"MangledDLT enabled - connected to {db_config.host}")
            return True

        except Exception as e:
            logger.error(f"Failed to enable MangledDLT: {e}")
            self._enabled = False
            return False

    def disable(self) -> bool:
        """Disable Spark operation interception."""
        try:
            # Disable interception
            self.interceptor.disable()
            self.session_wrapper.disable_interception()

            # Disconnect from Unity Catalog
            if self.connection:
                self.connection.disconnect()
                self.connection = None

            self._enabled = False
            logger.info("MangledDLT disabled")
            return True

        except Exception as e:
            logger.error(f"Failed to disable MangledDLT: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get current connection status."""
        status = {
            "connected": self._enabled and self.connection and self.connection.is_connected,
            "enabled": self._enabled,
            "interceptor_enabled": self.interceptor.enabled,
        }

        if self.connection and self.connection.config:
            status["workspace"] = self.connection.config.host
            status["auth_type"] = self.connection.config.auth_type
            status["profile"] = self.connection.config.profile

        if self.connection:
            status["last_used"] = str(self.connection.last_used) if self.connection.last_used else None
            status["retry_count"] = self.connection.retry_count

        return status

    def clear_cache(self) -> bool:
        """Clear the query cache."""
        try:
            self.interceptor.cache.clear()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = self.interceptor.cache.get_stats()

        # Add memory estimation
        if stats["entries"] > 0:
            # Rough estimation: 10MB per cached DataFrame
            stats["memory_mb"] = stats["entries"] * 10

        return stats

    def test_connection(self) -> bool:
        """Test the Unity Catalog connection."""
        if not self.connector:
            return False

        return self.connector.test_connection()

    def __enter__(self):
        """Context manager entry."""
        self.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disable()