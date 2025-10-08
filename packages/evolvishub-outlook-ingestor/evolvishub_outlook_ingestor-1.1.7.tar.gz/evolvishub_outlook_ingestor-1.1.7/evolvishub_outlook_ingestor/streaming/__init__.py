"""
Real-time streaming and event-driven processing for email data.

This module provides real-time streaming capabilities for email ingestion,
enabling immediate data availability and event-driven processing workflows.
"""

from .real_time_streamer import RealTimeEmailStreamer

# Kafka integration with graceful fallback
try:
    from .kafka_streamer import KafkaStreamer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

    # Create a placeholder class for when Kafka is not available
    class KafkaStreamer:
        def __init__(self, *args, **kwargs):
            raise ImportError("Kafka streaming requires aiokafka. Install with: pip install 'evolvishub-outlook-ingestor[streaming]'")

__all__ = [
    'RealTimeEmailStreamer',
    'KafkaStreamer'
]
