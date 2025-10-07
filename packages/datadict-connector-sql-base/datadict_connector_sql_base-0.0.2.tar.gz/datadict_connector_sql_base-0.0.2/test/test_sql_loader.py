"""
Tests for SQL base catalog loader.
"""

from datadict_connector_base import ItemType
from datadict_connector_sql_base import SqlLoader


class TestSqlLoader:
    """Test SQL loader functionality."""

    def test_create_loader(self):
        """Test creating a loader instance."""
        loader = SqlLoader()
        assert loader is not None

    def test_load_empty_files(self):
        """Test loading from empty file dict."""
        loader = SqlLoader()
        items = loader.load_from_files({})
        assert items == []

    def test_load_database_structure(self):
        """Test loading database and schema structure from database.yml."""
        loader = SqlLoader()
        files = {
            "database.yml": """
databases:
  - name: testdb
    description: Test database
    schemas:
      - name: public
        description: Public schema
      - name: analytics
        description: Analytics schema
"""
        }

        items = loader.load_from_files(files)

        # Should have 1 database + 2 schemas = 3 items
        assert len(items) == 3

        # Check database
        db_items = [i for i in items if i.type == ItemType.DATABASE]
        assert len(db_items) == 1
        assert db_items[0].name == "testdb"
        assert db_items[0].key == "testdb"
        assert db_items[0].description == "Test database"
        assert db_items[0].parent_key is None

        # Check schemas
        schema_items = [i for i in items if i.type == ItemType.SCHEMA]
        assert len(schema_items) == 2
        schema_names = {s.name for s in schema_items}
        assert schema_names == {"public", "analytics"}

        # Verify schema keys
        for schema in schema_items:
            assert schema.key == f"testdb.{schema.name}"
            assert schema.parent_key == "testdb"

    def test_load_table_with_columns(self):
        """Test loading table and columns from table file."""
        loader = SqlLoader()
        files = {
            "database.yml": """
databases:
  - name: testdb
    schemas:
      - name: public
""",
            "testdb/public/users.yml": """
name: users
metadata:
  database: testdb
  schema: public
description: User accounts
columns:
  - name: id
    type: integer
    description: Primary key
  - name: email
    type: varchar
    description: Email address
  - name: created_at
    type: timestamp
""",
        }

        items = loader.load_from_files(files)

        # Should have: 1 db, 1 schema, 1 table, 3 columns = 6 items
        assert len(items) == 6

        # Check table
        table_items = [i for i in items if i.type == ItemType.TABLE]
        assert len(table_items) == 1
        table = table_items[0]
        assert table.name == "users"
        assert table.key == "testdb.public.users"
        assert table.parent_key == "testdb.public"
        assert table.description == "User accounts"

        # Check columns
        column_items = [i for i in items if i.type == ItemType.COLUMN]
        assert len(column_items) == 3
        column_names = {c.name for c in column_items}
        assert column_names == {"id", "email", "created_at"}

        # Verify column properties
        for col in column_items:
            assert col.parent_key == "testdb.public.users"
            assert col.key.startswith("testdb.public.users.")
            assert "columnType" in col.properties

    def test_load_multiple_tables(self):
        """Test loading multiple tables in different schemas."""
        loader = SqlLoader()
        files = {
            "database.yml": """
databases:
  - name: mydb
    schemas:
      - name: public
      - name: sales
""",
            "mydb/public/users.yml": """
name: users
metadata:
  database: mydb
  schema: public
columns:
  - name: id
    type: integer
""",
            "mydb/sales/orders.yml": """
name: orders
metadata:
  database: mydb
  schema: sales
columns:
  - name: order_id
    type: integer
  - name: total
    type: decimal
""",
        }

        items = loader.load_from_files(files)

        # Check tables
        table_items = [i for i in items if i.type == ItemType.TABLE]
        assert len(table_items) == 2
        table_keys = {t.key for t in table_items}
        assert table_keys == {"mydb.public.users", "mydb.sales.orders"}

        # Check columns
        column_items = [i for i in items if i.type == ItemType.COLUMN]
        assert len(column_items) == 3

    def test_dependency_order(self):
        """Test that items are returned in dependency order."""
        loader = SqlLoader()
        files = {
            "database.yml": """
databases:
  - name: testdb
    schemas:
      - name: public
""",
            "testdb/public/users.yml": """
name: users
metadata:
  database: testdb
  schema: public
columns:
  - name: id
    type: integer
""",
        }

        items = loader.load_from_files(files)

        # Verify order: database -> schema -> table -> columns
        types_in_order = [item.type for item in items]

        # Database should come first
        assert types_in_order[0] == ItemType.DATABASE

        # Schema should come before table
        schema_idx = types_in_order.index(ItemType.SCHEMA)
        table_idx = next(i for i, t in enumerate(types_in_order) if t == ItemType.TABLE)
        assert schema_idx < table_idx

        # Table should come before columns
        column_indices = [i for i, t in enumerate(types_in_order) if t == ItemType.COLUMN]
        for col_idx in column_indices:
            assert table_idx < col_idx

    def test_archived_flag(self):
        """Test that archived flag is properly loaded."""
        loader = SqlLoader()
        files = {
            "database.yml": """
databases:
  - name: testdb
    archived: true
    schemas:
      - name: public
        archived: false
""",
            "testdb/public/users.yml": """
name: users
metadata:
  database: testdb
  schema: public
archived: true
columns:
  - name: id
    type: integer
    archived: true
""",
        }

        items = loader.load_from_files(files)

        # Check archived flags
        db = next(i for i in items if i.type == ItemType.DATABASE)
        assert db.archived is True

        schema = next(i for i in items if i.type == ItemType.SCHEMA)
        assert schema.archived is False

        table = next(i for i in items if i.type == ItemType.TABLE)
        assert table.archived is True

        col = next(i for i in items if i.type == ItemType.COLUMN)
        assert col.archived is True

    def test_skip_invalid_files(self):
        """Test that loader skips files that can't be parsed."""
        loader = SqlLoader()
        files = {
            "database.yml": """
databases:
  - name: testdb
    schemas:
      - name: public
""",
            "catalog.yml": "# This should be skipped",
            "testdb/public/invalid.yml": "not: valid: yaml: structure",
            "testdb/public/users.yml": """
name: users
metadata:
  database: testdb
  schema: public
columns:
  - name: id
    type: integer
""",
        }

        items = loader.load_from_files(files)

        # Should only load the valid database, schema, table, and column
        table_items = [i for i in items if i.type == ItemType.TABLE]
        assert len(table_items) == 1
        assert table_items[0].name == "users"

    def test_file_path_tracking(self):
        """Test that items track which file they came from."""
        loader = SqlLoader()
        files = {
            "database.yml": """
databases:
  - name: testdb
    schemas:
      - name: public
""",
            "testdb/public/users.yml": """
name: users
metadata:
  database: testdb
  schema: public
columns:
  - name: id
    type: integer
""",
        }

        items = loader.load_from_files(files)

        # Database and schema should come from database.yml
        db = next(i for i in items if i.type == ItemType.DATABASE)
        assert db.file_path == "database.yml"

        schema = next(i for i in items if i.type == ItemType.SCHEMA)
        assert schema.file_path == "database.yml"

        # Table and columns should come from the table file
        table = next(i for i in items if i.type == ItemType.TABLE)
        assert table.file_path == "testdb/public/users.yml"

        col = next(i for i in items if i.type == ItemType.COLUMN)
        assert col.file_path == "testdb/public/users.yml"
