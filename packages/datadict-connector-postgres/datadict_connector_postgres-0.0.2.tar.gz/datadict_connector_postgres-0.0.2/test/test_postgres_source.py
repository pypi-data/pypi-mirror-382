"""
Tests for PostgreSQL metadata source.
"""

import pandas as pd
from datadict_connector_postgres import PostgresSource


class TestPostgresSource:
    """Test PostgreSQL source functionality."""

    def test_create_source(self):
        """Test creating a PostgreSQL source."""
        source = PostgresSource()
        assert source is not None
        assert source.credentials is None

    def test_set_credentials_with_connection_string(self, postgres_credentials):
        """Test setting credentials with connection string."""
        source = PostgresSource()
        source.set_credentials(postgres_credentials)
        assert source.credentials is not None
        assert source.credentials.connection_string is not None

    def test_set_credentials_with_individual_params(self):
        """Test setting credentials with individual parameters."""
        source = PostgresSource()
        credentials = {
            "host": "localhost",
            "port": 5432,
            "database": "mydb",
            "username": "myuser",
            "password": "mypass",
        }
        source.set_credentials(credentials)
        assert source.credentials is not None
        assert source.credentials.host == "localhost"

    def test_read_metadata_structure(self, setup_test_database, postgres_credentials):
        """Test reading metadata returns correct DataFrame structure."""
        source = PostgresSource()
        source.set_credentials(postgres_credentials)

        df = source.read_metadata()

        # Verify DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

        # Verify required columns
        required_columns = {"type", "name", "key", "sub_type", "data_type", "parent_key"}
        assert required_columns.issubset(df.columns)

        source.close()

    def test_read_metadata_hierarchy(self, setup_test_database, postgres_credentials):
        """Test metadata contains all hierarchy levels."""
        source = PostgresSource()
        source.set_credentials(postgres_credentials)

        df = source.read_metadata()

        # Verify all types present
        types = set(df["type"].unique())
        expected_types = {"database", "schema", "table", "column"}
        assert expected_types.issubset(types)

        source.close()

    def test_database_level(self, setup_test_database, postgres_credentials):
        """Test database level metadata."""
        source = PostgresSource()
        source.set_credentials(postgres_credentials)

        df = source.read_metadata()

        # Verify database
        db_items = df[df["type"] == "database"]
        assert len(db_items) == 1
        db_item = db_items.iloc[0]
        assert db_item["name"] == "mydb"
        assert db_item["key"] == "mydb"
        assert pd.isna(db_item["parent_key"])

        source.close()

    def test_schema_level(self, setup_test_database, postgres_credentials):
        """Test schema level metadata."""
        source = PostgresSource()
        source.set_credentials(postgres_credentials)

        df = source.read_metadata()

        # Verify schemas
        schema_items = df[df["type"] == "schema"]
        schema_names = set(schema_items["name"])
        expected_schemas = {"public", "analytics", "sales"}
        assert expected_schemas.issubset(schema_names)

        # Verify parent references
        db_items = df[df["type"] == "database"]
        db_id = db_items.iloc[0]["id"]
        for _, schema in schema_items.iterrows():
            assert schema["parent_key"] == db_id
            assert "." in schema["key"]  # Should be db.schema format

        source.close()

    def test_table_level(self, setup_test_database, postgres_credentials):
        """Test table level metadata."""
        source = PostgresSource()
        source.set_credentials(postgres_credentials)

        df = source.read_metadata()

        # Verify specific tables
        table_items = df[df["type"] == "table"]
        table_keys = set(table_items["key"])
        expected_tables = {
            "mydb.public.users",
            "mydb.public.orders",
            "mydb.analytics.user_metrics",
            "mydb.sales.products",
        }
        assert expected_tables.issubset(table_keys)

        # Verify parent references
        for _, table in table_items.iterrows():
            assert table["parent_key"] is not None
            # Parent should be schema
            schema_key = table["parent_key"]
            assert schema_key.count(".") == 1  # db.schema format

        source.close()

    def test_column_level(self, setup_test_database, postgres_credentials):
        """Test column level metadata."""
        source = PostgresSource()
        source.set_credentials(postgres_credentials)

        df = source.read_metadata()

        # Verify specific columns
        column_items = df[df["type"] == "column"]
        column_keys = set(column_items["key"])
        expected_columns = {
            "mydb.public.users.id",
            "mydb.public.users.email",
            "mydb.sales.products.name",
            "mydb.sales.products.price",
        }
        assert expected_columns.issubset(column_keys)

        # Verify data types are populated
        for _, col in column_items.iterrows():
            assert col["data_type"] is not None
            assert col["data_type"] != ""

        # Verify parent references
        for _, col in column_items.iterrows():
            assert col["parent_key"] is not None
            # Parent should be table
            table_key = col["parent_key"]
            assert table_key.count(".") == 2  # db.schema.table format

        source.close()

    def test_deterministic_ids(self, setup_test_database, postgres_credentials):
        """Test that IDs are deterministic (no duplicates)."""
        source = PostgresSource()
        source.set_credentials(postgres_credentials)

        df = source.read_metadata()

        # Verify no duplicate IDs
        id_counts = df["id"].value_counts()
        assert all(count == 1 for count in id_counts)

        source.close()

    def test_close_disposes_engine(self, postgres_credentials):
        """Test that close() disposes the engine."""
        source = PostgresSource()
        source.set_credentials(postgres_credentials)

        # Access engine to initialize it
        engine = source._get_engine()
        assert engine is not None

        source.close()
        assert source._engine is None
