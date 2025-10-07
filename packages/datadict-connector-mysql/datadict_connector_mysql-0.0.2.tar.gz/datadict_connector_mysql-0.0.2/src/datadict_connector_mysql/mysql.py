"""
The MySQL/MariaDB connector for DataDict.
"""

from datadict_connector_base import (
    CatalogLoaderV2,
    ChangeApplier,
    ConnectorBase,
    MetadataSource,
    PathBuilder,
)
from datadict_connector_sql_base import SqlApplier, SqlLoader, SqlPathBuilder

from .mysql_source import MysqlSource


class MysqlConnector(ConnectorBase):
    """
    MySQL/MariaDB connector implementation.
    Provides factory methods for creating loader, applier, path builder, and source instances.
    """

    def make_loader(self) -> CatalogLoaderV2:
        """
        Create a MySQL catalog loader.

        Returns:
            SqlLoader instance
        """
        return SqlLoader()

    def make_path_builder(self, lookup_table: dict[str, str]) -> PathBuilder:
        """
        Create a MySQL path builder.

        Args:
            lookup_table: Dict mapping FQN keys to existing file paths

        Returns:
            SqlPathBuilder instance
        """
        return SqlPathBuilder(lookup_table)

    def make_applier(self) -> ChangeApplier:
        """
        Create a MySQL change applier.

        Returns:
            SqlApplier instance
        """
        return SqlApplier()

    def make_source(self) -> MetadataSource:
        """
        Create a MySQL metadata source.

        Returns:
            MysqlSource instance
        """
        return MysqlSource()

