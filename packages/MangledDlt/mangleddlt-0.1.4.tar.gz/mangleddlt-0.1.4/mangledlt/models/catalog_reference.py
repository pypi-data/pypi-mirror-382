"""CatalogReference entity for parsed Unity Catalog table references."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class CatalogReference:
    """Parsed reference to a Unity Catalog table."""

    catalog: str
    schema: str
    table: str

    @property
    def full_name(self) -> str:
        """Get fully qualified table name."""
        return f"{self.catalog}.{self.schema}.{self.table}"

    @classmethod
    def parse(cls, reference: str) -> "CatalogReference":
        """Parse a table reference string."""
        if not reference:
            raise ValueError("Table reference cannot be empty")

        parts = reference.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid table reference: {reference}. Expected format: catalog.schema.table")

        catalog, schema, table = parts

        # Validate each part
        pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*$"
        if not re.match(pattern, catalog):
            raise ValueError(f"Invalid catalog name: {catalog}")
        if not re.match(pattern, schema):
            raise ValueError(f"Invalid schema name: {schema}")
        if not re.match(pattern, table):
            raise ValueError(f"Invalid table name: {table}")

        return cls(catalog=catalog, schema=schema, table=table)

    def __hash__(self):
        """Make hashable for use as cache key."""
        return hash(self.full_name.lower())

    def __eq__(self, other):
        """Case-insensitive equality."""
        if not isinstance(other, CatalogReference):
            return False
        return self.full_name.lower() == other.full_name.lower()