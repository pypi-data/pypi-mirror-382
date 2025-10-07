"""
SQLite database connector for Evolvishub Outlook Ingestor.

This module provides a concrete implementation of the SQLite database connector
for storing and retrieving email data from Microsoft Outlook.
"""

import asyncio
import sqlite3
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
import os

from evolvishub_outlook_ingestor.connectors.base_connector import BaseConnector
from evolvishub_outlook_ingestor.core.data_models import (
    EmailMessage, EmailAttachment, OutlookFolder, ProcessingResult
)
from evolvishub_outlook_ingestor.core.exceptions import DatabaseError, ConnectionError


class SQLiteConnector(BaseConnector):
    """SQLite database connector for email data."""
    
    def __init__(self, name: str, config: Dict[str, Any], **kwargs):
        super().__init__(name, config, **kwargs)
        self._validate_config(['database'])
        
        # SQLite specific configuration
        self.database_path = config['database']
        self.timeout = config.get('timeout', 30.0)
        self.check_same_thread = config.get('check_same_thread', False)
        
        self.connection = None
    
    async def initialize(self) -> None:
        """Initialize the SQLite connection."""
        try:
            import aiosqlite
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
            
            # Create connection
            self.connection = await aiosqlite.connect(
                self.database_path,
                timeout=self.timeout,
                check_same_thread=self.check_same_thread
            )
            
            # Enable foreign keys
            await self.connection.execute("PRAGMA foreign_keys = ON")
            
            # Create tables if they don't exist
            await self._create_tables()
            
            self.logger.info(f"SQLite connector '{self.name}' initialized successfully")
            
        except ImportError:
            raise ConnectionError("aiosqlite library not installed. Install with: pip install aiosqlite")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize SQLite connector: {str(e)}")
    
    async def disconnect(self) -> None:
        """Close the SQLite connection."""
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.logger.info(f"SQLite connector '{self.name}' disconnected")
    
    async def _create_tables(self) -> None:
        """Create necessary tables for email storage."""
        # Create emails table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                message_id TEXT,
                conversation_id TEXT,
                subject TEXT,
                body TEXT,
                body_preview TEXT,
                body_type TEXT DEFAULT 'text',
                is_html INTEGER DEFAULT 0,
                sender_email TEXT,
                sender_name TEXT,
                from_email TEXT,
                from_name TEXT,
                to_recipients TEXT DEFAULT '[]',
                cc_recipients TEXT DEFAULT '[]',
                bcc_recipients TEXT DEFAULT '[]',
                reply_to TEXT DEFAULT '[]',
                sent_date TEXT,
                received_date TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                modified_date TEXT DEFAULT CURRENT_TIMESTAMP,
                importance TEXT DEFAULT 'normal',
                sensitivity TEXT DEFAULT 'normal',
                priority TEXT,
                is_read INTEGER DEFAULT 0,
                is_draft INTEGER DEFAULT 0,
                has_attachments INTEGER DEFAULT 0,
                is_flagged INTEGER DEFAULT 0,
                folder_id TEXT,
                folder_path TEXT,
                headers TEXT DEFAULT '{}',
                internet_headers TEXT DEFAULT '{}',
                categories TEXT DEFAULT '[]',
                in_reply_to TEXT,
                references TEXT DEFAULT '[]',
                size INTEGER,
                extended_properties TEXT DEFAULT '{}'
            )
        """)
        
        # Create attachments table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS email_attachments (
                id TEXT PRIMARY KEY,
                email_id TEXT REFERENCES emails(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                content_type TEXT,
                size INTEGER,
                attachment_type TEXT DEFAULT 'file',
                is_inline INTEGER DEFAULT 0,
                content_id TEXT,
                content_location TEXT,
                content_bytes BLOB,
                download_url TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                modified_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create folders table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS outlook_folders (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                display_name TEXT,
                parent_folder_id TEXT,
                folder_path TEXT,
                folder_type TEXT,
                total_item_count INTEGER DEFAULT 0,
                unread_item_count INTEGER DEFAULT 0,
                child_folder_count INTEGER DEFAULT 0,
                is_hidden INTEGER DEFAULT 0,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                modified_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_emails_message_id ON emails(message_id)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_emails_conversation_id ON emails(conversation_id)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_emails_sent_date ON emails(sent_date)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_emails_received_date ON emails(received_date)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_emails_folder_id ON emails(folder_id)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_emails_sender_email ON emails(sender_email)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_attachments_email_id ON email_attachments(email_id)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_folders_parent_id ON outlook_folders(parent_folder_id)")
        
        await self.connection.commit()
    
    async def store_email(self, email: EmailMessage) -> bool:
        """Store an email message in the database."""
        try:
            # Convert email addresses to JSON
            to_recipients = json.dumps([{"email": addr.email, "name": addr.name} for addr in email.to_recipients])
            cc_recipients = json.dumps([{"email": addr.email, "name": addr.name} for addr in email.cc_recipients])
            bcc_recipients = json.dumps([{"email": addr.email, "name": addr.name} for addr in email.bcc_recipients])
            reply_to = json.dumps([{"email": addr.email, "name": addr.name} for addr in email.reply_to])
            
            # Convert datetime to string
            sent_date = email.sent_date.isoformat() if email.sent_date else None
            received_date = email.received_date.isoformat() if email.received_date else None
            
            # Insert or replace email
            await self.connection.execute("""
                INSERT OR REPLACE INTO emails (
                    id, message_id, conversation_id, subject, body, body_preview,
                    body_type, is_html, sender_email, sender_name, from_email, from_name,
                    to_recipients, cc_recipients, bcc_recipients, reply_to,
                    sent_date, received_date, importance, sensitivity, priority,
                    is_read, is_draft, has_attachments, is_flagged,
                    folder_id, folder_path, headers, internet_headers,
                    categories, in_reply_to, references, size, extended_properties,
                    modified_date
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
                )
            """, (
                email.id, email.message_id, email.conversation_id,
                email.subject, email.body, email.body_preview,
                email.body_type, int(email.is_html),
                email.sender.email if email.sender else None,
                email.sender.name if email.sender else None,
                email.from_address.email if email.from_address else None,
                email.from_address.name if email.from_address else None,
                to_recipients, cc_recipients, bcc_recipients, reply_to,
                sent_date, received_date,
                email.importance.value, email.sensitivity.value, email.priority,
                int(email.is_read), int(email.is_draft), int(email.has_attachments), int(email.is_flagged),
                email.folder_id, email.folder_path,
                json.dumps(email.headers), json.dumps(email.internet_headers),
                json.dumps(email.categories), email.in_reply_to,
                json.dumps(email.references), email.size,
                json.dumps(email.extended_properties)
            ))
            
            # Store attachments
            for attachment in email.attachments:
                await self.store_attachment(attachment, email.id)
            
            await self.connection.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store email {email.id}: {str(e)}")
            raise DatabaseError(f"Failed to store email: {str(e)}")
    
    async def store_attachment(self, attachment: EmailAttachment, email_id: str) -> bool:
        """Store an email attachment."""
        try:
            created_date = attachment.created_date.isoformat() if attachment.created_date else None
            modified_date = attachment.modified_date.isoformat() if attachment.modified_date else None
            
            await self.connection.execute("""
                INSERT OR REPLACE INTO email_attachments (
                    id, email_id, name, content_type, size, attachment_type,
                    is_inline, content_id, content_location, content_bytes, download_url,
                    created_date, modified_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                attachment.id, email_id, attachment.name, attachment.content_type,
                attachment.size, attachment.attachment_type.value, int(attachment.is_inline),
                attachment.content_id, attachment.content_location,
                attachment.content_bytes, attachment.download_url, created_date
            ))
            
            await self.connection.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store attachment {attachment.id}: {str(e)}")
            raise DatabaseError(f"Failed to store attachment: {str(e)}")
    
    async def get_email(self, email_id: str) -> Optional[EmailMessage]:
        """Retrieve an email by ID."""
        try:
            # Get email
            cursor = await self.connection.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
            row = await cursor.fetchone()
            if not row:
                return None
            
            # Get attachments
            cursor = await self.connection.execute(
                "SELECT * FROM email_attachments WHERE email_id = ?", (email_id,)
            )
            attachment_rows = await cursor.fetchall()
            
            return self._row_to_email(row, attachment_rows)
            
        except Exception as e:
            self.logger.error(f"Failed to get email {email_id}: {str(e)}")
            raise DatabaseError(f"Failed to get email: {str(e)}")

    async def get_emails_by_folder(self, folder_id: str, limit: int = 100, offset: int = 0) -> List[EmailMessage]:
        """Get emails from a specific folder."""
        try:
            cursor = await self.connection.execute("""
                SELECT * FROM emails
                WHERE folder_id = ?
                ORDER BY received_date DESC
                LIMIT ? OFFSET ?
            """, (folder_id, limit, offset))

            rows = await cursor.fetchall()

            emails = []
            for row in rows:
                # Get attachments for this email
                cursor = await self.connection.execute(
                    "SELECT * FROM email_attachments WHERE email_id = ?", (row[0],)  # row[0] is id
                )
                attachment_rows = await cursor.fetchall()
                emails.append(self._row_to_email(row, attachment_rows))

            return emails

        except Exception as e:
            self.logger.error(f"Failed to get emails from folder {folder_id}: {str(e)}")
            raise DatabaseError(f"Failed to get emails from folder: {str(e)}")

    async def store_folder(self, folder: OutlookFolder) -> bool:
        """Store an Outlook folder."""
        try:
            created_date = folder.created_date.isoformat() if folder.created_date else None
            modified_date = folder.modified_date.isoformat() if folder.modified_date else None

            await self.connection.execute("""
                INSERT OR REPLACE INTO outlook_folders (
                    id, name, display_name, parent_folder_id, folder_path,
                    folder_type, total_item_count, unread_item_count,
                    child_folder_count, is_hidden, created_date, modified_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                folder.id, folder.name, folder.display_name,
                folder.parent_folder_id, folder.folder_path,
                folder.folder_type, folder.total_item_count,
                folder.unread_item_count, folder.child_folder_count,
                int(folder.is_hidden), created_date
            ))

            await self.connection.commit()
            return True

        except Exception as e:
            self.logger.error(f"Failed to store folder {folder.id}: {str(e)}")
            raise DatabaseError(f"Failed to store folder: {str(e)}")

    async def get_folder(self, folder_id: str) -> Optional[OutlookFolder]:
        """Get a folder by ID."""
        try:
            cursor = await self.connection.execute("SELECT * FROM outlook_folders WHERE id = ?", (folder_id,))
            row = await cursor.fetchone()
            if not row:
                return None

            return self._row_to_folder(row)

        except Exception as e:
            self.logger.error(f"Failed to get folder {folder_id}: {str(e)}")
            raise DatabaseError(f"Failed to get folder: {str(e)}")

    async def delete_email(self, email_id: str) -> bool:
        """Delete an email and its attachments."""
        try:
            # Delete attachments first
            await self.connection.execute("DELETE FROM email_attachments WHERE email_id = ?", (email_id,))

            # Delete email
            cursor = await self.connection.execute("DELETE FROM emails WHERE id = ?", (email_id,))

            await self.connection.commit()
            return cursor.rowcount > 0

        except Exception as e:
            self.logger.error(f"Failed to delete email {email_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete email: {str(e)}")

    async def search_emails(self, query: str, limit: int = 100) -> List[EmailMessage]:
        """Search emails by subject or body content."""
        try:
            cursor = await self.connection.execute("""
                SELECT * FROM emails
                WHERE subject LIKE ? OR body LIKE ?
                ORDER BY received_date DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))

            rows = await cursor.fetchall()

            emails = []
            for row in rows:
                # Get attachments for this email
                cursor = await self.connection.execute(
                    "SELECT * FROM email_attachments WHERE email_id = ?", (row[0],)  # row[0] is id
                )
                attachment_rows = await cursor.fetchall()
                emails.append(self._row_to_email(row, attachment_rows))

            return emails

        except Exception as e:
            self.logger.error(f"Failed to search emails: {str(e)}")
            raise DatabaseError(f"Failed to search emails: {str(e)}")

    def _row_to_email(self, row: tuple, attachment_rows: List[tuple]) -> EmailMessage:
        """Convert database row to EmailMessage object."""
        from evolvishub_outlook_ingestor.core.data_models import EmailAddress, EmailImportance, EmailSensitivity
        from datetime import datetime

        # Parse JSON fields
        to_recipients = [EmailAddress(**addr) for addr in json.loads(row[12] or '[]')]
        cc_recipients = [EmailAddress(**addr) for addr in json.loads(row[13] or '[]')]
        bcc_recipients = [EmailAddress(**addr) for addr in json.loads(row[14] or '[]')]
        reply_to = [EmailAddress(**addr) for addr in json.loads(row[15] or '[]')]

        # Parse datetime fields
        sent_date = datetime.fromisoformat(row[16]) if row[16] else None
        received_date = datetime.fromisoformat(row[17]) if row[17] else None
        created_date = datetime.fromisoformat(row[18]) if row[18] else None
        modified_date = datetime.fromisoformat(row[19]) if row[19] else None

        # Convert attachments
        attachments = []
        for att_row in attachment_rows:
            attachments.append(self._row_to_attachment(att_row))

        return EmailMessage(
            id=row[0],
            message_id=row[1],
            conversation_id=row[2],
            subject=row[3],
            body=row[4],
            body_preview=row[5],
            body_type=row[6],
            is_html=bool(row[7]),
            sender=EmailAddress(email=row[8], name=row[9]) if row[8] else None,
            from_address=EmailAddress(email=row[10], name=row[11]) if row[10] else None,
            to_recipients=to_recipients,
            cc_recipients=cc_recipients,
            bcc_recipients=bcc_recipients,
            reply_to=reply_to,
            sent_date=sent_date,
            received_date=received_date,
            created_date=created_date,
            modified_date=modified_date,
            importance=EmailImportance(row[20]),
            sensitivity=EmailSensitivity(row[21]),
            priority=row[22],
            is_read=bool(row[23]),
            is_draft=bool(row[24]),
            has_attachments=bool(row[25]),
            is_flagged=bool(row[26]),
            folder_id=row[27],
            folder_path=row[28],
            attachments=attachments,
            headers=json.loads(row[29] or '{}'),
            internet_headers=json.loads(row[30] or '{}'),
            categories=json.loads(row[31] or '[]'),
            in_reply_to=row[32],
            references=json.loads(row[33] or '[]'),
            size=row[34],
            extended_properties=json.loads(row[35] or '{}')
        )

    def _row_to_attachment(self, row: tuple) -> EmailAttachment:
        """Convert database row to EmailAttachment object."""
        from evolvishub_outlook_ingestor.core.data_models import AttachmentType
        from datetime import datetime

        created_date = datetime.fromisoformat(row[11]) if row[11] else None
        modified_date = datetime.fromisoformat(row[12]) if row[12] else None

        return EmailAttachment(
            id=row[0],
            name=row[2],
            content_type=row[3],
            size=row[4],
            attachment_type=AttachmentType(row[5]),
            is_inline=bool(row[6]),
            content_id=row[7],
            content_location=row[8],
            content_bytes=row[9],
            download_url=row[10],
            created_date=created_date,
            modified_date=modified_date
        )

    def _row_to_folder(self, row: tuple) -> OutlookFolder:
        """Convert database row to OutlookFolder object."""
        from datetime import datetime

        created_date = datetime.fromisoformat(row[10]) if row[10] else None
        modified_date = datetime.fromisoformat(row[11]) if row[11] else None

        return OutlookFolder(
            id=row[0],
            name=row[1],
            display_name=row[2],
            parent_folder_id=row[3],
            folder_path=row[4],
            folder_type=row[5],
            total_item_count=row[6],
            unread_item_count=row[7],
            child_folder_count=row[8],
            is_hidden=bool(row[9]),
            created_date=created_date,
            modified_date=modified_date
        )

    def _validate_config(self, required_keys: List[str]) -> None:
        """Validate that required configuration keys are present."""
        missing_keys = [key for key in required_keys if key not in self.config]
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the database connection."""
        try:
            cursor = await self.connection.execute("SELECT 1")
            result = await cursor.fetchone()

            # Get database file info
            file_size = os.path.getsize(self.database_path) if os.path.exists(self.database_path) else 0

            return {
                "status": "healthy",
                "database_path": self.database_path,
                "file_size_bytes": file_size,
                "test_query_result": result[0] if result else None
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "database_path": self.database_path
            }
