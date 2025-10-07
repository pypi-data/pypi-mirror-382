"""
DataDict PostgreSQL Connector Package

Provides PostgreSQL-specific implementations of DataDict connector interfaces.
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

from .postgres import PostgresConnector
from .postgres_source import PostgresCredentials, PostgresSource

__all__ = [
    "PostgresConnector",
    "SqlLoader",
    "SqlApplier",
    "SqlPathBuilder",
    "PostgresSource",
    "PostgresCredentials",
    "ColumnConfig",
    "Metadata",
    "TableConfig",
    "SchemaItemConfig",
    "DatabaseItemConfig",
    "DatabaseConfig",
]
