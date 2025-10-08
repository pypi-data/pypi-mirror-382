"""DBUtils wrapper for local development."""

import sys
import os
from typing import Optional


def _is_databricks_runtime() -> bool:
    """Check if running on Databricks runtime."""
    return 'dbruntime' in sys.modules or 'DBR_VERSION' in sys.modules


def _get_native_dbutils():
    """Get native dbutils if available."""
    try:
        import IPython
        return IPython.get_ipython().user_ns.get('dbutils')
    except:
        return None


class DBUtilsWrapper:
    """Wrapper for dbutils that works locally and on Databricks."""

    def __init__(self):
        """Initialize dbutils wrapper."""
        self._workspace_client: Optional[object] = None
        self._native_dbutils = None
        self._fs = None
        self._secrets = None

        if _is_databricks_runtime():
            self._native_dbutils = _get_native_dbutils()
        else:
            self._init_local()

    def _init_local(self):
        """Initialize local dbutils using WorkspaceClient."""
        if self._workspace_client:
            return

        try:
            from databricks.sdk import WorkspaceClient

            # Try to create WorkspaceClient with available config
            # It will use environment variables or CLI config automatically
            self._workspace_client = WorkspaceClient()
        except Exception:
            # Will be initialized later when credentials are available
            pass

    def _get_utility(self, name: str):
        """Get a dbutils utility by name."""
        if self._native_dbutils:
            return getattr(self._native_dbutils, name)

        if not self._workspace_client:
            self._init_local()

        if self._workspace_client:
            return getattr(self._workspace_client.dbutils, name)

        return None

    @property
    def fs(self):
        """Get filesystem utilities."""
        if not self._fs:
            self._fs = self._get_utility('fs')
        return self._fs

    @property
    def secrets(self):
        """Get secrets utilities."""
        if not self._secrets:
            self._secrets = self._get_utility('secrets')
        return self._secrets


# Global instance
_dbutils_instance: Optional[DBUtilsWrapper] = None


def get_dbutils() -> DBUtilsWrapper:
    """Get or create the global dbutils instance."""
    global _dbutils_instance
    if _dbutils_instance is None:
        _dbutils_instance = DBUtilsWrapper()
    return _dbutils_instance