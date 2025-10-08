"""
Change Data Capture (CDC) and delta processing for email data.

This module provides efficient incremental data processing capabilities,
tracking changes and processing only modified data to optimize performance.
"""

from .cdc_service import CDCService

__all__ = [
    'CDCService'
]
