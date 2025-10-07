"""
Tests for SQL base path builder.
"""

import pytest
from datadict_connector_base import ItemType
from datadict_connector_sql_base import SqlPathBuilder


class TestSqlPathBuilder:
    """Test SQL path builder functionality."""

    def test_create_path_builder(self):
        """Test creating a path builder instance."""
        path_builder = SqlPathBuilder({})
        assert path_builder is not None

    def test_database_path(self):
        """Test path generation for database."""
        path_builder = SqlPathBuilder({})
        path = path_builder.get_path("mydb", ItemType.DATABASE)
        assert path == "database.yml"

    def test_schema_path(self):
        """Test path generation for schema."""
        path_builder = SqlPathBuilder({})
        path = path_builder.get_path("mydb.public", ItemType.SCHEMA)
        assert path == "database.yml"

    def test_table_path(self):
        """Test path generation for table."""
        path_builder = SqlPathBuilder({})
        path = path_builder.get_path("mydb.public.users", ItemType.TABLE)
        assert path == "mydb/public/users.yml"

    def test_table_path_with_special_chars(self):
        """Test path generation for table with special characters."""
        path_builder = SqlPathBuilder({})
        path = path_builder.get_path("mydb.public.user_orders_2023", ItemType.TABLE)
        assert path == "mydb/public/user_orders_2023.yml"

    def test_column_path_matches_table(self):
        """Test that column path matches parent table path."""
        path_builder = SqlPathBuilder({})
        table_path = path_builder.get_path("mydb.public.users", ItemType.TABLE)
        column_path = path_builder.get_path("mydb.public.users.id", ItemType.COLUMN)
        assert column_path == table_path

    def test_lookup_table_fallback_to_default(self):
        """Test fallback to default when not in lookup table."""
        lookup_table = {
            "mydb.public.orders": "custom/orders.yml",
        }
        path_builder = SqlPathBuilder(lookup_table)

        # Not in lookup table, should use default
        path = path_builder.get_path("mydb.public.users", ItemType.TABLE)
        assert path == "mydb/public/users.yml"

    def test_multiple_databases(self):
        """Test paths for tables in different databases."""
        path_builder = SqlPathBuilder({})

        path1 = path_builder.get_path("db1.public.users", ItemType.TABLE)
        path2 = path_builder.get_path("db2.public.users", ItemType.TABLE)

        assert path1 == "db1/public/users.yml"
        assert path2 == "db2/public/users.yml"
        assert path1 != path2

    def test_multiple_schemas(self):
        """Test paths for tables in different schemas."""
        path_builder = SqlPathBuilder({})

        path1 = path_builder.get_path("mydb.public.users", ItemType.TABLE)
        path2 = path_builder.get_path("mydb.analytics.users", ItemType.TABLE)

        assert path1 == "mydb/public/users.yml"
        assert path2 == "mydb/analytics/users.yml"
        assert path1 != path2

    def test_invalid_database_key(self):
        """Test error handling for invalid database key."""
        path_builder = SqlPathBuilder({})
        # Database keys don't need validation, just return database.yml
        path = path_builder.get_path("", ItemType.DATABASE)
        assert path == "database.yml"

    def test_invalid_schema_key(self):
        """Test error handling for invalid schema key."""
        path_builder = SqlPathBuilder({})
        with pytest.raises(ValueError, match="Invalid schema key"):
            path_builder.get_path("invalid", ItemType.SCHEMA)

    def test_invalid_table_key(self):
        """Test error handling for invalid table key."""
        path_builder = SqlPathBuilder({})
        with pytest.raises(ValueError, match="Invalid table key"):
            path_builder.get_path("invalid.key", ItemType.TABLE)

    def test_invalid_column_key(self):
        """Test error handling for invalid column key."""
        path_builder = SqlPathBuilder({})
        with pytest.raises(ValueError, match="Invalid column key"):
            path_builder.get_path("invalid.key.test", ItemType.COLUMN)

    def test_slugify_table_names(self):
        """Test that table names are properly slugified."""
        path_builder = SqlPathBuilder({})

        # Spaces and special chars should be converted
        path = path_builder.get_path("mydb.public.My Table Name!", ItemType.TABLE)
        assert "my_table_name" in path
        assert " " not in path
        assert "!" not in path

    def test_default_path_method(self):
        """Test get_default_path method directly."""
        path_builder = SqlPathBuilder({})

        # Database
        path = path_builder.get_default_path("mydb", ItemType.DATABASE)
        assert path == "database.yml"

        # Schema
        path = path_builder.get_default_path("mydb.public", ItemType.SCHEMA)
        assert path == "database.yml"

        # Table
        path = path_builder.get_default_path("mydb.public.users", ItemType.TABLE)
        assert path == "mydb/public/users.yml"

        # Column
        path = path_builder.get_default_path("mydb.public.users.id", ItemType.COLUMN)
        assert path == "mydb/public/users.yml"

    def test_complex_schema_names(self):
        """Test handling of complex schema names."""
        path_builder = SqlPathBuilder({})

        path = path_builder.get_path("mydb.my_analytics_v2.users", ItemType.TABLE)
        assert path == "mydb/my_analytics_v2/users.yml"

    def test_long_table_names(self):
        """Test handling of very long table names."""
        path_builder = SqlPathBuilder({})

        long_name = "a" * 100
        path = path_builder.get_path(f"mydb.public.{long_name}", ItemType.TABLE)

        # Should be slugified and truncated to max length
        assert len(path.split("/")[-1]) <= 70  # filename + .yml extension
        assert path.startswith("mydb/public/")
