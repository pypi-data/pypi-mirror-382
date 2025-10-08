"""
Real-time email streaming service.

This module provides real-time streaming capabilities for email data,
enabling immediate processing and delivery of email updates as they occur.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Callable, AsyncIterator, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from evolvishub_outlook_ingestor.core.interfaces import IStreamingService, service_registry
from evolvishub_outlook_ingestor.core.data_models import EmailMessage, OutlookFolder
from evolvishub_outlook_ingestor.core.exceptions import StreamingError


class StreamingMode(Enum):
    """Streaming operation modes."""
    PUSH = "push"
    PULL = "pull"
    HYBRID = "hybrid"


@dataclass
class StreamSubscription:
    """Represents a streaming subscription."""
    subscription_id: str
    folder_id: Optional[str]
    callback: Callable[[EmailMessage], None]
    filters: Dict[str, Any]
    created_at: datetime
    last_activity: datetime
    is_active: bool = True


class RealTimeEmailStreamer(IStreamingService):
    """
    Real-time email streaming service with WebSocket and event-driven capabilities.
    
    This service provides real-time streaming of email data with support for:
    - Live email updates as they arrive
    - Folder-specific subscriptions
    - Custom filtering and routing
    - Backpressure handling
    - Connection management
    
    Example:
        ```python
        streamer = RealTimeEmailStreamer({
            'mode': StreamingMode.HYBRID,
            'buffer_size': 1000,
            'heartbeat_interval': 30
        })
        
        await streamer.start_streaming()
        
        async def handle_email(email: EmailMessage):
            print(f"New email: {email.subject}")
        
        subscription_id = await streamer.subscribe_to_folder(
            folder_id="inbox",
            callback=handle_email
        )
        ```
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.mode = config.get('mode', StreamingMode.HYBRID)
        self.buffer_size = config.get('buffer_size', 1000)
        self.heartbeat_interval = config.get('heartbeat_interval', 30)
        self.max_connections = config.get('max_connections', 100)
        self.poll_interval = config.get('poll_interval', 5)
        
        # State management
        self.is_streaming = False
        self.subscriptions: Dict[str, StreamSubscription] = {}
        self.email_buffer: asyncio.Queue = asyncio.Queue(maxsize=self.buffer_size)
        self.active_connections: Set[str] = set()
        
        # Background tasks
        self._streaming_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._buffer_processor_task: Optional[asyncio.Task] = None
        
        # Redis connection for distributed streaming (optional)
        self._redis_client = None
        if config.get('redis_url'):
            self._setup_redis(config['redis_url'])
    
    async def start_streaming(self) -> None:
        """Start the real-time streaming service."""
        if self.is_streaming:
            self.logger.warning("Streaming service is already running")
            return
        
        try:
            self.logger.info("Starting real-time email streaming service")
            
            # Initialize Redis if configured
            if self._redis_client:
                await self._redis_client.ping()
                self.logger.info("Redis connection established for distributed streaming")
            
            # Start background tasks
            self._streaming_task = asyncio.create_task(self._streaming_loop())
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            self._buffer_processor_task = asyncio.create_task(self._process_buffer())
            
            self.is_streaming = True
            self.logger.info("Real-time streaming service started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start streaming service: {str(e)}")
            raise StreamingError(f"Failed to start streaming: {str(e)}")
    
    async def stop_streaming(self) -> None:
        """Stop the real-time streaming service."""
        if not self.is_streaming:
            return
        
        self.logger.info("Stopping real-time email streaming service")
        
        # Cancel background tasks
        tasks = [self._streaming_task, self._heartbeat_task, self._buffer_processor_task]
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Clear subscriptions
        self.subscriptions.clear()
        self.active_connections.clear()
        
        # Close Redis connection
        if self._redis_client:
            await self._redis_client.close()
        
        self.is_streaming = False
        self.logger.info("Real-time streaming service stopped")
    
    async def stream_emails(self, callback: Callable[[EmailMessage], None]) -> AsyncIterator[EmailMessage]:
        """
        Stream emails in real-time.
        
        Args:
            callback: Function to call for each email
            
        Yields:
            EmailMessage: Streamed email messages
        """
        if not self.is_streaming:
            await self.start_streaming()
        
        subscription_id = f"stream_{datetime.utcnow().timestamp()}"
        
        try:
            # Create subscription
            subscription = StreamSubscription(
                subscription_id=subscription_id,
                folder_id=None,  # All folders
                callback=callback,
                filters={},
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            
            self.subscriptions[subscription_id] = subscription
            self.logger.info(f"Created email stream subscription: {subscription_id}")
            
            # Stream emails from buffer
            while subscription.is_active and self.is_streaming:
                try:
                    # Wait for email with timeout
                    email = await asyncio.wait_for(
                        self.email_buffer.get(),
                        timeout=self.heartbeat_interval
                    )
                    
                    # Update activity
                    subscription.last_activity = datetime.utcnow()
                    
                    # Apply filters if any
                    if self._passes_filters(email, subscription.filters):
                        # Call callback
                        if callback:
                            try:
                                if asyncio.iscoroutinefunction(callback):
                                    await callback(email)
                                else:
                                    callback(email)
                            except Exception as e:
                                self.logger.error(f"Error in stream callback: {str(e)}")
                        
                        yield email
                
                except asyncio.TimeoutError:
                    # Heartbeat - check if subscription is still active
                    if datetime.utcnow() - subscription.last_activity > timedelta(minutes=5):
                        self.logger.info(f"Subscription {subscription_id} inactive, removing")
                        subscription.is_active = False
                        break
                
                except Exception as e:
                    self.logger.error(f"Error in email streaming: {str(e)}")
                    break
        
        finally:
            # Clean up subscription
            self.subscriptions.pop(subscription_id, None)
            self.logger.info(f"Removed email stream subscription: {subscription_id}")
    
    async def subscribe_to_folder(self, folder_id: str, callback: Callable[[EmailMessage], None]) -> str:
        """
        Subscribe to email updates from a specific folder.
        
        Args:
            folder_id: ID of the folder to monitor
            callback: Function to call for each email update
            
        Returns:
            str: Subscription ID for managing the subscription
        """
        subscription_id = f"folder_{folder_id}_{datetime.utcnow().timestamp()}"
        
        subscription = StreamSubscription(
            subscription_id=subscription_id,
            folder_id=folder_id,
            callback=callback,
            filters={'folder_id': folder_id},
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        
        self.subscriptions[subscription_id] = subscription
        self.logger.info(f"Created folder subscription: {subscription_id} for folder: {folder_id}")
        
        return subscription_id
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from a streaming subscription.
        
        Args:
            subscription_id: ID of the subscription to remove
            
        Returns:
            bool: True if subscription was removed, False if not found
        """
        subscription = self.subscriptions.pop(subscription_id, None)
        if subscription:
            subscription.is_active = False
            self.logger.info(f"Removed subscription: {subscription_id}")
            return True
        return False
    
    async def publish_email(self, email: EmailMessage) -> None:
        """
        Publish an email to all active subscriptions.
        
        Args:
            email: Email message to publish
        """
        try:
            # Add to buffer if not full
            if not self.email_buffer.full():
                await self.email_buffer.put(email)
            else:
                self.logger.warning("Email buffer is full, dropping email")
            
            # Publish to Redis for distributed streaming
            if self._redis_client:
                await self._publish_to_redis(email)
        
        except Exception as e:
            self.logger.error(f"Error publishing email: {str(e)}")
    
    def _setup_redis(self, redis_url: str) -> None:
        """Setup Redis connection for distributed streaming."""
        try:
            import redis.asyncio as redis
            self._redis_client = redis.from_url(redis_url)
        except ImportError:
            self.logger.warning("Redis not available, distributed streaming disabled")
    
    async def _streaming_loop(self) -> None:
        """Main streaming loop for polling mode."""
        while self.is_streaming:
            try:
                if self.mode in [StreamingMode.PULL, StreamingMode.HYBRID]:
                    # Poll for new emails (implementation depends on email source)
                    await self._poll_for_emails()
                
                await asyncio.sleep(self.poll_interval)
            
            except Exception as e:
                self.logger.error(f"Error in streaming loop: {str(e)}")
                await asyncio.sleep(self.poll_interval)
    
    async def _heartbeat_loop(self) -> None:
        """Heartbeat loop to maintain connections and clean up inactive subscriptions."""
        while self.is_streaming:
            try:
                current_time = datetime.utcnow()
                inactive_subscriptions = []
                
                for sub_id, subscription in self.subscriptions.items():
                    # Check for inactive subscriptions (no activity for 10 minutes)
                    if current_time - subscription.last_activity > timedelta(minutes=10):
                        inactive_subscriptions.append(sub_id)
                
                # Remove inactive subscriptions
                for sub_id in inactive_subscriptions:
                    await self.unsubscribe(sub_id)
                
                await asyncio.sleep(self.heartbeat_interval)
            
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {str(e)}")
                await asyncio.sleep(self.heartbeat_interval)
    
    async def _process_buffer(self) -> None:
        """Process emails from the buffer and distribute to subscriptions."""
        while self.is_streaming:
            try:
                # Get email from buffer
                email = await self.email_buffer.get()
                
                # Distribute to matching subscriptions
                for subscription in self.subscriptions.values():
                    if subscription.is_active and self._passes_filters(email, subscription.filters):
                        try:
                            if asyncio.iscoroutinefunction(subscription.callback):
                                await subscription.callback(email)
                            else:
                                subscription.callback(email)
                            
                            subscription.last_activity = datetime.utcnow()
                        
                        except Exception as e:
                            self.logger.error(f"Error in subscription callback: {str(e)}")
            
            except Exception as e:
                self.logger.error(f"Error processing buffer: {str(e)}")
    
    async def _poll_for_emails(self) -> None:
        """Poll for new emails (to be implemented based on email source)."""
        # This would integrate with the email protocols (Graph API, Exchange, IMAP)
        # to poll for new emails and add them to the buffer
        pass
    
    async def _publish_to_redis(self, email: EmailMessage) -> None:
        """Publish email to Redis for distributed streaming."""
        if self._redis_client:
            try:
                email_data = {
                    'id': email.id,
                    'subject': email.subject,
                    'sender': email.sender.email if email.sender else None,
                    'timestamp': datetime.utcnow().isoformat()
                }
                await self._redis_client.publish('email_stream', json.dumps(email_data))
            except Exception as e:
                self.logger.error(f"Error publishing to Redis: {str(e)}")
    
    def _passes_filters(self, email: EmailMessage, filters: Dict[str, Any]) -> bool:
        """Check if email passes the subscription filters."""
        if not filters:
            return True
        
        for key, value in filters.items():
            if key == 'folder_id' and email.folder_id != value:
                return False
            elif key == 'sender' and (not email.sender or email.sender.email != value):
                return False
            elif key == 'subject_contains' and (not email.subject or value.lower() not in email.subject.lower()):
                return False
        
        return True
    
    async def get_subscription_stats(self) -> Dict[str, Any]:
        """Get statistics about active subscriptions."""
        active_count = sum(1 for sub in self.subscriptions.values() if sub.is_active)
        
        return {
            'total_subscriptions': len(self.subscriptions),
            'active_subscriptions': active_count,
            'buffer_size': self.email_buffer.qsize(),
            'max_buffer_size': self.buffer_size,
            'is_streaming': self.is_streaming,
            'mode': self.mode.value,
            'active_connections': len(self.active_connections)
        }
