"""
The postgres connector serves as a prototype database connector.
"""

from datadict_connector_base import (
    CatalogLoaderV2,
    ChangeApplier,
    ConnectorBase,
    MetadataSource,
    PathBuilder,
)
from datadict_connector_sql_base import SqlApplier, SqlLoader, SqlPathBuilder

from .postgres_source import PostgresSource


class PostgresConnector(ConnectorBase):
    """
    PostgreSQL connector implementation.
    Provides factory methods for creating loader, applier, path builder, and source instances.
    """

    def make_loader(self) -> CatalogLoaderV2:
        """
        Create a PostgreSQL catalog loader.

        Returns:
            SqlLoader instance
        """
        return SqlLoader()

    def make_path_builder(self, lookup_table: dict[str, str]) -> PathBuilder:
        """
        Create a PostgreSQL path builder.

        Args:
            lookup_table: Dict mapping FQN keys to existing file paths

        Returns:
            SqlPathBuilder instance
        """
        return SqlPathBuilder(lookup_table)

    def make_applier(self) -> ChangeApplier:
        """
        Create a PostgreSQL change applier.

        Returns:
            SqlApplier instance
        """
        return SqlApplier()

    def make_source(self) -> MetadataSource:
        """
        Create a PostgreSQL metadata source.

        Returns:
            PostgresSource instance
        """
        return PostgresSource()
