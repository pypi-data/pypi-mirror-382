"""DatabricksConfig entity for storing connection configuration."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabricksConfig:
    """Stores configuration for connecting to a Databricks workspace."""

    host: str
    auth_type: str = "pat"
    token: Optional[str] = None
    cluster_id: Optional[str] = None
    warehouse_id: Optional[str] = None
    profile: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.host:
            raise ValueError("Host is required")

        if not self.host.startswith("https://") and not self.host.startswith("http://"):
            self.host = f"https://{self.host}"

        if self.auth_type == "pat" and not self.token:
            raise ValueError("Token is required for PAT authentication")

        if self.auth_type == "oauth" and (not self.client_id or not self.client_secret):
            raise ValueError("Client ID and secret required for OAuth")

        if not self.warehouse_id and not self.cluster_id:
            raise ValueError("Either warehouse_id or cluster_id must be provided")

    def validate(self) -> bool:
        """Validate the configuration."""
        try:
            if self.auth_type == "pat":
                return bool(self.token and len(self.token) >= 10)
            elif self.auth_type == "oauth":
                return bool(self.client_id and self.client_secret)
            elif self.auth_type == "sp":
                return bool(self.client_id and self.client_secret)
            return False
        except Exception:
            return False