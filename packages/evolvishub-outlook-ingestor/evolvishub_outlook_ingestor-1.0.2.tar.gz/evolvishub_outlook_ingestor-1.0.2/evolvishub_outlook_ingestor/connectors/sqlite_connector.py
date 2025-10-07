"""
SQLite database connector for Evolvishub Outlook Ingestor.

This module implements the SQLite database connector using aiosqlite
for lightweight, file-based database operations suitable for development,
testing, and small-scale production environments.

Features:
- Async database operations with aiosqlite
- File-based database storage
- In-memory database support for testing
- Proper database schema with indexes
- Batch insert operations
- Transaction support
- JSON fields for email metadata and headers
- WAL mode for better concurrency
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

import aiosqlite
from aiosqlite import Connection

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
        mask_sensitive_data,
        sanitize_input,
    )
    return get_credential_manager, mask_sensitive_data, sanitize_input


class SQLiteConnector(BaseConnector):
    """SQLite database connector using aiosqlite."""
    
    def __init__(self, name: str, config: Dict[str, Any], **kwargs):
        """
        Initialize SQLite connector.
        
        Args:
            name: Connector name
            config: Configuration dictionary containing:
                - database_path: Path to SQLite database file (or ":memory:" for in-memory)
                - enable_wal: Enable WAL mode for better concurrency
                - timeout: Database timeout in seconds
                - check_same_thread: Check same thread (default: False for async)
                - journal_mode: Journal mode (WAL, DELETE, TRUNCATE, PERSIST, MEMORY, OFF)
                - synchronous: Synchronous mode (FULL, NORMAL, OFF)
                - cache_size: Cache size in pages
        """
        # SQLite doesn't use traditional connection pooling, so disable it
        super().__init__(name, config, enable_connection_pooling=False, **kwargs)

        # Get credential manager (lazy loading)
        get_credential_manager, _, _ = _get_security_utils()
        self._credential_manager = get_credential_manager()

        # SQLite configuration
        self.database_path = config.get("database_path", "outlook_data.db")
        self.enable_wal = config.get("enable_wal", True)
        self.timeout = config.get("timeout", 30.0)
        self.check_same_thread = config.get("check_same_thread", False)
        self.journal_mode = config.get("journal_mode", "WAL")
        self.synchronous = config.get("synchronous", "NORMAL")
        self.cache_size = config.get("cache_size", -64000)  # 64MB cache
        
        # Connection
        self.connection: Optional[Connection] = None
        
        # Schema definitions
        self.schema_sql = self._get_schema_sql()
        
        # Ensure database directory exists
        if self.database_path != ":memory:":
            db_dir = Path(self.database_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
    
    async def _initialize_connection(self) -> None:
        """Initialize SQLite connection."""
        try:
            self.logger.info(
                "Connecting to SQLite database",
                database_path=self.database_path,
                connector=self.name
            )
            
            # Connect to SQLite database
            self.connection = await aiosqlite.connect(
                self.database_path,
                timeout=self.timeout,
                check_same_thread=self.check_same_thread
            )
            
            # Configure SQLite for optimal performance
            await self._configure_sqlite()
            
            self.logger.info(
                "SQLite connection established",
                database_path=self.database_path,
                connector=self.name
            )
            
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to SQLite database: {e}",
                database_type="sqlite",
                cause=e
            )
    
    async def _initialize_pool(self) -> None:
        """SQLite doesn't use connection pooling - delegate to single connection."""
        await self._initialize_connection()
    
    async def _cleanup_connection(self) -> None:
        """Cleanup SQLite connection."""
        if self.connection:
            try:
                await self.connection.close()
                self.logger.info("SQLite connection closed", connector=self.name)
            except Exception as e:
                self.logger.warning(
                    "Error closing SQLite connection",
                    connector=self.name,
                    error=str(e)
                )
            finally:
                self.connection = None
    
    async def _cleanup_pool(self) -> None:
        """SQLite doesn't use connection pooling - delegate to single connection."""
        await self._cleanup_connection()
    
    async def _test_connection(self) -> None:
        """Test SQLite connection."""
        if not self.connection:
            raise ConnectionError("No SQLite connection available")
        
        try:
            # Test with a simple query
            async with self.connection.execute("SELECT 1") as cursor:
                result = await cursor.fetchone()
                if result[0] != 1:
                    raise ConnectionError("SQLite connection test failed")
                    
            self.logger.debug("SQLite connection test passed", connector=self.name)
            
        except Exception as e:
            raise ConnectionError(f"SQLite connection test failed: {e}")
    
    async def _configure_sqlite(self) -> None:
        """Configure SQLite for optimal performance."""
        try:
            # Enable WAL mode for better concurrency
            if self.enable_wal and self.database_path != ":memory:":
                await self.connection.execute(f"PRAGMA journal_mode = {self.journal_mode}")
            
            # Set synchronous mode
            await self.connection.execute(f"PRAGMA synchronous = {self.synchronous}")
            
            # Set cache size
            await self.connection.execute(f"PRAGMA cache_size = {self.cache_size}")
            
            # Enable foreign keys
            await self.connection.execute("PRAGMA foreign_keys = ON")
            
            # Set busy timeout
            await self.connection.execute(f"PRAGMA busy_timeout = {int(self.timeout * 1000)}")
            
            await self.connection.commit()
            
            self.logger.debug(
                "SQLite configuration applied",
                journal_mode=self.journal_mode,
                synchronous=self.synchronous,
                cache_size=self.cache_size,
                connector=self.name
            )
            
        except Exception as e:
            self.logger.warning(
                "Failed to configure SQLite",
                connector=self.name,
                error=str(e)
            )
    
    async def _initialize_schema(self) -> None:
        """Initialize SQLite database schema."""
        try:
            self.logger.info("Initializing SQLite schema", connector=self.name)
            
            # Execute schema creation
            for statement in self.schema_sql:
                await self.connection.execute(statement)
            
            await self.connection.commit()
            
            self.logger.info("SQLite schema initialized", connector=self.name)
            
        except Exception as e:
            raise DatabaseError(
                f"Failed to initialize SQLite schema: {e}",
                database_type="sqlite",
                operation="initialize_schema",
                cause=e
            )
    
    def _get_schema_sql(self) -> List[str]:
        """Get SQLite schema SQL statements."""
        return [
            # Emails table
            """
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                message_id TEXT UNIQUE,
                subject TEXT,
                body TEXT,
                body_preview TEXT,
                sender_email TEXT,
                sender_name TEXT,
                received_date TIMESTAMP,
                sent_date TIMESTAMP,
                importance TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                has_attachments BOOLEAN DEFAULT FALSE,
                folder_id TEXT,
                folder_name TEXT,
                categories TEXT,  -- JSON array
                headers TEXT,     -- JSON object
                metadata TEXT,    -- JSON object
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Recipients table
            """
            CREATE TABLE IF NOT EXISTS email_recipients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT NOT NULL,
                recipient_type TEXT NOT NULL,  -- to, cc, bcc
                email_address TEXT NOT NULL,
                display_name TEXT,
                FOREIGN KEY (email_id) REFERENCES emails (id) ON DELETE CASCADE
            )
            """,
            
            # Attachments table
            """
            CREATE TABLE IF NOT EXISTS email_attachments (
                id TEXT PRIMARY KEY,
                email_id TEXT NOT NULL,
                name TEXT NOT NULL,
                content_type TEXT,
                size INTEGER,
                content BLOB,  -- For small attachments stored in database
                content_hash TEXT,
                is_inline BOOLEAN DEFAULT FALSE,
                attachment_type TEXT,
                extended_properties TEXT,  -- JSON object for storage info
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails (id) ON DELETE CASCADE
            )
            """,
            
            # Folders table
            """
            CREATE TABLE IF NOT EXISTS outlook_folders (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                parent_folder_id TEXT,
                folder_type TEXT,
                total_item_count INTEGER DEFAULT 0,
                unread_item_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            
            # Full-text search virtual table for email content
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS emails_fts USING fts5(
                subject, body, sender_name, sender_email,
                content='emails',
                content_rowid='rowid'
            )
            """,
            
            # Triggers to keep FTS table in sync
            """
            CREATE TRIGGER IF NOT EXISTS emails_fts_insert AFTER INSERT ON emails BEGIN
                INSERT INTO emails_fts(rowid, subject, body, sender_name, sender_email)
                VALUES (new.rowid, new.subject, new.body, new.sender_name, new.sender_email);
            END
            """,
            
            """
            CREATE TRIGGER IF NOT EXISTS emails_fts_delete AFTER DELETE ON emails BEGIN
                INSERT INTO emails_fts(emails_fts, rowid, subject, body, sender_name, sender_email)
                VALUES ('delete', old.rowid, old.subject, old.body, old.sender_name, old.sender_email);
            END
            """,
            
            """
            CREATE TRIGGER IF NOT EXISTS emails_fts_update AFTER UPDATE ON emails BEGIN
                INSERT INTO emails_fts(emails_fts, rowid, subject, body, sender_name, sender_email)
                VALUES ('delete', old.rowid, old.subject, old.body, old.sender_name, old.sender_email);
                INSERT INTO emails_fts(rowid, subject, body, sender_name, sender_email)
                VALUES (new.rowid, new.subject, new.body, new.sender_name, new.sender_email);
            END
            """
        ]

    async def _store_email_impl(
        self,
        email: EmailMessage,
        transaction: Optional[Any] = None,
        **kwargs
    ) -> str:
        """Store email in SQLite database."""
        try:
            # Prepare email data
            email_data = self._prepare_email_data(email)

            # Insert email
            await self.connection.execute(
                """
                INSERT OR REPLACE INTO emails (
                    id, message_id, subject, body, body_preview,
                    sender_email, sender_name, received_date, sent_date,
                    importance, is_read, has_attachments, folder_id, folder_name,
                    categories, headers, metadata, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                email_data
            )

            # Store recipients
            if email.recipients:
                await self._store_recipients(email.id, email.recipients)

            # Store attachments
            if email.attachments:
                await self._store_attachments(email.id, email.attachments)

            if not transaction:
                await self.connection.commit()

            return email.id

        except Exception as e:
            if not transaction:
                await self.connection.rollback()
            raise DatabaseError(
                f"Failed to store email in SQLite: {e}",
                database_type="sqlite",
                operation="store_email",
                cause=e
            )

    async def _store_emails_batch_impl(
        self,
        emails: List[EmailMessage],
        transaction: Optional[Any] = None,
        **kwargs
    ) -> List[str]:
        """Store multiple emails in SQLite database."""
        try:
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

            # Batch insert emails
            await self.connection.executemany(
                """
                INSERT OR REPLACE INTO emails (
                    id, message_id, subject, body, body_preview,
                    sender_email, sender_name, received_date, sent_date,
                    importance, is_read, has_attachments, folder_id, folder_name,
                    categories, headers, metadata, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                email_data_batch
            )

            # Batch insert recipients
            if recipients_batch:
                await self.connection.executemany(
                    """
                    INSERT INTO email_recipients (email_id, recipient_type, email_address, display_name)
                    VALUES (?, ?, ?, ?)
                    """,
                    recipients_batch
                )

            # Batch insert attachments
            if attachments_batch:
                await self.connection.executemany(
                    """
                    INSERT OR REPLACE INTO email_attachments (
                        id, email_id, name, content_type, size, content,
                        content_hash, is_inline, attachment_type, extended_properties
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    attachments_batch
                )

            if not transaction:
                await self.connection.commit()

            return stored_ids

        except Exception as e:
            if not transaction:
                await self.connection.rollback()
            raise DatabaseError(
                f"Failed to store emails batch in SQLite: {e}",
                database_type="sqlite",
                operation="store_emails_batch",
                cause=e
            )

    async def _get_email_impl(
        self,
        email_id: str,
        include_attachments: bool = True,
        **kwargs
    ) -> Optional[EmailMessage]:
        """Retrieve email from SQLite database."""
        try:
            # Get email data
            async with self.connection.execute(
                "SELECT * FROM emails WHERE id = ?",
                (email_id,)
            ) as cursor:
                email_row = await cursor.fetchone()

            if not email_row:
                return None

            # Convert row to EmailMessage
            email = self._row_to_email(email_row)

            # Get recipients
            email.recipients = await self._get_recipients(email_id)

            # Get attachments if requested
            if include_attachments:
                email.attachments = await self._get_attachments(email_id)

            return email

        except Exception as e:
            raise DatabaseError(
                f"Failed to retrieve email from SQLite: {e}",
                database_type="sqlite",
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
        """Search emails in SQLite database."""
        try:
            # Build query
            query_parts = ["SELECT * FROM emails WHERE 1=1"]
            params = []

            # Add filters
            if "sender_email" in filters:
                query_parts.append("AND sender_email = ?")
                params.append(filters["sender_email"])

            if "subject_contains" in filters:
                query_parts.append("AND subject LIKE ?")
                params.append(f"%{filters['subject_contains']}%")

            if "date_from" in filters:
                query_parts.append("AND received_date >= ?")
                params.append(filters["date_from"])

            if "date_to" in filters:
                query_parts.append("AND received_date <= ?")
                params.append(filters["date_to"])

            if "folder_id" in filters:
                query_parts.append("AND folder_id = ?")
                params.append(filters["folder_id"])

            if "has_attachments" in filters:
                query_parts.append("AND has_attachments = ?")
                params.append(filters["has_attachments"])

            # Full-text search
            if "search_text" in filters:
                query_parts = ["SELECT emails.* FROM emails JOIN emails_fts ON emails.rowid = emails_fts.rowid WHERE emails_fts MATCH ?"]
                params = [filters["search_text"]]

            # Add sorting
            if sort_by:
                query_parts.append(f"ORDER BY {sort_by} {sort_order.upper()}")
            else:
                query_parts.append("ORDER BY received_date DESC")

            # Add pagination
            if limit:
                query_parts.append("LIMIT ?")
                params.append(limit)

            if offset > 0:
                query_parts.append("OFFSET ?")
                params.append(offset)

            query = " ".join(query_parts)

            # Execute query
            emails = []
            async with self.connection.execute(query, params) as cursor:
                async for row in cursor:
                    email = self._row_to_email(row)
                    # Get recipients and attachments for each email
                    email.recipients = await self._get_recipients(email.id)
                    email.attachments = await self._get_attachments(email.id)
                    emails.append(email)

            return emails

        except Exception as e:
            raise DatabaseError(
                f"Failed to search emails in SQLite: {e}",
                database_type="sqlite",
                operation="search_emails",
                cause=e
            )

    async def _begin_transaction(self, isolation_level: Optional[str] = None) -> Any:
        """Begin SQLite transaction."""
        try:
            if isolation_level:
                await self.connection.execute(f"BEGIN {isolation_level}")
            else:
                await self.connection.execute("BEGIN")
            return self.connection
        except Exception as e:
            raise TransactionError(f"Failed to begin SQLite transaction: {e}")

    async def _commit_transaction(self, transaction: Any) -> None:
        """Commit SQLite transaction."""
        try:
            await self.connection.commit()
        except Exception as e:
            raise TransactionError(f"Failed to commit SQLite transaction: {e}")

    async def _rollback_transaction(self, transaction: Any) -> None:
        """Rollback SQLite transaction."""
        try:
            await self.connection.rollback()
        except Exception as e:
            raise TransactionError(f"Failed to rollback SQLite transaction: {e}")

    def _prepare_email_data(self, email: EmailMessage) -> tuple:
        """Prepare email data for SQLite insertion."""
        return (
            email.id,
            email.message_id,
            email.subject,
            email.body,
            email.body_preview,
            email.sender.email if email.sender else None,
            email.sender.name if email.sender else None,
            email.received_date,
            email.sent_date,
            email.importance,
            email.is_read,
            bool(email.attachments),
            email.folder.id if email.folder else None,
            email.folder.name if email.folder else None,
            json.dumps(email.categories) if email.categories else None,
            json.dumps(email.headers) if email.headers else None,
            json.dumps(email.metadata) if email.metadata else None,
            datetime.now(timezone.utc)
        )

    def _prepare_attachment_data(self, email_id: str, attachment: EmailAttachment) -> tuple:
        """Prepare attachment data for SQLite insertion."""
        return (
            attachment.id,
            email_id,
            attachment.name,
            attachment.content_type,
            attachment.size,
            attachment.content,
            attachment.content_hash,
            attachment.is_inline,
            attachment.attachment_type,
            json.dumps(attachment.extended_properties) if attachment.extended_properties else None
        )

    def _row_to_email(self, row) -> EmailMessage:
        """Convert SQLite row to EmailMessage."""
        from evolvishub_outlook_ingestor.core.data_models import EmailAddress, OutlookFolder

        # Create sender
        sender = None
        if row[5]:  # sender_email
            sender = EmailAddress(email=row[5], name=row[6])

        # Create folder
        folder = None
        if row[12]:  # folder_id
            folder = OutlookFolder(id=row[12], name=row[13])

        # Parse JSON fields
        categories = json.loads(row[14]) if row[14] else []
        headers = json.loads(row[15]) if row[15] else {}
        metadata = json.loads(row[16]) if row[16] else {}

        return EmailMessage(
            id=row[0],
            message_id=row[1],
            subject=row[2],
            body=row[3],
            body_preview=row[4],
            sender=sender,
            received_date=row[7],
            sent_date=row[8],
            importance=row[9],
            is_read=row[10],
            folder=folder,
            categories=categories,
            headers=headers,
            metadata=metadata
        )

    async def _store_recipients(self, email_id: str, recipients: Dict[str, List]) -> None:
        """Store email recipients."""
        recipient_data = []
        for recipient_type, recipient_list in recipients.items():
            for recipient in recipient_list:
                recipient_data.append((
                    email_id,
                    recipient_type,
                    recipient.email,
                    recipient.name
                ))

        if recipient_data:
            await self.connection.executemany(
                """
                INSERT INTO email_recipients (email_id, recipient_type, email_address, display_name)
                VALUES (?, ?, ?, ?)
                """,
                recipient_data
            )

    async def _store_attachments(self, email_id: str, attachments: List[EmailAttachment]) -> None:
        """Store email attachments."""
        attachment_data = []
        for attachment in attachments:
            attachment_data.append(self._prepare_attachment_data(email_id, attachment))

        if attachment_data:
            await self.connection.executemany(
                """
                INSERT OR REPLACE INTO email_attachments (
                    id, email_id, name, content_type, size, content,
                    content_hash, is_inline, attachment_type, extended_properties
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                attachment_data
            )

    async def _get_recipients(self, email_id: str) -> Dict[str, List]:
        """Get email recipients."""
        from evolvishub_outlook_ingestor.core.data_models import EmailAddress

        recipients = {"to": [], "cc": [], "bcc": []}

        async with self.connection.execute(
            "SELECT recipient_type, email_address, display_name FROM email_recipients WHERE email_id = ?",
            (email_id,)
        ) as cursor:
            async for row in cursor:
                recipient_type, email_address, display_name = row
                recipient = EmailAddress(email=email_address, name=display_name)
                if recipient_type in recipients:
                    recipients[recipient_type].append(recipient)

        return recipients

    async def _get_attachments(self, email_id: str) -> List[EmailAttachment]:
        """Get email attachments."""
        attachments = []

        async with self.connection.execute(
            "SELECT * FROM email_attachments WHERE email_id = ?",
            (email_id,)
        ) as cursor:
            async for row in cursor:
                extended_properties = json.loads(row[9]) if row[9] else {}

                attachment = EmailAttachment(
                    id=row[0],
                    name=row[2],
                    content_type=row[3],
                    size=row[4],
                    content=row[5],
                    content_hash=row[6],
                    is_inline=row[7],
                    attachment_type=row[8],
                    extended_properties=extended_properties
                )
                attachments.append(attachment)

        return attachments
