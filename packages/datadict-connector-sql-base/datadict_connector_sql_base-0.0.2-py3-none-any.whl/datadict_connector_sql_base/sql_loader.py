from typing import Dict, List

from datadict_connector_base import CatalogItem, CatalogLoaderV2, ItemType, parse_yaml_string

from .sql_schemas import DatabaseConfig, TableConfig


class SqlLoader(CatalogLoaderV2):
    """
    SQL database catalog loader that loads items from YAML file contents.
    Works with any SQL database (PostgreSQL, MySQL, MariaDB, etc.)
    """

    def load_from_files(self, files: Dict[str, str]) -> List[CatalogItem]:
        """
        Load all database catalog items from file contents.

        Returns items in dependency order (parents before children):
        1. Databases
        2. Schemas
        3. Tables
        4. Columns

        Args:
            files: Dict mapping normalized paths to file contents
                   e.g., {"database.yml": "...", "mydb/public/users.yml": "..."}
        """
        items = []

        # Load database/schema structure from database.yml if it exists
        if "database.yml" in files:
            items.extend(self._load_database_structure(files["database.yml"]))

        # Track defined databases and schemas for validation
        defined_databases = set()
        defined_schemas = set()
        for item in items:
            if item.type == ItemType.DATABASE:
                defined_databases.add(item.key)
            elif item.type == ItemType.SCHEMA:
                defined_schemas.add(item.key)

        # Load table files
        items.extend(self._load_table_files(files, defined_databases, defined_schemas))

        return items

    def _load_database_structure(self, content: str) -> List[CatalogItem]:
        """Load database and schema structure from database.yml content."""
        items = []
        database_data = parse_yaml_string(content)
        database_config = DatabaseConfig(**database_data)

        for db_config in database_config.databases:
            database_fqn = db_config.name

            # Create database item
            database_item = CatalogItem(
                name=db_config.name,
                key=database_fqn,
                type=ItemType.DATABASE,
                description=db_config.description,
                notes=db_config.notes,
                archived=db_config.archived or False,
                properties={"fullQualifiedName": database_fqn},
                file_path="database.yml",
            )
            items.append(database_item)

            # Create schema items
            for schema_config in db_config.schemas:
                schema_fqn = f"{database_fqn}.{schema_config.name}"

                schema_item = CatalogItem(
                    name=schema_config.name,
                    key=schema_fqn,
                    parent_key=database_fqn,
                    type=ItemType.SCHEMA,
                    description=schema_config.description,
                    notes=schema_config.notes,
                    archived=schema_config.archived or False,
                    properties={"fullQualifiedName": schema_fqn},
                    file_path="database.yml",
                )
                items.append(schema_item)

        return items

    def _load_table_files(
        self, files: Dict[str, str], defined_databases: set, defined_schemas: set
    ) -> List[CatalogItem]:
        """Load table and column items from file contents."""
        items = []

        # Process all files except catalog.yml and database.yml
        for file_path, content in files.items():
            if file_path in ["catalog.yml", "database.yml"]:
                continue

            if not file_path.endswith(".yml"):
                continue

            try:
                table_data = parse_yaml_string(content)

                # Check if this looks like a table file (has name and columns)
                if not ("name" in table_data and "columns" in table_data):
                    continue

                # Parse as TableConfig with metadata
                table_config = TableConfig.model_validate(table_data)
                database_name = table_config.metadata.database
                schema_name = table_config.metadata.schema_name

                # Add table and column items
                table_items = self._create_table_items(
                    file_path,
                    table_config,
                    database_name,
                    schema_name,
                    defined_databases,
                    defined_schemas,
                )
                items.extend(table_items)

            except Exception:
                # If parsing fails completely, skip this file
                continue

        return items

    def _create_table_items(
        self,
        file_path: str,
        table_config: TableConfig,
        database_name: str,
        schema_name: str,
        defined_databases: set,
        defined_schemas: set,
    ) -> List[CatalogItem]:
        """Create table and column items from table config."""
        items = []

        # Validate that database and schema are defined
        database_fqn = database_name
        schema_fqn = f"{database_name}.{schema_name}"

        if database_fqn not in defined_databases:
            raise ValueError(
                f"Table '{table_config.name}' references undefined database '{database_name}'. "
                f"Database must be defined in database.yml"
            )

        if schema_fqn not in defined_schemas:
            raise ValueError(
                f"Table '{table_config.name}' references undefined schema '{schema_name}' "
                f"in database '{database_name}'. Schema must be defined in database.yml"
            )

        # Generate table item
        table_fqn = f"{database_name}.{schema_name}.{table_config.name}"

        table_type = table_config.metadata.table_type
        properties = {"fullQualifiedName": table_fqn}
        if table_type and table_type != "BASE TABLE":
            properties["tableType"] = table_type

        table_item = CatalogItem(
            name=table_config.name,
            key=table_fqn,
            parent_key=schema_fqn,
            type=ItemType.TABLE,
            sub_type=table_type,
            description=table_config.description,
            notes=table_config.notes,
            archived=table_config.archived or False,
            properties=properties,
            file_path=file_path,
        )
        items.append(table_item)

        # Generate column items
        for column_config in table_config.columns:
            column_fqn = f"{table_fqn}.{column_config.name}"

            column_item = CatalogItem(
                name=column_config.name,
                key=column_fqn,
                parent_key=table_fqn,
                type=ItemType.COLUMN,
                description=column_config.description,
                archived=column_config.archived or False,
                properties={
                    "columnType": column_config.type,
                    "fullQualifiedName": column_fqn,
                },
                file_path=file_path,
            )
            items.append(column_item)

        return items

