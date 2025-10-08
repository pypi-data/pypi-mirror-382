"""
Real-time streaming and event-driven processing for email data.

This module provides real-time streaming capabilities for email ingestion,
enabling immediate data availability and event-driven processing workflows.
"""

from .real_time_streamer import RealTimeEmailStreamer
from .event_processor import EventProcessor
from .websocket_server import WebSocketEmailServer
from .stream_manager import StreamManager

__all__ = [
    'RealTimeEmailStreamer',
    'EventProcessor', 
    'WebSocketEmailServer',
    'StreamManager'
]
