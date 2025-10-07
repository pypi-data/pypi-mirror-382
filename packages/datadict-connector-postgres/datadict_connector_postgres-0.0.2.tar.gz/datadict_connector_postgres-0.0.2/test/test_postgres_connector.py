"""
Tests for PostgreSQL connector factory.
"""

from datadict_connector_base import CatalogLoaderV2, ChangeApplier, MetadataSource, PathBuilder
from datadict_connector_postgres import (
    PostgresConnector,
    PostgresSource,
    SqlApplier,
    SqlLoader,
    SqlPathBuilder,
)


class TestPostgresConnector:
    """Test PostgreSQL connector factory methods."""

    def test_create_connector(self):
        """Test creating a connector instance."""
        connector = PostgresConnector()
        assert connector is not None

    def test_make_loader(self):
        """Test make_loader factory method."""
        connector = PostgresConnector()
        loader = connector.make_loader()

        assert loader is not None
        assert isinstance(loader, CatalogLoaderV2)
        assert isinstance(loader, SqlLoader)

    def test_make_path_builder(self):
        """Test make_path_builder factory method."""
        connector = PostgresConnector()
        lookup_table = {"test.key": "test/path.yml"}
        path_builder = connector.make_path_builder(lookup_table)

        assert path_builder is not None
        assert isinstance(path_builder, PathBuilder)
        assert isinstance(path_builder, SqlPathBuilder)

    def test_make_path_builder_with_empty_lookup(self):
        """Test make_path_builder with empty lookup table."""
        connector = PostgresConnector()
        path_builder = connector.make_path_builder({})

        assert path_builder is not None
        assert isinstance(path_builder, SqlPathBuilder)

    def test_make_applier(self):
        """Test make_applier factory method."""
        connector = PostgresConnector()
        applier = connector.make_applier()

        assert applier is not None
        assert isinstance(applier, ChangeApplier)
        assert isinstance(applier, SqlApplier)

    def test_make_source(self):
        """Test make_source factory method."""
        connector = PostgresConnector()
        source = connector.make_source()

        assert source is not None
        assert isinstance(source, MetadataSource)
        assert isinstance(source, PostgresSource)

    def test_all_components_independent(self):
        """Test that all components can be created independently."""
        connector = PostgresConnector()

        loader = connector.make_loader()
        path_builder = connector.make_path_builder({})
        applier = connector.make_applier()
        source = connector.make_source()

        # All should be independent instances
        assert loader is not None
        assert path_builder is not None
        assert applier is not None
        assert source is not None

    def test_multiple_instances(self):
        """Test creating multiple instances of the same component."""
        connector = PostgresConnector()

        loader1 = connector.make_loader()
        loader2 = connector.make_loader()

        # Should create new instances each time
        assert loader1 is not loader2

    def test_connector_is_stateless(self):
        """Test that connector doesn't maintain state."""
        connector = PostgresConnector()

        # Creating components shouldn't affect connector state
        connector.make_loader()
        connector.make_path_builder({})
        connector.make_applier()
        connector.make_source()

        # Should still be able to create more
        loader = connector.make_loader()
        assert loader is not None

    def test_connector_can_be_cached(self):
        """Test that connector instance can be reused (long-lived)."""
        connector = PostgresConnector()

        # Create multiple components from same connector
        loader1 = connector.make_loader()
        loader2 = connector.make_loader()
        source1 = connector.make_source()
        source2 = connector.make_source()

        # All should work independently
        assert loader1 is not None
        assert loader2 is not None
        assert source1 is not None
        assert source2 is not None
