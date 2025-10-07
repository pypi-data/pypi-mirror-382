"""
DataDict MySQL/MariaDB Connector Package

Provides MySQL and MariaDB-specific implementations of DataDict connector interfaces.
"""

__version__ = "0.0.1"

from datadict_connector_sql_base import (
    ColumnConfig,
    DatabaseConfig,
    DatabaseItemConfig,
    Metadata,
    SchemaItemConfig,
    SqlApplier,
    SqlLoader,
    SqlPathBuilder,
    TableConfig,
)

from .mysql import MysqlConnector
from .mysql_source import MysqlCredentials, MysqlSource

__all__ = [
    "MysqlConnector",
    "SqlLoader",
    "SqlApplier",
    "SqlPathBuilder",
    "MysqlSource",
    "MysqlCredentials",
    "ColumnConfig",
    "Metadata",
    "TableConfig",
    "SchemaItemConfig",
    "DatabaseItemConfig",
    "DatabaseConfig",
]

