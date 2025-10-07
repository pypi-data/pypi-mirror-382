"""
MongoDB database connector for Evolvishub Outlook Ingestor.

This module implements the MongoDB database connector using motor
for high-performance async database operations.

Features:
- Async database operations with motor
- Document-based storage for emails
- GridFS for large attachment storage
- Proper indexing for search performance
- Aggregation pipelines for complex queries
- Flexible schema design
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

import gridfs
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket

from evolvishub_outlook_ingestor.connectors.base_connector import BaseConnector
from evolvishub_outlook_ingestor.core.data_models import EmailMessage, EmailAttachment
from evolvishub_outlook_ingestor.core.exceptions import (
    ConnectionError,
    DatabaseError,
    QueryError,
    TransactionError,
)


class MongoDBConnector(BaseConnector):
    """MongoDB database connector using motor."""
    
    def __init__(self, name: str, config: Dict[str, Any], **kwargs):
        """
        Initialize MongoDB connector.
        
        Args:
            name: Connector name
            config: Configuration dictionary containing:
                - host: Database host
                - port: Database port
                - database: Database name
                - username: Database username
                - password: Database password
                - auth_source: Authentication database
                - replica_set: Replica set name
        """
        super().__init__(name, config, **kwargs)
        
        # MongoDB configuration
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 27017)
        self.database_name = config.get("database", "outlook_data")
        self.username = config.get("username", "")
        self.password = config.get("password", "")
        self.auth_source = config.get("auth_source", "admin")
        self.replica_set = config.get("replica_set")
        
        # MongoDB client and database
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.gridfs_bucket: Optional[AsyncIOMotorGridFSBucket] = None
        
        # Collection names
        self.emails_collection_name = "emails"
        self.attachments_collection_name = "attachments"
        
        # GridFS settings
        self.gridfs_threshold = config.get("gridfs_threshold", 16 * 1024 * 1024)  # 16MB
    
    async def _initialize_connection(self) -> None:
        """Initialize single connection (not used with MongoDB)."""
        pass  # MongoDB uses connection pooling by default
    
    async def _initialize_pool(self) -> None:
        """Initialize MongoDB connection."""
        try:
            # Build connection URI
            if self.username and self.password:
                auth_part = f"{self.username}:{self.password}@"
            else:
                auth_part = ""
            
            replica_part = f"?replicaSet={self.replica_set}" if self.replica_set else ""
            uri = f"mongodb://{auth_part}{self.host}:{self.port}/{self.database_name}{replica_part}"
            
            # Create client
            self.client = AsyncIOMotorClient(
                uri,
                authSource=self.auth_source if self.username else None,
                maxPoolSize=self._pool_config.max_size if self.enable_connection_pooling else 10,
                minPoolSize=self._pool_config.min_size if self.enable_connection_pooling else 1,
                serverSelectionTimeoutMS=self.config.get("pool_timeout", 30) * 1000,
            )
            
            # Get database
            self.database = self.client[self.database_name]
            
            # Initialize GridFS bucket
            self.gridfs_bucket = AsyncIOMotorGridFSBucket(self.database)
            
            self.logger.info(
                "MongoDB connection initialized",
                host=self.host,
                port=self.port,
                database=self.database_name
            )
            
        except Exception as e:
            raise ConnectionError(
                f"Failed to initialize MongoDB connection: {e}",
                host=self.host,
                port=self.port,
                cause=e
            )
    
    async def _cleanup_connection(self) -> None:
        """Cleanup single connection (not used with MongoDB)."""
        pass
    
    async def _cleanup_pool(self) -> None:
        """Cleanup MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            self.gridfs_bucket = None
    
    async def _test_connection(self) -> None:
        """Test database connection."""
        if not self.client:
            raise ConnectionError("MongoDB client not initialized")
        
        try:
            # Ping the database
            await self.client.admin.command('ping')
            
        except Exception as e:
            raise ConnectionError(
                f"MongoDB connection test failed: {e}",
                host=self.host,
                port=self.port,
                cause=e
            )
    
    async def _initialize_schema(self) -> None:
        """Initialize database schema (indexes) if needed."""
        if not self.database:
            raise DatabaseError("Database not initialized")
        
        try:
            # Create indexes for emails collection
            emails_collection = self.database[self.emails_collection_name]
            
            # Create indexes
            await emails_collection.create_index("message_id", unique=True, sparse=True)
            await emails_collection.create_index("conversation_id")
            await emails_collection.create_index("sent_date")
            await emails_collection.create_index("received_date")
            await emails_collection.create_index("folder_id")
            await emails_collection.create_index("folder_path")
            await emails_collection.create_index("is_read")
            await emails_collection.create_index("has_attachments")
            await emails_collection.create_index("sender.email")
            await emails_collection.create_index("ingested_at")
            
            # Text index for full-text search
            await emails_collection.create_index([
                ("subject", "text"),
                ("body", "text")
            ])
            
            # Compound indexes for common queries
            await emails_collection.create_index([
                ("folder_id", 1),
                ("received_date", -1)
            ])
            await emails_collection.create_index([
                ("is_read", 1),
                ("received_date", -1)
            ])
            
            # Create indexes for attachments collection
            attachments_collection = self.database[self.attachments_collection_name]
            await attachments_collection.create_index("email_id")
            await attachments_collection.create_index("content_type")
            await attachments_collection.create_index("size")
            
            self.logger.info("MongoDB schema (indexes) initialized")
            
        except Exception as e:
            self.logger.warning(
                "Failed to initialize schema (indexes may already exist)",
                error=str(e)
            )
    
    async def _store_email_impl(
        self,
        email: EmailMessage,
        transaction: Optional[Any] = None,
        **kwargs
    ) -> str:
        """Store a single email in MongoDB."""
        if not self.database:
            raise DatabaseError("Database not initialized")
        
        try:
            # Convert email to document
            email_doc = self._email_to_document(email)
            
            # Store email
            emails_collection = self.database[self.emails_collection_name]
            
            # Use upsert to handle duplicates
            await emails_collection.replace_one(
                {"id": email.id},
                email_doc,
                upsert=True
            )
            
            # Store attachments
            if email.attachments:
                await self._store_attachments_mongo(email.id, email.attachments)
            
            return email.id
            
        except Exception as e:
            raise DatabaseError(
                f"Failed to store email: {e}",
                database_type=self.name,
                operation="store_email",
                cause=e
            )
    
    def _email_to_document(self, email: EmailMessage) -> Dict[str, Any]:
        """Convert EmailMessage to MongoDB document."""
        # Convert email addresses to dictionaries
        def addr_to_dict(addr):
            return {"email": addr.email, "name": addr.name} if addr else None
        
        def addrs_to_list(addrs):
            return [addr_to_dict(addr) for addr in addrs if addr]
        
        doc = {
            "id": email.id,
            "message_id": email.message_id,
            "conversation_id": email.conversation_id,
            "subject": email.subject,
            "body": email.body,
            "body_type": email.body_type,
            "is_html": email.is_html,
            
            # Sender and recipients
            "sender": addr_to_dict(email.sender),
            "from_address": addr_to_dict(email.from_address),
            "to_recipients": addrs_to_list(email.to_recipients),
            "cc_recipients": addrs_to_list(email.cc_recipients),
            "bcc_recipients": addrs_to_list(email.bcc_recipients),
            "reply_to": addrs_to_list(email.reply_to),
            
            # Dates
            "sent_date": email.sent_date,
            "received_date": email.received_date,
            "created_date": email.created_date,
            "modified_date": email.modified_date,
            
            # Properties
            "importance": email.importance.value if email.importance else "normal",
            "sensitivity": email.sensitivity.value if email.sensitivity else "normal",
            "priority": email.priority,
            
            # Flags
            "is_read": email.is_read,
            "is_draft": email.is_draft,
            "has_attachments": email.has_attachments,
            "is_flagged": email.is_flagged,
            
            # Folder information
            "folder_id": email.folder_id,
            "folder_path": email.folder_path,
            
            # Headers and metadata
            "headers": email.headers,
            "internet_headers": email.internet_headers,
            "categories": email.categories,
            
            # Threading
            "in_reply_to": email.in_reply_to,
            "references": email.references,
            
            # Size and extended properties
            "size": email.size,
            "extended_properties": email.extended_properties,
            
            # Timestamps
            "ingested_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        return doc

    async def _store_attachments_mongo(
        self,
        email_id: str,
        attachments: List[EmailAttachment]
    ) -> None:
        """Store email attachments in MongoDB."""
        attachments_collection = self.database[self.attachments_collection_name]

        for attachment in attachments:
            try:
                # Prepare attachment document
                attachment_doc = {
                    "id": attachment.id,
                    "email_id": email_id,
                    "name": attachment.name,
                    "content_type": attachment.content_type,
                    "size": attachment.size,
                    "attachment_type": attachment.attachment_type.value,
                    "is_inline": attachment.is_inline,
                    "content_id": attachment.content_id,
                    "content_location": attachment.content_location,
                    "created_date": attachment.created_date,
                    "modified_date": attachment.modified_date,
                    "is_safe": attachment.is_safe,
                    "scan_result": attachment.scan_result,
                    "ingested_at": datetime.utcnow(),
                }

                # Handle content storage
                if attachment.content:
                    if len(attachment.content) > self.gridfs_threshold:
                        # Store large attachments in GridFS
                        file_id = await self.gridfs_bucket.upload_from_stream(
                            attachment.name,
                            attachment.content,
                            metadata={
                                "email_id": email_id,
                                "attachment_id": attachment.id,
                                "content_type": attachment.content_type,
                            }
                        )
                        attachment_doc["gridfs_file_id"] = file_id
                    else:
                        # Store small attachments directly in document
                        attachment_doc["content"] = attachment.content

                # Upsert attachment
                await attachments_collection.replace_one(
                    {"id": attachment.id},
                    attachment_doc,
                    upsert=True
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
        if not self.database:
            raise DatabaseError("Database not initialized")

        try:
            emails_collection = self.database[self.emails_collection_name]

            # Prepare batch operations
            operations = []
            attachment_operations = []

            for email in emails:
                # Email document
                email_doc = self._email_to_document(email)

                # Create upsert operation
                operations.append({
                    "replaceOne": {
                        "filter": {"id": email.id},
                        "replacement": email_doc,
                        "upsert": True
                    }
                })

                # Prepare attachment operations
                for attachment in email.attachments:
                    attachment_doc = {
                        "id": attachment.id,
                        "email_id": email.id,
                        "name": attachment.name,
                        "content_type": attachment.content_type,
                        "size": attachment.size,
                        "attachment_type": attachment.attachment_type.value,
                        "is_inline": attachment.is_inline,
                        "content_id": attachment.content_id,
                        "content_location": attachment.content_location,
                        "created_date": attachment.created_date,
                        "modified_date": attachment.modified_date,
                        "is_safe": attachment.is_safe,
                        "scan_result": attachment.scan_result,
                        "ingested_at": datetime.utcnow(),
                    }

                    # Handle content (simplified for batch - store directly)
                    if attachment.content and len(attachment.content) <= self.gridfs_threshold:
                        attachment_doc["content"] = attachment.content

                    attachment_operations.append({
                        "replaceOne": {
                            "filter": {"id": attachment.id},
                            "replacement": attachment_doc,
                            "upsert": True
                        }
                    })

            # Execute batch operations
            if operations:
                await emails_collection.bulk_write(operations, ordered=False)

            if attachment_operations:
                attachments_collection = self.database[self.attachments_collection_name]
                await attachments_collection.bulk_write(attachment_operations, ordered=False)

            return [email.id for email in emails]

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
        if not self.database:
            raise DatabaseError("Database not initialized")

        try:
            emails_collection = self.database[self.emails_collection_name]

            # Get email document
            email_doc = await emails_collection.find_one({"id": email_id})

            if not email_doc:
                return None

            # Get attachments if requested
            attachments = []
            if include_attachments:
                attachments_collection = self.database[self.attachments_collection_name]
                attachment_docs = await attachments_collection.find({"email_id": email_id}).to_list(None)

                for att_doc in attachment_docs:
                    attachment = await self._document_to_attachment(att_doc)
                    if attachment:
                        attachments.append(attachment)

            return self._document_to_email(email_doc, attachments)

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
        if not self.database:
            raise DatabaseError("Database not initialized")

        try:
            emails_collection = self.database[self.emails_collection_name]

            # Build query
            query = {}

            for key, value in filters.items():
                if key == "folder_id":
                    query["folder_id"] = value
                elif key == "is_read":
                    query["is_read"] = value
                elif key == "has_attachments":
                    query["has_attachments"] = value
                elif key == "sender_email":
                    query["sender.email"] = value
                elif key == "subject_contains":
                    query["subject"] = {"$regex": value, "$options": "i"}
                elif key == "date_from":
                    query["sent_date"] = {"$gte": value}
                elif key == "date_to":
                    if "sent_date" in query:
                        query["sent_date"]["$lte"] = value
                    else:
                        query["sent_date"] = {"$lte": value}
                elif key == "text_search":
                    query["$text"] = {"$search": value}

            # Build cursor
            cursor = emails_collection.find(query)

            # Add sorting
            if sort_by:
                sort_direction = -1 if sort_order.lower() == "desc" else 1
                cursor = cursor.sort(sort_by, sort_direction)
            else:
                cursor = cursor.sort("received_date", -1)

            # Add pagination
            if offset:
                cursor = cursor.skip(offset)
            if limit:
                cursor = cursor.limit(limit)

            # Execute query
            email_docs = await cursor.to_list(None)

            # Convert to EmailMessage objects
            emails = []
            for email_doc in email_docs:
                # Get attachments
                attachments_collection = self.database[self.attachments_collection_name]
                attachment_docs = await attachments_collection.find({"email_id": email_doc["id"]}).to_list(None)

                attachments = []
                for att_doc in attachment_docs:
                    attachment = await self._document_to_attachment(att_doc)
                    if attachment:
                        attachments.append(attachment)

                email = self._document_to_email(email_doc, attachments)
                emails.append(email)

            return emails

        except Exception as e:
            raise DatabaseError(
                f"Failed to search emails: {e}",
                database_type=self.name,
                operation="search_emails",
                cause=e
            )

    def _document_to_email(self, doc: Dict[str, Any], attachments: List[EmailAttachment]) -> EmailMessage:
        """Convert MongoDB document to EmailMessage."""
        from evolvishub_outlook_ingestor.core.data_models import EmailAddress, EmailImportance, EmailSensitivity

        # Parse email addresses
        def parse_addr(addr_data):
            if not addr_data:
                return None
            return EmailAddress(email=addr_data.get('email', ''), name=addr_data.get('name', ''))

        def parse_addrs(addrs_data):
            if not addrs_data:
                return []
            return [EmailAddress(email=addr.get('email', ''), name=addr.get('name', ''))
                   for addr in addrs_data if addr]

        return EmailMessage(
            id=doc.get('id'),
            message_id=doc.get('message_id'),
            conversation_id=doc.get('conversation_id'),
            subject=doc.get('subject'),
            body=doc.get('body'),
            body_type=doc.get('body_type'),
            is_html=doc.get('is_html'),
            sender=parse_addr(doc.get('sender')),
            from_address=parse_addr(doc.get('from_address')),
            to_recipients=parse_addrs(doc.get('to_recipients')),
            cc_recipients=parse_addrs(doc.get('cc_recipients')),
            bcc_recipients=parse_addrs(doc.get('bcc_recipients')),
            reply_to=parse_addrs(doc.get('reply_to')),
            sent_date=doc.get('sent_date'),
            received_date=doc.get('received_date'),
            created_date=doc.get('created_date'),
            modified_date=doc.get('modified_date'),
            importance=EmailImportance(doc.get('importance', 'normal')),
            sensitivity=EmailSensitivity(doc.get('sensitivity', 'normal')),
            priority=doc.get('priority'),
            is_read=doc.get('is_read'),
            is_draft=doc.get('is_draft'),
            has_attachments=doc.get('has_attachments'),
            is_flagged=doc.get('is_flagged'),
            folder_id=doc.get('folder_id'),
            folder_path=doc.get('folder_path'),
            attachments=attachments,
            headers=doc.get('headers', {}),
            internet_headers=doc.get('internet_headers', {}),
            categories=doc.get('categories', []),
            in_reply_to=doc.get('in_reply_to'),
            references=doc.get('references', []),
            size=doc.get('size'),
            extended_properties=doc.get('extended_properties', {}),
        )

    async def _document_to_attachment(self, doc: Dict[str, Any]) -> Optional[EmailAttachment]:
        """Convert MongoDB document to EmailAttachment."""
        from evolvishub_outlook_ingestor.core.data_models import AttachmentType

        try:
            # Get content
            content = None
            if "content" in doc:
                content = doc["content"]
            elif "gridfs_file_id" in doc:
                # Retrieve from GridFS
                try:
                    content = await self.gridfs_bucket.download_to_stream(doc["gridfs_file_id"])
                except Exception as e:
                    self.logger.warning(
                        "Failed to retrieve attachment from GridFS",
                        file_id=doc["gridfs_file_id"],
                        error=str(e)
                    )

            return EmailAttachment(
                id=doc.get('id'),
                name=doc.get('name'),
                content_type=doc.get('content_type'),
                size=doc.get('size'),
                attachment_type=AttachmentType(doc.get('attachment_type', 'file')),
                is_inline=doc.get('is_inline'),
                content_id=doc.get('content_id'),
                content_location=doc.get('content_location'),
                content=content,
                created_date=doc.get('created_date'),
                modified_date=doc.get('modified_date'),
                is_safe=doc.get('is_safe'),
                scan_result=doc.get('scan_result'),
            )

        except Exception as e:
            self.logger.warning(
                "Failed to convert attachment document",
                attachment_id=doc.get('id'),
                error=str(e)
            )
            return None

    async def _begin_transaction(self, isolation_level: Optional[str] = None) -> Any:
        """Begin database transaction (MongoDB sessions)."""
        if not self.client:
            raise DatabaseError("MongoDB client not initialized")

        # Start session
        session = await self.client.start_session()

        # Start transaction
        session.start_transaction()

        return session

    async def _commit_transaction(self, transaction: Any) -> None:
        """Commit database transaction."""
        try:
            await transaction.commit_transaction()
        finally:
            await transaction.end_session()

    async def _rollback_transaction(self, transaction: Any) -> None:
        """Rollback database transaction."""
        try:
            await transaction.abort_transaction()
        finally:
            await transaction.end_session()
