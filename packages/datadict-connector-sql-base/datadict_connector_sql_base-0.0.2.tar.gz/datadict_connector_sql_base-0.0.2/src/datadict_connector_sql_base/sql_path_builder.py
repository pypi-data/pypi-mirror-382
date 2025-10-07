from typing import Dict

from datadict_connector_base import ItemType, PathBuilder

from .sql_keys import slugify_filename


class SqlPathBuilder(PathBuilder):
    """
    Path builder for SQL database catalogs.

    Default path structure:
    - database.yml: All databases and schemas
    - {database}/{schema}/{table}.yml: Individual table files with columns
    """

    def __init__(self, lookup_table: Dict[str, str]):
        super().__init__(lookup_table)

    def get_default_path(self, key: str, item_type: ItemType) -> str:
        """
        Generate the default physical YAML file path (relative to the catalog root) for an item.

        Strategy:
        - database -> "database.yml" (single file at catalog root)
        - schema   -> "database.yml" (single file at catalog root)
        - table    -> "<db>/<schema>/<table>.yml"
        - column   -> same file as its parent table
        """
        parts = key.split(".")

        if item_type == ItemType.DATABASE:
            # All databases use single database.yml at catalog root
            return "database.yml"

        if item_type == ItemType.SCHEMA:
            if len(parts) < 2:
                raise ValueError(f"Invalid schema key: {key}")
            # All schemas use single database.yml at catalog root
            return "database.yml"

        if item_type == ItemType.TABLE:
            if len(parts) < 3:
                raise ValueError(f"Invalid table key: {key}")
            database, schema, table = parts[0], parts[1], parts[2]
            filename = f"{slugify_filename(table)}.yml"
            return f"{database}/{schema}/{filename}"

        if item_type == ItemType.COLUMN:
            if len(parts) < 4:
                raise ValueError(f"Invalid column key: {key}")
            # Columns are stored in the same file as their parent table
            database, schema, table = parts[0], parts[1], parts[2]
            filename = f"{slugify_filename(table)}.yml"
            return f"{database}/{schema}/{filename}"

        raise ValueError(f"Unsupported item type: {item_type}")

