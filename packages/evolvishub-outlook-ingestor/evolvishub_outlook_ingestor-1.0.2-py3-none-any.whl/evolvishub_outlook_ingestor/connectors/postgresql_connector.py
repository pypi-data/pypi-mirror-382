"""
PostgreSQL database connector for Evolvishub Outlook Ingestor.

This module implements the PostgreSQL database connector using asyncpg
for high-performance async database operations.

Features:
- Async database operations with asyncpg
- Connection pooling for high throughput
- Proper database schema with indexes
- Batch insert operations
- Transaction support
- JSON fields for email metadata and headers
"""

import asyncio
import json
from datetime import datetime
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


class PostgreSQLConnector(BaseConnector):
    """PostgreSQL database connector using asyncpg."""
    
    def __init__(self, name: str, config: Dict[str, Any], **kwargs):
        """
        Initialize PostgreSQL connector.
        
        Args:
            name: Connector name
            config: Configuration dictionary containing:
                - host: Database host
                - port: Database port
                - database: Database name
                - username: Database username
                - password: Database password
                - pool_size: Connection pool size
                - max_overflow: Maximum pool overflow
                - ssl_mode: SSL mode
        """
        super().__init__(name, config, **kwargs)

        # Get credential manager (lazy loading)
        get_credential_manager, _, _, _ = _get_security_utils()
        self._credential_manager = get_credential_manager()

        # PostgreSQL configuration
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 5432)
        self.database = config.get("database", "outlook_data")
        self.username = config.get("username", "postgres")

        # Secure password handling
        password_raw = config.get("password", "")
        password_env = config.get("password_env", "POSTGRES_PASSWORD")

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

        self.ssl_mode = config.get("ssl_mode", "require")  # Default to require SSL
        
        # Connection pool
        self.pool: Optional[Pool] = None
        
        # Schema definitions
        self.schema_sql = self._get_schema_sql()
    
    async def _initialize_connection(self) -> None:
        """Initialize single connection (not used with pooling)."""
        pass  # We use connection pooling instead
    
    async def _initialize_pool(self) -> None:
        """Initialize connection pool."""
        try:
            # Get decrypted password
            password = self._credential_manager.decrypt_credential(self._encrypted_password)

            # Build secure connection string
            _, create_secure_dsn, _, _ = _get_security_utils()
            dsn = create_secure_dsn(
                host=self.host,
                port=self.port,
                database=self.database,
                username=self.username,
                password=password,
                driver="postgresql"
            )
            
            # SSL configuration
            ssl_context = None
            if self.ssl_mode in ["require", "verify-ca", "verify-full"]:
                import ssl
                ssl_context = ssl.create_default_context()
                if self.ssl_mode == "require":
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                dsn,
                min_size=self._pool_config.min_size,
                max_size=self._pool_config.max_size,
                ssl=ssl_context,
                command_timeout=self.config.get("pool_timeout", 30),
            )
            
            # Log with masked credentials
            self.logger.info(
                "PostgreSQL connection pool initialized",
                host=self.host,
                port=self.port,
                database=self.database,
                pool_size=f"{self._pool_config.min_size}-{self._pool_config.max_size}",
                ssl_mode=self.ssl_mode
            )
            
        except Exception as e:
            raise ConnectionError(
                f"Failed to initialize PostgreSQL pool: {e}",
                host=self.host,
                port=self.port,
                cause=e
            )
    
    async def _cleanup_connection(self) -> None:
        """Cleanup single connection (not used with pooling)."""
        pass
    
    async def _cleanup_pool(self) -> None:
        """Cleanup connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def _test_connection(self) -> None:
        """Test database connection."""
        if not self.pool:
            raise ConnectionError("Connection pool not initialized")
        
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                
        except Exception as e:
            raise ConnectionError(
                f"PostgreSQL connection test failed: {e}",
                host=self.host,
                port=self.port,
                cause=e
            )
    
    async def _initialize_schema(self) -> None:
        """Initialize database schema if needed."""
        if not self.pool:
            raise DatabaseError("Connection pool not initialized")
        
        try:
            async with self.pool.acquire() as conn:
                # Execute schema creation
                await conn.execute(self.schema_sql)
                
                self.logger.info("PostgreSQL schema initialized")
                
        except Exception as e:
            self.logger.warning(
                "Failed to initialize schema (may already exist)",
                error=str(e)
            )
    
    def _get_schema_sql(self) -> str:
        """Get SQL for creating database schema."""
        return """
        -- Create emails table
        CREATE TABLE IF NOT EXISTS emails (
            id VARCHAR(255) PRIMARY KEY,
            message_id VARCHAR(255),
            conversation_id VARCHAR(255),
            subject TEXT,
            body TEXT,
            body_type VARCHAR(10) DEFAULT 'text',
            is_html BOOLEAN DEFAULT FALSE,
            
            -- Sender and recipients (JSON arrays)
            sender JSONB,
            from_address JSONB,
            to_recipients JSONB DEFAULT '[]'::jsonb,
            cc_recipients JSONB DEFAULT '[]'::jsonb,
            bcc_recipients JSONB DEFAULT '[]'::jsonb,
            reply_to JSONB DEFAULT '[]'::jsonb,
            
            -- Dates
            sent_date TIMESTAMP,
            received_date TIMESTAMP,
            created_date TIMESTAMP,
            modified_date TIMESTAMP,
            
            -- Properties
            importance VARCHAR(10) DEFAULT 'normal',
            sensitivity VARCHAR(20) DEFAULT 'normal',
            priority VARCHAR(10),
            
            -- Flags
            is_read BOOLEAN DEFAULT FALSE,
            is_draft BOOLEAN DEFAULT FALSE,
            has_attachments BOOLEAN DEFAULT FALSE,
            is_flagged BOOLEAN DEFAULT FALSE,
            
            -- Folder information
            folder_id VARCHAR(255),
            folder_path TEXT,
            
            -- Headers and metadata
            headers JSONB DEFAULT '{}'::jsonb,
            internet_headers JSONB DEFAULT '{}'::jsonb,
            categories JSONB DEFAULT '[]'::jsonb,
            
            -- Threading
            in_reply_to VARCHAR(255),
            references JSONB DEFAULT '[]'::jsonb,
            
            -- Size and extended properties
            size INTEGER DEFAULT 0,
            extended_properties JSONB DEFAULT '{}'::jsonb,
            
            -- Timestamps
            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create attachments table
        CREATE TABLE IF NOT EXISTS attachments (
            id VARCHAR(255) PRIMARY KEY,
            email_id VARCHAR(255) REFERENCES emails(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            content_type VARCHAR(255),
            size INTEGER DEFAULT 0,
            attachment_type VARCHAR(20) DEFAULT 'file',
            is_inline BOOLEAN DEFAULT FALSE,
            content_id VARCHAR(255),
            content_location TEXT,
            
            -- Content (for small attachments)
            content BYTEA,
            
            -- Metadata
            created_date TIMESTAMP,
            modified_date TIMESTAMP,
            is_safe BOOLEAN,
            scan_result TEXT,
            
            -- Timestamps
            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_emails_message_id ON emails(message_id);
        CREATE INDEX IF NOT EXISTS idx_emails_conversation_id ON emails(conversation_id);
        CREATE INDEX IF NOT EXISTS idx_emails_sent_date ON emails(sent_date);
        CREATE INDEX IF NOT EXISTS idx_emails_received_date ON emails(received_date);
        CREATE INDEX IF NOT EXISTS idx_emails_folder_id ON emails(folder_id);
        CREATE INDEX IF NOT EXISTS idx_emails_folder_path ON emails(folder_path);
        CREATE INDEX IF NOT EXISTS idx_emails_is_read ON emails(is_read);
        CREATE INDEX IF NOT EXISTS idx_emails_has_attachments ON emails(has_attachments);
        CREATE INDEX IF NOT EXISTS idx_emails_ingested_at ON emails(ingested_at);
        
        -- JSON indexes for better query performance
        CREATE INDEX IF NOT EXISTS idx_emails_sender_email ON emails USING GIN ((sender->>'email'));
        CREATE INDEX IF NOT EXISTS idx_emails_headers ON emails USING GIN (headers);
        
        -- Attachment indexes
        CREATE INDEX IF NOT EXISTS idx_attachments_email_id ON attachments(email_id);
        CREATE INDEX IF NOT EXISTS idx_attachments_content_type ON attachments(content_type);
        CREATE INDEX IF NOT EXISTS idx_attachments_size ON attachments(size);
        
        -- Full-text search index on email content
        CREATE INDEX IF NOT EXISTS idx_emails_subject_fts ON emails USING GIN (to_tsvector('english', subject));
        CREATE INDEX IF NOT EXISTS idx_emails_body_fts ON emails USING GIN (to_tsvector('english', body));
        
        -- Update trigger for updated_at
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        DROP TRIGGER IF EXISTS update_emails_updated_at ON emails;
        CREATE TRIGGER update_emails_updated_at
            BEFORE UPDATE ON emails
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """

    async def _store_email_impl(
        self,
        email: EmailMessage,
        transaction: Optional[Any] = None,
        **kwargs
    ) -> str:
        """Store a single email in PostgreSQL."""
        if not self.pool:
            raise DatabaseError("Connection pool not initialized")

        try:
            # Use provided transaction or acquire new connection
            if transaction:
                conn = transaction
            else:
                conn = await self.pool.acquire()

            try:
                # Prepare email data
                email_data = self._prepare_email_data(email)

                # Insert email
                query = """
                INSERT INTO emails (
                    id, message_id, conversation_id, subject, body, body_type, is_html,
                    sender, from_address, to_recipients, cc_recipients, bcc_recipients, reply_to,
                    sent_date, received_date, created_date, modified_date,
                    importance, sensitivity, priority,
                    is_read, is_draft, has_attachments, is_flagged,
                    folder_id, folder_path,
                    headers, internet_headers, categories,
                    in_reply_to, references,
                    size, extended_properties
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7,
                    $8, $9, $10, $11, $12, $13,
                    $14, $15, $16, $17,
                    $18, $19, $20,
                    $21, $22, $23, $24,
                    $25, $26,
                    $27, $28, $29,
                    $30, $31,
                    $32, $33
                )
                ON CONFLICT (id) DO UPDATE SET
                    message_id = EXCLUDED.message_id,
                    subject = EXCLUDED.subject,
                    body = EXCLUDED.body,
                    is_read = EXCLUDED.is_read,
                    updated_at = CURRENT_TIMESTAMP
                """

                await conn.execute(query, *email_data)

                # Store attachments
                if email.attachments:
                    await self._store_attachments(conn, email.id, email.attachments)

                return email.id

            finally:
                if not transaction:
                    await self.pool.release(conn)

        except Exception as e:
            raise DatabaseError(
                f"Failed to store email: {e}",
                database_type=self.name,
                operation="store_email",
                cause=e
            )

    def _prepare_email_data(self, email: EmailMessage) -> tuple:
        """Prepare email data for database insertion."""
        # Convert email addresses to JSON
        def addr_to_dict(addr):
            return {"email": addr.email, "name": addr.name} if addr else None

        def addrs_to_list(addrs):
            return [addr_to_dict(addr) for addr in addrs if addr]

        return (
            email.id,
            email.message_id,
            email.conversation_id,
            email.subject,
            email.body,
            email.body_type,
            email.is_html,
            json.dumps(addr_to_dict(email.sender)),
            json.dumps(addr_to_dict(email.from_address)),
            json.dumps(addrs_to_list(email.to_recipients)),
            json.dumps(addrs_to_list(email.cc_recipients)),
            json.dumps(addrs_to_list(email.bcc_recipients)),
            json.dumps(addrs_to_list(email.reply_to)),
            email.sent_date,
            email.received_date,
            email.created_date,
            email.modified_date,
            email.importance.value if email.importance else 'normal',
            email.sensitivity.value if email.sensitivity else 'normal',
            email.priority,
            email.is_read,
            email.is_draft,
            email.has_attachments,
            email.is_flagged,
            email.folder_id,
            email.folder_path,
            json.dumps(email.headers),
            json.dumps(email.internet_headers),
            json.dumps(email.categories),
            email.in_reply_to,
            json.dumps(email.references),
            email.size,
            json.dumps(email.extended_properties),
        )

    async def _store_attachments(
        self,
        conn: Connection,
        email_id: str,
        attachments: List[EmailAttachment]
    ) -> None:
        """Store email attachments."""
        for attachment in attachments:
            try:
                query = """
                INSERT INTO attachments (
                    id, email_id, name, content_type, size, attachment_type,
                    is_inline, content_id, content_location, content,
                    created_date, modified_date, is_safe, scan_result
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14
                )
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    content_type = EXCLUDED.content_type,
                    size = EXCLUDED.size
                """

                await conn.execute(
                    query,
                    attachment.id,
                    email_id,
                    attachment.name,
                    attachment.content_type,
                    attachment.size,
                    attachment.attachment_type.value,
                    attachment.is_inline,
                    attachment.content_id,
                    attachment.content_location,
                    attachment.content,
                    attachment.created_date,
                    attachment.modified_date,
                    attachment.is_safe,
                    attachment.scan_result,
                )

            except Exception as e:
                self.logger.warning(
                    "Failed to store attachment",
                    attachment_id=attachment.id,
                    email_id=email_id,
                    error=str(e)
                )

    async def _store_emails_batch_impl(
        self,
        emails: List[EmailMessage],
        transaction: Optional[Any] = None,
        **kwargs
    ) -> List[str]:
        """Store multiple emails in batch."""
        if not self.pool:
            raise DatabaseError("Connection pool not initialized")

        stored_ids = []

        try:
            # Use provided transaction or acquire new connection
            if transaction:
                conn = transaction
            else:
                conn = await self.pool.acquire()

            try:
                # Prepare batch data
                email_records = []
                attachment_records = []

                for email in emails:
                    email_data = self._prepare_email_data(email)
                    email_records.append(email_data)

                    # Prepare attachment data
                    for attachment in email.attachments:
                        attachment_data = (
                            attachment.id,
                            email.id,
                            attachment.name,
                            attachment.content_type,
                            attachment.size,
                            attachment.attachment_type.value,
                            attachment.is_inline,
                            attachment.content_id,
                            attachment.content_location,
                            attachment.content,
                            attachment.created_date,
                            attachment.modified_date,
                            attachment.is_safe,
                            attachment.scan_result,
                        )
                        attachment_records.append(attachment_data)

                # Batch insert emails
                if email_records:
                    email_query = """
                    INSERT INTO emails (
                        id, message_id, conversation_id, subject, body, body_type, is_html,
                        sender, from_address, to_recipients, cc_recipients, bcc_recipients, reply_to,
                        sent_date, received_date, created_date, modified_date,
                        importance, sensitivity, priority,
                        is_read, is_draft, has_attachments, is_flagged,
                        folder_id, folder_path,
                        headers, internet_headers, categories,
                        in_reply_to, references,
                        size, extended_properties
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7,
                        $8, $9, $10, $11, $12, $13,
                        $14, $15, $16, $17,
                        $18, $19, $20,
                        $21, $22, $23, $24,
                        $25, $26,
                        $27, $28, $29,
                        $30, $31,
                        $32, $33
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        message_id = EXCLUDED.message_id,
                        subject = EXCLUDED.subject,
                        body = EXCLUDED.body,
                        is_read = EXCLUDED.is_read,
                        updated_at = CURRENT_TIMESTAMP
                    """

                    await conn.executemany(email_query, email_records)
                    stored_ids = [email.id for email in emails]

                # Batch insert attachments
                if attachment_records:
                    attachment_query = """
                    INSERT INTO attachments (
                        id, email_id, name, content_type, size, attachment_type,
                        is_inline, content_id, content_location, content,
                        created_date, modified_date, is_safe, scan_result
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        content_type = EXCLUDED.content_type,
                        size = EXCLUDED.size
                    """

                    await conn.executemany(attachment_query, attachment_records)

                return stored_ids

            finally:
                if not transaction:
                    await self.pool.release(conn)

        except Exception as e:
            raise DatabaseError(
                f"Failed to store emails batch: {e}",
                database_type=self.name,
                operation="store_emails_batch",
                cause=e
            )

    async def _get_email_impl(
        self,
        email_id: str,
        include_attachments: bool = True,
        **kwargs
    ) -> Optional[EmailMessage]:
        """Retrieve an email by ID."""
        if not self.pool:
            raise DatabaseError("Connection pool not initialized")

        try:
            async with self.pool.acquire() as conn:
                # Get email
                query = "SELECT * FROM emails WHERE id = $1"
                row = await conn.fetchrow(query, email_id)

                if not row:
                    return None

                # Get attachments if requested
                attachments = []
                if include_attachments:
                    att_query = "SELECT * FROM attachments WHERE email_id = $1"
                    att_rows = await conn.fetch(att_query, email_id)
                    attachments = [self._row_to_attachment(att_row) for att_row in att_rows]

                return self._row_to_email(row, attachments)

        except Exception as e:
            raise DatabaseError(
                f"Failed to retrieve email: {e}",
                database_type=self.name,
                operation="get_email",
                cause=e
            )

    async def _search_emails_impl(
        self,
        filters: Dict[str, Any],
        limit: Optional[int] = None,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        **kwargs
    ) -> List[EmailMessage]:
        """Search emails based on filters."""
        if not self.pool:
            raise DatabaseError("Connection pool not initialized")

        try:
            async with self.pool.acquire() as conn:
                # Build query
                where_clauses = []
                params = []
                param_count = 0

                for key, value in filters.items():
                    param_count += 1
                    if key == "folder_id":
                        where_clauses.append(f"folder_id = ${param_count}")
                        params.append(value)
                    elif key == "is_read":
                        where_clauses.append(f"is_read = ${param_count}")
                        params.append(value)
                    elif key == "has_attachments":
                        where_clauses.append(f"has_attachments = ${param_count}")
                        params.append(value)
                    elif key == "sender_email":
                        where_clauses.append(f"sender->>'email' = ${param_count}")
                        params.append(value)
                    elif key == "subject_contains":
                        where_clauses.append(f"subject ILIKE ${param_count}")
                        params.append(f"%{value}%")
                    elif key == "date_from":
                        where_clauses.append(f"sent_date >= ${param_count}")
                        params.append(value)
                    elif key == "date_to":
                        where_clauses.append(f"sent_date <= ${param_count}")
                        params.append(value)

                # Build full query
                query = "SELECT * FROM emails"
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)

                # Add sorting
                if sort_by:
                    query += f" ORDER BY {sort_by} {sort_order.upper()}"
                else:
                    query += " ORDER BY received_date DESC"

                # Add pagination
                if limit:
                    param_count += 1
                    query += f" LIMIT ${param_count}"
                    params.append(limit)

                if offset:
                    param_count += 1
                    query += f" OFFSET ${param_count}"
                    params.append(offset)

                # Execute query
                rows = await conn.fetch(query, *params)

                # Convert to EmailMessage objects
                emails = []
                for row in rows:
                    # Get attachments
                    att_query = "SELECT * FROM attachments WHERE email_id = $1"
                    att_rows = await conn.fetch(att_query, row['id'])
                    attachments = [self._row_to_attachment(att_row) for att_row in att_rows]

                    email = self._row_to_email(row, attachments)
                    emails.append(email)

                return emails

        except Exception as e:
            raise DatabaseError(
                f"Failed to search emails: {e}",
                database_type=self.name,
                operation="search_emails",
                cause=e
            )

    def _row_to_email(self, row: dict, attachments: List[EmailAttachment]) -> EmailMessage:
        """Convert database row to EmailMessage."""
        from evolvishub_outlook_ingestor.core.data_models import EmailImportance, EmailSensitivity

        # Parse JSON fields
        def parse_addr(addr_json):
            if not addr_json:
                return None
            addr_data = json.loads(addr_json) if isinstance(addr_json, str) else addr_json
            if addr_data:
                from evolvishub_outlook_ingestor.core.data_models import EmailAddress
                return EmailAddress(email=addr_data.get('email', ''), name=addr_data.get('name', ''))
            return None

        def parse_addrs(addrs_json):
            if not addrs_json:
                return []
            addrs_data = json.loads(addrs_json) if isinstance(addrs_json, str) else addrs_json
            from evolvishub_outlook_ingestor.core.data_models import EmailAddress
            return [EmailAddress(email=addr.get('email', ''), name=addr.get('name', ''))
                   for addr in addrs_data if addr]

        return EmailMessage(
            id=row['id'],
            message_id=row['message_id'],
            conversation_id=row['conversation_id'],
            subject=row['subject'],
            body=row['body'],
            body_type=row['body_type'],
            is_html=row['is_html'],
            sender=parse_addr(row['sender']),
            from_address=parse_addr(row['from_address']),
            to_recipients=parse_addrs(row['to_recipients']),
            cc_recipients=parse_addrs(row['cc_recipients']),
            bcc_recipients=parse_addrs(row['bcc_recipients']),
            reply_to=parse_addrs(row['reply_to']),
            sent_date=row['sent_date'],
            received_date=row['received_date'],
            created_date=row['created_date'],
            modified_date=row['modified_date'],
            importance=EmailImportance(row['importance']) if row['importance'] else EmailImportance.NORMAL,
            sensitivity=EmailSensitivity(row['sensitivity']) if row['sensitivity'] else EmailSensitivity.NORMAL,
            priority=row['priority'],
            is_read=row['is_read'],
            is_draft=row['is_draft'],
            has_attachments=row['has_attachments'],
            is_flagged=row['is_flagged'],
            folder_id=row['folder_id'],
            folder_path=row['folder_path'],
            attachments=attachments,
            headers=json.loads(row['headers']) if row['headers'] else {},
            internet_headers=json.loads(row['internet_headers']) if row['internet_headers'] else {},
            categories=json.loads(row['categories']) if row['categories'] else [],
            in_reply_to=row['in_reply_to'],
            references=json.loads(row['references']) if row['references'] else [],
            size=row['size'],
            extended_properties=json.loads(row['extended_properties']) if row['extended_properties'] else {},
        )

    def _row_to_attachment(self, row: dict) -> EmailAttachment:
        """Convert database row to EmailAttachment."""
        from evolvishub_outlook_ingestor.core.data_models import AttachmentType

        return EmailAttachment(
            id=row['id'],
            name=row['name'],
            content_type=row['content_type'],
            size=row['size'],
            attachment_type=AttachmentType(row['attachment_type']) if row['attachment_type'] else AttachmentType.FILE,
            is_inline=row['is_inline'],
            content_id=row['content_id'],
            content_location=row['content_location'],
            content=row['content'],
            created_date=row['created_date'],
            modified_date=row['modified_date'],
            is_safe=row['is_safe'],
            scan_result=row['scan_result'],
        )

    async def _begin_transaction(self, isolation_level: Optional[str] = None) -> Any:
        """Begin database transaction."""
        if not self.pool:
            raise DatabaseError("Connection pool not initialized")

        conn = await self.pool.acquire()

        # Start transaction
        if isolation_level:
            await conn.execute(f"BEGIN ISOLATION LEVEL {isolation_level}")
        else:
            await conn.execute("BEGIN")

        return conn

    async def _commit_transaction(self, transaction: Any) -> None:
        """Commit database transaction."""
        try:
            await transaction.execute("COMMIT")
        finally:
            await self.pool.release(transaction)

    async def _rollback_transaction(self, transaction: Any) -> None:
        """Rollback database transaction."""
        try:
            await transaction.execute("ROLLBACK")
        finally:
            await self.pool.release(transaction)
