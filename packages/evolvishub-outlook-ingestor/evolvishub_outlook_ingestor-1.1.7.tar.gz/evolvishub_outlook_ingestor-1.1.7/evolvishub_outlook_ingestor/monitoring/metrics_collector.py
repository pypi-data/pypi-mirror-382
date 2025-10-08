"""
Metrics collection for monitoring and observability.

This module provides comprehensive metrics collection capabilities using
Prometheus and custom business metrics.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.core.exceptions import MonitoringError

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    """A metric measurement."""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]
    metric_type: str  # counter, gauge, histogram


class MetricsCollector:
    """
    Collects and exports metrics for monitoring.
    
    Provides comprehensive metrics collection including:
    - Performance metrics
    - Business metrics
    - System health metrics
    - Custom application metrics
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the metrics collector.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.metrics: List[Metric] = []
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        
    async def initialize(self) -> None:
        """Initialize the metrics collector."""
        logger.info("Initializing MetricsCollector")
        
    async def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        self.counters[name] = self.counters.get(name, 0) + value
        
        metric = Metric(
            name=name,
            value=self.counters[name],
            timestamp=datetime.utcnow(),
            labels=labels or {},
            metric_type="counter"
        )
        
        self.metrics.append(metric)
        
    async def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric."""
        self.gauges[name] = value
        
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            labels=labels or {},
            metric_type="gauge"
        )
        
        self.metrics.append(metric)
        
    async def record_email_processed(self, email: EmailMessage, processing_time: float) -> None:
        """Record email processing metrics."""
        await self.increment_counter("emails_processed_total", labels={"status": "success"})
        await self.set_gauge("email_processing_duration_seconds", processing_time)
        
    async def get_metrics(self) -> List[Metric]:
        """Get all collected metrics."""
        return self.metrics.copy()
        
    async def export_metrics(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        for metric in self.metrics:
            labels_str = ""
            if metric.labels:
                label_pairs = [f'{k}="{v}"' for k, v in metric.labels.items()]
                labels_str = "{" + ",".join(label_pairs) + "}"
            
            lines.append(f"{metric.name}{labels_str} {metric.value}")
        
        return "\n".join(lines)
