"""Unity Catalog connector for data access."""

from typing import Any, Optional
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, BooleanType, TimestampType
from ..models.unity_catalog_connection import UnityCatalogConnection
from ..models.catalog_reference import CatalogReference


class UnityCatalogConnector:
    """Handles Unity Catalog connections and data fetching."""

    def __init__(self, connection: UnityCatalogConnection):
        """Initialize with a Unity Catalog connection."""
        self.connection = connection
        self.spark = SparkSession.builder \
            .master("local[*]") \
            .appName("MangledDLT") \
            .getOrCreate()

    def fetch_table(self, table_ref: CatalogReference) -> DataFrame:
        """Fetch entire table from Unity Catalog."""
        query = f"SELECT * FROM {table_ref.full_name}"
        return self.execute_query(query)

    def fetch_table_with_limit(self, table_ref: CatalogReference, limit: int) -> DataFrame:
        """Fetch table with row limit."""
        query = f"SELECT * FROM {table_ref.full_name} LIMIT {limit}"
        return self.execute_query(query)

    def fetch_table_schema(self, table_ref: CatalogReference) -> Any:
        """Fetch table schema information."""
        query = f"DESCRIBE TABLE {table_ref.full_name}"
        return self.execute_query(query)

    def table_exists(self, table_ref: CatalogReference) -> bool:
        """Check if table exists in Unity Catalog."""
        try:
            query = f"SHOW TABLES IN {table_ref.catalog}.{table_ref.schema} LIKE '{table_ref.table}'"
            result = self.execute_query(query)
            return result.count() > 0 if result is not None else False
        except:
            return False

    def execute_query(self, query: str) -> DataFrame:
        """Execute a SQL query and return results as Spark DataFrame."""
        if not self.connection.is_connected:
            self.connection.connect()

        try:
            # Execute query through Databricks connection
            if hasattr(self.connection.connection, 'cursor'):
                cursor = self.connection.connection.cursor()
                cursor.execute(query)

                # Get column information
                columns = [desc[0] for desc in cursor.description] if cursor.description else []

                # Fetch all data
                data = cursor.fetchall()
                cursor.close()

                # Convert directly to Spark DataFrame
                if data and columns:
                    # Create Spark DataFrame from rows
                    return self.spark.createDataFrame(data, schema=columns)
                else:
                    # Return empty DataFrame with schema if no data
                    return self.spark.createDataFrame([], schema=StructType([]))
            else:
                # Fallback if connection doesn't have cursor
                result = self.connection.execute_query(query)
                if result:
                    return self.spark.createDataFrame(result)
                return self.spark.createDataFrame([], schema=StructType([]))

        except Exception as e:
            from ..exceptions import TableNotFoundError
            if "table" in str(e).lower() and "not found" in str(e).lower():
                raise TableNotFoundError(f"Table not found: {query}")
            raise

    def test_connection(self) -> bool:
        """Test the Unity Catalog connection."""
        try:
            query = "SELECT 1"
            result = self.execute_query(query)
            return result is not None and result.count() >= 0
        except:
            return False