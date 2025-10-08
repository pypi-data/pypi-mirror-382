"""Parser utilities for table references."""

import re
from typing import Optional, Tuple
from ..models.catalog_reference import CatalogReference
from ..exceptions import InvalidReferenceError


class TableReferenceParser:
    """Parse and validate table references."""

    # Pattern for valid SQL identifiers
    IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

    @classmethod
    def parse(cls, reference: str) -> CatalogReference:
        """Parse a table reference string into CatalogReference."""
        if not reference:
            raise InvalidReferenceError("Table reference cannot be empty")

        # Remove any backticks or quotes
        reference = reference.replace("`", "").replace('"', "").replace("'", "")

        # Split by dot
        parts = reference.split(".")

        if len(parts) == 1:
            raise InvalidReferenceError(f"Invalid table reference: {reference}. Missing catalog and schema.")

        if len(parts) == 2:
            raise InvalidReferenceError(f"Invalid table reference: {reference}. Missing catalog.")

        if len(parts) != 3:
            raise InvalidReferenceError(f"Invalid table reference: {reference}. Expected format: catalog.schema.table")

        catalog, schema, table = parts

        # Validate each part
        if not cls.is_valid_identifier(catalog):
            raise InvalidReferenceError(f"Invalid catalog name: {catalog}")

        if not cls.is_valid_identifier(schema):
            raise InvalidReferenceError(f"Invalid schema name: {schema}")

        if not cls.is_valid_identifier(table):
            raise InvalidReferenceError(f"Invalid table name: {table}")

        return CatalogReference(catalog=catalog, schema=schema, table=table)

    @classmethod
    def is_valid_identifier(cls, identifier: str) -> bool:
        """Check if string is a valid SQL identifier."""
        if not identifier:
            return False
        return cls.IDENTIFIER_PATTERN.match(identifier) is not None

    @classmethod
    def normalize_reference(cls, reference: str) -> str:
        """Normalize a table reference to standard format."""
        parsed = cls.parse(reference)
        return parsed.full_name