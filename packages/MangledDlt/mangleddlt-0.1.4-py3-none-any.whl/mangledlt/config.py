"""Configuration management for MangledDLT."""

from typing import Optional, Dict, Any
from pathlib import Path
import os
from .models.databricks_config import DatabricksConfig
from .auth.databricks_cli import DatabricksCLIAuth


class Config:
    """Configuration management for MangledDLT."""

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """Initialize with optional configuration dictionary."""
        if config_dict:
            self._config = DatabricksConfig(
                host=config_dict.get("host", ""),
                auth_type=config_dict.get("auth_type", "pat"),
                token=config_dict.get("token"),
                cluster_id=config_dict.get("cluster_id"),
                warehouse_id=config_dict.get("warehouse_id"),
                profile=config_dict.get("profile"),
                client_id=config_dict.get("client_id"),
                client_secret=config_dict.get("client_secret")
            )
        else:
            self._config = None

        # Cache settings
        self.cache_enabled = config_dict.get("cache_enabled", True) if config_dict else True
        self.cache_ttl = config_dict.get("cache_ttl", 300) if config_dict else 300
        self.cache_max_size = config_dict.get("cache_max_size", 100) if config_dict else 100

    @classmethod
    def from_file(cls, path: str = "~/.databrickscfg", profile: str = "DEFAULT") -> "Config":
        """Load configuration from Databricks CLI config file."""
        config = DatabricksCLIAuth.load_from_cli(profile)
        if not config:
            raise ValueError(f"Could not load profile {profile} from {path}")

        return cls({
            "host": config.host,
            "auth_type": config.auth_type,
            "token": config.token,
            "cluster_id": config.cluster_id,
            "warehouse_id": config.warehouse_id,
            "profile": profile
        })

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        config = DatabricksCLIAuth.load_from_env()
        if not config:
            raise ValueError("Could not load configuration from environment variables")

        return cls({
            "host": config.host,
            "auth_type": config.auth_type,
            "token": config.token,
            "cluster_id": config.cluster_id,
            "warehouse_id": config.warehouse_id
        })

    @classmethod
    def auto_detect(cls, profile: Optional[str] = None) -> "Config":
        """Auto-detect configuration from environment or CLI."""
        # Try environment first
        try:
            return cls.from_env()
        except:
            pass

        # Try CLI config
        try:
            return cls.from_file(profile=profile or "DEFAULT")
        except:
            pass

        # Return empty config
        return cls()

    def validate(self) -> bool:
        """Validate the configuration."""
        if not self._config:
            return False
        return self._config.validate()

    def get_databricks_config(self) -> Optional[DatabricksConfig]:
        """Get the underlying DatabricksConfig."""
        return self._config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = {
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "cache_max_size": self.cache_max_size
        }

        if self._config:
            result.update({
                "host": self._config.host,
                "auth_type": self._config.auth_type,
                "token": self._config.token,
                "cluster_id": self._config.cluster_id,
                "warehouse_id": self._config.warehouse_id,
                "profile": self._config.profile
            })

        return result