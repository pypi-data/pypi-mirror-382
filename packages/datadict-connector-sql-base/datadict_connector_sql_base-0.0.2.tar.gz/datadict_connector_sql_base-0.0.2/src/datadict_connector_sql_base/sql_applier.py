from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional

from datadict_connector_base import (
    ChangeApplier,
    ChangeType,
    ItemChange,
    ItemType,
    PhysicalChangeRequest,
)
from ruamel.yaml import YAML

from .sql_path_builder import SqlPathBuilder


class SqlApplier(ChangeApplier):
    """
    SQL database change applier that converts ItemChange objects into file operations.
    Returns PhysicalChangeRequest objects without executing them.
    Works with any SQL database (PostgreSQL, MySQL, MariaDB, etc.)
    """

    def __init__(self):
        self.yaml = YAML()
        self.yaml.default_flow_style = False
        self._file_cache: dict[str, Any] = {}
        self._catalog_root: Optional[str] = None

    def _resolve_catalog_root(self, lookup_table: Dict[str, str]) -> Optional[str]:
        """Cache catalog root so we can read existing files when present."""
        root = lookup_table.get("__catalog_root__")
        if root:
            self._catalog_root = str(root)
        return self._catalog_root

    def _load_file_data(self, path: str, lookup_table: Dict[str, str]) -> Any:
        """Return parsed YAML content for path, using cache when possible."""
        if path in self._file_cache:
            return self._file_cache[path]

        data: Any = {}
        catalog_root = self._resolve_catalog_root(lookup_table)
        if catalog_root:
            file_path = Path(catalog_root) / path
            if file_path.exists():
                with open(file_path, "r") as f:
                    loaded = self.yaml.load(f) or {}
                data = loaded

        if not isinstance(data, dict):
            data = {}

        self._file_cache[path] = data
        return data

    def _dump_yaml(self, data: Any) -> str:
        stream = StringIO()
        self.yaml.dump(data, stream)
        return stream.getvalue()

    def apply_change(
        self, change: ItemChange, lookup_table: Dict[str, str]
    ) -> List[PhysicalChangeRequest]:
        """
        Convert an ItemChange into physical file change requests.

        Args:
            change: The change to apply
            lookup_table: Dict mapping FQN keys to existing file paths

        Returns:
            List of PhysicalChangeRequest objects
        """
        path_builder = SqlPathBuilder(lookup_table)
        item_type = ItemType(change.type) if change.type else None

        if item_type == ItemType.DATABASE:
            return self._apply_database_change(change, path_builder, lookup_table)
        elif item_type == ItemType.SCHEMA:
            return self._apply_schema_change(change, path_builder, lookup_table)
        elif item_type == ItemType.TABLE:
            return self._apply_table_change(change, path_builder, lookup_table)
        elif item_type == ItemType.COLUMN:
            return self._apply_column_change(change, path_builder, lookup_table)
        else:
            raise ValueError(f"Unsupported item type: {item_type}")

    def _apply_database_change(
        self,
        change: ItemChange,
        path_builder: SqlPathBuilder,
        lookup_table: Dict[str, str],
    ) -> List[PhysicalChangeRequest]:
        """Apply change to database in database.yml."""
        if not change.key:
            raise ValueError("Change key is required")

        path = path_builder.get_path(change.key, ItemType.DATABASE)
        parts = change.key.split(".")
        db_name = parts[0]

        data = self._load_file_data(path, lookup_table)
        databases = data.get("databases")
        if not isinstance(databases, list):
            databases = list(databases) if databases else []
        data["databases"] = databases

        changed = False

        existing_db = next((db for db in databases if db.get("name") == db_name), None)

        if change.change == ChangeType.CREATE:
            if existing_db is None:
                new_db = {"name": db_name}
                if change.name and change.name != db_name:
                    new_db["description"] = change.name
                databases.append(new_db)
                changed = True
            else:
                if change.name and change.name != db_name:
                    if existing_db.get("description") != change.name:
                        existing_db["description"] = change.name
                        changed = True

        elif change.change == ChangeType.MODIFY and existing_db is not None:
            if change.name and change.name != db_name:
                if existing_db.get("description") != change.name:
                    existing_db["description"] = change.name
                    changed = True

        elif (
            change.change in (ChangeType.ARCHIVE, ChangeType.UNARCHIVE) and existing_db is not None
        ):
            archived = change.change == ChangeType.ARCHIVE
            if archived:
                if not existing_db.get("archived"):
                    existing_db["archived"] = True
                    changed = True
            else:
                if existing_db.pop("archived", None):
                    changed = True

        if not changed:
            return []

        self._file_cache[path] = data
        content = self._dump_yaml(data)

        return [PhysicalChangeRequest(path=path, action="set", content=content)]

    def _apply_schema_change(
        self,
        change: ItemChange,
        path_builder: SqlPathBuilder,
        lookup_table: Dict[str, str],
    ) -> List[PhysicalChangeRequest]:
        """Apply change to schema in database.yml."""
        if not change.key:
            raise ValueError("Change key is required")

        path = path_builder.get_path(change.key, ItemType.SCHEMA)
        parts = change.key.split(".")
        if len(parts) < 2:
            raise ValueError(f"Invalid schema key: {change.key}")
        db_name, schema_name = parts[0], parts[1]

        data = self._load_file_data(path, lookup_table)
        databases = data.get("databases")
        if not isinstance(databases, list):
            databases = list(databases) if databases else []
        data["databases"] = databases

        target_db = next((db for db in databases if db.get("name") == db_name), None)
        if target_db is None:
            raise ValueError(f"Database {db_name} not found in database.yml")

        schemas = target_db.get("schemas")
        if not isinstance(schemas, list):
            schemas = list(schemas) if schemas else []
        target_db["schemas"] = schemas

        existing_schema = next((s for s in schemas if s.get("name") == schema_name), None)
        changed = False

        if change.change == ChangeType.CREATE:
            if existing_schema is None:
                new_schema = {"name": schema_name}
                if change.name and change.name != schema_name:
                    new_schema["description"] = change.name
                schemas.append(new_schema)
                changed = True
            else:
                if change.name and change.name != schema_name:
                    if existing_schema.get("description") != change.name:
                        existing_schema["description"] = change.name
                        changed = True

        elif change.change == ChangeType.MODIFY and existing_schema is not None:
            if change.name and change.name != schema_name:
                if existing_schema.get("description") != change.name:
                    existing_schema["description"] = change.name
                    changed = True

        elif (
            change.change in (ChangeType.ARCHIVE, ChangeType.UNARCHIVE)
            and existing_schema is not None
        ):
            archived = change.change == ChangeType.ARCHIVE
            if archived:
                if not existing_schema.get("archived"):
                    existing_schema["archived"] = True
                    changed = True
            else:
                if existing_schema.pop("archived", None):
                    changed = True

        if not changed:
            return []

        self._file_cache[path] = data
        content = self._dump_yaml(data)

        return [PhysicalChangeRequest(path=path, action="set", content=content)]

    def _apply_table_change(
        self,
        change: ItemChange,
        path_builder: SqlPathBuilder,
        lookup_table: Dict[str, str],
    ) -> List[PhysicalChangeRequest]:
        """Apply change to table file."""
        if not change.key:
            raise ValueError("Change key is required")

        path = path_builder.get_path(change.key, ItemType.TABLE)
        parts = change.key.split(".")
        if len(parts) < 3:
            raise ValueError(f"Invalid table key: {change.key}")
        db_name, schema_name, table_name = parts[0], parts[1], parts[2]

        data = self._load_file_data(path, lookup_table)
        if not isinstance(data, dict):
            data = {}
        self._file_cache[path] = data

        changed = False

        metadata_obj = data.get("metadata")
        if isinstance(metadata_obj, dict):
            metadata = metadata_obj
        else:
            metadata = {}
            if metadata_obj is not None:
                changed = True
        data["metadata"] = metadata

        columns_obj = data.get("columns")
        if isinstance(columns_obj, list):
            columns = columns_obj
        else:
            columns = list(columns_obj) if columns_obj else []
            if columns_obj is not None:
                changed = True
        data["columns"] = columns

        if change.change == ChangeType.CREATE:
            if data.get("name") != table_name:
                data["name"] = table_name
                changed = True
            if metadata.get("database") != db_name:
                metadata["database"] = db_name
                changed = True
            if metadata.get("schema") != schema_name:
                metadata["schema"] = schema_name
                changed = True
            if change.name and change.name != table_name:
                if data.get("description") != change.name:
                    data["description"] = change.name
                    changed = True
        elif change.change == ChangeType.MODIFY:
            if change.name and change.name != table_name:
                if data.get("description") != change.name:
                    data["description"] = change.name
                    changed = True

        elif change.change in (ChangeType.ARCHIVE, ChangeType.UNARCHIVE):
            archived_flag = change.change == ChangeType.ARCHIVE
            if archived_flag:
                if not data.get("archived"):
                    data["archived"] = True
                changed = True
            else:
                removed = data.pop("archived", None)
                if removed is not None:
                    changed = True
                else:
                    # Ensure we still create a request so callers persist state
                    changed = True

        desired_table_type = change.sub_type if change.sub_type else None
        existing_table_type = metadata.get("tableType")
        if desired_table_type and desired_table_type != "BASE TABLE":
            if existing_table_type != desired_table_type:
                metadata["tableType"] = desired_table_type
                changed = True
        else:
            if existing_table_type is not None:
                metadata.pop("tableType", None)
                changed = True

        if not changed:
            return []

        content = self._dump_yaml(data)
        return [PhysicalChangeRequest(path=path, action="set", content=content)]

    def _apply_column_change(
        self,
        change: ItemChange,
        path_builder: SqlPathBuilder,
        lookup_table: Dict[str, str],
    ) -> List[PhysicalChangeRequest]:
        """Apply change to column in table file."""
        if not change.key:
            raise ValueError("Change key is required")

        # Columns are stored in parent table file
        parts = change.key.split(".")
        if len(parts) < 4:
            raise ValueError(f"Invalid column key: {change.key}")
        column_name = parts[3]
        table_key = ".".join(parts[:3])

        path = path_builder.get_path(table_key, ItemType.TABLE)
        data = self._load_file_data(path, lookup_table)
        if not isinstance(data, dict):
            data = {}
        self._file_cache[path] = data

        columns = data.get("columns")
        if not isinstance(columns, list):
            columns = list(columns) if columns else []
        data["columns"] = columns

        changed = False

        if change.change == ChangeType.CREATE:
            for col in columns:
                if col.get("name") == column_name:
                    return []

            new_col = {"name": column_name, "type": change.data_type or "string"}
            if change.name and change.name != column_name:
                new_col["description"] = change.name
            columns.append(new_col)
            changed = True

        elif change.change == ChangeType.MODIFY:
            target_col = next((col for col in columns if col.get("name") == column_name), None)
            if not target_col:
                return []

            if change.name and change.name != column_name:
                if target_col.get("description") != change.name:
                    target_col["description"] = change.name
                    changed = True
            if change.data_type and target_col.get("type") != change.data_type:
                target_col["type"] = change.data_type
                changed = True

        elif change.change in (ChangeType.ARCHIVE, ChangeType.UNARCHIVE):
            target_col = next((col for col in columns if col.get("name") == column_name), None)
            if not target_col:
                return []

            archived = change.change == ChangeType.ARCHIVE
            if archived:
                if not target_col.get("archived"):
                    target_col["archived"] = True
                    changed = True
            else:
                if target_col.pop("archived", None):
                    changed = True

        if not changed:
            return []

        content = self._dump_yaml(data)
        return [PhysicalChangeRequest(path=path, action="set", content=content)]

