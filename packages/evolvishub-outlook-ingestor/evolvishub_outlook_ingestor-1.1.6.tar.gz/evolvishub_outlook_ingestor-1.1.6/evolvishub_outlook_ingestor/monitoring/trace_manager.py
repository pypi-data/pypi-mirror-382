"""
Distributed tracing and request tracking.

This module provides comprehensive tracing capabilities for monitoring
request flows and performance across distributed systems.
"""

import asyncio
import logging
import time
import uuid
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from contextlib import asynccontextmanager

from evolvishub_outlook_ingestor.core.exceptions import MonitoringError

logger = logging.getLogger(__name__)


@dataclass
class Span:
    """A trace span."""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[float]
    tags: Dict[str, Any]
    logs: List[Dict[str, Any]]
    status: str  # 'ok', 'error', 'timeout'


class TraceManager:
    """
    Manages distributed tracing and request tracking.
    
    Provides comprehensive tracing including:
    - Span creation and management
    - Trace correlation across services
    - Performance monitoring
    - Request flow visualization
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the trace manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.active_spans: Dict[str, Span] = {}
        self.completed_traces: List[Span] = []
        
    async def initialize(self) -> None:
        """Initialize the trace manager."""
        logger.info("Initializing TraceManager")
        
    def start_span(
        self, 
        operation_name: str, 
        parent_span_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> str:
        """Start a new span."""
        span_id = str(uuid.uuid4())
        if not trace_id:
            trace_id = str(uuid.uuid4())
        
        span = Span(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=datetime.utcnow(),
            end_time=None,
            duration_ms=None,
            tags={},
            logs=[],
            status='ok'
        )
        
        self.active_spans[span_id] = span
        return span_id
        
    def finish_span(self, span_id: str, status: str = 'ok') -> None:
        """Finish a span."""
        if span_id in self.active_spans:
            span = self.active_spans[span_id]
            span.end_time = datetime.utcnow()
            span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
            span.status = status
            
            self.completed_traces.append(span)
            del self.active_spans[span_id]
    
    @asynccontextmanager
    async def trace_operation(self, operation_name: str, **tags):
        """Context manager for tracing operations."""
        span_id = self.start_span(operation_name)
        
        # Add tags
        if span_id in self.active_spans:
            self.active_spans[span_id].tags.update(tags)
        
        try:
            yield span_id
            self.finish_span(span_id, 'ok')
        except Exception as e:
            self.finish_span(span_id, 'error')
            if span_id in self.completed_traces:
                # Find the completed span and add error info
                for span in self.completed_traces:
                    if span.span_id == span_id:
                        span.tags['error'] = str(e)
                        break
            raise
    
    def get_trace(self, trace_id: str) -> List[Span]:
        """Get all spans for a trace."""
        return [span for span in self.completed_traces if span.trace_id == trace_id]
