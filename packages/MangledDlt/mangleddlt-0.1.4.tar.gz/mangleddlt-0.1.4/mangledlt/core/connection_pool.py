"""Connection pooling for Unity Catalog connections."""

from typing import List, Optional
from datetime import datetime, timedelta
import threading
from ..models.unity_catalog_connection import UnityCatalogConnection
from ..models.databricks_config import DatabricksConfig


class ConnectionPool:
    """Manages a pool of Unity Catalog connections."""

    def __init__(self, config: DatabricksConfig, max_connections: int = 5):
        """Initialize the connection pool."""
        self.config = config
        self.max_connections = max_connections
        self.connections: List[UnityCatalogConnection] = []
        self.available_connections: List[UnityCatalogConnection] = []
        self.lock = threading.Lock()

    def get_connection(self) -> UnityCatalogConnection:
        """Get an available connection from the pool."""
        with self.lock:
            # Reuse existing connection if available
            while self.available_connections:
                conn = self.available_connections.pop()

                # Check if connection is still valid
                if conn.is_connected:
                    # Check if not stale (used within last 5 minutes)
                    if conn.last_used and datetime.now() - conn.last_used < timedelta(minutes=5):
                        return conn
                    else:
                        # Reconnect if stale
                        try:
                            conn.disconnect()
                            conn.connect()
                            return conn
                        except:
                            pass

                # Remove invalid connection
                if conn in self.connections:
                    self.connections.remove(conn)

            # Create new connection if under limit
            if len(self.connections) < self.max_connections:
                conn = UnityCatalogConnection(self.config)
                conn.connect()
                self.connections.append(conn)
                return conn

            # Wait for a connection to become available
            # In production, this would use a condition variable
            raise RuntimeError("Connection pool exhausted")

    def return_connection(self, conn: UnityCatalogConnection):
        """Return a connection to the pool."""
        with self.lock:
            if conn in self.connections and conn.is_connected:
                if conn not in self.available_connections:
                    self.available_connections.append(conn)

    def close_all(self):
        """Close all connections in the pool."""
        with self.lock:
            for conn in self.connections:
                try:
                    conn.disconnect()
                except:
                    pass
            self.connections.clear()
            self.available_connections.clear()

    def get_stats(self) -> dict:
        """Get pool statistics."""
        with self.lock:
            return {
                "total_connections": len(self.connections),
                "available_connections": len(self.available_connections),
                "in_use_connections": len(self.connections) - len(self.available_connections),
                "max_connections": self.max_connections
            }