"""
Tests for MySQL connector.
"""

from datadict_connector_mysql import MysqlConnector


class TestMysqlConnector:
    """Test MySQL connector functionality."""

    def test_create_connector(self):
        """Test creating a MySQL connector."""
        connector = MysqlConnector()
        assert connector is not None

    def test_make_loader(self):
        """Test creating a loader."""
        connector = MysqlConnector()
        loader = connector.make_loader()
        assert loader is not None

    def test_make_applier(self):
        """Test creating an applier."""
        connector = MysqlConnector()
        applier = connector.make_applier()
        assert applier is not None

    def test_make_path_builder(self):
        """Test creating a path builder."""
        connector = MysqlConnector()
        path_builder = connector.make_path_builder({})
        assert path_builder is not None

    def test_make_source(self):
        """Test creating a metadata source."""
        connector = MysqlConnector()
        source = connector.make_source()
        assert source is not None

