"""
Email Ingestor - Focused email ingestion library.

This module provides the primary interface for email ingestion from Microsoft
Outlook using Microsoft Graph API. It's designed as a pure data ingestion
library that can be easily integrated into other applications and microservices.

Features:
- Complete Microsoft Graph email operations
- Batch processing with progress tracking
- Multiple output formats (database connectors, file exports)
- Error handling and retry mechanisms
- Configurable data transformation
- Clean, simple integration interface
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable
from uuid import UUID, uuid4

from evolvishub_outlook_ingestor.core.config import Settings
from evolvishub_outlook_ingestor.core.data_models import (
    EmailMessage,
    ProcessingResult,
    ProcessingStatus,
    BatchProcessingConfig,
)
from evolvishub_outlook_ingestor.core.exceptions import (
    ConfigurationError,
    OutlookIngestorError,
    ProcessingError,
)
from evolvishub_outlook_ingestor.core.logging import LoggerMixin, set_correlation_id
from evolvishub_outlook_ingestor.protocols.microsoft_graph import GraphAPIAdapter
from evolvishub_outlook_ingestor.protocols.email_ingestor_protocol import (
    IngestionConfig,
    IngestionProgress,
)
from evolvishub_outlook_ingestor.connectors.database_connector import DatabaseConnector


class EmailIngestor(LoggerMixin):
    """
    Focused email ingestor for Microsoft Outlook.
    
    This class provides a clean, simple interface for email ingestion
    that can be easily integrated into other applications and microservices.
    """
    
    def __init__(
        self,
        settings: Optional[Settings] = None,
        graph_adapter: Optional[Any] = None,
        database_connector: Optional[DatabaseConnector] = None
    ):
        """
        Initialize the email ingestor.
        
        Args:
            settings: Configuration settings
            graph_adapter: Microsoft Graph API adapter
            database_connector: Optional database connector for storage
        """
        self.settings = settings or Settings()
        self.graph_adapter = graph_adapter
        self.database_connector = database_connector

        # Use GraphAPIAdapter directly instead of EmailIngestorProtocol wrapper
        if graph_adapter and not isinstance(graph_adapter, GraphAPIAdapter):
            # If it's not already a GraphAPIAdapter, we might need to wrap it
            # For now, assume it's compatible
            self.protocol = graph_adapter
        else:
            self.protocol = graph_adapter

        self._session_id = str(uuid4())

        # Operation tracking (enhanced functionality)
        self._active_operations: Dict[UUID, ProcessingResult] = {}

        # Set correlation ID for logging
        set_correlation_id(self._session_id)

        self.logger.info("Email ingestor initialized (using GraphAPIAdapter directly)", session_id=self._session_id)
    
    async def initialize(self, config: Optional[IngestionConfig] = None) -> bool:
        """
        Initialize the email ingestor.
        
        Args:
            config: Optional ingestion configuration
            
        Returns:
            True if initialization successful
        """
        try:
            if not self.graph_adapter:
                raise ConfigurationError("Graph adapter is required")
            
            # Use GraphAPIAdapter directly (no wrapper protocol)
            self.protocol = self.graph_adapter

            # Initialize GraphAPIAdapter if it has an initialize method
            if hasattr(self.protocol, 'initialize'):
                await self.protocol.initialize()
            elif hasattr(self.protocol, '_authenticate'):
                # Ensure authentication is set up
                await self.protocol._authenticate()
            
            # Initialize database connector if provided
            if self.database_connector:
                await self.database_connector.initialize()
            
            self.logger.info("Email ingestor initialization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize email ingestor: {e}")
            raise ConfigurationError(f"Failed to initialize email ingestor: {e}") from e
    
    async def ingest_emails(
        self,
        folder_ids: Optional[List[str]] = None,
        user_id: str = "me",
        config: Optional[IngestionConfig] = None,
        output_format: str = "database"
    ) -> ProcessingResult:
        """
        Ingest emails from specified folders.
        
        Args:
            folder_ids: List of folder IDs to ingest from (None for all folders)
            user_id: User ID or 'me' for current user
            config: Optional ingestion configuration
            output_format: Output format ('database', 'json', 'csv')
            
        Returns:
            ProcessingResult with ingestion results
        """
        if not self.protocol:
            raise ConfigurationError("Email ingestor not initialized")
        
        start_time = datetime.utcnow()
        
        try:
            self.logger.info("Starting email ingestion", 
                           folder_ids=folder_ids, user_id=user_id, output_format=output_format)
            
            # Perform ingestion
            progress = await self.protocol.ingest_all_emails(
                user_id=user_id,
                folder_ids=folder_ids,
                config=config
            )
            
            # Get all emails from the ingestion
            all_emails = []
            if folder_ids is None:
                folders = await self.protocol.get_folders(user_id)
                folder_ids = [folder.id for folder in folders]
            
            for folder_id in folder_ids:
                try:
                    emails = await self.protocol.get_emails(
                        folder_id=folder_id,
                        user_id=user_id,
                        config=config
                    )
                    all_emails.extend(emails)
                except Exception as e:
                    self.logger.warning(f"Failed to get emails from folder {folder_id}: {e}")
            
            # Process output format
            output_data = await self._process_output(all_emails, output_format)
            
            # Create result
            result = ProcessingResult(
                session_id=self._session_id,
                status=ProcessingStatus.COMPLETED if progress.failed_emails == 0 else ProcessingStatus.PARTIAL,
                total_emails=progress.total_emails,
                processed_emails=progress.processed_emails,
                failed_emails=progress.failed_emails,
                start_time=start_time,
                end_time=datetime.utcnow(),
                output_data=output_data,
                metadata={
                    "folders_processed": len(folder_ids) if folder_ids else 0,
                    "success_rate": progress.success_rate,
                    "output_format": output_format
                }
            )
            
            self.logger.info("Email ingestion completed", 
                           processed=progress.processed_emails,
                           failed=progress.failed_emails,
                           success_rate=progress.success_rate)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Email ingestion failed: {e}")
            
            # Create error result
            result = ProcessingResult(
                session_id=self._session_id,
                status=ProcessingStatus.FAILED,
                total_emails=0,
                processed_emails=0,
                failed_emails=0,
                start_time=start_time,
                end_time=datetime.utcnow(),
                error_message=str(e),
                metadata={"error_type": type(e).__name__}
            )
            
            return result
    
    async def search_emails(
        self,
        query: str,
        user_id: str = "me",
        folder_id: Optional[str] = None,
        limit: Optional[int] = None,
        output_format: str = "list"
    ) -> Union[List[EmailMessage], Dict[str, Any]]:
        """
        Search emails with specified query.
        
        Args:
            query: Search query
            user_id: User ID or 'me' for current user
            folder_id: Optional folder ID to search within
            limit: Maximum number of results
            output_format: Output format ('list', 'json', 'csv')
            
        Returns:
            Search results in specified format
        """
        if not self.protocol:
            raise ConfigurationError("Email ingestor not initialized")
        
        try:
            emails = await self.protocol.search_emails(
                query=query,
                user_id=user_id,
                folder_id=folder_id,
                limit=limit
            )
            
            if output_format == "list":
                return emails
            else:
                return await self._process_output(emails, output_format)
            
        except Exception as e:
            self.logger.error(f"Email search failed: {e}")
            raise ProcessingError(f"Email search failed: {e}") from e
    
    async def get_conversation_thread(
        self,
        conversation_id: str,
        user_id: str = "me",
        output_format: str = "list"
    ) -> Union[List[EmailMessage], Dict[str, Any]]:
        """
        Get all emails in a conversation thread.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID or 'me' for current user
            output_format: Output format ('list', 'json', 'csv')
            
        Returns:
            Conversation emails in specified format
        """
        if not self.protocol:
            raise ConfigurationError("Email ingestor not initialized")
        
        try:
            emails = await self.protocol.get_conversation_thread(
                conversation_id=conversation_id,
                user_id=user_id
            )
            
            if output_format == "list":
                return emails
            else:
                return await self._process_output(emails, output_format)
            
        except Exception as e:
            self.logger.error(f"Failed to get conversation thread: {e}")
            raise ProcessingError(f"Failed to get conversation thread: {e}") from e
    
    async def get_folders(self, user_id: str = "me") -> List[Dict[str, Any]]:
        """
        Get all mail folders for a user.
        
        Args:
            user_id: User ID or 'me' for current user
            
        Returns:
            List of folder information
        """
        if not self.protocol:
            raise ConfigurationError("Email ingestor not initialized")
        
        try:
            folders = await self.protocol.get_folders(user_id)
            return [
                {
                    "id": folder.id,
                    "display_name": folder.display_name,
                    "total_item_count": folder.total_item_count,
                    "unread_item_count": folder.unread_item_count
                }
                for folder in folders
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get folders: {e}")
            raise ProcessingError(f"Failed to get folders: {e}") from e
    
    async def _process_output(self, emails: List[EmailMessage], output_format: str) -> Any:
        """Process emails into specified output format."""
        if output_format == "database" and self.database_connector:
            # Store in database
            await self.database_connector.store_emails(emails)
            return {"stored_count": len(emails), "database": self.database_connector.config.database_type}
        
        elif output_format == "json":
            # Convert to JSON-serializable format
            return [email.model_dump() for email in emails]
        
        elif output_format == "csv":
            # Convert to CSV-friendly format
            csv_data = []
            for email in emails:
                csv_data.append({
                    "id": email.id,
                    "subject": email.subject,
                    "sender": email.sender.address if email.sender else "",
                    "received_date": email.received_date.isoformat() if email.received_date else "",
                    "is_read": email.is_read,
                    "has_attachments": email.has_attachments
                })
            return csv_data
        
        else:
            return emails
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        if not self.protocol:
            return {"status": "not_initialized"}
        
        return await self.protocol.health_check()
    
    def get_progress(self) -> Optional[IngestionProgress]:
        """Get current ingestion progress."""
        if not self.protocol:
            return None
        
        return self.protocol.get_progress()
    
    async def ingest_emails_batch(
        self,
        folder_ids: Optional[List[str]] = None,
        user_id: str = "me",
        config: Optional[IngestionConfig] = None,
        batch_config: Optional[BatchProcessingConfig] = None,
        output_format: str = "database"
    ) -> ProcessingResult:
        """
        Ingest emails with advanced batch processing capabilities.

        This method provides enhanced batch processing with configurable
        batch sizes, parallel processing, and detailed progress tracking.

        Args:
            folder_ids: List of folder IDs to process
            user_id: User ID or 'me' for current user
            config: Ingestion configuration
            batch_config: Batch processing configuration
            output_format: Output format ('database', 'json', 'csv')

        Returns:
            ProcessingResult with detailed batch processing metrics
        """
        operation_id = uuid4()

        # Create default batch config if not provided
        if not batch_config:
            batch_config = BatchProcessingConfig(
                batch_size=50,
                max_concurrent_batches=3,
                retry_attempts=2
            )

        # Initialize result tracking
        result = ProcessingResult(
            operation_id=operation_id,
            status=ProcessingStatus.IN_PROGRESS,
            total_items=0,
            processed_items=0,
            failed_items=0,
            start_time=datetime.now(),
            metadata={"batch_config": batch_config.__dict__}
        )

        self._active_operations[operation_id] = result

        try:
            self.logger.info(f"Starting batch email ingestion",
                           operation_id=str(operation_id),
                           batch_size=batch_config.batch_size)

            # Get emails using existing method
            emails = await self.protocol.get_emails(
                folder_ids=folder_ids,
                user_id=user_id,
                config=config
            )

            result.total_items = len(emails)

            # Process in batches
            if batch_config.max_concurrent_batches > 1:
                result = await self._process_emails_parallel(emails, batch_config, result, output_format)
            else:
                result = await self._process_emails_sequential_batch(emails, batch_config, result, output_format)

            result.status = ProcessingStatus.COMPLETED
            result.end_time = datetime.now()

            self.logger.info(f"Batch email ingestion completed",
                           operation_id=str(operation_id),
                           processed=result.processed_items,
                           failed=result.failed_items)

            return result

        except Exception as e:
            result.status = ProcessingStatus.FAILED
            result.end_time = datetime.now()
            result.error_message = str(e)

            self.logger.error(f"Batch email ingestion failed: {e}",
                            operation_id=str(operation_id))

            return result

        finally:
            self._active_operations.pop(operation_id, None)

    def get_active_operations(self) -> Dict[UUID, ProcessingResult]:
        """
        Get currently active operations.

        Returns:
            Dictionary mapping operation IDs to their processing results
        """
        return self._active_operations.copy()

    def get_operation_status(self, operation_id: UUID) -> Optional[ProcessingResult]:
        """
        Get status of a specific operation.

        Args:
            operation_id: UUID of the operation

        Returns:
            ProcessingResult if operation exists, None otherwise
        """
        return self._active_operations.get(operation_id)

    async def health_check_detailed(self) -> Dict[str, Any]:
        """
        Perform detailed health check with comprehensive status information.

        Returns:
            Detailed health status including component status, metrics, and diagnostics
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "session_id": self._session_id,
            "components": {},
            "metrics": {},
            "active_operations": len(self._active_operations)
        }

        try:
            # Check protocol health
            if self.protocol:
                protocol_health = await self.protocol.health_check()
                health_status["components"]["protocol"] = protocol_health
            else:
                health_status["components"]["protocol"] = {"status": "not_initialized"}
                health_status["status"] = "degraded"

            # Check database connector health
            if self.database_connector:
                try:
                    db_health = await self.database_connector.health_check()
                    health_status["components"]["database"] = db_health
                except Exception as e:
                    health_status["components"]["database"] = {
                        "status": "error",
                        "error": str(e)
                    }
                    health_status["status"] = "degraded"
            else:
                health_status["components"]["database"] = {"status": "not_configured"}

            # Add metrics
            health_status["metrics"] = {
                "total_operations_tracked": len(self._active_operations),
                "session_uptime_seconds": 0  # Simplified for now
            }

        except Exception as e:
            health_status["status"] = "error"
            health_status["error"] = str(e)

        return health_status

    async def cleanup(self):
        """Cleanup resources."""
        try:
            if self.protocol:
                await self.protocol.cleanup()

            if self.database_connector:
                await self.database_connector.cleanup()

            # Clear active operations
            self._active_operations.clear()

            self.logger.info("Email ingestor cleanup completed")

        except Exception as e:
            self.logger.error(f"Failed to cleanup email ingestor: {e}")

    async def _process_emails_parallel(
        self,
        emails: List[EmailMessage],
        batch_config: BatchProcessingConfig,
        result: ProcessingResult,
        output_format: str
    ) -> ProcessingResult:
        """Process emails in parallel batches."""
        import asyncio

        # Split emails into batches
        batches = [
            emails[i:i + batch_config.batch_size]
            for i in range(0, len(emails), batch_config.batch_size)
        ]

        # Process batches with concurrency limit
        semaphore = asyncio.Semaphore(batch_config.max_concurrent_batches)

        async def process_batch(batch: List[EmailMessage], batch_num: int):
            async with semaphore:
                try:
                    processed_batch = await self._process_output(batch, output_format)
                    result.processed_items += len(batch)
                    self.logger.debug(f"Batch {batch_num + 1} completed",
                                    batch_size=len(batch))
                except Exception as e:
                    result.failed_items += len(batch)
                    result.warnings.append(f"Batch {batch_num + 1} failed: {e}")
                    self.logger.warning(f"Batch {batch_num + 1} failed: {e}")

        # Execute all batches
        tasks = [process_batch(batch, i) for i, batch in enumerate(batches)]
        await asyncio.gather(*tasks, return_exceptions=True)

        return result

    async def _process_emails_sequential_batch(
        self,
        emails: List[EmailMessage],
        batch_config: BatchProcessingConfig,
        result: ProcessingResult,
        output_format: str
    ) -> ProcessingResult:
        """Process emails in sequential batches."""
        # Split emails into batches
        batches = [
            emails[i:i + batch_config.batch_size]
            for i in range(0, len(emails), batch_config.batch_size)
        ]

        for i, batch in enumerate(batches):
            try:
                processed_batch = await self._process_output(batch, output_format)
                result.processed_items += len(batch)
                self.logger.debug(f"Batch {i + 1}/{len(batches)} completed",
                                batch_size=len(batch))
            except Exception as e:
                result.failed_items += len(batch)
                result.warnings.append(f"Batch {i + 1} failed: {e}")
                self.logger.warning(f"Batch {i + 1} failed: {e}")

        return result


# Convenience function for simple usage
async def ingest_emails_simple(
    client_id: str,
    client_secret: str,
    tenant_id: str,
    user_id: str = "me",
    folder_ids: Optional[List[str]] = None,
    output_format: str = "json"
) -> Dict[str, Any]:
    """
    Simple function to ingest emails with minimal configuration.
    
    Args:
        client_id: Azure app client ID
        client_secret: Azure app client secret
        tenant_id: Azure tenant ID
        user_id: User ID or 'me' for current user
        folder_ids: List of folder IDs to ingest from
        output_format: Output format ('json', 'csv')
        
    Returns:
        Ingestion results
    """
    from evolvishub_outlook_ingestor.protocols.microsoft_graph import GraphAPIAdapter
    from evolvishub_outlook_ingestor.core.config import Settings
    
    # Create settings
    settings = Settings()
    settings.graph_api.client_id = client_id
    settings.graph_api.client_secret = client_secret
    settings.graph_api.tenant_id = tenant_id
    
    # Create adapter
    adapter = GraphAPIAdapter("graph_api", {
        "client_id": client_id,
        "client_secret": client_secret,
        "tenant_id": tenant_id
    })
    await adapter.initialize()
    
    # Create ingestor
    ingestor = EmailIngestor(settings=settings, graph_adapter=adapter)
    await ingestor.initialize()
    
    try:
        # Perform ingestion
        result = await ingestor.ingest_emails(
            folder_ids=folder_ids,
            user_id=user_id,
            output_format=output_format
        )
        
        return {
            "status": result.status.value,
            "processed_emails": result.processed_emails,
            "failed_emails": result.failed_emails,
            "data": result.output_data
        }
        
    finally:
        await ingestor.cleanup()
