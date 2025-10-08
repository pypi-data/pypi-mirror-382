"""
Change Data Capture (CDC) service for efficient incremental processing.

This module provides comprehensive CDC capabilities for tracking and processing
only changed email data, dramatically improving performance for large datasets.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from evolvishub_outlook_ingestor.core.interfaces import ICDCService, service_registry
from evolvishub_outlook_ingestor.core.data_models import EmailMessage, EmailAttachment, OutlookFolder
from evolvishub_outlook_ingestor.core.exceptions import DatabaseError


class ChangeType(Enum):
    """Types of changes that can be tracked."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MOVE = "move"
    READ = "read"
    UNREAD = "unread"


class EntityType(Enum):
    """Types of entities that can be tracked."""
    EMAIL = "email"
    ATTACHMENT = "attachment"
    FOLDER = "folder"


@dataclass
class ChangeRecord:
    """Represents a change record in the CDC system."""
    id: str
    entity_id: str
    entity_type: EntityType
    change_type: ChangeType
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    processed: bool = False
    retry_count: int = 0


class CDCService(ICDCService):
    """
    Change Data Capture service for efficient incremental email processing.
    
    This service tracks all changes to email data and provides efficient
    delta processing capabilities, reducing the need to reprocess unchanged data.
    
    Features:
    - Tracks all CRUD operations on emails, attachments, and folders
    - Provides efficient delta queries
    - Supports batch processing of changes
    - Handles change conflicts and retries
    - Maintains change history for auditing
    
    Example:
        ```python
        cdc = CDCService({
            'storage_connector': postgresql_connector,
            'batch_size': 1000,
            'retention_days': 30
        })
        
        await cdc.initialize()
        
        # Track a change
        await cdc.track_change(
            entity_id="email_123",
            entity_type="email",
            change_type="update",
            data={"subject": "Updated subject"}
        )
        
        # Get changes since timestamp
        changes = await cdc.get_changes_since(
            timestamp=yesterday,
            entity_type="email"
        )
        ```
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.storage_connector = config.get('storage_connector')
        self.batch_size = config.get('batch_size', 1000)
        self.retention_days = config.get('retention_days', 30)
        self.enable_compression = config.get('enable_compression', True)
        self.max_retries = config.get('max_retries', 3)
        
        # State management
        self.is_initialized = False
        self._change_buffer: List[ChangeRecord] = []
        self._processing_lock = asyncio.Lock()
        
        # Background tasks
        self._batch_processor_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Metrics
        self.metrics = {
            'changes_tracked': 0,
            'changes_processed': 0,
            'changes_failed': 0,
            'last_processed_timestamp': None
        }
    
    async def initialize(self) -> None:
        """Initialize the CDC service."""
        if self.is_initialized:
            return
        
        try:
            self.logger.info("Initializing CDC service")
            
            # Validate storage connector
            if not self.storage_connector:
                raise ValueError("Storage connector is required for CDC service")
            
            # Create CDC tables
            await self._create_cdc_tables()
            
            # Start background tasks
            self._batch_processor_task = asyncio.create_task(self._batch_processor())
            self._cleanup_task = asyncio.create_task(self._cleanup_old_changes())
            
            self.is_initialized = True
            self.logger.info("CDC service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize CDC service: {str(e)}")
            raise DatabaseError(f"CDC initialization failed: {str(e)}")
    
    async def shutdown(self) -> None:
        """Shutdown the CDC service."""
        if not self.is_initialized:
            return
        
        self.logger.info("Shutting down CDC service")
        
        # Cancel background tasks
        tasks = [self._batch_processor_task, self._cleanup_task]
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Process remaining changes
        if self._change_buffer:
            await self._flush_changes()
        
        self.is_initialized = False
        self.logger.info("CDC service shutdown complete")
    
    async def track_change(self, entity_id: str, entity_type: str, change_type: str, data: Dict[str, Any]) -> None:
        """
        Track a change to an entity.
        
        Args:
            entity_id: Unique identifier of the entity
            entity_type: Type of entity (email, attachment, folder)
            change_type: Type of change (create, update, delete, etc.)
            data: Change data payload
        """
        try:
            change_record = ChangeRecord(
                id=f"{entity_type}_{entity_id}_{datetime.utcnow().timestamp()}",
                entity_id=entity_id,
                entity_type=EntityType(entity_type),
                change_type=ChangeType(change_type),
                timestamp=datetime.utcnow(),
                data=data,
                metadata={
                    'source': 'cdc_service',
                    'version': '1.0'
                }
            )
            
            # Add to buffer
            async with self._processing_lock:
                self._change_buffer.append(change_record)
                self.metrics['changes_tracked'] += 1
            
            # Flush if buffer is full
            if len(self._change_buffer) >= self.batch_size:
                await self._flush_changes()
            
            self.logger.debug(f"Tracked change: {change_record.id}")
            
        except Exception as e:
            self.logger.error(f"Failed to track change: {str(e)}")
            self.metrics['changes_failed'] += 1
            raise
    
    async def get_changes_since(self, timestamp: datetime, entity_type: str) -> List[Dict[str, Any]]:
        """
        Get all changes since a specific timestamp.
        
        Args:
            timestamp: Timestamp to get changes since
            entity_type: Type of entity to filter by
            
        Returns:
            List of change records
        """
        try:
            # Flush pending changes first
            await self._flush_changes()
            
            # Query changes from storage
            if hasattr(self.storage_connector, 'execute'):
                # SQL-based connector
                query = """
                    SELECT * FROM cdc_changes 
                    WHERE timestamp > %s AND entity_type = %s 
                    ORDER BY timestamp ASC
                """
                results = await self.storage_connector.execute(query, (timestamp, entity_type))
                
                return [self._row_to_change_dict(row) for row in results]
            
            elif hasattr(self.storage_connector, 'find'):
                # MongoDB-based connector
                cursor = self.storage_connector.database.cdc_changes.find({
                    'timestamp': {'$gt': timestamp},
                    'entity_type': entity_type
                }).sort('timestamp', 1)
                
                results = await cursor.to_list(length=None)
                return [self._doc_to_change_dict(doc) for doc in results]
            
            else:
                raise ValueError("Unsupported storage connector for CDC")
        
        except Exception as e:
            self.logger.error(f"Failed to get changes since {timestamp}: {str(e)}")
            raise DatabaseError(f"Failed to retrieve changes: {str(e)}")
    
    async def get_latest_timestamp(self, entity_type: str) -> Optional[datetime]:
        """
        Get the latest change timestamp for an entity type.
        
        Args:
            entity_type: Type of entity
            
        Returns:
            Latest timestamp or None if no changes exist
        """
        try:
            if hasattr(self.storage_connector, 'execute'):
                # SQL-based connector
                query = """
                    SELECT MAX(timestamp) FROM cdc_changes 
                    WHERE entity_type = %s
                """
                result = await self.storage_connector.execute(query, (entity_type,))
                return result[0][0] if result and result[0][0] else None
            
            elif hasattr(self.storage_connector, 'find'):
                # MongoDB-based connector
                result = await self.storage_connector.database.cdc_changes.find_one(
                    {'entity_type': entity_type},
                    sort=[('timestamp', -1)]
                )
                return result['timestamp'] if result else None
            
            else:
                raise ValueError("Unsupported storage connector for CDC")
        
        except Exception as e:
            self.logger.error(f"Failed to get latest timestamp for {entity_type}: {str(e)}")
            return None
    
    async def get_entity_changes(self, entity_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all changes for a specific entity.
        
        Args:
            entity_id: ID of the entity
            limit: Maximum number of changes to return
            
        Returns:
            List of change records for the entity
        """
        try:
            if hasattr(self.storage_connector, 'execute'):
                # SQL-based connector
                query = """
                    SELECT * FROM cdc_changes 
                    WHERE entity_id = %s 
                    ORDER BY timestamp DESC 
                    LIMIT %s
                """
                results = await self.storage_connector.execute(query, (entity_id, limit))
                return [self._row_to_change_dict(row) for row in results]
            
            elif hasattr(self.storage_connector, 'find'):
                # MongoDB-based connector
                cursor = self.storage_connector.database.cdc_changes.find({
                    'entity_id': entity_id
                }).sort('timestamp', -1).limit(limit)
                
                results = await cursor.to_list(length=limit)
                return [self._doc_to_change_dict(doc) for doc in results]
        
        except Exception as e:
            self.logger.error(f"Failed to get entity changes for {entity_id}: {str(e)}")
            return []
    
    async def mark_changes_processed(self, change_ids: List[str]) -> None:
        """
        Mark changes as processed.
        
        Args:
            change_ids: List of change IDs to mark as processed
        """
        try:
            if hasattr(self.storage_connector, 'execute'):
                # SQL-based connector
                placeholders = ','.join(['%s'] * len(change_ids))
                query = f"""
                    UPDATE cdc_changes 
                    SET processed = TRUE, processed_at = NOW() 
                    WHERE id IN ({placeholders})
                """
                await self.storage_connector.execute(query, change_ids)
            
            elif hasattr(self.storage_connector, 'update_many'):
                # MongoDB-based connector
                await self.storage_connector.database.cdc_changes.update_many(
                    {'id': {'$in': change_ids}},
                    {'$set': {'processed': True, 'processed_at': datetime.utcnow()}}
                )
            
            self.metrics['changes_processed'] += len(change_ids)
            self.logger.debug(f"Marked {len(change_ids)} changes as processed")
        
        except Exception as e:
            self.logger.error(f"Failed to mark changes as processed: {str(e)}")
    
    async def _create_cdc_tables(self) -> None:
        """Create CDC tables in the storage backend."""
        if hasattr(self.storage_connector, 'execute'):
            # SQL-based connector
            await self.storage_connector.execute("""
                CREATE TABLE IF NOT EXISTS cdc_changes (
                    id VARCHAR(255) PRIMARY KEY,
                    entity_id VARCHAR(255) NOT NULL,
                    entity_type VARCHAR(50) NOT NULL,
                    change_type VARCHAR(50) NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    data JSONB NOT NULL,
                    metadata JSONB DEFAULT '{}',
                    processed BOOLEAN DEFAULT FALSE,
                    processed_at TIMESTAMP WITH TIME ZONE,
                    retry_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Create indexes
            await self.storage_connector.execute(
                "CREATE INDEX IF NOT EXISTS idx_cdc_timestamp ON cdc_changes(timestamp)"
            )
            await self.storage_connector.execute(
                "CREATE INDEX IF NOT EXISTS idx_cdc_entity ON cdc_changes(entity_id, entity_type)"
            )
            await self.storage_connector.execute(
                "CREATE INDEX IF NOT EXISTS idx_cdc_processed ON cdc_changes(processed)"
            )
        
        elif hasattr(self.storage_connector, 'create_index'):
            # MongoDB-based connector
            await self.storage_connector.database.cdc_changes.create_index("timestamp")
            await self.storage_connector.database.cdc_changes.create_index([("entity_id", 1), ("entity_type", 1)])
            await self.storage_connector.database.cdc_changes.create_index("processed")
    
    async def _flush_changes(self) -> None:
        """Flush pending changes to storage."""
        if not self._change_buffer:
            return
        
        async with self._processing_lock:
            changes_to_flush = self._change_buffer.copy()
            self._change_buffer.clear()
        
        try:
            if hasattr(self.storage_connector, 'execute_many'):
                # SQL-based connector
                values = []
                for change in changes_to_flush:
                    values.append((
                        change.id, change.entity_id, change.entity_type.value,
                        change.change_type.value, change.timestamp,
                        json.dumps(change.data), json.dumps(change.metadata),
                        change.processed, change.retry_count
                    ))
                
                query = """
                    INSERT INTO cdc_changes 
                    (id, entity_id, entity_type, change_type, timestamp, data, metadata, processed, retry_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                await self.storage_connector.execute_many(query, values)
            
            elif hasattr(self.storage_connector, 'insert_many'):
                # MongoDB-based connector
                documents = [asdict(change) for change in changes_to_flush]
                # Convert enums to strings
                for doc in documents:
                    doc['entity_type'] = doc['entity_type'].value
                    doc['change_type'] = doc['change_type'].value
                
                await self.storage_connector.database.cdc_changes.insert_many(documents)
            
            self.logger.debug(f"Flushed {len(changes_to_flush)} changes to storage")
        
        except Exception as e:
            self.logger.error(f"Failed to flush changes: {str(e)}")
            # Put changes back in buffer for retry
            async with self._processing_lock:
                self._change_buffer.extend(changes_to_flush)
            raise
    
    async def _batch_processor(self) -> None:
        """Background task to process changes in batches."""
        while self.is_initialized:
            try:
                if len(self._change_buffer) >= self.batch_size:
                    await self._flush_changes()
                
                await asyncio.sleep(5)  # Check every 5 seconds
            
            except Exception as e:
                self.logger.error(f"Error in batch processor: {str(e)}")
                await asyncio.sleep(10)
    
    async def _cleanup_old_changes(self) -> None:
        """Background task to clean up old change records."""
        while self.is_initialized:
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
                
                if hasattr(self.storage_connector, 'execute'):
                    # SQL-based connector
                    await self.storage_connector.execute(
                        "DELETE FROM cdc_changes WHERE timestamp < %s AND processed = TRUE",
                        (cutoff_date,)
                    )
                
                elif hasattr(self.storage_connector, 'delete_many'):
                    # MongoDB-based connector
                    await self.storage_connector.database.cdc_changes.delete_many({
                        'timestamp': {'$lt': cutoff_date},
                        'processed': True
                    })
                
                # Run cleanup daily
                await asyncio.sleep(24 * 60 * 60)
            
            except Exception as e:
                self.logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(60 * 60)  # Retry in 1 hour
    
    def _row_to_change_dict(self, row: tuple) -> Dict[str, Any]:
        """Convert SQL row to change dictionary."""
        return {
            'id': row[0],
            'entity_id': row[1],
            'entity_type': row[2],
            'change_type': row[3],
            'timestamp': row[4],
            'data': json.loads(row[5]) if row[5] else {},
            'metadata': json.loads(row[6]) if row[6] else {},
            'processed': row[7],
            'retry_count': row[9]
        }
    
    def _doc_to_change_dict(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to change dictionary."""
        return {
            'id': doc['id'],
            'entity_id': doc['entity_id'],
            'entity_type': doc['entity_type'],
            'change_type': doc['change_type'],
            'timestamp': doc['timestamp'],
            'data': doc['data'],
            'metadata': doc.get('metadata', {}),
            'processed': doc.get('processed', False),
            'retry_count': doc.get('retry_count', 0)
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get CDC service metrics."""
        return {
            **self.metrics,
            'buffer_size': len(self._change_buffer),
            'is_initialized': self.is_initialized,
            'retention_days': self.retention_days
        }
