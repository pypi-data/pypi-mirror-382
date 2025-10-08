"""SparkInterceptor for redirecting Spark operations to Unity Catalog."""

from typing import Optional, Any, Dict
from ..models.unity_catalog_connection import UnityCatalogConnection
from ..models.catalog_reference import CatalogReference
from ..cache.query_cache import QueryCache


class SparkInterceptor:
    """Core interceptor that redirects Spark operations."""

    _instance = None

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the interceptor."""
        if not hasattr(self, 'initialized'):
            self.enabled = False
            self.connection: Optional[UnityCatalogConnection] = None
            self.cache = QueryCache()
            self.original_read = None
            self.original_readStream = None
            self.initialized = True

    def enable(self, connection: UnityCatalogConnection) -> bool:
        """Enable interception."""
        try:
            self.connection = connection
            self._patch_spark_methods()
            self.enabled = True
            return True
        except Exception:
            return False

    def disable(self) -> bool:
        """Disable interception."""
        try:
            self._restore_spark_methods()
            self.enabled = False
            if self.connection:
                self.connection.disconnect()
            return True
        except Exception:
            return False

    def _patch_spark_methods(self):
        """Monkey-patch Spark read methods."""
        try:
            import pyspark.sql
            # Store original methods
            if not self.original_read:
                self.original_read = pyspark.sql.DataFrameReader.table
                self.original_readStream = pyspark.sql.streaming.DataStreamReader.table if hasattr(pyspark.sql, 'streaming') else None

            # Replace with intercepted versions
            pyspark.sql.DataFrameReader.table = self._intercept_read_table
            if hasattr(pyspark.sql, 'streaming'):
                pyspark.sql.streaming.DataStreamReader.table = self._intercept_readstream_table
        except ImportError:
            pass

    def _restore_spark_methods(self):
        """Restore original Spark methods."""
        try:
            import pyspark.sql
            if self.original_read:
                pyspark.sql.DataFrameReader.table = self.original_read
            if self.original_readStream and hasattr(pyspark.sql, 'streaming'):
                pyspark.sql.streaming.DataStreamReader.table = self.original_readStream
        except ImportError:
            pass

    def _intercept_read_table(self, table_name: str):
        """Intercept spark.read.table() calls."""
        # Get the singleton interceptor instance
        interceptor = SparkInterceptor()

        if not interceptor.enabled or not interceptor.connection:
            # Fall back to original if not enabled
            if interceptor.original_read:
                return interceptor.original_read(self, table_name)
            raise RuntimeError("Spark interception not properly initialized")

        # Parse table reference
        from ..utils.parser import TableReferenceParser
        from ..exceptions import InvalidReferenceError

        try:
            ref = TableReferenceParser.parse(table_name)
        except Exception as e:
            raise InvalidReferenceError(str(e))

        # Check cache
        cached = interceptor.cache.get(ref)
        if cached is not None:
            return cached

        # Fetch from Unity Catalog
        data = interceptor.fetch_from_unity_catalog(ref)

        # Cache and return
        interceptor.cache.put(ref, data)
        return data

    def _intercept_readstream_table(self, table_name: str):
        """Intercept spark.readStream.table() calls."""
        # Get the singleton interceptor instance
        interceptor = SparkInterceptor()

        if not interceptor.enabled or not interceptor.connection:
            if interceptor.original_readStream:
                return interceptor.original_readStream(self, table_name)
            raise RuntimeError("Spark stream interception not properly initialized")

        # Parse table reference
        from ..utils.parser import TableReferenceParser
        ref = TableReferenceParser.parse(table_name)

        # Create streaming reader
        return interceptor.create_stream_from_unity_catalog(ref)

    def fetch_from_unity_catalog(self, ref: CatalogReference) -> Any:
        """Fetch data from Unity Catalog with retry logic."""
        from ..utils.error_handler import ErrorHandler
        from ..connectors.unity_catalog import UnityCatalogConnector
        from ..exceptions import TableNotFoundError
        import time

        # Create connector if needed
        connector = UnityCatalogConnector(self.connection)

        # Retry logic for transient failures
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Check if table exists first
                if not connector.table_exists(ref):
                    raise TableNotFoundError(f"Table not found: {ref.full_name}")

                # Fetch the data - now returns PySpark DataFrame directly
                df = connector.fetch_table(ref)

                # Return the PySpark DataFrame directly
                return df

            except TableNotFoundError:
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                    # Try to reconnect
                    if not self.connection.is_connected:
                        self.connection.connect()
                else:
                    raise ConnectionError(f"Failed to fetch table after {max_retries} attempts: {e}")

        return None

    def create_stream_from_unity_catalog(self, ref: CatalogReference) -> Any:
        """Create a streaming reader for Unity Catalog table."""
        # This would implement streaming logic
        # For now, return a mock streaming reader
        class MockStreamReader:
            def option(self, key, value):
                return self

            def options(self, **options):
                return self

            def schema(self, schema):
                return self

            def format(self, source):
                return self

            def load(self):
                return self

            def start(self):
                return self

        return MockStreamReader()