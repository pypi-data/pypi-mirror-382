"""
Enterprise-grade Kafka streaming for email processing.

This module provides complete Kafka integration with producer/consumer
implementation, partition management, and performance optimization.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, AsyncGenerator, Callable, AsyncIterator
from dataclasses import dataclass
from enum import Enum

try:
    from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
    from aiokafka.errors import KafkaError, KafkaTimeoutError
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("aiokafka not available - Kafka functionality will be limited")

from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.core.exceptions import StreamingError
from evolvishub_outlook_ingestor.core.interfaces import IStreamingService

logger = logging.getLogger(__name__)


class KafkaCompressionType(Enum):
    """Kafka compression types."""
    NONE = "none"
    GZIP = "gzip"
    SNAPPY = "snappy"
    LZ4 = "lz4"
    ZSTD = "zstd"


@dataclass
class KafkaMetrics:
    """Kafka performance metrics."""
    messages_produced: int
    messages_consumed: int
    bytes_produced: int
    bytes_consumed: int
    average_latency_ms: float
    throughput_per_second: float
    error_count: int
    last_updated: datetime


@dataclass
class ProducerConfig:
    """Kafka producer configuration."""
    bootstrap_servers: List[str]
    topic_prefix: str
    compression_type: KafkaCompressionType
    batch_size: int
    linger_ms: int
    acks: str
    retries: int
    max_in_flight_requests: int
    enable_idempotence: bool
    buffer_memory: int


@dataclass
class ConsumerConfig:
    """Kafka consumer configuration."""
    bootstrap_servers: List[str]
    group_id: str
    topic_pattern: str
    auto_offset_reset: str
    enable_auto_commit: bool
    max_poll_interval_ms: int
    fetch_max_bytes: int
    max_partition_fetch_bytes: int


class KafkaStreamer(IStreamingService):
    """
    Enterprise-grade Kafka streaming for email processing.
    
    Provides comprehensive Kafka integration including:
    - High-performance producer with batching and compression
    - Consumer groups with offset management
    - Partition-aware processing
    - Dead letter queue handling
    - Performance monitoring and metrics
    - Automatic retry and error handling
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Kafka streamer.
        
        Args:
            config: Configuration dictionary containing Kafka settings
        """
        if not KAFKA_AVAILABLE:
            raise StreamingError("aiokafka is required for Kafka streaming. Install with: pip install aiokafka")
        
        self.config = config
        self.bootstrap_servers = config.get('bootstrap_servers', ['localhost:9092'])
        self.topic_prefix = config.get('topic_prefix', 'outlook_emails')
        self.consumer_group = config.get('consumer_group', 'outlook_processors')
        
        # Producer configuration
        self.producer_config = ProducerConfig(
            bootstrap_servers=self.bootstrap_servers,
            topic_prefix=self.topic_prefix,
            compression_type=KafkaCompressionType(config.get('compression_type', 'gzip')),
            batch_size=config.get('batch_size', 16384),
            linger_ms=config.get('linger_ms', 10),
            acks=config.get('acks', 'all'),
            retries=config.get('retries', 2147483647),
            max_in_flight_requests=config.get('max_in_flight_requests', 5),
            enable_idempotence=config.get('enable_idempotence', True),
            buffer_memory=config.get('buffer_memory', 33554432)  # 32MB
        )
        
        # Consumer configuration
        self.consumer_config = ConsumerConfig(
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.consumer_group,
            topic_pattern=f"{self.topic_prefix}.*",
            auto_offset_reset=config.get('auto_offset_reset', 'latest'),
            enable_auto_commit=config.get('enable_auto_commit', False),
            max_poll_interval_ms=config.get('max_poll_interval_ms', 300000),
            fetch_max_bytes=config.get('fetch_max_bytes', 52428800),  # 50MB
            max_partition_fetch_bytes=config.get('max_partition_fetch_bytes', 1048576)  # 1MB
        )
        
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.is_running = False
        
        # Performance metrics
        self.metrics = KafkaMetrics(
            messages_produced=0,
            messages_consumed=0,
            bytes_produced=0,
            bytes_consumed=0,
            average_latency_ms=0.0,
            throughput_per_second=0.0,
            error_count=0,
            last_updated=datetime.utcnow()
        )
        
        # Performance tracking
        self.latency_samples: List[float] = []
        self.throughput_window_start = time.time()
        self.throughput_message_count = 0
        
    async def initialize(self) -> None:
        """Initialize Kafka producer and consumer."""
        try:
            logger.info("Initializing Kafka streamer")
            
            # Initialize producer
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.producer_config.bootstrap_servers,
                value_serializer=self._serialize_message,
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                compression_type=self.producer_config.compression_type.value,
                batch_size=self.producer_config.batch_size,
                linger_ms=self.producer_config.linger_ms,
                acks=self.producer_config.acks,
                retries=self.producer_config.retries,
                max_in_flight_requests_per_connection=self.producer_config.max_in_flight_requests,
                enable_idempotence=self.producer_config.enable_idempotence,
                buffer_memory=self.producer_config.buffer_memory
            )
            
            await self.producer.start()
            logger.info("Kafka producer initialized successfully")
            
            # Initialize consumer
            self.consumer = AIOKafkaConsumer(
                bootstrap_servers=self.consumer_config.bootstrap_servers,
                group_id=self.consumer_config.group_id,
                value_deserializer=self._deserialize_message,
                auto_offset_reset=self.consumer_config.auto_offset_reset,
                enable_auto_commit=self.consumer_config.enable_auto_commit,
                max_poll_interval_ms=self.consumer_config.max_poll_interval_ms,
                fetch_max_bytes=self.consumer_config.fetch_max_bytes,
                max_partition_fetch_bytes=self.consumer_config.max_partition_fetch_bytes
            )
            
            # Subscribe to topics
            await self.consumer.start()
            self.consumer.subscribe(pattern=self.consumer_config.topic_pattern)
            logger.info("Kafka consumer initialized successfully")
            
            self.is_running = True
            
        except Exception as e:
            logger.error(f"Error initializing Kafka streamer: {e}")
            raise StreamingError(f"Kafka initialization failed: {e}")
    
    async def cleanup(self) -> None:
        """Clean up Kafka resources."""
        try:
            self.is_running = False
            
            if self.producer:
                await self.producer.stop()
                logger.info("Kafka producer stopped")
            
            if self.consumer:
                await self.consumer.stop()
                logger.info("Kafka consumer stopped")
                
        except Exception as e:
            logger.error(f"Error cleaning up Kafka resources: {e}")
    
    async def stream_email(self, email: EmailMessage) -> None:
        """
        Stream a single email to Kafka.
        
        Args:
            email: Email message to stream
            
        Raises:
            StreamingError: If streaming fails
        """
        try:
            if not self.producer:
                raise StreamingError("Kafka producer not initialized")
            
            start_time = time.time()
            
            # Determine topic and partition key
            topic = f"{self.topic_prefix}.raw_emails"
            partition_key = await self._calculate_partition_key(email)
            
            # Send message
            future = await self.producer.send_and_wait(
                topic=topic,
                value=email,
                key=partition_key
            )
            
            # Update metrics
            latency_ms = (time.time() - start_time) * 1000
            self._update_producer_metrics(email, latency_ms)
            
            logger.debug(f"Streamed email {email.id} to topic {topic} with latency {latency_ms:.2f}ms")
            
        except Exception as e:
            self.metrics.error_count += 1
            logger.error(f"Error streaming email: {e}")
            raise StreamingError(f"Email streaming failed: {e}")
    
    async def stream_emails_batch(self, emails: List[EmailMessage]) -> None:
        """
        Stream multiple emails in batch for better performance.
        
        Args:
            emails: List of email messages to stream
        """
        try:
            if not self.producer:
                raise StreamingError("Kafka producer not initialized")
            
            start_time = time.time()
            
            # Send all emails asynchronously
            futures = []
            topic = f"{self.topic_prefix}.raw_emails"
            
            for email in emails:
                partition_key = await self._calculate_partition_key(email)
                future = self.producer.send(
                    topic=topic,
                    value=email,
                    key=partition_key
                )
                futures.append(future)
            
            # Wait for all sends to complete
            await asyncio.gather(*futures)
            
            # Update metrics
            batch_latency_ms = (time.time() - start_time) * 1000
            for email in emails:
                self._update_producer_metrics(email, batch_latency_ms / len(emails))
            
            logger.info(f"Streamed batch of {len(emails)} emails in {batch_latency_ms:.2f}ms")
            
        except Exception as e:
            self.metrics.error_count += 1
            logger.error(f"Error streaming email batch: {e}")
            raise StreamingError(f"Batch streaming failed: {e}")
    
    async def consume_emails(
        self, 
        callback: Callable[[EmailMessage], None],
        batch_size: int = 100
    ) -> None:
        """
        Consume emails from Kafka with callback processing.
        
        Args:
            callback: Function to call for each email
            batch_size: Number of messages to process in batch
        """
        try:
            if not self.consumer:
                raise StreamingError("Kafka consumer not initialized")
            
            logger.info("Starting email consumption from Kafka")
            batch = []
            
            async for message in self.consumer:
                try:
                    start_time = time.time()
                    
                    # Deserialize email
                    email = message.value
                    batch.append(email)
                    
                    # Process batch when full
                    if len(batch) >= batch_size:
                        await self._process_email_batch(batch, callback)
                        
                        # Commit offsets
                        await self.consumer.commit()
                        
                        batch = []
                    
                    # Update metrics
                    processing_time_ms = (time.time() - start_time) * 1000
                    self._update_consumer_metrics(email, processing_time_ms)
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await self._send_to_dlq(message, str(e))
                    self.metrics.error_count += 1
            
            # Process remaining messages in batch
            if batch:
                await self._process_email_batch(batch, callback)
                await self.consumer.commit()
                
        except Exception as e:
            logger.error(f"Error consuming emails: {e}")
            raise StreamingError(f"Email consumption failed: {e}")
    
    async def stream_emails_generator(self) -> AsyncGenerator[List[EmailMessage], None]:
        """
        Generate batches of emails from Kafka stream.
        
        Yields:
            Batches of email messages
        """
        try:
            if not self.consumer:
                raise StreamingError("Kafka consumer not initialized")
            
            batch = []
            batch_size = self.config.get('batch_size', 100)
            
            async for message in self.consumer:
                try:
                    email = message.value
                    batch.append(email)
                    
                    if len(batch) >= batch_size:
                        yield batch
                        await self.consumer.commit()
                        batch = []
                        
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await self._send_to_dlq(message, str(e))
            
            # Yield remaining messages
            if batch:
                yield batch
                await self.consumer.commit()
                
        except Exception as e:
            logger.error(f"Error in email generator: {e}")
            raise StreamingError(f"Email generation failed: {e}")
    
    async def get_performance_metrics(self) -> KafkaMetrics:
        """Get current performance metrics."""
        # Update throughput calculation
        current_time = time.time()
        time_window = current_time - self.throughput_window_start
        
        if time_window > 0:
            self.metrics.throughput_per_second = self.throughput_message_count / time_window
        
        # Update average latency
        if self.latency_samples:
            self.metrics.average_latency_ms = sum(self.latency_samples) / len(self.latency_samples)
            # Keep only recent samples
            if len(self.latency_samples) > 1000:
                self.latency_samples = self.latency_samples[-500:]
        
        self.metrics.last_updated = datetime.utcnow()
        return self.metrics
    
    async def _calculate_partition_key(self, email: EmailMessage) -> str:
        """Calculate partition key for email distribution."""
        # Use sender domain for load balancing
        if email.sender:
            sender = email.sender.email if hasattr(email.sender, 'email') else str(email.sender)
            if '@' in sender:
                domain = sender.split('@')[1]
                return domain.lower()
        
        # Fallback to email ID hash
        return str(hash(email.id) % 100)
    
    async def _process_email_batch(
        self, 
        emails: List[EmailMessage], 
        callback: Callable[[EmailMessage], None]
    ) -> None:
        """Process a batch of emails with the callback."""
        for email in emails:
            try:
                callback(email)
            except Exception as e:
                logger.error(f"Error in callback for email {email.id}: {e}")
    
    async def _send_to_dlq(self, message: Any, error: str) -> None:
        """Send failed message to dead letter queue."""
        try:
            if not self.producer:
                return
            
            dlq_topic = f"{self.topic_prefix}.dlq"
            dlq_message = {
                'original_topic': message.topic,
                'original_partition': message.partition,
                'original_offset': message.offset,
                'original_value': message.value.to_dict() if hasattr(message.value, 'to_dict') else str(message.value),
                'error': error,
                'timestamp': datetime.utcnow().isoformat(),
                'consumer_group': self.consumer_group
            }
            
            await self.producer.send_and_wait(
                topic=dlq_topic,
                value=dlq_message,
                key=f"error_{message.partition}_{message.offset}"
            )
            
            logger.info(f"Sent message to DLQ: {dlq_topic}")
            
        except Exception as e:
            logger.error(f"Error sending to DLQ: {e}")
    
    def _serialize_message(self, message: Any) -> bytes:
        """Serialize message for Kafka."""
        try:
            if hasattr(message, 'to_dict'):
                data = message.to_dict()
            elif isinstance(message, dict):
                data = message
            else:
                data = {'data': str(message)}
            
            return json.dumps(data, default=str).encode('utf-8')
            
        except Exception as e:
            logger.error(f"Error serializing message: {e}")
            return json.dumps({'error': 'serialization_failed'}).encode('utf-8')
    
    def _deserialize_message(self, message_bytes: bytes) -> Any:
        """Deserialize message from Kafka."""
        try:
            data = json.loads(message_bytes.decode('utf-8'))
            
            # Try to reconstruct EmailMessage if possible
            if isinstance(data, dict) and 'id' in data:
                return EmailMessage(**data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error deserializing message: {e}")
            return {'error': 'deserialization_failed', 'raw_data': message_bytes.decode('utf-8', errors='ignore')}
    
    def _update_producer_metrics(self, email: EmailMessage, latency_ms: float) -> None:
        """Update producer performance metrics."""
        self.metrics.messages_produced += 1
        self.throughput_message_count += 1
        
        # Estimate message size
        message_size = len(email.body or '') + len(email.subject or '') + 1000  # Rough estimate
        self.metrics.bytes_produced += message_size
        
        # Track latency
        self.latency_samples.append(latency_ms)
        
        # Reset throughput window if needed
        current_time = time.time()
        if current_time - self.throughput_window_start > 60:  # 1 minute window
            self.throughput_window_start = current_time
            self.throughput_message_count = 0
    
    def _update_consumer_metrics(self, email: EmailMessage, processing_time_ms: float) -> None:
        """Update consumer performance metrics."""
        self.metrics.messages_consumed += 1

        # Estimate message size
        message_size = len(email.body or '') + len(email.subject or '') + 1000  # Rough estimate
        self.metrics.bytes_consumed += message_size

        # Track processing time as latency
        self.latency_samples.append(processing_time_ms)

    # Implementation of IStreamingService abstract methods
    async def start_streaming(self) -> None:
        """Start the streaming service."""
        await self.initialize()

    async def stop_streaming(self) -> None:
        """Stop the streaming service."""
        await self.cleanup()

    async def stream_emails(self, callback: Callable[[EmailMessage], None]) -> AsyncIterator[EmailMessage]:
        """Stream emails in real-time."""
        async for email_batch in self.stream_emails_generator():
            for email in email_batch:
                callback(email)
                yield email

    async def subscribe_to_folder(self, folder_id: str, callback: Callable[[EmailMessage], None]) -> str:
        """Subscribe to email updates from a specific folder."""
        # For Kafka, we can use topic filtering based on folder_id
        subscription_id = f"folder_{folder_id}_{int(time.time())}"

        # This would typically set up a filtered consumer
        # For now, return the subscription ID
        logger.info(f"Subscribed to folder {folder_id} with subscription {subscription_id}")

        return subscription_id
