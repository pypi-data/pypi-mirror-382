"""UnityCatalogConnection entity for managing UC connections."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any
from ..models.databricks_config import DatabricksConfig


@dataclass
class UnityCatalogConnection:
    """Manages connection to Unity Catalog via databricks-sql-connector."""

    config: DatabricksConfig
    connection: Optional[Any] = None
    is_connected: bool = False
    last_used: Optional[datetime] = None
    retry_count: int = 0

    def connect(self):
        """Establish connection to Unity Catalog."""
        from databricks import sql
        import os

        try:
            # Support environment variables
            host = self.config.host or os.getenv("DATABRICKS_HOST")
            http_path = f"/sql/1.0/warehouses/{self.config.warehouse_id}" if self.config.warehouse_id else os.getenv("DATABRICKS_HTTP_PATH")
            token = self.config.token or os.getenv("DATABRICKS_PAT") or os.getenv("DATABRICKS_TOKEN")

            self.connection = sql.connect(
                server_hostname=host.replace("https://", "").replace("http://", ""),
                http_path=http_path,
                access_token=token
            )
            self.is_connected = True
            self.last_used = datetime.now()
            self.retry_count = 0
        except Exception as e:
            self.is_connected = False
            self.retry_count += 1
            raise ConnectionError(f"Failed to connect to Unity Catalog: {e}")

    def disconnect(self):
        """Close the connection."""
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
        self.connection = None
        self.is_connected = False

    def execute_query(self, query: str) -> Any:
        """Execute a SQL query."""
        if not self.is_connected:
            self.connect()

        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            self.last_used = datetime.now()
            return result
        finally:
            cursor.close()