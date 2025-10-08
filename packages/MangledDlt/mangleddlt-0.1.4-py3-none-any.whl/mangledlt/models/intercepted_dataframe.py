"""InterceptedDataFrame entity for wrapped DataFrames."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from pyspark.sql import DataFrame
from ..models.catalog_reference import CatalogReference


@dataclass
class InterceptedDataFrame:
    """Wrapper that maintains DataFrame API compatibility."""

    data: DataFrame  # Now directly stores PySpark DataFrame
    source_table: CatalogReference
    fetch_time: datetime = None
    from_cache: bool = False

    def __post_init__(self):
        """Initialize fetch time if not provided."""
        if self.fetch_time is None:
            self.fetch_time = datetime.now()

    @property
    def spark_df(self):
        """Get the Spark DataFrame."""
        return self.data

    # Delegate all DataFrame methods to the underlying PySpark DataFrame
    def select(self, *cols):
        """Select columns."""
        return self.data.select(*cols)

    def filter(self, condition):
        """Filter rows."""
        return self.data.filter(condition)

    def where(self, condition):
        """Alias for filter."""
        return self.data.where(condition)

    def groupBy(self, *cols):
        """Group by columns."""
        return self.data.groupBy(*cols)

    def agg(self, *exprs):
        """Aggregate functions."""
        return self.data.agg(*exprs)

    def join(self, other, on, how='inner'):
        """Join with another DataFrame."""
        if isinstance(other, InterceptedDataFrame):
            return self.data.join(other.data, on, how)
        return self.data.join(other, on, how)

    def show(self, n=20, truncate=True):
        """Display rows."""
        return self.data.show(n, truncate)

    def collect(self):
        """Collect all rows."""
        return self.data.collect()

    def count(self):
        """Count rows."""
        return self.data.count()

    @property
    def schema(self):
        """Get schema."""
        return self.data.schema

    @property
    def columns(self):
        """Get column names."""
        return self.data.columns

    @property
    def dtypes(self):
        """Get column data types."""
        return self.data.dtypes