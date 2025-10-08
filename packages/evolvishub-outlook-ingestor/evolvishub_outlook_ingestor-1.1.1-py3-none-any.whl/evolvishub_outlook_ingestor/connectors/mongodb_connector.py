"""
MongoDB database connector for Evolvishub Outlook Ingestor.

This module provides a concrete implementation of the MongoDB database connector
for storing and retrieving email data from Microsoft Outlook.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from bson import ObjectId

from evolvishub_outlook_ingestor.connectors.base_connector import BaseConnector
from evolvishub_outlook_ingestor.core.data_models import (
    EmailMessage, EmailAttachment, OutlookFolder, ProcessingResult
)
from evolvishub_outlook_ingestor.core.exceptions import DatabaseError, ConnectionError


class MongoDBConnector(BaseConnector):
    """MongoDB database connector for email data."""
    
    def __init__(self, name: str, config: Dict[str, Any], **kwargs):
        super().__init__(name, config, **kwargs)
        self._validate_config(['host', 'database'])
        
        # MongoDB specific configuration
        self.host = config['host']
        self.port = config.get('port', 27017)
        self.database_name = config['database']
        self.username = config.get('username')
        self.password = config.get('password')
        self.auth_source = config.get('auth_source', 'admin')
        self.replica_set = config.get('replica_set')
        
        self.client = None
        self.database = None
    
    async def initialize(self) -> None:
        """Initialize the MongoDB connection."""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            
            # Build connection string
            if self.username and self.password:
                connection_string = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}"
                if self.auth_source:
                    connection_string += f"?authSource={self.auth_source}"
                if self.replica_set:
                    connection_string += f"&replicaSet={self.replica_set}"
            else:
                connection_string = f"mongodb://{self.host}:{self.port}/{self.database_name}"
                if self.replica_set:
                    connection_string += f"?replicaSet={self.replica_set}"
            
            # Create client
            self.client = AsyncIOMotorClient(
                connection_string,
                maxPoolSize=self.config.get('max_pool_size', 20),
                minPoolSize=self.config.get('min_pool_size', 5),
                maxIdleTimeMS=self.config.get('max_idle_time_ms', 300000),  # 5 minutes
                serverSelectionTimeoutMS=self.config.get('server_selection_timeout_ms', 30000),  # 30 seconds
                appname=f'evolvishub-outlook-ingestor-{self.name}'
            )
            
            # Get database
            self.database = self.client[self.database_name]
            
            # Create indexes
            await self._create_indexes()
            
            self.logger.info(f"MongoDB connector '{self.name}' initialized successfully")
            
        except ImportError:
            raise ConnectionError("motor library not installed. Install with: pip install motor")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize MongoDB connector: {str(e)}")
    
    async def disconnect(self) -> None:
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            self.logger.info(f"MongoDB connector '{self.name}' disconnected")
    
    async def _create_indexes(self) -> None:
        """Create necessary indexes for email collections."""
        # Emails collection indexes
        emails_collection = self.database.emails
        await emails_collection.create_index("message_id")
        await emails_collection.create_index("conversation_id")
        await emails_collection.create_index("sent_date")
        await emails_collection.create_index("received_date")
        await emails_collection.create_index("folder_id")
        await emails_collection.create_index("sender.email")
        await emails_collection.create_index([("subject", "text"), ("body", "text")])
        
        # Attachments collection indexes
        attachments_collection = self.database.email_attachments
        await attachments_collection.create_index("email_id")
        await attachments_collection.create_index("name")
        
        # Folders collection indexes
        folders_collection = self.database.outlook_folders
        await folders_collection.create_index("parent_folder_id")
        await folders_collection.create_index("folder_path")
    
    async def store_email(self, email: EmailMessage) -> bool:
        """Store an email message in the database."""
        try:
            # Convert email to document
            email_doc = self._email_to_document(email)
            
            # Upsert email
            result = await self.database.emails.replace_one(
                {"_id": email.id},
                email_doc,
                upsert=True
            )
            
            # Store attachments separately
            for attachment in email.attachments:
                await self.store_attachment(attachment, email.id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store email {email.id}: {str(e)}")
            raise DatabaseError(f"Failed to store email: {str(e)}")
    
    async def store_attachment(self, attachment: EmailAttachment, email_id: str) -> bool:
        """Store an email attachment."""
        try:
            # Convert attachment to document
            attachment_doc = self._attachment_to_document(attachment, email_id)
            
            # Upsert attachment
            result = await self.database.email_attachments.replace_one(
                {"_id": attachment.id},
                attachment_doc,
                upsert=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store attachment {attachment.id}: {str(e)}")
            raise DatabaseError(f"Failed to store attachment: {str(e)}")
    
    async def get_email(self, email_id: str) -> Optional[EmailMessage]:
        """Retrieve an email by ID."""
        try:
            # Get email document
            email_doc = await self.database.emails.find_one({"_id": email_id})
            if not email_doc:
                return None
            
            # Get attachments
            attachment_docs = await self.database.email_attachments.find(
                {"email_id": email_id}
            ).to_list(length=None)
            
            return self._document_to_email(email_doc, attachment_docs)
            
        except Exception as e:
            self.logger.error(f"Failed to get email {email_id}: {str(e)}")
            raise DatabaseError(f"Failed to get email: {str(e)}")
    
    async def get_emails_by_folder(self, folder_id: str, limit: int = 100, offset: int = 0) -> List[EmailMessage]:
        """Get emails from a specific folder."""
        try:
            # Get email documents
            cursor = self.database.emails.find({"folder_id": folder_id}).sort("received_date", -1).skip(offset).limit(limit)
            email_docs = await cursor.to_list(length=limit)
            
            emails = []
            for email_doc in email_docs:
                # Get attachments for this email
                attachment_docs = await self.database.email_attachments.find(
                    {"email_id": email_doc["_id"]}
                ).to_list(length=None)
                
                emails.append(self._document_to_email(email_doc, attachment_docs))
            
            return emails
            
        except Exception as e:
            self.logger.error(f"Failed to get emails from folder {folder_id}: {str(e)}")
            raise DatabaseError(f"Failed to get emails from folder: {str(e)}")
    
    async def store_folder(self, folder: OutlookFolder) -> bool:
        """Store an Outlook folder."""
        try:
            # Convert folder to document
            folder_doc = self._folder_to_document(folder)
            
            # Upsert folder
            result = await self.database.outlook_folders.replace_one(
                {"_id": folder.id},
                folder_doc,
                upsert=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store folder {folder.id}: {str(e)}")
            raise DatabaseError(f"Failed to store folder: {str(e)}")
    
    async def get_folder(self, folder_id: str) -> Optional[OutlookFolder]:
        """Get a folder by ID."""
        try:
            folder_doc = await self.database.outlook_folders.find_one({"_id": folder_id})
            if not folder_doc:
                return None
            
            return self._document_to_folder(folder_doc)
            
        except Exception as e:
            self.logger.error(f"Failed to get folder {folder_id}: {str(e)}")
            raise DatabaseError(f"Failed to get folder: {str(e)}")
    
    async def delete_email(self, email_id: str) -> bool:
        """Delete an email and its attachments."""
        try:
            # Delete attachments first
            await self.database.email_attachments.delete_many({"email_id": email_id})
            
            # Delete email
            result = await self.database.emails.delete_one({"_id": email_id})
            
            return result.deleted_count > 0
            
        except Exception as e:
            self.logger.error(f"Failed to delete email {email_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete email: {str(e)}")
    
    async def search_emails(self, query: str, limit: int = 100) -> List[EmailMessage]:
        """Search emails by subject or body content."""
        try:
            # Use text search
            cursor = self.database.emails.find(
                {"$text": {"$search": query}}
            ).sort("received_date", -1).limit(limit)
            
            email_docs = await cursor.to_list(length=limit)
            
            emails = []
            for email_doc in email_docs:
                # Get attachments for this email
                attachment_docs = await self.database.email_attachments.find(
                    {"email_id": email_doc["_id"]}
                ).to_list(length=None)
                
                emails.append(self._document_to_email(email_doc, attachment_docs))
            
            return emails
            
        except Exception as e:
            self.logger.error(f"Failed to search emails: {str(e)}")
            raise DatabaseError(f"Failed to search emails: {str(e)}")

    def _email_to_document(self, email: EmailMessage) -> Dict[str, Any]:
        """Convert EmailMessage to MongoDB document."""
        doc = {
            "_id": email.id,
            "message_id": email.message_id,
            "conversation_id": email.conversation_id,
            "subject": email.subject,
            "body": email.body,
            "body_preview": email.body_preview,
            "body_type": email.body_type,
            "is_html": email.is_html,
            "sender": {"email": email.sender.email, "name": email.sender.name} if email.sender else None,
            "from_address": {"email": email.from_address.email, "name": email.from_address.name} if email.from_address else None,
            "to_recipients": [{"email": addr.email, "name": addr.name} for addr in email.to_recipients],
            "cc_recipients": [{"email": addr.email, "name": addr.name} for addr in email.cc_recipients],
            "bcc_recipients": [{"email": addr.email, "name": addr.name} for addr in email.bcc_recipients],
            "reply_to": [{"email": addr.email, "name": addr.name} for addr in email.reply_to],
            "sent_date": email.sent_date,
            "received_date": email.received_date,
            "created_date": email.created_date or datetime.utcnow(),
            "modified_date": datetime.utcnow(),
            "importance": email.importance.value,
            "sensitivity": email.sensitivity.value,
            "priority": email.priority,
            "is_read": email.is_read,
            "is_draft": email.is_draft,
            "has_attachments": email.has_attachments,
            "is_flagged": email.is_flagged,
            "folder_id": email.folder_id,
            "folder_path": email.folder_path,
            "headers": email.headers,
            "internet_headers": email.internet_headers,
            "categories": email.categories,
            "in_reply_to": email.in_reply_to,
            "references": email.references,
            "size": email.size,
            "extended_properties": email.extended_properties
        }
        return doc

    def _attachment_to_document(self, attachment: EmailAttachment, email_id: str) -> Dict[str, Any]:
        """Convert EmailAttachment to MongoDB document."""
        doc = {
            "_id": attachment.id,
            "email_id": email_id,
            "name": attachment.name,
            "content_type": attachment.content_type,
            "size": attachment.size,
            "attachment_type": attachment.attachment_type.value,
            "is_inline": attachment.is_inline,
            "content_id": attachment.content_id,
            "content_location": attachment.content_location,
            "content_bytes": attachment.content_bytes,
            "download_url": attachment.download_url,
            "created_date": attachment.created_date or datetime.utcnow(),
            "modified_date": datetime.utcnow()
        }
        return doc

    def _folder_to_document(self, folder: OutlookFolder) -> Dict[str, Any]:
        """Convert OutlookFolder to MongoDB document."""
        doc = {
            "_id": folder.id,
            "name": folder.name,
            "display_name": folder.display_name,
            "parent_folder_id": folder.parent_folder_id,
            "folder_path": folder.folder_path,
            "folder_type": folder.folder_type,
            "total_item_count": folder.total_item_count,
            "unread_item_count": folder.unread_item_count,
            "child_folder_count": folder.child_folder_count,
            "is_hidden": folder.is_hidden,
            "created_date": folder.created_date or datetime.utcnow(),
            "modified_date": datetime.utcnow()
        }
        return doc

    def _document_to_email(self, doc: Dict[str, Any], attachment_docs: List[Dict[str, Any]]) -> EmailMessage:
        """Convert MongoDB document to EmailMessage object."""
        from evolvishub_outlook_ingestor.core.data_models import EmailAddress, EmailImportance, EmailSensitivity

        # Convert attachments
        attachments = []
        for att_doc in attachment_docs:
            attachments.append(self._document_to_attachment(att_doc))

        return EmailMessage(
            id=doc["_id"],
            message_id=doc.get("message_id"),
            conversation_id=doc.get("conversation_id"),
            subject=doc.get("subject"),
            body=doc.get("body"),
            body_preview=doc.get("body_preview"),
            body_type=doc.get("body_type", "text"),
            is_html=doc.get("is_html", False),
            sender=EmailAddress(**doc["sender"]) if doc.get("sender") else None,
            from_address=EmailAddress(**doc["from_address"]) if doc.get("from_address") else None,
            to_recipients=[EmailAddress(**addr) for addr in doc.get("to_recipients", [])],
            cc_recipients=[EmailAddress(**addr) for addr in doc.get("cc_recipients", [])],
            bcc_recipients=[EmailAddress(**addr) for addr in doc.get("bcc_recipients", [])],
            reply_to=[EmailAddress(**addr) for addr in doc.get("reply_to", [])],
            sent_date=doc.get("sent_date"),
            received_date=doc.get("received_date"),
            created_date=doc.get("created_date"),
            modified_date=doc.get("modified_date"),
            importance=EmailImportance(doc.get("importance", "normal")),
            sensitivity=EmailSensitivity(doc.get("sensitivity", "normal")),
            priority=doc.get("priority"),
            is_read=doc.get("is_read", False),
            is_draft=doc.get("is_draft", False),
            has_attachments=doc.get("has_attachments", False),
            is_flagged=doc.get("is_flagged", False),
            folder_id=doc.get("folder_id"),
            folder_path=doc.get("folder_path"),
            attachments=attachments,
            headers=doc.get("headers", {}),
            internet_headers=doc.get("internet_headers", {}),
            categories=doc.get("categories", []),
            in_reply_to=doc.get("in_reply_to"),
            references=doc.get("references", []),
            size=doc.get("size"),
            extended_properties=doc.get("extended_properties", {})
        )

    def _document_to_attachment(self, doc: Dict[str, Any]) -> EmailAttachment:
        """Convert MongoDB document to EmailAttachment object."""
        from evolvishub_outlook_ingestor.core.data_models import AttachmentType

        return EmailAttachment(
            id=doc["_id"],
            name=doc["name"],
            content_type=doc.get("content_type"),
            size=doc.get("size"),
            attachment_type=AttachmentType(doc.get("attachment_type", "file")),
            is_inline=doc.get("is_inline", False),
            content_id=doc.get("content_id"),
            content_location=doc.get("content_location"),
            content_bytes=doc.get("content_bytes"),
            download_url=doc.get("download_url"),
            created_date=doc.get("created_date"),
            modified_date=doc.get("modified_date")
        )

    def _document_to_folder(self, doc: Dict[str, Any]) -> OutlookFolder:
        """Convert MongoDB document to OutlookFolder object."""
        return OutlookFolder(
            id=doc["_id"],
            name=doc["name"],
            display_name=doc.get("display_name"),
            parent_folder_id=doc.get("parent_folder_id"),
            folder_path=doc.get("folder_path"),
            folder_type=doc.get("folder_type"),
            total_item_count=doc.get("total_item_count", 0),
            unread_item_count=doc.get("unread_item_count", 0),
            child_folder_count=doc.get("child_folder_count", 0),
            is_hidden=doc.get("is_hidden", False),
            created_date=doc.get("created_date"),
            modified_date=doc.get("modified_date")
        )

    def _validate_config(self, required_keys: List[str]) -> None:
        """Validate that required configuration keys are present."""
        missing_keys = [key for key in required_keys if key not in self.config]
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the database connection."""
        try:
            # Test connection with a simple operation
            result = await self.database.command("ping")

            # Get server info
            server_info = await self.client.server_info()

            return {
                "status": "healthy",
                "database": self.database_name,
                "host": self.host,
                "port": self.port,
                "server_version": server_info.get("version"),
                "ping_result": result
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "database": self.database_name,
                "host": self.host,
                "port": self.port
            }
