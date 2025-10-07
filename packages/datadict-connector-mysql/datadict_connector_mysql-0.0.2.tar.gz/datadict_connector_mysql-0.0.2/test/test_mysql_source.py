"""
Tests for MySQL metadata source.
"""

import pandas as pd
import pytest
from datadict_connector_mysql import MysqlSource


class TestMysqlSource:
    """Test MySQL source functionality."""

    def test_create_source(self):
        """Test creating a MySQL source."""
        source = MysqlSource()
        assert source is not None
        assert source.credentials is None

    def test_set_credentials_with_connection_string(self, mysql_credentials):
        """Test setting credentials with connection string."""
        source = MysqlSource()
        creds = {
            "connection_string": f"mysql://{mysql_credentials['username']}:{mysql_credentials['password']}"
            f"@{mysql_credentials['host']}:{mysql_credentials['port']}/{mysql_credentials['database']}"
        }
        source.set_credentials(creds)
        assert source.credentials is not None
        assert source.credentials.connection_string is not None

    def test_set_credentials_with_mariadb_connection_string(self, mysql_credentials):
        """Test setting credentials with MariaDB connection string."""
        source = MysqlSource()
        creds = {
            "connection_string": f"mariadb://{mysql_credentials['username']}:{mysql_credentials['password']}"
            f"@{mysql_credentials['host']}:{mysql_credentials['port']}/{mysql_credentials['database']}"
        }
        source.set_credentials(creds)
        assert source.credentials is not None
        # Should convert mariadb:// to mysql+pymysql://
        connection_string = source.credentials.to_connection_string()
        assert connection_string.startswith("mysql+pymysql://")

    def test_set_credentials_with_individual_params(self):
        """Test setting credentials with individual parameters."""
        source = MysqlSource()
        credentials = {
            "host": "localhost",
            "port": 3306,
            "database": "mydb",
            "username": "myuser",
            "password": "mypass",
        }
        source.set_credentials(credentials)
        assert source.credentials is not None
        assert source.credentials.host == "localhost"

    def test_read_metadata_structure(self, setup_test_database, mysql_credentials):
        """Test reading metadata returns correct DataFrame structure."""
        source = MysqlSource()
        source.set_credentials(mysql_credentials)

        df = source.read_metadata()

        # Verify DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

        # Verify required columns
        assert "type" in df.columns
        assert "name" in df.columns
        assert "key" in df.columns
        assert "id" in df.columns

        # Verify we have different item types
        types = df["type"].unique()
        assert "database" in types
        assert "schema" in types
        assert "table" in types
        assert "column" in types

        source.close()

    def test_read_metadata_hierarchy(self, setup_test_database, mysql_credentials):
        """Test that metadata maintains proper hierarchy."""
        source = MysqlSource()
        source.set_credentials(mysql_credentials)

        df = source.read_metadata()

        # Get database
        databases = df[df["type"] == "database"]
        assert len(databases) > 0
        db_key = databases.iloc[0]["key"]

        # Get schemas - should have database as parent
        schemas = df[df["type"] == "schema"]
        assert len(schemas) > 0
        for _, schema in schemas.iterrows():
            assert schema["parent_key"] == databases.iloc[0]["id"]
            assert schema["key"].startswith(db_key + ".")

        # Get tables - should have schema as parent
        tables = df[df["type"] == "table"]
        assert len(tables) > 0

        # Get columns - should have table as parent
        columns = df[df["type"] == "column"]
        assert len(columns) > 0

        source.close()

    def test_read_lineage(self, setup_test_database, mysql_credentials):
        """Test reading lineage from views."""
        source = MysqlSource()
        source.set_credentials(mysql_credentials)

        lineage_df = source.read_lineage()

        # Should have lineage from the user_orders view
        if lineage_df is not None:
            assert isinstance(lineage_df, pd.DataFrame)
            assert "src_key" in lineage_df.columns
            assert "dst_key" in lineage_df.columns
            assert "edge_type" in lineage_df.columns

            # Verify edge_type
            assert all(lineage_df["edge_type"] == "depends_on")

        source.close()

    def test_credentials_validation(self):
        """Test that credentials validation works."""
        source = MysqlSource()

        # Missing required fields should raise error
        with pytest.raises(ValueError):
            source.set_credentials({"host": "localhost"})

    def test_connection_string_normalization(self):
        """Test that connection strings are normalized correctly."""
        source = MysqlSource()

        # Test mysql:// prefix
        source.set_credentials({"connection_string": "mysql://user:pass@host:3306/db"})
        conn_str = source.credentials.to_connection_string()
        assert conn_str.startswith("mysql+pymysql://")

        # Test mariadb:// prefix
        source.set_credentials({"connection_string": "mariadb://user:pass@host:3306/db"})
        conn_str = source.credentials.to_connection_string()
        assert conn_str.startswith("mysql+pymysql://")

        # Test plain string (no prefix)
        source.set_credentials({"connection_string": "user:pass@host:3306/db"})
        conn_str = source.credentials.to_connection_string()
        assert conn_str.startswith("mysql+pymysql://")

