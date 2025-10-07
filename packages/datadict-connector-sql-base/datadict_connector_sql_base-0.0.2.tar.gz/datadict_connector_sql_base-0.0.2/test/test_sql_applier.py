"""
Tests for SQL base change applier.
"""

import pytest
from datadict_connector_base import ChangeType, ItemChange, ItemType
from datadict_connector_sql_base import SqlApplier


class TestSqlApplier:
    """Test SQL applier functionality."""

    def test_create_applier(self):
        """Test creating an applier instance."""
        applier = SqlApplier()
        assert applier is not None

    def test_create_database(self):
        """Test applying CREATE change for database."""
        applier = SqlApplier()
        change = ItemChange(
            key="testdb",
            type=ItemType.DATABASE,
            change=ChangeType.CREATE,
            name="Test Database",
        )

        requests = applier.apply_change(change, {})

        assert len(requests) == 1
        assert requests[0].path == "database.yml"
        assert requests[0].action == "set"
        assert "testdb" in requests[0].content
        assert "databases:" in requests[0].content

    def test_create_table(self):
        """Test applying CREATE change for table."""
        applier = SqlApplier()
        change = ItemChange(
            key="testdb.public.users",
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
            name="User table",
        )

        requests = applier.apply_change(change, {})

        assert len(requests) == 1
        assert requests[0].path == "testdb/public/users.yml"
        assert requests[0].action == "set"
        assert "name: users" in requests[0].content
        assert "metadata:" in requests[0].content
        assert "database: testdb" in requests[0].content
        assert "schema: public" in requests[0].content

    def test_create_column(self):
        """Test applying CREATE change for column."""
        applier = SqlApplier()
        change = ItemChange(
            key="testdb.public.users.email",
            type=ItemType.COLUMN,
            change=ChangeType.CREATE,
            name="Email column",
            data_type="varchar",
        )

        requests = applier.apply_change(change, {})

        assert len(requests) == 1
        # Column should modify parent table file
        assert requests[0].path == "testdb/public/users.yml"
        assert requests[0].action == "set"

    def test_modify_table(self):
        """Test applying MODIFY change for table."""
        applier = SqlApplier()
        change = ItemChange(
            key="testdb.public.users",
            type=ItemType.TABLE,
            change=ChangeType.MODIFY,
            name="Updated description",
        )

        requests = applier.apply_change(change, {})

        assert len(requests) == 1
        assert requests[0].path == "testdb/public/users.yml"
        assert requests[0].action == "set"

    def test_archive_table(self):
        """Test applying ARCHIVE change for table."""
        applier = SqlApplier()
        change = ItemChange(
            key="testdb.public.users",
            type=ItemType.TABLE,
            change=ChangeType.ARCHIVE,
        )

        requests = applier.apply_change(change, {})

        assert len(requests) == 1
        assert requests[0].path == "testdb/public/users.yml"
        assert "archived: true" in requests[0].content or "archived:" in requests[0].content

    def test_unarchive_table(self):
        """Test applying UNARCHIVE change for table."""
        applier = SqlApplier()
        change = ItemChange(
            key="testdb.public.users",
            type=ItemType.TABLE,
            change=ChangeType.UNARCHIVE,
        )

        requests = applier.apply_change(change, {})

        assert len(requests) == 1
        assert requests[0].path == "testdb/public/users.yml"

    def test_lookup_table_used_for_paths(self):
        """Test that lookup table is used for path resolution."""
        applier = SqlApplier()
        lookup_table = {
            "testdb.public.users": "custom/users.yml",
        }

        change = ItemChange(
            key="testdb.public.users",
            type=ItemType.TABLE,
            change=ChangeType.MODIFY,
            name="Updated",
        )

        requests = applier.apply_change(change, lookup_table)

        assert len(requests) == 1
        assert requests[0].path == "custom/users.yml"

    def test_no_file_io_performed(self):
        """Test that applier does not perform file I/O."""
        applier = SqlApplier()
        change = ItemChange(
            key="testdb.public.users",
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
        )

        # Should not raise any file-related errors
        requests = applier.apply_change(change, {})

        # Should return requests, not execute them
        assert len(requests) > 0
        assert all(hasattr(r, "path") for r in requests)
        assert all(hasattr(r, "action") for r in requests)
        assert all(hasattr(r, "content") for r in requests)

    def test_returns_physical_change_requests(self):
        """Test that applier returns PhysicalChangeRequest objects."""
        applier = SqlApplier()
        change = ItemChange(
            key="testdb.public.users",
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
        )

        requests = applier.apply_change(change, {})

        assert len(requests) > 0
        for request in requests:
            assert hasattr(request, "path")
            assert hasattr(request, "action")
            assert hasattr(request, "content")
            assert isinstance(request.path, str)
            assert isinstance(request.action, str)
            assert isinstance(request.content, str)

    def test_invalid_change_type_raises_error(self):
        """Test that invalid item type raises error."""
        applier = SqlApplier()
        change = ItemChange(
            key="testdb.public.users",
            type=ItemType.DOC,  # Not supported by postgres
            change=ChangeType.CREATE,
        )

        with pytest.raises(ValueError, match="Unsupported item type"):
            applier.apply_change(change, {})

    def test_missing_key_raises_error(self):
        """Test that missing key raises error."""
        applier = SqlApplier()
        change = ItemChange(
            key=None,
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
        )

        with pytest.raises(ValueError, match="key is required"):
            applier.apply_change(change, {})

    def test_yaml_content_is_valid(self):
        """Test that generated YAML content is valid."""
        applier = SqlApplier()
        change = ItemChange(
            key="testdb.public.users",
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
            name="User accounts",
        )

        requests = applier.apply_change(change, {})

        # Should be valid YAML
        import yaml

        content = requests[0].content
        parsed = yaml.safe_load(content)
        assert isinstance(parsed, dict)
        assert "name" in parsed

    def test_column_uses_parent_table_path(self):
        """Test that column changes use parent table file path."""
        applier = SqlApplier()

        # Column change
        change = ItemChange(
            key="testdb.public.users.email",
            type=ItemType.COLUMN,
            change=ChangeType.CREATE,
            data_type="varchar",
        )

        requests = applier.apply_change(change, {})

        # Should modify parent table file
        assert requests[0].path == "testdb/public/users.yml"

    def test_multiple_databases(self):
        """Test changes for tables in different databases."""
        applier = SqlApplier()

        change1 = ItemChange(
            key="db1.public.users",
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
        )

        change2 = ItemChange(
            key="db2.public.users",
            type=ItemType.TABLE,
            change=ChangeType.CREATE,
        )

        requests1 = applier.apply_change(change1, {})
        requests2 = applier.apply_change(change2, {})

        # Should use different paths
        assert requests1[0].path != requests2[0].path
        assert requests1[0].path == "db1/public/users.yml"
        assert requests2[0].path == "db2/public/users.yml"
