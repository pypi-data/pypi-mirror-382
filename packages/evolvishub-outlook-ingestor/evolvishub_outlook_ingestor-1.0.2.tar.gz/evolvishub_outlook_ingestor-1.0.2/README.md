<div align="center">
  <img src="https://evolvis.ai/wp-content/uploads/2025/08/evie-solutions-03.png" alt="Evolvis AI - Evie Solutions Logo" width="400">
</div>

# Evolvishub Outlook Ingestor

**Production-ready, secure email ingestion system for Microsoft Outlook with advanced processing, monitoring, and hybrid storage capabilities.**

A comprehensive Python library for ingesting, processing, and storing email data from Microsoft Outlook and Exchange systems. Built with enterprise-grade security, performance, and scalability in mind, featuring intelligent hybrid storage architecture for optimal cost and performance.

## Download Statistics

[![PyPI Downloads](https://pepy.tech/badge/evolvishub-outlook-ingestor/month)](https://pepy.tech/project/evolvishub-outlook-ingestor)
[![Total Downloads](https://pepy.tech/badge/evolvishub-outlook-ingestor)](https://pepy.tech/project/evolvishub-outlook-ingestor)
[![PyPI Version](https://img.shields.io/pypi/v/evolvishub-outlook-ingestor)](https://pypi.org/project/evolvishub-outlook-ingestor/)
[![Python Versions](https://img.shields.io/pypi/pyversions/evolvishub-outlook-ingestor)](https://pypi.org/project/evolvishub-outlook-ingestor/)
[![License](https://img.shields.io/pypi/l/evolvishub-outlook-ingestor)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Hints](https://img.shields.io/badge/type%20hints-yes-brightgreen.svg)](https://mypy.readthedocs.io/)

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [About Evolvis AI](#about-evolvis-ai)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Hybrid Storage Configuration](#hybrid-storage-configuration)
- [Configuration](#configuration)
- [Performance](#performance)
- [Advanced Usage](#advanced-usage)
- [Support and Documentation](#support-and-documentation)
- [Technical Specifications](#technical-specifications)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Features

### Protocol Support
- **Microsoft Graph API** - Modern OAuth2-based access to Office 365 and Exchange Online
- **Exchange Web Services (EWS)** - Enterprise-grade access to on-premises Exchange servers
- **IMAP/POP3** - Universal email protocol support for legacy systems and third-party providers

### Database Integration
- **PostgreSQL** - High-performance relational database with advanced indexing and async support
- **MongoDB** - Scalable NoSQL document storage for flexible email data structures
- **MySQL** - Reliable relational database support for existing infrastructure
- **SQLite** - Lightweight file-based database for development, testing, and small deployments
- **Microsoft SQL Server** - Enterprise database for Windows-centric environments with advanced features
- **MariaDB** - Open-source MySQL alternative with enhanced performance and features
- **Oracle Database** - Enterprise-grade database for mission-critical applications
- **CockroachDB** - Distributed, cloud-native database for global scale and resilience
- **ClickHouse** - High-performance columnar database for analytics and real-time queries

### Data Lake Integration
- **Delta Lake** - Apache Spark-based ACID transactional storage layer with time travel capabilities
- **Apache Iceberg** - Open table format for large-scale analytics with schema evolution support
- **Hybrid Analytics** - Seamless integration between operational databases and analytical data lakes

### Hybrid Storage Architecture
- **MinIO** - Self-hosted S3-compatible storage for on-premises control and high performance
- **AWS S3** - Enterprise cloud storage with global CDN, lifecycle policies, and encryption
- **Azure Blob Storage** - Microsoft ecosystem integration with hot/cool/archive storage tiers
- **Google Cloud Storage** - Global infrastructure with ML integration and advanced analytics
- **Intelligent Routing** - Size-based and content-type-based storage decisions with configurable rules
- **Content Deduplication** - SHA256-based deduplication to eliminate duplicate attachments
- **Automatic Compression** - GZIP/ZLIB compression for text-based attachments
- **Secure Access** - Pre-signed URLs with configurable expiration for secure attachment access

### Performance & Scalability
- **Async/Await Architecture** - Non-blocking operations for maximum throughput (1000+ emails/minute)
- **Hybrid Storage Strategy** - Intelligent routing between database and object storage
- **Batch Processing** - Efficient handling of large email volumes with concurrent workers
- **Connection Pooling** - Optimized database connections for enterprise workloads
- **Memory Optimization** - Smart caching and resource management for large datasets
- **Multi-tier Storage** - Automatic lifecycle management between hot/warm/cold storage

### Enterprise Security
- **Credential Encryption** - Fernet symmetric encryption for sensitive data storage
- **Input Sanitization** - Protection against SQL injection, XSS, and other attacks
- **Secure Configuration** - Environment variable-based configuration with validation
- **Audit Logging** - Complete audit trail without sensitive data exposure
- **Access Control** - IAM-based permissions and secure URL generation

### Developer Experience
- **Type Safety** - Full type hints and IDE support for enhanced development experience
- **Comprehensive Testing** - 80%+ test coverage with unit, integration, and performance tests
- **Extensive Documentation** - Complete API reference with examples and best practices
- **Configuration-Based Setup** - Flexible YAML/JSON configuration with validation
- **Error Handling** - Comprehensive exception hierarchy with automatic retry logic

## Architecture

### System Overview

```mermaid
graph TB
    subgraph "Email Sources"
        A[Microsoft Graph API]
        B[Exchange Web Services]
        C[IMAP/POP3]
    end

    subgraph "Evolvishub Outlook Ingestor"
        D[Protocol Adapters]
        E[Enhanced Attachment Processor]
        F[Email Processor]
        G[Security Layer]
    end

    subgraph "Storage Layer"
        H[Database Storage]
        I[Object Storage]
    end

    subgraph "Database Backends"
        J[PostgreSQL]
        K[MongoDB]
        L[MySQL]
    end

    subgraph "Object Storage Backends"
        M[MinIO]
        N[AWS S3]
        O[Azure Blob]
        P[Google Cloud Storage]
    end

    A --> D
    B --> D
    C --> D
    D --> F
    D --> E
    F --> G
    E --> G
    G --> H
    G --> I
    H --> J
    H --> K
    H --> L
    I --> M
    I --> N
    I --> O
    I --> P
```

### Hybrid Storage Strategy

```mermaid
sequenceDiagram
    participant E as Email Processor
    participant AP as Attachment Processor
    participant DB as Database
    participant OS as Object Storage

    E->>AP: Process Email with Attachments
    AP->>AP: Evaluate Storage Rules

    alt Small Attachment (<1MB)
        AP->>DB: Store in Database
        DB-->>AP: Confirmation
    else Medium Attachment (1-5MB)
        AP->>OS: Store Content
        AP->>DB: Store Metadata + Reference
        OS-->>AP: Storage Key
        DB-->>AP: Confirmation
    else Large Attachment (>5MB)
        AP->>OS: Store Content Only
        OS-->>AP: Storage Key + Metadata
    end

    AP-->>E: Processing Complete
```

### Data Flow Architecture

```mermaid
flowchart LR
    subgraph "Ingestion Layer"
        A[Email Source] --> B[Protocol Adapter]
        B --> C[Rate Limiter]
        C --> D[Authentication]
    end

    subgraph "Processing Layer"
        D --> E[Email Processor]
        E --> F[Attachment Processor]
        F --> G[Security Scanner]
        G --> H[Deduplication Engine]
        H --> I[Compression Engine]
    end

    subgraph "Storage Decision Engine"
        I --> J{Storage Rules}
        J -->|Small Files| K[Database Storage]
        J -->|Medium Files| L[Hybrid Storage]
        J -->|Large Files| M[Object Storage]
    end

    subgraph "Storage Backends"
        K --> N[(PostgreSQL/MongoDB)]
        L --> N
        L --> O[(MinIO/S3/Azure/GCS)]
        M --> O
    end
```

## About Evolvis AI

**Evolvis AI** is a cutting-edge technology company specializing in AI-powered solutions for enterprise email processing, data ingestion, and intelligent automation. Founded with a mission to revolutionize how organizations handle and analyze their email communications, Evolvis AI develops sophisticated tools that combine artificial intelligence with robust engineering practices.

### Our Focus
- **AI-Powered Email Processing** - Advanced algorithms for intelligent email analysis, classification, and extraction
- **Enterprise Data Solutions** - Scalable systems for large-scale email ingestion and processing
- **Intelligent Automation** - Smart workflows that adapt to organizational needs and patterns
- **Security-First Architecture** - Enterprise-grade security and compliance for sensitive email data

### Innovation at Scale
Evolvis AI's solutions are designed to handle enterprise-scale email processing challenges, from small businesses to global corporations. Our technology stack emphasizes performance, security, and scalability while maintaining ease of use and deployment flexibility.

**Learn more about our solutions:** [https://evolvis.ai](https://evolvis.ai)

## Installation

### Basic Installation

```bash
# Install core package
pip install evolvishub-outlook-ingestor
```

### Feature-Specific Installation

```bash
# Protocol adapters (Microsoft Graph, EWS, IMAP/POP3)
pip install evolvishub-outlook-ingestor[protocols]

# Core database connectors (PostgreSQL, MongoDB, MySQL)
pip install evolvishub-outlook-ingestor[database]

# Individual database connectors
pip install evolvishub-outlook-ingestor[database-sqlite]      # SQLite
pip install evolvishub-outlook-ingestor[database-mssql]       # SQL Server
pip install evolvishub-outlook-ingestor[database-mariadb]     # MariaDB
pip install evolvishub-outlook-ingestor[database-oracle]      # Oracle
pip install evolvishub-outlook-ingestor[database-cockroachdb] # CockroachDB

# All database connectors
pip install evolvishub-outlook-ingestor[database-all]

# Data lake connectors
pip install evolvishub-outlook-ingestor[datalake-delta]    # Delta Lake
pip install evolvishub-outlook-ingestor[datalake-iceberg]  # Apache Iceberg
pip install evolvishub-outlook-ingestor[database-clickhouse] # ClickHouse

# All data lake connectors
pip install evolvishub-outlook-ingestor[datalake-all]

# Object storage support (MinIO S3-compatible)
pip install evolvishub-outlook-ingestor[storage]

# Data processing features (HTML parsing, image processing)
pip install evolvishub-outlook-ingestor[processing]
```

### Cloud Storage Installation

```bash
# AWS S3 support
pip install evolvishub-outlook-ingestor[cloud-aws]

# Azure Blob Storage support
pip install evolvishub-outlook-ingestor[cloud-azure]

# Google Cloud Storage support
pip install evolvishub-outlook-ingestor[cloud-gcp]

# All cloud storage backends
pip install evolvishub-outlook-ingestor[cloud-all]
```

### Complete Installation

```bash
# Install all features and dependencies
pip install evolvishub-outlook-ingestor[all]

# Development installation with testing tools
pip install evolvishub-outlook-ingestor[dev]
```

### Requirements

- **Python**: 3.9 or higher
- **Operating System**: Linux, macOS, Windows
- **Memory**: Minimum 512MB RAM (2GB+ recommended for large datasets)
- **Storage**: Varies based on email volume and attachment storage strategy

## Quick Start

### Basic Email Ingestion

```python
import asyncio
from evolvishub_outlook_ingestor.protocols.microsoft_graph import GraphAPIAdapter
from evolvishub_outlook_ingestor.connectors.postgresql_connector import PostgreSQLConnector
from evolvishub_outlook_ingestor.processors.email_processor import EmailProcessor

async def basic_email_ingestion():
    # Configure Microsoft Graph API
    graph_config = {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "tenant_id": "your_tenant_id"
    }

    # Configure PostgreSQL database
    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "outlook_data",
        "username": "postgres",
        "password": "your_password"
    }

    # Initialize components
    async with GraphAPIAdapter("graph", graph_config) as protocol, \
               PostgreSQLConnector("db", db_config) as connector:

        # Create email processor
        processor = EmailProcessor("email_processor")

        # Fetch and process emails
        emails = await protocol.fetch_emails(limit=10)

        for email in emails:
            # Process email content
            result = await processor.process(email)

            # Store in database
            if result.status.value == "success":
                await connector.store_email(result.processed_data)
                print(f"Stored email: {email.subject}")

asyncio.run(basic_email_ingestion())
```

## Hybrid Storage Configuration

### Enterprise-Grade Attachment Processing

```python
import asyncio
from evolvishub_outlook_ingestor.processors.enhanced_attachment_processor import (
    EnhancedAttachmentProcessor,
    StorageStrategy
)
from evolvishub_outlook_ingestor.connectors.minio_connector import MinIOConnector
from evolvishub_outlook_ingestor.connectors.aws_s3_connector import AWSS3Connector
from evolvishub_outlook_ingestor.connectors.postgresql_connector import PostgreSQLConnector

async def hybrid_storage_setup():
    # Configure MinIO for hot storage (frequently accessed files)
    minio_config = {
        "endpoint_url": "localhost:9000",
        "access_key": "minioadmin",
        "secret_key": "minioadmin",
        "bucket_name": "email-attachments-hot",
        "use_ssl": False  # Set to True for production
    }

    # Configure AWS S3 for archive storage (long-term storage)
    s3_config = {
        "access_key": "your_aws_access_key",
        "secret_key": "your_aws_secret_key",
        "bucket_name": "email-attachments-archive",
        "region": "us-east-1"
    }

    # Configure enhanced attachment processor with intelligent routing
    processor_config = {
        "storage_strategy": "hybrid",
        "size_threshold": 1024 * 1024,  # 1MB threshold
        "enable_compression": True,
        "enable_deduplication": True,
        "enable_virus_scanning": False,  # Configure as needed
        "default_storage_backend": "hot_storage",

        # Intelligent storage routing rules
        "storage_rules": [
            {
                "name": "large_files",
                "condition": "size > 5*1024*1024",  # Files > 5MB
                "strategy": "storage_only",
                "storage_backend": "archive_storage"
            },
            {
                "name": "medium_files",
                "condition": "size > 1024*1024 and size <= 5*1024*1024",  # 1-5MB
                "strategy": "hybrid",
                "storage_backend": "hot_storage"
            },
            {
                "name": "small_files",
                "condition": "size <= 1024*1024",  # Files <= 1MB
                "strategy": "database_only"
            },
            {
                "name": "compressible_text",
                "condition": "content_type.startswith('text/') and size > 1024",
                "strategy": "hybrid",
                "storage_backend": "hot_storage",
                "compress": True,
                "compression_type": "gzip"
            }
        ]
    }

    # Initialize storage connectors
    minio_connector = MinIOConnector("hot_storage", minio_config)
    s3_connector = AWSS3Connector("archive_storage", s3_config)

    # Initialize enhanced processor
    processor = EnhancedAttachmentProcessor("hybrid_attachments", processor_config)

    async with minio_connector, s3_connector:
        # Add storage backends to processor
        await processor.add_storage_backend("hot_storage", minio_connector)
        await processor.add_storage_backend("archive_storage", s3_connector)

        # Process emails with intelligent attachment routing
        # (email processing code here)

        # Generate secure URLs for attachment access
        storage_info = {
            "storage_location": "2024/01/15/abc123.pdf",
            "storage_backend": "hot_storage"
        }

        backend = processor.storage_backends[storage_info["storage_backend"]]
        secure_url = await backend.generate_presigned_url(
            storage_info["storage_location"],
            expires_in=3600  # 1 hour expiration
        )

        print(f"Secure attachment URL: {secure_url}")

asyncio.run(hybrid_storage_setup())
```

### Storage Strategy Decision Matrix

| File Size | Content Type | Storage Strategy | Backend | Compression |
|-----------|--------------|------------------|---------|-------------|
| < 1MB | Any | Database Only | PostgreSQL/MongoDB | No |
| 1-5MB | Documents/Images | Hybrid | MinIO/Hot Storage | Optional |
| 1-5MB | Text Files | Hybrid | MinIO/Hot Storage | Yes (GZIP) |
| > 5MB | Any | Storage Only | AWS S3/Archive | Optional |
| > 10MB | Any | Storage Only | AWS S3/Glacier | Yes |

### Database Selection Guide

| Database | Best For | Pros | Cons | Recommended Use Case |
|----------|----------|------|------|---------------------|
| **SQLite** | Development, Testing, Small Scale | Simple setup, no server required, ACID compliant | Single writer, limited concurrency | Development environments, small deployments (<10K emails/day) |
| **PostgreSQL** | General Purpose, High Performance | Excellent performance, rich features, strong consistency | Requires server setup and maintenance | Most production deployments, complex queries |
| **MongoDB** | Flexible Schema, Document Storage | Schema flexibility, horizontal scaling, JSON-native | Eventual consistency, memory usage | Variable email structures, rapid prototyping |
| **MySQL/MariaDB** | Web Applications, Existing Infrastructure | Wide adoption, good performance, familiar | Limited JSON support (older versions) | Web applications, existing MySQL infrastructure |
| **SQL Server** | Windows Environments, Enterprise | Enterprise features, excellent tooling, integration | Windows-centric, licensing costs | Windows-based enterprises, .NET applications |
| **Oracle** | Mission-Critical, Large Enterprise | Proven reliability, advanced features, scalability | High cost, complexity | Large enterprises, mission-critical systems |
| **CockroachDB** | Global Scale, Cloud-Native | Distributed, strong consistency, cloud-native | Newer technology, learning curve | Global deployments, cloud-native applications |

### Data Lake and Analytics Selection Guide

| Platform | Best For | Pros | Cons | Recommended Use Case |
|----------|----------|------|------|---------------------|
| **Delta Lake** | ACID Analytics, Time Travel | ACID transactions, time travel, schema evolution, Spark ecosystem | Requires Spark, Java/Scala ecosystem | Data science workflows, ML pipelines, audit requirements |
| **Apache Iceberg** | Multi-Engine Analytics | Engine agnostic, hidden partitioning, snapshot isolation | Newer ecosystem, complex setup | Multi-tool analytics, data warehouse modernization |
| **ClickHouse** | Real-Time Analytics | Extremely fast queries, columnar storage, SQL interface | Limited transaction support, specialized use case | Real-time dashboards, email analytics, reporting |

### Hybrid Architecture Patterns

| Pattern | Description | Use Case | Benefits |
|---------|-------------|----------|----------|
| **Operational + Analytics** | PostgreSQL for operations, Delta Lake for analytics | Real-time app + historical analysis | Best of both worlds, optimized for each workload |
| **Hot + Cold Storage** | ClickHouse for recent data, Iceberg for historical | Email analytics with time-based access patterns | Cost optimization, query performance |
| **Multi-Engine Lake** | Iceberg with Spark, Trino, and Flink | Complex analytics requiring different compute engines | Flexibility, avoid vendor lock-in |

## Configuration

### Complete Configuration Example

Create a `config.yaml` file for comprehensive system configuration:

```yaml
# Database configuration examples

# PostgreSQL
database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  database: "outlook_data"
  username: "postgres"
  password: "your_password"
  pool_size: 20
  max_overflow: 30

# SQLite (for development/testing)
database:
  type: "sqlite"
  database_path: "outlook_data.db"
  enable_wal: true
  timeout: 30.0

# SQL Server
database:
  type: "mssql"
  server: "localhost\\SQLEXPRESS"
  port: 1433
  database: "outlook_data"
  username: "sa"
  password: "your_password"
  trusted_connection: false
  encrypt: true

# MariaDB
database:
  type: "mariadb"
  host: "localhost"
  port: 3306
  database: "outlook_data"
  username: "root"
  password: "your_password"
  charset: "utf8mb4"

# Oracle Database
database:
  type: "oracle"
  host: "localhost"
  port: 1521
  service_name: "XEPDB1"
  username: "outlook_user"
  password: "your_password"

# CockroachDB
database:
  type: "cockroachdb"
  host: "localhost"
  port: 26257
  database: "outlook_data"
  username: "root"
  password: "your_password"
  sslmode: "require"

# Data Lake configuration examples

# Delta Lake (local)
database:
  type: "deltalake"
  table_path: "./delta-tables/emails"
  app_name: "outlook-ingestor"
  master: "local[*]"
  partition_columns: ["received_date_partition", "sender_domain"]
  z_order_columns: ["received_date", "sender_email"]
  enable_time_travel: true

# Delta Lake (AWS S3)
database:
  type: "deltalake"
  table_path: "s3a://my-bucket/delta-tables/emails"
  app_name: "outlook-ingestor-prod"
  master: "spark://spark-master:7077"
  cloud_provider: "aws"
  cloud_config:
    access_key: "your_access_key"
    secret_key: "your_secret_key"
    region: "us-west-2"

# Apache Iceberg (Hadoop catalog)
database:
  type: "iceberg"
  catalog_type: "hadoop"
  warehouse_path: "./iceberg-warehouse"
  namespace: "outlook_data"
  table_name: "emails"
  enable_compaction: true

# Apache Iceberg (AWS Glue catalog)
database:
  type: "iceberg"
  catalog_type: "glue"
  catalog_config:
    warehouse: "s3://my-bucket/iceberg-warehouse"
    region: "us-west-2"
  namespace: "outlook_analytics"
  table_name: "emails"

# ClickHouse (local)
database:
  type: "clickhouse"
  host: "localhost"
  port: 8123
  database: "outlook_data"
  username: "default"
  password: "your_password"
  compression: true

# ClickHouse (cluster)
database:
  type: "clickhouse"
  host: "clickhouse-cluster.example.com"
  port: 8123
  database: "outlook_data"
  username: "analytics_user"
  password: "your_password"
  cluster: "outlook_cluster"
  secure: true

# Protocol configurations
protocols:
  graph_api:
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    tenant_id: "your_tenant_id"
    scopes: ["https://graph.microsoft.com/.default"]

  exchange:
    server: "outlook.office365.com"
    username: "your_email@company.com"
    password: "your_password"
    autodiscover: true

# Storage backend configurations
storage:
  minio:
    endpoint_url: "localhost:9000"
    access_key: "minioadmin"
    secret_key: "minioadmin"
    bucket_name: "email-attachments"
    use_ssl: false

  aws_s3:
    access_key: "your_aws_access_key"
    secret_key: "your_aws_secret_key"
    bucket_name: "email-attachments-prod"
    region: "us-east-1"

  azure_blob:
    connection_string: "DefaultEndpointsProtocol=https;AccountName=..."
    container_name: "email-attachments"

# Enhanced attachment processing
attachment_processing:
  storage_strategy: "hybrid"
  size_threshold: 1048576  # 1MB
  enable_compression: true
  enable_deduplication: true
  enable_virus_scanning: false
  max_attachment_size: 52428800  # 50MB

  storage_rules:
    - name: "large_files"
      condition: "size > 5*1024*1024"
      strategy: "storage_only"
      storage_backend: "aws_s3"
    - name: "medium_files"
      condition: "size > 1024*1024 and size <= 5*1024*1024"
      strategy: "hybrid"
      storage_backend: "minio"
    - name: "small_files"
      condition: "size <= 1024*1024"
      strategy: "database_only"

# Processing settings
processing:
  batch_size: 1000
  max_workers: 10
  timeout_seconds: 300
  retry_attempts: 3
  retry_delay: 1.0

# Email settings
email:
  extract_attachments: true
  include_folders:
    - "Inbox"
    - "Sent Items"
    - "Archive"
  exclude_folders:
    - "Deleted Items"
    - "Junk Email"

# Security settings
security:
  encrypt_credentials: true
  master_key: "your_encryption_key"
  enable_audit_logging: true

# Monitoring settings
monitoring:
  enable_metrics: true
  metrics_port: 8080
  health_check_interval: 30
  log_level: "INFO"
```

### Environment Variables

```bash
# Database settings
export DATABASE__HOST=localhost
export DATABASE__PORT=5432
export DATABASE__USERNAME=postgres
export DATABASE__PASSWORD=your_password

# Graph API settings
export PROTOCOLS__GRAPH_API__CLIENT_ID=your_client_id
export PROTOCOLS__GRAPH_API__CLIENT_SECRET=your_client_secret
export PROTOCOLS__GRAPH_API__TENANT_ID=your_tenant_id

# Storage backend settings
export STORAGE__MINIO__ACCESS_KEY=minioadmin
export STORAGE__MINIO__SECRET_KEY=minioadmin
export STORAGE__AWS_S3__ACCESS_KEY=your_aws_access_key
export STORAGE__AWS_S3__SECRET_KEY=your_aws_secret_key

# Security settings
export SECURITY__MASTER_KEY=your_encryption_key
export SECURITY__ENCRYPT_CREDENTIALS=true

# Load configuration file
export CONFIG_FILE=/path/to/config.yaml
```

## Performance

### Throughput Benchmarks

| Configuration | Emails/Minute | Attachments/Minute | Memory Usage |
|---------------|---------------|-------------------|--------------|
| Basic (Database Only) | 500-800 | 200-400 | 256MB |
| Hybrid Storage | 800-1200 | 400-800 | 512MB |
| Object Storage Only | 1000-1500 | 600-1200 | 128MB |
| Multi-tier Enterprise | 1200-2000 | 800-1500 | 1GB |

### Performance Optimization

```python
# High-performance configuration
performance_config = {
    "processing": {
        "batch_size": 2000,        # Larger batches for better throughput
        "max_workers": 20,         # More concurrent workers
        "connection_pool_size": 50, # Larger connection pool
        "prefetch_count": 100      # Prefetch more emails
    },

    "attachment_processing": {
        "enable_compression": True,     # Reduce storage I/O
        "enable_deduplication": True,   # Avoid duplicate processing
        "concurrent_uploads": 10,       # Parallel storage uploads
        "chunk_size": 8192             # Optimal chunk size for uploads
    },

    "storage": {
        "connection_timeout": 30,       # Reasonable timeout
        "retry_attempts": 3,           # Automatic retries
        "use_connection_pooling": True  # Reuse connections
    }
}
```

### Memory Management

```mermaid
graph LR
    A[Email Batch] --> B{Size Check}
    B -->|Small| C[Database Storage]
    B -->|Medium| D[Hybrid Processing]
    B -->|Large| E[Stream to Object Storage]

    C --> F[Memory: ~1MB per email]
    D --> G[Memory: ~100KB per email]
    E --> H[Memory: ~10KB per email]

    F --> I[Total: 256MB for 1000 emails]
    G --> J[Total: 100MB for 1000 emails]
    H --> K[Total: 10MB for 1000 emails]
```

### Scaling Recommendations

#### Small Deployments (< 10,000 emails/day)
- **Configuration**: Basic database storage
- **Resources**: 2 CPU cores, 4GB RAM
- **Storage**: PostgreSQL with SSD storage

#### Medium Deployments (10,000 - 100,000 emails/day)
- **Configuration**: Hybrid storage with MinIO
- **Resources**: 4 CPU cores, 8GB RAM
- **Storage**: PostgreSQL + MinIO cluster

#### Large Deployments (100,000+ emails/day)
- **Configuration**: Multi-tier object storage
- **Resources**: 8+ CPU cores, 16GB+ RAM
- **Storage**: PostgreSQL + AWS S3/Azure Blob + CDN

## Advanced Usage

### Protocol Adapters

#### Microsoft Graph API Adapter
- **Features**: OAuth2 authentication, rate limiting, pagination support
- **Configuration**: Client ID, Client Secret, Tenant ID
- **Usage**: Modern REST API for Office 365 and Outlook.com

```python
from evolvishub_outlook_ingestor.protocols import GraphAPIAdapter

adapter = GraphAPIAdapter("graph_api", {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "tenant_id": "your_tenant_id",
    "rate_limit": 100,  # requests per minute
})
```

#### Exchange Web Services (EWS) Adapter
- **Features**: Basic and OAuth2 authentication, connection pooling
- **Configuration**: Server URL, credentials, timeout settings
- **Usage**: On-premises Exchange servers and Exchange Online

```python
from evolvishub_outlook_ingestor.protocols import ExchangeWebServicesAdapter

adapter = ExchangeWebServicesAdapter("exchange", {
    "server": "outlook.office365.com",
    "username": "your_email@company.com",
    "password": "your_password",
    "auth_type": "basic",  # or "oauth2"
})
```

#### IMAP/POP3 Adapter
- **Features**: SSL/TLS support, folder synchronization, UID tracking
- **Configuration**: Server details, authentication credentials
- **Usage**: Standard email protocols for broad compatibility

```python
from evolvishub_outlook_ingestor.protocols import IMAPAdapter

adapter = IMAPAdapter("imap", {
    "server": "outlook.office365.com",
    "port": 993,
    "username": "your_email@company.com",
    "password": "your_password",
    "use_ssl": True,
})
```

### Database Connectors

#### PostgreSQL Connector
- **Features**: Async operations, connection pooling, JSON fields, full-text search
- **Schema**: Optimized tables with proper indexes for email data
- **Performance**: Batch operations, transaction support

```python
from evolvishub_outlook_ingestor.connectors import PostgreSQLConnector

connector = PostgreSQLConnector("postgresql", {
    "host": "localhost",
    "port": 5432,
    "database": "outlook_data",
    "username": "postgres",
    "password": "your_password",
    "pool_size": 20,
})
```

#### MongoDB Connector
- **Features**: Document storage, GridFS for large attachments, aggregation pipelines
- **Schema**: Flexible document structure with proper indexing
- **Scalability**: Horizontal scaling support, replica sets

```python
from evolvishub_outlook_ingestor.connectors import MongoDBConnector

connector = MongoDBConnector("mongodb", {
    "host": "localhost",
    "port": 27017,
    "database": "outlook_data",
    "username": "mongo_user",
    "password": "your_password",
})
```

### Data Processors

#### Email Processor
- **Features**: Content normalization, HTML to text conversion, duplicate detection
- **Capabilities**: Email validation, link extraction, encoding detection
- **Configuration**: Customizable processing rules

```python
from evolvishub_outlook_ingestor.processors import EmailProcessor

processor = EmailProcessor("email", {
    "normalize_content": True,
    "extract_links": True,
    "validate_addresses": True,
    "html_to_text": True,
    "remove_duplicates": True,
})
```

#### Attachment Processor
- **Features**: File type detection, virus scanning hooks, metadata extraction
- **Security**: Size validation, type filtering, content analysis
- **Optimization**: Image compression, hash calculation

```python
from evolvishub_outlook_ingestor.processors import AttachmentProcessor

processor = AttachmentProcessor("attachment", {
    "max_attachment_size": 50 * 1024 * 1024,  # 50MB
    "scan_for_viruses": True,
    "extract_metadata": True,
    "calculate_hashes": True,
    "compress_images": True,
})
```

## 🔧 Advanced Usage

### Hybrid Storage Configuration

```python
import asyncio
from evolvishub_outlook_ingestor.processors.enhanced_attachment_processor import (
    EnhancedAttachmentProcessor,
    StorageStrategy
)
from evolvishub_outlook_ingestor.connectors.minio_connector import MinIOConnector
from evolvishub_outlook_ingestor.connectors.aws_s3_connector import AWSS3Connector

async def setup_hybrid_storage():
    # Configure storage backends
    minio_config = {
        "endpoint_url": "localhost:9000",
        "access_key": "minioadmin",
        "secret_key": "minioadmin",
        "bucket_name": "email-attachments-hot",
        "use_ssl": False
    }

    s3_config = {
        "access_key": "your_aws_access_key",
        "secret_key": "your_aws_secret_key",
        "bucket_name": "email-attachments-archive",
        "region": "us-east-1"
    }

    # Initialize storage connectors
    minio_connector = MinIOConnector("hot_storage", minio_config)
    s3_connector = AWSS3Connector("archive_storage", s3_config)

    # Configure enhanced processor with storage rules
    processor_config = {
        "storage_strategy": "hybrid",
        "size_threshold": 1024 * 1024,  # 1MB
        "enable_compression": True,
        "enable_deduplication": True,
        "storage_rules": [
            {
                "name": "large_files",
                "condition": "size > 5*1024*1024",  # Files > 5MB
                "strategy": "storage_only",
                "storage_backend": "archive_storage"
            },
            {
                "name": "medium_files",
                "condition": "size > 1024*1024 and size <= 5*1024*1024",
                "strategy": "hybrid",
                "storage_backend": "hot_storage"
            },
            {
                "name": "small_files",
                "condition": "size <= 1024*1024",
                "strategy": "database_only"
            }
        ]
    }

    # Create enhanced processor
    processor = EnhancedAttachmentProcessor("hybrid_attachments", processor_config)

    # Add storage backends
    async with minio_connector, s3_connector:
        await processor.add_storage_backend("hot_storage", minio_connector)
        await processor.add_storage_backend("archive_storage", s3_connector)

        # Process emails with hybrid storage
        result = await processor.process(email_with_attachments)

        # Generate secure URLs for attachment access
        for storage_info in result.metadata.get("storage_infos", []):
            if storage_info.get("storage_backend"):
                backend = processor.storage_backends[storage_info["storage_backend"]]
                secure_url = await backend.generate_presigned_url(
                    storage_info["storage_location"],
                    expires_in=3600  # 1 hour
                )
                print(f"Secure URL: {secure_url}")

asyncio.run(setup_hybrid_storage())
```

### Custom Protocol Adapter

```python
from evolvishub_outlook_ingestor.protocols import BaseProtocol
from evolvishub_outlook_ingestor.core.data_models import EmailMessage

class CustomProtocol(BaseProtocol):
    async def _fetch_emails_impl(self, **kwargs):
        # Implement custom email fetching logic
        emails = []
        # ... fetch emails from custom source
        return emails

# Use custom protocol
ingestor = OutlookIngestor(
    settings=settings,
    protocol_adapters={"custom": CustomProtocol("custom", config)}
)
```

### Batch Processing with Progress Tracking

```python
from evolvishub_outlook_ingestor.core.data_models import BatchProcessingConfig

async def process_with_progress():
    def progress_callback(processed, total, rate):
        print(f"Progress: {processed}/{total} ({rate:.2f} emails/sec)")
    
    batch_config = BatchProcessingConfig(
        batch_size=500,
        max_workers=8,
        progress_callback=progress_callback
    )
    
    result = await ingestor.process_emails(
        protocol="exchange",
        database="mongodb",
        batch_config=batch_config
    )
```

### Database Transactions

```python
from evolvishub_outlook_ingestor.connectors import PostgreSQLConnector

async def transactional_processing():
    connector = PostgreSQLConnector("postgres", config)
    await connector.initialize()
    
    async with connector.transaction() as tx:
        # All operations within this block are transactional
        for email in emails:
            await connector.store_email(email, transaction=tx)
        # Automatically commits on success, rolls back on error
```

## 🏗️ Architecture

### Component Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Protocols     │    │   Processors     │    │   Connectors    │
│                 │    │                  │    │                 │
│ • Exchange EWS  │───▶│ • Email Proc.    │───▶│ • PostgreSQL    │
│ • Graph API     │    │ • Attachment     │    │ • MongoDB       │
│ • IMAP/POP3     │    │ • Batch Proc.    │    │ • MySQL         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │   Core Framework    │
                    │                     │
                    │ • Configuration     │
                    │ • Logging           │
                    │ • Error Handling    │
                    │ • Retry Logic       │
                    │ • Metrics           │
                    └─────────────────────┘
```

### Design Patterns

- **Strategy Pattern**: Interchangeable protocol adapters
- **Factory Pattern**: Dynamic component creation
- **Repository Pattern**: Database abstraction
- **Observer Pattern**: Progress and metrics tracking
- **Circuit Breaker**: Fault tolerance

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=evolvishub_outlook_ingestor --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m performance   # Performance tests only

# Run tests in parallel
pytest -n auto
```

## 📊 Performance

### Benchmarks

- **Email Processing**: 1000+ emails/minute
- **Memory Usage**: <100MB for 10K emails
- **Database Throughput**: 500+ inserts/second
- **Concurrent Connections**: 50+ simultaneous

### Optimization Tips

1. **Use Batch Processing**: Process emails in batches for better throughput
2. **Enable Connection Pooling**: Reuse database connections
3. **Configure Rate Limiting**: Avoid API throttling
4. **Monitor Memory Usage**: Use streaming for large datasets
5. **Tune Worker Count**: Match your system's CPU cores

## 🔍 Monitoring

### Metrics Collection

```python
# Enable Prometheus metrics
settings.monitoring.enable_metrics = True
settings.monitoring.metrics_port = 8000

# Access metrics endpoint
# http://localhost:8000/metrics
```

### Health Checks

```python
# Check component health
status = await ingestor.get_status()
print(f"Protocol Status: {status['protocols']}")
print(f"Database Status: {status['database']}")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/evolvisai/metcal.git
cd metcal/shared/libs/evolvis-outlook-ingestor

# Install development dependencies
pip install -e ".[dev]"

# Run pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 📄 License

This project is licensed under the Evolvis AI License - see the [LICENSE](LICENSE) file for details.

## 📚 API Reference

### Core Components

**Protocol Adapters**
- `GraphAPIAdapter`: Microsoft Graph API integration
- `ExchangeWebServicesAdapter`: Exchange Web Services (EWS) support
- `IMAPAdapter`: IMAP protocol support

**Database Connectors**
- `PostgreSQLConnector`: PostgreSQL database integration
- `MongoDBConnector`: MongoDB database integration

**Data Processors**
- `EmailProcessor`: Email content processing and normalization
- `AttachmentProcessor`: Attachment handling and security scanning

**Security Utilities**
- `SecureCredentialManager`: Credential encryption and management
- `CredentialMasker`: Sensitive data masking for logs
- `InputSanitizer`: Input validation and sanitization

### Configuration Reference

```python
# Complete configuration example
config = {
    "graph_api": {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "tenant_id": "your_tenant_id",
        "rate_limit": 100,  # requests per minute
        "timeout": 30,      # request timeout in seconds
    },
    "database": {
        "host": "localhost",
        "port": 5432,
        "database": "outlook_ingestor",
        "username": "ingestor_user",
        "password": "secure_password",
        "ssl_mode": "require",
        "enable_connection_pooling": True,
        "pool_size": 10,
    },
    "email_processing": {
        "normalize_content": True,
        "extract_links": True,
        "validate_addresses": True,
        "html_to_text": True,
        "remove_duplicates": True,
    },
    "attachment_processing": {
        "max_attachment_size": 10 * 1024 * 1024,  # 10MB
        "extract_metadata": True,
        "calculate_hashes": True,
        "scan_for_viruses": False,
    }
}
```

### Error Handling

```python
from evolvishub_outlook_ingestor.core.exceptions import (
    ConnectionError,
    AuthenticationError,
    DatabaseError,
    ProcessingError,
    ValidationError,
)

try:
    await protocol.fetch_emails()
except AuthenticationError:
    # Handle authentication issues
    print("Check your API credentials")
except ConnectionError:
    # Handle network/connection issues
    print("Check network connectivity")
except ProcessingError as e:
    # Handle processing errors
    print(f"Processing failed: {e}")
```

## Support and Documentation

### Documentation Resources
- **[Storage Architecture Guide](docs/STORAGE_ARCHITECTURE.md)** - Comprehensive guide to hybrid storage configuration
- **[Migration Guide](docs/MIGRATION_GUIDE.md)** - Step-by-step migration from basic to hybrid storage
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation with examples
- **[Performance Tuning](docs/PERFORMANCE_TUNING.md)** - Optimization guidelines for large-scale deployments

### Community and Support
- **[GitHub Issues](https://github.com/evolvisai/metcal/issues)** - Bug reports and feature requests
- **[GitHub Discussions](https://github.com/evolvisai/metcal/discussions)** - Community discussions and Q&A
- **[Examples Directory](examples/)** - Comprehensive usage examples and tutorials

### Enterprise Support
For enterprise deployments requiring dedicated support, custom integrations, or professional services, please contact our team for tailored solutions and SLA-backed support options.

## Technical Specifications

### Supported Platforms
- **Operating Systems**: Linux (Ubuntu 18.04+, CentOS 7+), macOS (10.15+), Windows (10+)
- **Python Versions**: 3.9, 3.10, 3.11, 3.12
- **Database Systems**: PostgreSQL 12+, MongoDB 4.4+, MySQL 8.0+
- **Object Storage**: MinIO, AWS S3, Azure Blob Storage, Google Cloud Storage

### Performance Characteristics
- **Throughput**: Up to 2,000 emails/minute with hybrid storage
- **Concurrency**: Support for 50+ concurrent processing workers
- **Memory Efficiency**: <10KB per email with object storage strategy
- **Storage Optimization**: Up to 70% reduction in database size with intelligent routing

### Security Compliance
- **Encryption**: AES-256 encryption for credentials and sensitive data
- **Authentication**: OAuth2, Basic Auth, and certificate-based authentication
- **Access Control**: Role-based access control and audit logging
- **Compliance**: GDPR, HIPAA, and SOX compliance features available

## Acknowledgments

This project is built on top of excellent open-source technologies:

- **[Pydantic](https://pydantic.dev/)** - Data validation and settings management
- **[SQLAlchemy](https://sqlalchemy.org/)** - Database ORM with async support
- **[asyncio](https://docs.python.org/3/library/asyncio.html)** - Asynchronous programming framework
- **[pytest](https://pytest.org/)** - Testing framework with async support
- **[Black](https://black.readthedocs.io/)**, **[isort](https://pycqa.github.io/isort/)**, **[mypy](https://mypy.readthedocs.io/)** - Code quality and type checking tools

## License

### Evolvis AI License

This software is proprietary to **Evolvis AI** and is protected by copyright and other intellectual property laws.

#### 📋 **License Terms**

- **✅ Evaluation and Non-Commercial Use**: This package is available for evaluation, research, and non-commercial use
- **⚠️ Commercial Use Restrictions**: Commercial or production use of this library requires a valid Evolvis AI License
- **🚫 Redistribution Prohibited**: Redistribution or commercial use without proper licensing is strictly prohibited

#### 💼 **Commercial Licensing**

For commercial licensing, production deployments, or enterprise use, please contact:

**Montgomery Miralles**
📧 **Email**: [m.miralles@evolvis.ai](mailto:m.miralles@evolvis.ai)
🏢 **Company**: Evolvis AI
🌐 **Website**: [https://evolvis.ai](https://evolvis.ai)

#### ⚖️ **Important Notice**

> **Commercial users must obtain proper licensing before deploying this software in production environments.** Unauthorized commercial use may result in legal action. Contact Montgomery Miralles for licensing agreements and compliance requirements.

#### 📄 **Full License**

For complete license terms and conditions, see the [LICENSE](LICENSE) file included with this distribution.

---

**Evolvishub Outlook Ingestor** - Enterprise-grade email ingestion with intelligent hybrid storage architecture.
