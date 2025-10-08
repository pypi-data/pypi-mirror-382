"""
PostgreSQL database connector for Evolvishub Outlook Ingestor.

This module provides a concrete implementation of the PostgreSQL database connector
for storing and retrieving email data from Microsoft Outlook.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from decimal import Decimal
import json

from evolvishub_outlook_ingestor.connectors.base_connector import BaseConnector
from evolvishub_outlook_ingestor.core.data_models import (
    EmailMessage, EmailAttachment, OutlookFolder, ProcessingResult
)
from evolvishub_outlook_ingestor.core.exceptions import DatabaseError, ConnectionError


class PostgreSQLConnector(BaseConnector):
    """PostgreSQL database connector for email data."""
    
    def __init__(self, name: str, config: Dict[str, Any], **kwargs):
        super().__init__(name, config, **kwargs)
        self._validate_config(['host', 'database', 'username'])
        
        # PostgreSQL specific configuration
        self.host = config['host']
        self.port = config.get('port', 5432)
        self.database = config['database']
        self.username = config['username']
        self.password = config.get('password', '')
        self.ssl_mode = config.get('ssl_mode', 'prefer')
        
        self.pool = None
    
    async def initialize(self) -> None:
        """Initialize the PostgreSQL connection pool."""
        try:
            import asyncpg
            
            # Build connection string
            dsn = f"postgresql://{self.username}"
            if self.password:
                dsn += f":{self.password}"
            dsn += f"@{self.host}:{self.port}/{self.database}"
            
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                dsn,
                min_size=self.config.get('min_pool_size', 5),
                max_size=self.config.get('max_pool_size', 20),
                command_timeout=self.config.get('command_timeout', 60),
                server_settings={
                    'application_name': f'evolvishub-outlook-ingestor-{self.name}',
                    'timezone': 'UTC'
                }
            )
            
            # Create tables if they don't exist
            await self._create_tables()
            
            self.logger.info(f"PostgreSQL connector '{self.name}' initialized successfully")
            
        except ImportError:
            raise ConnectionError("asyncpg library not installed. Install with: pip install asyncpg")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize PostgreSQL connector: {str(e)}")
    
    async def disconnect(self) -> None:
        """Close the PostgreSQL connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            self.logger.info(f"PostgreSQL connector '{self.name}' disconnected")
    
    async def _create_tables(self) -> None:
        """Create necessary tables for email storage."""
        async with self.pool.acquire() as conn:
            # Create emails table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id VARCHAR(255) PRIMARY KEY,
                    message_id VARCHAR(255),
                    conversation_id VARCHAR(255),
                    subject TEXT,
                    body TEXT,
                    body_preview TEXT,
                    body_type VARCHAR(50) DEFAULT 'text',
                    is_html BOOLEAN DEFAULT FALSE,
                    sender_email VARCHAR(255),
                    sender_name VARCHAR(255),
                    from_email VARCHAR(255),
                    from_name VARCHAR(255),
                    to_recipients JSONB DEFAULT '[]',
                    cc_recipients JSONB DEFAULT '[]',
                    bcc_recipients JSONB DEFAULT '[]',
                    reply_to JSONB DEFAULT '[]',
                    sent_date TIMESTAMP WITH TIME ZONE,
                    received_date TIMESTAMP WITH TIME ZONE,
                    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    modified_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    importance VARCHAR(20) DEFAULT 'normal',
                    sensitivity VARCHAR(20) DEFAULT 'normal',
                    priority VARCHAR(20),
                    is_read BOOLEAN DEFAULT FALSE,
                    is_draft BOOLEAN DEFAULT FALSE,
                    has_attachments BOOLEAN DEFAULT FALSE,
                    is_flagged BOOLEAN DEFAULT FALSE,
                    folder_id VARCHAR(255),
                    folder_path TEXT,
                    headers JSONB DEFAULT '{}',
                    internet_headers JSONB DEFAULT '{}',
                    categories JSONB DEFAULT '[]',
                    in_reply_to VARCHAR(255),
                    references JSONB DEFAULT '[]',
                    size INTEGER,
                    extended_properties JSONB DEFAULT '{}'
                )
            """)
            
            # Create attachments table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS email_attachments (
                    id VARCHAR(255) PRIMARY KEY,
                    email_id VARCHAR(255) REFERENCES emails(id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    content_type VARCHAR(255),
                    size INTEGER,
                    attachment_type VARCHAR(50) DEFAULT 'file',
                    is_inline BOOLEAN DEFAULT FALSE,
                    content_id VARCHAR(255),
                    content_location VARCHAR(255),
                    content_bytes BYTEA,
                    download_url TEXT,
                    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    modified_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Create folders table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS outlook_folders (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    display_name VARCHAR(255),
                    parent_folder_id VARCHAR(255),
                    folder_path TEXT,
                    folder_type VARCHAR(50),
                    total_item_count INTEGER DEFAULT 0,
                    unread_item_count INTEGER DEFAULT 0,
                    child_folder_count INTEGER DEFAULT 0,
                    is_hidden BOOLEAN DEFAULT FALSE,
                    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    modified_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Create indexes for better performance
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_emails_message_id ON emails(message_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_emails_conversation_id ON emails(conversation_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_emails_sent_date ON emails(sent_date)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_emails_received_date ON emails(received_date)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_emails_folder_id ON emails(folder_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_emails_sender_email ON emails(sender_email)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_attachments_email_id ON email_attachments(email_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_folders_parent_id ON outlook_folders(parent_folder_id)")
    
    async def store_email(self, email: EmailMessage) -> bool:
        """Store an email message in the database."""
        try:
            async with self.pool.acquire() as conn:
                # Convert email addresses to JSON
                to_recipients = [{"email": addr.email, "name": addr.name} for addr in email.to_recipients]
                cc_recipients = [{"email": addr.email, "name": addr.name} for addr in email.cc_recipients]
                bcc_recipients = [{"email": addr.email, "name": addr.name} for addr in email.bcc_recipients]
                reply_to = [{"email": addr.email, "name": addr.name} for addr in email.reply_to]
                
                # Insert email
                await conn.execute("""
                    INSERT INTO emails (
                        id, message_id, conversation_id, subject, body, body_preview,
                        body_type, is_html, sender_email, sender_name, from_email, from_name,
                        to_recipients, cc_recipients, bcc_recipients, reply_to,
                        sent_date, received_date, importance, sensitivity, priority,
                        is_read, is_draft, has_attachments, is_flagged,
                        folder_id, folder_path, headers, internet_headers,
                        categories, in_reply_to, references, size, extended_properties
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12,
                        $13, $14, $15, $16, $17, $18, $19, $20, $21,
                        $22, $23, $24, $25, $26, $27, $28, $29,
                        $30, $31, $32, $33, $34
                    ) ON CONFLICT (id) DO UPDATE SET
                        subject = EXCLUDED.subject,
                        body = EXCLUDED.body,
                        modified_date = NOW()
                """, 
                    email.id, email.message_id, email.conversation_id,
                    email.subject, email.body, email.body_preview,
                    email.body_type, email.is_html,
                    email.sender.email if email.sender else None,
                    email.sender.name if email.sender else None,
                    email.from_address.email if email.from_address else None,
                    email.from_address.name if email.from_address else None,
                    json.dumps(to_recipients), json.dumps(cc_recipients),
                    json.dumps(bcc_recipients), json.dumps(reply_to),
                    email.sent_date, email.received_date,
                    email.importance.value, email.sensitivity.value, email.priority,
                    email.is_read, email.is_draft, email.has_attachments, email.is_flagged,
                    email.folder_id, email.folder_path,
                    json.dumps(email.headers), json.dumps(email.internet_headers),
                    json.dumps(email.categories), email.in_reply_to,
                    json.dumps(email.references), email.size,
                    json.dumps(email.extended_properties)
                )
                
                # Store attachments
                for attachment in email.attachments:
                    await self.store_attachment(attachment, email.id, conn)
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store email {email.id}: {str(e)}")
            raise DatabaseError(f"Failed to store email: {str(e)}")
    
    async def store_attachment(self, attachment: EmailAttachment, email_id: str, conn=None) -> bool:
        """Store an email attachment."""
        try:
            if conn is None:
                async with self.pool.acquire() as conn:
                    return await self._store_attachment_with_conn(attachment, email_id, conn)
            else:
                return await self._store_attachment_with_conn(attachment, email_id, conn)
        except Exception as e:
            self.logger.error(f"Failed to store attachment {attachment.id}: {str(e)}")
            raise DatabaseError(f"Failed to store attachment: {str(e)}")
    
    async def _store_attachment_with_conn(self, attachment: EmailAttachment, email_id: str, conn) -> bool:
        """Store attachment with existing connection."""
        await conn.execute("""
            INSERT INTO email_attachments (
                id, email_id, name, content_type, size, attachment_type,
                is_inline, content_id, content_location, content_bytes, download_url
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                content_type = EXCLUDED.content_type,
                modified_date = NOW()
        """,
            attachment.id, email_id, attachment.name, attachment.content_type,
            attachment.size, attachment.attachment_type.value, attachment.is_inline,
            attachment.content_id, attachment.content_location,
            attachment.content_bytes, attachment.download_url
        )
        return True

    async def get_email(self, email_id: str) -> Optional[EmailMessage]:
        """Retrieve an email by ID."""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("SELECT * FROM emails WHERE id = $1", email_id)
                if not row:
                    return None

                # Get attachments
                attachment_rows = await conn.fetch(
                    "SELECT * FROM email_attachments WHERE email_id = $1", email_id
                )

                return self._row_to_email(row, attachment_rows)

        except Exception as e:
            self.logger.error(f"Failed to get email {email_id}: {str(e)}")
            raise DatabaseError(f"Failed to get email: {str(e)}")

    async def get_emails_by_folder(self, folder_id: str, limit: int = 100, offset: int = 0) -> List[EmailMessage]:
        """Get emails from a specific folder."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM emails
                    WHERE folder_id = $1
                    ORDER BY received_date DESC
                    LIMIT $2 OFFSET $3
                """, folder_id, limit, offset)

                emails = []
                for row in rows:
                    # Get attachments for this email
                    attachment_rows = await conn.fetch(
                        "SELECT * FROM email_attachments WHERE email_id = $1", row['id']
                    )
                    emails.append(self._row_to_email(row, attachment_rows))

                return emails

        except Exception as e:
            self.logger.error(f"Failed to get emails from folder {folder_id}: {str(e)}")
            raise DatabaseError(f"Failed to get emails from folder: {str(e)}")

    async def store_folder(self, folder: OutlookFolder) -> bool:
        """Store an Outlook folder."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO outlook_folders (
                        id, name, display_name, parent_folder_id, folder_path,
                        folder_type, total_item_count, unread_item_count,
                        child_folder_count, is_hidden
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        display_name = EXCLUDED.display_name,
                        total_item_count = EXCLUDED.total_item_count,
                        unread_item_count = EXCLUDED.unread_item_count,
                        child_folder_count = EXCLUDED.child_folder_count,
                        modified_date = NOW()
                """,
                    folder.id, folder.name, folder.display_name,
                    folder.parent_folder_id, folder.folder_path,
                    folder.folder_type, folder.total_item_count,
                    folder.unread_item_count, folder.child_folder_count,
                    folder.is_hidden
                )
                return True

        except Exception as e:
            self.logger.error(f"Failed to store folder {folder.id}: {str(e)}")
            raise DatabaseError(f"Failed to store folder: {str(e)}")

    async def get_folder(self, folder_id: str) -> Optional[OutlookFolder]:
        """Get a folder by ID."""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("SELECT * FROM outlook_folders WHERE id = $1", folder_id)
                if not row:
                    return None

                return self._row_to_folder(row)

        except Exception as e:
            self.logger.error(f"Failed to get folder {folder_id}: {str(e)}")
            raise DatabaseError(f"Failed to get folder: {str(e)}")

    async def delete_email(self, email_id: str) -> bool:
        """Delete an email and its attachments."""
        try:
            async with self.pool.acquire() as conn:
                # Delete attachments first (cascade should handle this, but being explicit)
                await conn.execute("DELETE FROM email_attachments WHERE email_id = $1", email_id)

                # Delete email
                result = await conn.execute("DELETE FROM emails WHERE id = $1", email_id)

                # Check if any rows were affected
                return "DELETE 1" in result

        except Exception as e:
            self.logger.error(f"Failed to delete email {email_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete email: {str(e)}")

    async def search_emails(self, query: str, limit: int = 100) -> List[EmailMessage]:
        """Search emails by subject or body content."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM emails
                    WHERE subject ILIKE $1 OR body ILIKE $1
                    ORDER BY received_date DESC
                    LIMIT $2
                """, f"%{query}%", limit)

                emails = []
                for row in rows:
                    # Get attachments for this email
                    attachment_rows = await conn.fetch(
                        "SELECT * FROM email_attachments WHERE email_id = $1", row['id']
                    )
                    emails.append(self._row_to_email(row, attachment_rows))

                return emails

        except Exception as e:
            self.logger.error(f"Failed to search emails: {str(e)}")
            raise DatabaseError(f"Failed to search emails: {str(e)}")

    def _row_to_email(self, row: dict, attachment_rows: List[dict]) -> EmailMessage:
        """Convert database row to EmailMessage object."""
        from evolvishub_outlook_ingestor.core.data_models import EmailAddress, EmailImportance, EmailSensitivity

        # Convert JSON fields back to objects
        to_recipients = [EmailAddress(**addr) for addr in json.loads(row['to_recipients'] or '[]')]
        cc_recipients = [EmailAddress(**addr) for addr in json.loads(row['cc_recipients'] or '[]')]
        bcc_recipients = [EmailAddress(**addr) for addr in json.loads(row['bcc_recipients'] or '[]')]
        reply_to = [EmailAddress(**addr) for addr in json.loads(row['reply_to'] or '[]')]

        # Convert attachments
        attachments = []
        for att_row in attachment_rows:
            attachments.append(self._row_to_attachment(att_row))

        return EmailMessage(
            id=row['id'],
            message_id=row['message_id'],
            conversation_id=row['conversation_id'],
            subject=row['subject'],
            body=row['body'],
            body_preview=row['body_preview'],
            body_type=row['body_type'],
            is_html=row['is_html'],
            sender=EmailAddress(email=row['sender_email'], name=row['sender_name']) if row['sender_email'] else None,
            from_address=EmailAddress(email=row['from_email'], name=row['from_name']) if row['from_email'] else None,
            to_recipients=to_recipients,
            cc_recipients=cc_recipients,
            bcc_recipients=bcc_recipients,
            reply_to=reply_to,
            sent_date=row['sent_date'],
            received_date=row['received_date'],
            created_date=row['created_date'],
            modified_date=row['modified_date'],
            importance=EmailImportance(row['importance']),
            sensitivity=EmailSensitivity(row['sensitivity']),
            priority=row['priority'],
            is_read=row['is_read'],
            is_draft=row['is_draft'],
            has_attachments=row['has_attachments'],
            is_flagged=row['is_flagged'],
            folder_id=row['folder_id'],
            folder_path=row['folder_path'],
            attachments=attachments,
            headers=json.loads(row['headers'] or '{}'),
            internet_headers=json.loads(row['internet_headers'] or '{}'),
            categories=json.loads(row['categories'] or '[]'),
            in_reply_to=row['in_reply_to'],
            references=json.loads(row['references'] or '[]'),
            size=row['size'],
            extended_properties=json.loads(row['extended_properties'] or '{}')
        )

    def _row_to_attachment(self, row: dict) -> EmailAttachment:
        """Convert database row to EmailAttachment object."""
        from evolvishub_outlook_ingestor.core.data_models import AttachmentType

        return EmailAttachment(
            id=row['id'],
            name=row['name'],
            content_type=row['content_type'],
            size=row['size'],
            attachment_type=AttachmentType(row['attachment_type']),
            is_inline=row['is_inline'],
            content_id=row['content_id'],
            content_location=row['content_location'],
            content_bytes=row['content_bytes'],
            download_url=row['download_url'],
            created_date=row['created_date'],
            modified_date=row['modified_date']
        )

    def _row_to_folder(self, row: dict) -> OutlookFolder:
        """Convert database row to OutlookFolder object."""
        return OutlookFolder(
            id=row['id'],
            name=row['name'],
            display_name=row['display_name'],
            parent_folder_id=row['parent_folder_id'],
            folder_path=row['folder_path'],
            folder_type=row['folder_type'],
            total_item_count=row['total_item_count'],
            unread_item_count=row['unread_item_count'],
            child_folder_count=row['child_folder_count'],
            is_hidden=row['is_hidden'],
            created_date=row['created_date'],
            modified_date=row['modified_date']
        )

    async def _begin_transaction(self, isolation_level: Optional[str] = None):
        """Begin a database transaction."""
        conn = await self.pool.acquire()
        if isolation_level:
            await conn.execute(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}")
        return await conn.transaction()

    async def _commit_transaction(self, transaction):
        """Commit a database transaction."""
        await transaction.commit()

    async def _rollback_transaction(self, transaction):
        """Rollback a database transaction."""
        await transaction.rollback()

    def _validate_config(self, required_keys: List[str]) -> None:
        """Validate that required configuration keys are present."""
        missing_keys = [key for key in required_keys if key not in self.config]
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the database connection."""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return {
                    "status": "healthy",
                    "database": self.database,
                    "host": self.host,
                    "port": self.port,
                    "pool_size": self.pool.get_size() if self.pool else 0,
                    "test_query_result": result
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "database": self.database,
                "host": self.host,
                "port": self.port
            }
