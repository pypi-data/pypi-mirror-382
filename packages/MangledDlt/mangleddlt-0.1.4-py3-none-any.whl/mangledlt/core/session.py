"""SparkSession wrapper for MangledDLT."""

from typing import Optional, Any


class SparkSessionWrapper:
    """Wrapper for SparkSession with interception capabilities."""

    def __init__(self, spark_session: Any = None):
        """Initialize with optional existing SparkSession."""
        self.spark = spark_session
        self._interceptor = None

    def get_or_create(self) -> Any:
        """Get existing or create new SparkSession."""
        if not self.spark:
            try:
                from pyspark.sql import SparkSession
                self.spark = SparkSession.builder \
                    .appName("MangledDLT") \
                    .config("spark.sql.adaptive.enabled", "true") \
                    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
                    .getOrCreate()
            except ImportError:
                raise ImportError("PySpark is required but not installed. Install with: pip install pyspark")

        return self.spark

    def is_databricks_runtime(self) -> bool:
        """Check if running in Databricks runtime."""
        if not self.spark:
            return False

        try:
            # Check for Databricks-specific configuration
            cluster_id = self.spark.conf.get("spark.databricks.service.clusterId", None)
            return cluster_id is not None
        except:
            return False

    def enable_interception(self, interceptor: Any):
        """Enable Spark operation interception."""
        self._interceptor = interceptor
        if self.spark and self._interceptor:
            # The interceptor handles the actual patching
            return True
        return False

    def disable_interception(self):
        """Disable Spark operation interception."""
        if self._interceptor:
            self._interceptor.disable()
            self._interceptor = None
            return True
        return False