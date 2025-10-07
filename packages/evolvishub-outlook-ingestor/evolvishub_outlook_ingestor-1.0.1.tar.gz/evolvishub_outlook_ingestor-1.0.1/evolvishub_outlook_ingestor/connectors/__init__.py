"""
Database and Storage Connectors for Evolvishub Outlook Ingestor.

This module provides connectors for various database systems and storage backends,
enabling flexible data persistence and retrieval for email ingestion workflows.

Available Database Connectors:
- BaseConnector: Abstract base class for all database connectors
- PostgreSQLConnector: PostgreSQL database connector with async support
- MongoDBConnector: MongoDB NoSQL database connector
- SQLiteConnector: SQLite file-based database connector
- MSSQLConnector: Microsoft SQL Server database connector
- MariaDBConnector: MariaDB database connector
- OracleConnector: Oracle Database connector
- CockroachDBConnector: CockroachDB distributed database connector

Available Data Lake Connectors:
- DeltaLakeConnector: Apache Spark-based ACID transactional storage layer
- IcebergConnector: Open table format for large-scale analytics
- ClickHouseConnector: High-performance columnar database for analytics

Available Storage Connectors:
- BaseStorageConnector: Abstract base class for all storage connectors
- MinIOConnector: MinIO S3-compatible object storage connector
- AWSS3Connector: Amazon S3 cloud storage connector
- AzureBlobConnector: Microsoft Azure Blob Storage connector
- GCSConnector: Google Cloud Storage connector
"""

import logging
from typing import Dict, Type, Any, Union

# Import base connectors
from evolvishub_outlook_ingestor.connectors.base_connector import BaseConnector

# Database connectors
try:
    from evolvishub_outlook_ingestor.connectors.postgresql_connector import PostgreSQLConnector
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    logging.warning("PostgreSQL connector not available: missing dependencies")

try:
    from evolvishub_outlook_ingestor.connectors.mongodb_connector import MongoDBConnector
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    logging.warning("MongoDB connector not available: missing dependencies")

try:
    from evolvishub_outlook_ingestor.connectors.sqlite_connector import SQLiteConnector
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False
    logging.warning("SQLite connector not available: missing dependencies")

try:
    from evolvishub_outlook_ingestor.connectors.mssql_connector import MSSQLConnector
    MSSQL_AVAILABLE = True
except ImportError:
    MSSQL_AVAILABLE = False
    logging.warning("SQL Server connector not available: missing dependencies")

try:
    from evolvishub_outlook_ingestor.connectors.mariadb_connector import MariaDBConnector
    MARIADB_AVAILABLE = True
except ImportError:
    MARIADB_AVAILABLE = False
    logging.warning("MariaDB connector not available: missing dependencies")

try:
    from evolvishub_outlook_ingestor.connectors.oracle_connector import OracleConnector
    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False
    logging.warning("Oracle connector not available: missing dependencies")

try:
    from evolvishub_outlook_ingestor.connectors.cockroachdb_connector import CockroachDBConnector
    COCKROACHDB_AVAILABLE = True
except ImportError:
    COCKROACHDB_AVAILABLE = False
    logging.warning("CockroachDB connector not available: missing dependencies")

# Data Lake connectors
try:
    from evolvishub_outlook_ingestor.connectors.deltalake_connector import DeltaLakeConnector
    DELTALAKE_AVAILABLE = True
except ImportError:
    DELTALAKE_AVAILABLE = False
    logging.warning("Delta Lake connector not available: missing dependencies")

try:
    from evolvishub_outlook_ingestor.connectors.iceberg_connector import IcebergConnector
    ICEBERG_AVAILABLE = True
except ImportError:
    ICEBERG_AVAILABLE = False
    logging.warning("Apache Iceberg connector not available: missing dependencies")

try:
    from evolvishub_outlook_ingestor.connectors.clickhouse_connector import ClickHouseConnector
    CLICKHOUSE_AVAILABLE = True
except ImportError:
    CLICKHOUSE_AVAILABLE = False
    logging.warning("ClickHouse connector not available: missing dependencies")

# Storage connectors
try:
    from evolvishub_outlook_ingestor.connectors.base_storage_connector import BaseStorageConnector
    STORAGE_BASE_AVAILABLE = True
except ImportError:
    STORAGE_BASE_AVAILABLE = False
    logging.warning("Storage base connector not available")

try:
    from evolvishub_outlook_ingestor.connectors.minio_connector import MinIOConnector
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    logging.warning("MinIO connector not available: missing dependencies")

try:
    from evolvishub_outlook_ingestor.connectors.aws_s3_connector import AWSS3Connector
    AWS_S3_AVAILABLE = True
except ImportError:
    AWS_S3_AVAILABLE = False
    logging.warning("AWS S3 connector not available: missing dependencies")

try:
    from evolvishub_outlook_ingestor.connectors.azure_blob_connector import AzureBlobConnector
    AZURE_BLOB_AVAILABLE = True
except ImportError:
    AZURE_BLOB_AVAILABLE = False
    logging.warning("Azure Blob Storage connector not available: missing dependencies")

try:
    from evolvishub_outlook_ingestor.connectors.gcs_connector import GCSConnector
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    logging.warning("Google Cloud Storage connector not available: missing dependencies")


# Database connector registry
DATABASE_CONNECTOR_REGISTRY: Dict[str, Type[BaseConnector]] = {
    "base": BaseConnector,
}

if POSTGRESQL_AVAILABLE:
    DATABASE_CONNECTOR_REGISTRY["postgresql"] = PostgreSQLConnector
    DATABASE_CONNECTOR_REGISTRY["postgres"] = PostgreSQLConnector

if MONGODB_AVAILABLE:
    DATABASE_CONNECTOR_REGISTRY["mongodb"] = MongoDBConnector
    DATABASE_CONNECTOR_REGISTRY["mongo"] = MongoDBConnector

if SQLITE_AVAILABLE:
    DATABASE_CONNECTOR_REGISTRY["sqlite"] = SQLiteConnector
    DATABASE_CONNECTOR_REGISTRY["sqlite3"] = SQLiteConnector

if MSSQL_AVAILABLE:
    DATABASE_CONNECTOR_REGISTRY["mssql"] = MSSQLConnector
    DATABASE_CONNECTOR_REGISTRY["sqlserver"] = MSSQLConnector
    DATABASE_CONNECTOR_REGISTRY["sql_server"] = MSSQLConnector

if MARIADB_AVAILABLE:
    DATABASE_CONNECTOR_REGISTRY["mariadb"] = MariaDBConnector
    DATABASE_CONNECTOR_REGISTRY["maria"] = MariaDBConnector

if ORACLE_AVAILABLE:
    DATABASE_CONNECTOR_REGISTRY["oracle"] = OracleConnector
    DATABASE_CONNECTOR_REGISTRY["oracle_db"] = OracleConnector

if COCKROACHDB_AVAILABLE:
    DATABASE_CONNECTOR_REGISTRY["cockroachdb"] = CockroachDBConnector
    DATABASE_CONNECTOR_REGISTRY["cockroach"] = CockroachDBConnector
    DATABASE_CONNECTOR_REGISTRY["crdb"] = CockroachDBConnector

# Data Lake connectors
if DELTALAKE_AVAILABLE:
    DATABASE_CONNECTOR_REGISTRY["deltalake"] = DeltaLakeConnector
    DATABASE_CONNECTOR_REGISTRY["delta"] = DeltaLakeConnector
    DATABASE_CONNECTOR_REGISTRY["delta_lake"] = DeltaLakeConnector

if ICEBERG_AVAILABLE:
    DATABASE_CONNECTOR_REGISTRY["iceberg"] = IcebergConnector
    DATABASE_CONNECTOR_REGISTRY["apache_iceberg"] = IcebergConnector

if CLICKHOUSE_AVAILABLE:
    DATABASE_CONNECTOR_REGISTRY["clickhouse"] = ClickHouseConnector
    DATABASE_CONNECTOR_REGISTRY["ch"] = ClickHouseConnector

# Storage connector registry
STORAGE_CONNECTOR_REGISTRY: Dict[str, Type] = {}

if STORAGE_BASE_AVAILABLE:
    STORAGE_CONNECTOR_REGISTRY["base_storage"] = BaseStorageConnector

if MINIO_AVAILABLE:
    STORAGE_CONNECTOR_REGISTRY["minio"] = MinIOConnector
    STORAGE_CONNECTOR_REGISTRY["s3"] = MinIOConnector  # Alias for S3-compatible

if AWS_S3_AVAILABLE:
    STORAGE_CONNECTOR_REGISTRY["aws_s3"] = AWSS3Connector
    STORAGE_CONNECTOR_REGISTRY["amazon_s3"] = AWSS3Connector

if AZURE_BLOB_AVAILABLE:
    STORAGE_CONNECTOR_REGISTRY["azure_blob"] = AzureBlobConnector
    STORAGE_CONNECTOR_REGISTRY["azure"] = AzureBlobConnector

if GCS_AVAILABLE:
    STORAGE_CONNECTOR_REGISTRY["gcs"] = GCSConnector
    STORAGE_CONNECTOR_REGISTRY["google_cloud_storage"] = GCSConnector


def get_database_connector_class(connector_type: str) -> Type[BaseConnector]:
    """
    Get database connector class by type name.

    Args:
        connector_type: Type of connector (e.g., 'postgresql', 'mongodb')

    Returns:
        Database connector class

    Raises:
        ValueError: If connector type is not supported
    """
    connector_type = connector_type.lower()
    if connector_type not in DATABASE_CONNECTOR_REGISTRY:
        available = ", ".join(DATABASE_CONNECTOR_REGISTRY.keys())
        raise ValueError(f"Unsupported database connector type: {connector_type}. Available: {available}")

    return DATABASE_CONNECTOR_REGISTRY[connector_type]


def get_storage_connector_class(connector_type: str) -> Type:
    """
    Get storage connector class by type name.

    Args:
        connector_type: Type of connector (e.g., 'minio', 'aws_s3', 'azure_blob', 'gcs')

    Returns:
        Storage connector class

    Raises:
        ValueError: If connector type is not supported
    """
    connector_type = connector_type.lower()
    if connector_type not in STORAGE_CONNECTOR_REGISTRY:
        available = ", ".join(STORAGE_CONNECTOR_REGISTRY.keys())
        raise ValueError(f"Unsupported storage connector type: {connector_type}. Available: {available}")

    return STORAGE_CONNECTOR_REGISTRY[connector_type]


def create_database_connector(connector_type: str, name: str, config: Dict[str, Any]) -> BaseConnector:
    """
    Create a database connector instance.

    Args:
        connector_type: Type of connector
        name: Unique name for the connector instance
        config: Configuration dictionary

    Returns:
        Configured database connector instance
    """
    connector_class = get_database_connector_class(connector_type)
    return connector_class(name, config)


def create_storage_connector(connector_type: str, name: str, config: Union[Dict[str, Any], Any]):
    """
    Create a storage connector instance.

    Args:
        connector_type: Type of connector
        name: Unique name for the connector instance
        config: Configuration dictionary or StorageConfig object

    Returns:
        Configured storage connector instance
    """
    connector_class = get_storage_connector_class(connector_type)
    return connector_class(name, config)


def list_available_connectors() -> Dict[str, Dict[str, bool]]:
    """
    List all available connectors and their availability status.

    Returns:
        Dictionary with 'database' and 'storage' keys containing availability status
    """
    return {
        "database": {
            "postgresql": POSTGRESQL_AVAILABLE,
            "mongodb": MONGODB_AVAILABLE,
            "sqlite": SQLITE_AVAILABLE,
            "mssql": MSSQL_AVAILABLE,
            "mariadb": MARIADB_AVAILABLE,
            "oracle": ORACLE_AVAILABLE,
            "cockroachdb": COCKROACHDB_AVAILABLE,
            "clickhouse": CLICKHOUSE_AVAILABLE,
        },
        "datalake": {
            "deltalake": DELTALAKE_AVAILABLE,
            "iceberg": ICEBERG_AVAILABLE,
        },
        "storage": {
            "minio": MINIO_AVAILABLE,
            "aws_s3": AWS_S3_AVAILABLE,
            "azure_blob": AZURE_BLOB_AVAILABLE,
            "gcs": GCS_AVAILABLE,
        }
    }


__all__ = [
    # Base classes
    "BaseConnector",
    "BaseStorageConnector",

    # Database connectors
    "PostgreSQLConnector",
    "MongoDBConnector",
    "SQLiteConnector",
    "MSSQLConnector",
    "MariaDBConnector",
    "OracleConnector",
    "CockroachDBConnector",
    "ClickHouseConnector",

    # Data Lake connectors
    "DeltaLakeConnector",
    "IcebergConnector",

    # Storage connectors
    "MinIOConnector",
    "AWSS3Connector",
    "AzureBlobConnector",
    "GCSConnector",

    # Registries
    "DATABASE_CONNECTOR_REGISTRY",
    "STORAGE_CONNECTOR_REGISTRY",

    # Factory functions
    "get_database_connector_class",
    "get_storage_connector_class",
    "create_database_connector",
    "create_storage_connector",
    "list_available_connectors",

    # Availability flags
    "POSTGRESQL_AVAILABLE",
    "MONGODB_AVAILABLE",
    "SQLITE_AVAILABLE",
    "MSSQL_AVAILABLE",
    "MARIADB_AVAILABLE",
    "ORACLE_AVAILABLE",
    "COCKROACHDB_AVAILABLE",
    "CLICKHOUSE_AVAILABLE",
    "DELTALAKE_AVAILABLE",
    "ICEBERG_AVAILABLE",
    "MINIO_AVAILABLE",
    "AWS_S3_AVAILABLE",
    "AZURE_BLOB_AVAILABLE",
    "GCS_AVAILABLE",
]
