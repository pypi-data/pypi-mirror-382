"""
DataDict SQL Base Connector Package

Provides shared SQL database connector components for DataDict.
Used as base for PostgreSQL, MySQL, MariaDB, and other SQL database connectors.
"""

__version__ = "0.0.1"

from .sql_applier import SqlApplier
from .sql_keys import (
    parse_column_key,
    parse_database_key,
    parse_schema_key,
    parse_table_key,
    slugify_filename,
)
from .sql_loader import SqlLoader
from .sql_path_builder import SqlPathBuilder
from .sql_schemas import (
    ColumnConfig,
    DatabaseConfig,
    DatabaseItemConfig,
    Metadata,
    SchemaItemConfig,
    TableConfig,
)

__all__ = [
    "SqlLoader",
    "SqlApplier",
    "SqlPathBuilder",
    "ColumnConfig",
    "Metadata",
    "TableConfig",
    "SchemaItemConfig",
    "DatabaseItemConfig",
    "DatabaseConfig",
    "slugify_filename",
    "parse_database_key",
    "parse_schema_key",
    "parse_table_key",
    "parse_column_key",
]

