import re
from typing import Tuple

MAX_SLUG_LENGTH = 64


def slugify_filename(name: str) -> str:
    """
    Create a filesystem-safe filename slug.

    Rules:
    - lowercase
    - non-alphanumeric become underscores
    - collapse repeated underscores
    - trim leading/trailing underscores
    - limit to MAX_SLUG_LENGTH
    """
    lowered = name.lower()
    replaced = re.sub(r"[^a-z0-9]+", "_", lowered)
    collapsed = re.sub(r"_+", "_", replaced)
    trimmed = collapsed.strip("_")
    return trimmed[:MAX_SLUG_LENGTH] if len(trimmed) > MAX_SLUG_LENGTH else trimmed


def parse_database_key(key: str) -> str:
    """
    Parse database name from FQN key.

    Args:
        key: FQN like "database"

    Returns:
        Database name
    """
    return key


def parse_schema_key(key: str) -> Tuple[str, str]:
    """
    Parse database and schema names from FQN key.

    Args:
        key: FQN like "database.schema"

    Returns:
        Tuple of (database, schema)
    """
    parts = key.split(".")
    return parts[0], parts[1]


def parse_table_key(key: str) -> Tuple[str, str, str]:
    """
    Parse database, schema, and table names from FQN key.

    Args:
        key: FQN like "database.schema.table"

    Returns:
        Tuple of (database, schema, table)
    """
    parts = key.split(".")
    return parts[0], parts[1], parts[2]


def parse_column_key(key: str) -> Tuple[str, str, str, str]:
    """
    Parse database, schema, table, and column names from FQN key.

    Args:
        key: FQN like "database.schema.table.column"

    Returns:
        Tuple of (database, schema, table, column)
    """
    parts = key.split(".")
    return parts[0], parts[1], parts[2], parts[3]

