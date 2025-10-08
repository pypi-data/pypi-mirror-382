"""Databricks CLI authentication integration."""

import os
from configparser import ConfigParser
from pathlib import Path
from typing import Optional, Dict
from ..models.databricks_config import DatabricksConfig


class DatabricksCLIAuth:
    """Handles authentication using Databricks CLI configuration."""

    DEFAULT_CONFIG_PATH = "~/.databrickscfg"

    @classmethod
    def load_from_cli(cls, profile: str = "DEFAULT") -> Optional[DatabricksConfig]:
        """Load configuration from Databricks CLI config file."""
        config_path = Path(cls.DEFAULT_CONFIG_PATH).expanduser()

        if not config_path.exists():
            return None

        parser = ConfigParser()
        parser.read(config_path)

        if profile not in parser:
            return None

        section = parser[profile]

        # Handle different authentication methods
        auth_type = "pat"  # Default
        client_id = None
        client_secret = None

        if section.get("auth_type"):
            auth_type = section.get("auth_type")

        if auth_type in ["oauth", "sp"]:
            client_id = section.get("client_id")
            client_secret = section.get("client_secret")

        return DatabricksConfig(
            host=section.get("host", ""),
            token=section.get("token", ""),
            auth_type=auth_type,
            warehouse_id=section.get("warehouse_id"),
            cluster_id=section.get("cluster_id"),
            profile=profile,
            client_id=client_id,
            client_secret=client_secret
        )

    @classmethod
    def load_from_env(cls) -> Optional[DatabricksConfig]:
        """Load configuration from environment variables."""
        host = os.getenv("DATABRICKS_HOST")
        token = os.getenv("DATABRICKS_TOKEN") or os.getenv("DATABRICKS_PAT")
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        cluster_id = os.getenv("DATABRICKS_CLUSTER_ID")
        http_path = os.getenv("DATABRICKS_HTTP_PATH")

        if not host:
            return None

        # Extract warehouse ID from HTTP path if provided
        if http_path and not warehouse_id:
            # Format: /sql/1.0/warehouses/{warehouse_id}
            parts = http_path.split("/")
            if len(parts) >= 5 and parts[1] == "sql" and parts[3] == "warehouses":
                warehouse_id = parts[4]

        return DatabricksConfig(
            host=host,
            token=token,
            auth_type="pat",
            warehouse_id=warehouse_id,
            cluster_id=cluster_id
        )

    @classmethod
    def load_config(cls, profile: Optional[str] = None) -> Optional[DatabricksConfig]:
        """Load configuration from environment or CLI config."""
        # Environment variables take precedence
        config = cls.load_from_env()
        if config:
            return config

        # Fall back to CLI config
        return cls.load_from_cli(profile or "DEFAULT")

    @classmethod
    def validate_auth(cls, config: DatabricksConfig) -> bool:
        """Validate authentication configuration."""
        if not config:
            return False

        if not config.host:
            return False

        if config.auth_type == "pat" and not config.token:
            return False

        return True