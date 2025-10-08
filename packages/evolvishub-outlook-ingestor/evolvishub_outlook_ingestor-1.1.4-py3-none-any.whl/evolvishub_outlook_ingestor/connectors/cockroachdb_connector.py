"""
CockroachDB database connector for Evolvishub Outlook Ingestor.

This module implements the CockroachDB database connector using asyncpg
for distributed, cloud-native deployments with horizontal scalability.

Features:
- Async database operations with asyncpg
- Connection pooling for high throughput
- Proper database schema with indexes and partitioning
- Batch insert operations with UPSERT statements
- Transaction support with serializable isolation
- JSON fields for email metadata and headers
- Full-text search capabilities
- Optimized for CockroachDB distributed architecture
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

import asyncpg
from asyncpg import Connection, Pool

from evolvishub_outlook_ingestor.connectors.base_connector import BaseConnector
from evolvishub_outlook_ingestor.core.data_models import EmailMessage, EmailAttachment
from evolvishub_outlook_ingestor.core.exceptions import (
    ConnectionError,
    DatabaseError,
    QueryError,
    TransactionError,
)

# Import security utilities with lazy loading to avoid circular imports
def _get_security_utils():
    from evolvishub_outlook_ingestor.utils.security import (
        get_credential_manager,
        create_secure_dsn,
        mask_sensitive_data,
        sanitize_input,
    )
    return get_credential_manager, create_secure_dsn, mask_sensitive_data, sanitize_input


class CockroachDBConnector(BaseConnector):
    """CockroachDB database connector using asyncpg."""
    
    def __init__(self, name: str, config: Dict[str, Any], **kwargs):
        """
        Initialize CockroachDB connector.
        
        Args:
            name: Connector name
            config: Configuration dictionary containing:
                - host: CockroachDB host
                - port: CockroachDB port (default: 26257)
                - database: Database name
                - username: Database username
                - password: Database password
                - cluster: Cluster name for CockroachDB Cloud
                - sslmode: SSL mode (require, prefer, disable)
                - sslcert: SSL certificate file path
                - sslkey: SSL key file path
                - sslrootcert: SSL root certificate file path
                - application_name: Application name for connection
                - pool_size: Connection pool size
                - max_overflow: Maximum pool overflow
                - command_timeout: Command timeout in seconds
                - server_settings: Additional server settings
        """
        super().__init__(name, config, **kwargs)

        # Get credential manager (lazy loading)
        get_credential_manager, create_secure_dsn, _, _ = _get_security_utils()
        self._credential_manager = get_credential_manager()
        self._create_secure_dsn = create_secure_dsn

        # CockroachDB configuration
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 26257)
        self.database = config.get("database", "outlook_data")
        self.username = config.get("username", "root")
        self.cluster = config.get("cluster", "")
        self.sslmode = config.get("sslmode", "require")
        self.sslcert = config.get("sslcert", "")
        self.sslkey = config.get("sslkey", "")
        self.sslrootcert = config.get("sslrootcert", "")
        self.application_name = config.get("application_name", "evolvishub-outlook-ingestor")
        self.command_timeout = config.get("command_timeout", 60)
        self.server_settings = config.get("server_settings", {})

        # Secure password handling
        password_raw = config.get("password", "")
        password_env = config.get("password_env", "COCKROACHDB_PASSWORD")

        # Try to get password from environment first, then from config
        self._password = (
            self._credential_manager.get_credential_from_env(password_env) or
            password_raw
        )

        # Encrypt password for storage
        if self._password:
            self._encrypted_password = self._credential_manager.encrypt_credential(self._password)
        else:
            self._encrypted_password = ""
        
        # Connection pool
        self.pool: Optional[Pool] = None
        
        # Schema definitions
        self.schema_sql = self._get_schema_sql()
    
    async def _initialize_connection(self) -> None:
        """Initialize single CockroachDB connection (not used with pooling)."""
        try:
            # Decrypt password for connection
            password = ""
            if self._encrypted_password:
                password = self._credential_manager.decrypt_credential(self._encrypted_password)
            
            dsn = self._build_dsn(password)
            
            self.logger.info(
                "Connecting to CockroachDB",
                host=self.host,
                database=self.database,
                connector=self.name
            )
            
            self._connection = await asyncpg.connect(
                dsn=dsn,
                command_timeout=self.command_timeout,
                server_settings=self.server_settings
            )
            
            self.logger.info(
                "CockroachDB connection established",
                host=self.host,
                database=self.database,
                connector=self.name
            )
            
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to CockroachDB: {e}",
                database_type="cockroachdb",
                cause=e
            )
    
    async def _initialize_pool(self) -> None:
        """Initialize CockroachDB connection pool."""
        try:
            # Decrypt password for connection
            password = ""
            if self._encrypted_password:
                password = self._credential_manager.decrypt_credential(self._encrypted_password)
            
            dsn = self._build_dsn(password)
            
            self.logger.info(
                "Creating CockroachDB connection pool",
                host=self.host,
                database=self.database,
                pool_size=self._pool_config.max_size,
                connector=self.name
            )
            
            self.pool = await asyncpg.create_pool(
                dsn=dsn,
                min_size=self._pool_config.min_size,
                max_size=self._pool_config.max_size,
                command_timeout=self.command_timeout,
                server_settings=self.server_settings
            )
            
            self.logger.info(
                "CockroachDB connection pool created",
                host=self.host,
                database=self.database,
                connector=self.name
            )
            
        except Exception as e:
            raise ConnectionError(
                f"Failed to create CockroachDB connection pool: {e}",
                database_type="cockroachdb",
                cause=e
            )
    
    async def _cleanup_connection(self) -> None:
        """Cleanup CockroachDB connection."""
        if self._connection:
            try:
                await self._connection.close()
                self.logger.info("CockroachDB connection closed", connector=self.name)
            except Exception as e:
                self.logger.warning(
                    "Error closing CockroachDB connection",
                    connector=self.name,
                    error=str(e)
                )
            finally:
                self._connection = None
    
    async def _cleanup_pool(self) -> None:
        """Cleanup CockroachDB connection pool."""
        if self.pool:
            try:
                await self.pool.close()
                self.logger.info("CockroachDB connection pool closed", connector=self.name)
            except Exception as e:
                self.logger.warning(
                    "Error closing CockroachDB connection pool",
                    connector=self.name,
                    error=str(e)
                )
            finally:
                self.pool = None
    
    async def _test_connection(self) -> None:
        """Test CockroachDB connection."""
        try:
            if self.enable_connection_pooling:
                async with self.pool.acquire() as connection:
                    result = await connection.fetchval("SELECT 1")
                    if result != 1:
                        raise ConnectionError("CockroachDB connection test failed")
            else:
                result = await self._connection.fetchval("SELECT 1")
                if result != 1:
                    raise ConnectionError("CockroachDB connection test failed")
                        
            self.logger.debug("CockroachDB connection test passed", connector=self.name)
            
        except Exception as e:
            raise ConnectionError(f"CockroachDB connection test failed: {e}")
    
    def _build_dsn(self, password: str) -> str:
        """Build CockroachDB connection string."""
        try:
            # Build DSN components
            dsn_parts = [
                f"postgresql://{self.username}:{password}@{self.host}:{self.port}/{self.database}"
            ]
            
            # Add query parameters
            params = []
            
            if self.sslmode:
                params.append(f"sslmode={self.sslmode}")
            
            if self.sslcert:
                params.append(f"sslcert={self.sslcert}")
            
            if self.sslkey:
                params.append(f"sslkey={self.sslkey}")
            
            if self.sslrootcert:
                params.append(f"sslrootcert={self.sslrootcert}")
            
            if self.application_name:
                params.append(f"application_name={self.application_name}")
            
            if self.cluster:
                params.append(f"options=--cluster%3D{self.cluster}")
            
            if params:
                dsn_parts.append("?" + "&".join(params))
            
            dsn = "".join(dsn_parts)
            
            # Use secure DSN creation if available
            return self._create_secure_dsn(dsn, mask_password=True)
            
        except Exception as e:
            raise ConnectionError(f"Failed to build CockroachDB connection string: {e}")
    
    def _get_schema_sql(self) -> List[str]:
        """Get CockroachDB schema SQL statements."""
        return [
            # Emails table with partitioning by received_date
            """
            CREATE TABLE IF NOT EXISTS emails (
                id STRING PRIMARY KEY,
                message_id STRING UNIQUE,
                subject TEXT,
                body TEXT,
                body_preview TEXT,
                sender_email STRING,
                sender_name STRING,
                received_date TIMESTAMPTZ,
                sent_date TIMESTAMPTZ,
                importance STRING,
                is_read BOOL DEFAULT FALSE,
                has_attachments BOOL DEFAULT FALSE,
                folder_id STRING,
                folder_name STRING,
                categories JSONB,  -- JSONB for better performance
                headers JSONB,     -- JSONB for better performance
                metadata JSONB,    -- JSONB for better performance
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            ) PARTITION BY RANGE (received_date)
            """,
            
            # Create partitions for emails table (example for current and next year)
            """
            CREATE TABLE IF NOT EXISTS emails_2024 PARTITION OF emails
            FOR VALUES FROM ('2024-01-01') TO ('2025-01-01')
            """,
            
            """
            CREATE TABLE IF NOT EXISTS emails_2025 PARTITION OF emails
            FOR VALUES FROM ('2025-01-01') TO ('2026-01-01')
            """,
            
            # Recipients table
            """
            CREATE TABLE IF NOT EXISTS email_recipients (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email_id STRING NOT NULL,
                recipient_type STRING NOT NULL CHECK (recipient_type IN ('to', 'cc', 'bcc')),
                email_address STRING NOT NULL,
                display_name STRING,
                CONSTRAINT fk_recipients_email FOREIGN KEY (email_id) REFERENCES emails (id) ON DELETE CASCADE
            )
            """,

            # Attachments table
            """
            CREATE TABLE IF NOT EXISTS email_attachments (
                id STRING PRIMARY KEY,
                email_id STRING NOT NULL,
                name STRING NOT NULL,
                content_type STRING,
                size INT,
                content BYTES,  -- For small attachments stored in database
                content_hash STRING,
                is_inline BOOL DEFAULT FALSE,
                attachment_type STRING,
                extended_properties JSONB,  -- JSONB for storage info
                created_at TIMESTAMPTZ DEFAULT NOW(),
                CONSTRAINT fk_attachments_email FOREIGN KEY (email_id) REFERENCES emails (id) ON DELETE CASCADE
            )
            """,

            # Folders table
            """
            CREATE TABLE IF NOT EXISTS outlook_folders (
                id STRING PRIMARY KEY,
                name STRING NOT NULL,
                parent_folder_id STRING,
                folder_type STRING,
                total_item_count INT DEFAULT 0,
                unread_item_count INT DEFAULT 0,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
            """,

            # Indexes for performance
            "CREATE INDEX IF NOT EXISTS idx_emails_message_id ON emails (message_id)",
            "CREATE INDEX IF NOT EXISTS idx_emails_sender ON emails (sender_email)",
            "CREATE INDEX IF NOT EXISTS idx_emails_received_date ON emails (received_date)",
            "CREATE INDEX IF NOT EXISTS idx_emails_folder ON emails (folder_id)",
            "CREATE INDEX IF NOT EXISTS idx_emails_has_attachments ON emails (has_attachments)",
            "CREATE INDEX IF NOT EXISTS idx_recipients_email_id ON email_recipients (email_id)",
            "CREATE INDEX IF NOT EXISTS idx_recipients_type ON email_recipients (recipient_type)",
            "CREATE INDEX IF NOT EXISTS idx_attachments_email_id ON email_attachments (email_id)",
            "CREATE INDEX IF NOT EXISTS idx_attachments_hash ON email_attachments (content_hash)",
            "CREATE INDEX IF NOT EXISTS idx_folders_parent ON outlook_folders (parent_folder_id)",

            # GIN indexes for JSONB fields for fast JSON queries
            "CREATE INDEX IF NOT EXISTS idx_emails_categories_gin ON emails USING GIN (categories)",
            "CREATE INDEX IF NOT EXISTS idx_emails_headers_gin ON emails USING GIN (headers)",
            "CREATE INDEX IF NOT EXISTS idx_emails_metadata_gin ON emails USING GIN (metadata)",
            "CREATE INDEX IF NOT EXISTS idx_attachments_properties_gin ON email_attachments USING GIN (extended_properties)"
        ]

    async def _initialize_schema(self) -> None:
        """Initialize CockroachDB database schema."""
        try:
            self.logger.info("Initializing CockroachDB schema", connector=self.name)

            if self.enable_connection_pooling:
                async with self.pool.acquire() as connection:
                    await self._execute_schema_statements(connection)
            else:
                await self._execute_schema_statements(self._connection)

            self.logger.info("CockroachDB schema initialized", connector=self.name)

        except Exception as e:
            raise DatabaseError(
                f"Failed to initialize CockroachDB schema: {e}",
                database_type="cockroachdb",
                operation="initialize_schema",
                cause=e
            )

    async def _execute_schema_statements(self, connection: Connection) -> None:
        """Execute schema creation statements."""
        for statement in self.schema_sql:
            try:
                await connection.execute(statement)
            except Exception as e:
                self.logger.warning(
                    "Schema statement failed (may already exist)",
                    statement=statement[:100] + "..." if len(statement) > 100 else statement,
                    error=str(e),
                    connector=self.name
                )

    async def _store_email_impl(
        self,
        email: EmailMessage,
        transaction: Optional[Any] = None,
        **kwargs
    ) -> str:
        """Store email in CockroachDB database."""
        try:
            connection = transaction if transaction else (
                self.pool.acquire() if self.enable_connection_pooling else self._connection
            )

            if self.enable_connection_pooling and not transaction:
                async with connection as conn:
                    return await self._store_email_with_connection(email, conn, transaction)
            else:
                return await self._store_email_with_connection(email, connection, transaction)

        except Exception as e:
            raise DatabaseError(
                f"Failed to store email in CockroachDB: {e}",
                database_type="cockroachdb",
                operation="store_email",
                cause=e
            )

    async def _store_email_with_connection(self, email: EmailMessage, connection: Connection, transaction: Optional[Any] = None) -> str:
        """Store email with specific connection."""
        # Prepare email data
        email_data = self._prepare_email_data(email)

        # Use UPSERT for CockroachDB
        upsert_sql = """
        UPSERT INTO emails (
            id, message_id, subject, body, body_preview,
            sender_email, sender_name, received_date, sent_date,
            importance, is_read, has_attachments, folder_id, folder_name,
            categories, headers, metadata, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
        """

        await connection.execute(upsert_sql, *email_data)

        # Store recipients
        if email.recipients:
            await self._store_recipients_with_connection(connection, email.id, email.recipients)

        # Store attachments
        if email.attachments:
            await self._store_attachments_with_connection(connection, email.id, email.attachments)

        return email.id

    async def _store_emails_batch_impl(
        self,
        emails: List[EmailMessage],
        transaction: Optional[Any] = None,
        **kwargs
    ) -> List[str]:
        """Store multiple emails in CockroachDB database."""
        try:
            connection = transaction if transaction else (
                self.pool.acquire() if self.enable_connection_pooling else self._connection
            )

            if self.enable_connection_pooling and not transaction:
                async with connection as conn:
                    return await self._store_emails_batch_with_connection(emails, conn, transaction)
            else:
                return await self._store_emails_batch_with_connection(emails, connection, transaction)

        except Exception as e:
            raise DatabaseError(
                f"Failed to store emails batch in CockroachDB: {e}",
                database_type="cockroachdb",
                operation="store_emails_batch",
                cause=e
            )

    async def _store_emails_batch_with_connection(self, emails: List[EmailMessage], connection: Connection, transaction: Optional[Any] = None) -> List[str]:
        """Store emails batch with specific connection."""
        stored_ids = []

        # Prepare batch data
        email_data_batch = []
        recipients_batch = []
        attachments_batch = []

        for email in emails:
            email_data = self._prepare_email_data(email)
            email_data_batch.append(email_data)
            stored_ids.append(email.id)

            # Collect recipients
            if email.recipients:
                for recipient_type, recipients in email.recipients.items():
                    for recipient in recipients:
                        recipients_batch.append((
                            email.id,
                            recipient_type,
                            recipient.email,
                            recipient.name
                        ))

            # Collect attachments
            if email.attachments:
                for attachment in email.attachments:
                    attachment_data = self._prepare_attachment_data(email.id, attachment)
                    attachments_batch.append(attachment_data)

        # Batch upsert emails
        if email_data_batch:
            upsert_sql = """
            UPSERT INTO emails (
                id, message_id, subject, body, body_preview,
                sender_email, sender_name, received_date, sent_date,
                importance, is_read, has_attachments, folder_id, folder_name,
                categories, headers, metadata, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
            """
            await connection.executemany(upsert_sql, email_data_batch)

        # Batch insert recipients
        if recipients_batch:
            await connection.executemany(
                """
                INSERT INTO email_recipients (email_id, recipient_type, email_address, display_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT DO NOTHING
                """,
                recipients_batch
            )

        # Batch upsert attachments
        if attachments_batch:
            await connection.executemany(
                """
                UPSERT INTO email_attachments (
                    id, email_id, name, content_type, size, content,
                    content_hash, is_inline, attachment_type, extended_properties
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                attachments_batch
            )

        return stored_ids

    async def _get_email_impl(
        self,
        email_id: str,
        include_attachments: bool = True,
        **kwargs
    ) -> Optional[EmailMessage]:
        """Retrieve email from CockroachDB database."""
        try:
            if self.enable_connection_pooling:
                async with self.pool.acquire() as connection:
                    return await self._get_email_with_connection(email_id, include_attachments, connection)
            else:
                return await self._get_email_with_connection(email_id, include_attachments, self._connection)

        except Exception as e:
            raise DatabaseError(
                f"Failed to retrieve email from CockroachDB: {e}",
                database_type="cockroachdb",
                operation="get_email",
                cause=e
            )

    async def _get_email_with_connection(
        self,
        email_id: str,
        include_attachments: bool,
        connection: Connection
    ) -> Optional[EmailMessage]:
        """Retrieve email with specific connection."""
        # Get email data
        email_row = await connection.fetchrow("SELECT * FROM emails WHERE id = $1", email_id)

        if not email_row:
            return None

        # Convert row to EmailMessage
        email = self._row_to_email(email_row)

        # Get recipients
        email.recipients = await self._get_recipients_with_connection(connection, email_id)

        # Get attachments if requested
        if include_attachments:
            email.attachments = await self._get_attachments_with_connection(connection, email_id)

        return email
