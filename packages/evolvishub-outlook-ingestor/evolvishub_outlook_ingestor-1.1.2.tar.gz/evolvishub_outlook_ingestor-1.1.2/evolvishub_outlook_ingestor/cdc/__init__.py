"""
Change Data Capture (CDC) and delta processing for email data.

This module provides efficient incremental data processing capabilities,
tracking changes and processing only modified data to optimize performance.
"""

from .cdc_service import CDCService
from .delta_processor import DeltaProcessor
from .change_tracker import ChangeTracker

__all__ = [
    'CDCService',
    'DeltaProcessor',
    'ChangeTracker'
]
