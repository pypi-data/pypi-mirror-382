"""
Evolvishub Outlook Ingestor

A comprehensive Python library for fetching data from Microsoft Outlook servers
and storing it in various databases with support for multiple protocols and
high-performance batch processing.

Key Features:
- Multiple Outlook protocols (Exchange Web Services, Microsoft Graph API, IMAP/POP3)
- Configurable database connectors (PostgreSQL, MongoDB, MySQL)
- Structured data extraction from emails (headers, body, attachments, metadata)
- Batch processing for large-scale email datasets
- Clean architecture with Repository, Factory, and Strategy patterns
- Async/await support for high-performance data processing
- Comprehensive error handling and retry mechanisms
- Horizontal scalability and high-load scenarios support

Example Usage:
    ```python
    from evolvishub_outlook_ingestor import OutlookIngestor
    from evolvishub_outlook_ingestor.core.config import get_settings
    
    # Initialize with configuration
    settings = get_settings()
    ingestor = OutlookIngestor(settings)
    
    # Process emails asynchronously
    await ingestor.process_emails(
        protocol="graph_api",
        database="postgresql",
        batch_size=1000
    )
    ```
"""

from typing import TYPE_CHECKING

# Version information
__version__ = "1.0.2"
__author__ = "Alban Maxhuni, PhD"
__email__ = "a.maxhuni@evolvis.ai"
__license__ = "Evolvis AI"

# Public API exports
from evolvishub_outlook_ingestor.core.config import Settings, get_settings
from evolvishub_outlook_ingestor.core.data_models import (
    EmailMessage,
    EmailAddress,
    EmailAttachment,
    OutlookFolder,
    ProcessingResult,
    ProcessingStatus,
)
from evolvishub_outlook_ingestor.core.exceptions import (
    OutlookIngestorError,
    ProtocolError,
    DatabaseError,
    ConfigurationError,
    AuthenticationError,
)

# Conditional imports for type checking
if TYPE_CHECKING:
    from evolvishub_outlook_ingestor.core.base_processor import BaseProcessor
    from evolvishub_outlook_ingestor.protocols.base_protocol import BaseProtocol
    from evolvishub_outlook_ingestor.connectors.base_connector import BaseConnector

# Main ingestor class
from evolvishub_outlook_ingestor.core.ingestor import OutlookIngestor

# Protocol adapters with proper error handling
def _import_protocols():
    """Import protocol adapters with detailed error reporting."""
    try:
        from evolvishub_outlook_ingestor.protocols import (
            BaseProtocol,
            GraphAPIAdapter,
            ExchangeWebServicesAdapter,
            IMAPAdapter,
        )
        return True, {
            'BaseProtocol': BaseProtocol,
            'GraphAPIAdapter': GraphAPIAdapter,
            'ExchangeWebServicesAdapter': ExchangeWebServicesAdapter,
            'IMAPAdapter': IMAPAdapter,
        }
    except ImportError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Protocol adapters not available: {e}")
        logger.info("Install protocol dependencies: pip install 'evolvishub-outlook-ingestor[protocols]'")
        return False, {}

# Database connectors with proper error handling
def _import_connectors():
    """Import database connectors with detailed error reporting."""
    try:
        from evolvishub_outlook_ingestor.connectors import (
            BaseConnector,
            PostgreSQLConnector,
            MongoDBConnector,
        )
        return True, {
            'BaseConnector': BaseConnector,
            'PostgreSQLConnector': PostgreSQLConnector,
            'MongoDBConnector': MongoDBConnector,
        }
    except ImportError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Database connectors not available: {e}")
        logger.info("Install database dependencies: pip install 'evolvishub-outlook-ingestor[database]'")
        return False, {}

# Processors with proper error handling
def _import_processors():
    """Import processors with detailed error reporting."""
    try:
        from evolvishub_outlook_ingestor.processors import (
            EmailProcessor,
            AttachmentProcessor,
        )
        return True, {
            'EmailProcessor': EmailProcessor,
            'AttachmentProcessor': AttachmentProcessor,
        }
    except ImportError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Processors not available: {e}")
        logger.info("Install processing dependencies: pip install 'evolvishub-outlook-ingestor[processing]'")
        return False, {}

# Import components with error handling
_PROTOCOLS_AVAILABLE, _PROTOCOL_CLASSES = _import_protocols()
_CONNECTORS_AVAILABLE, _CONNECTOR_CLASSES = _import_connectors()
_PROCESSORS_AVAILABLE, _PROCESSOR_CLASSES = _import_processors()

# Make classes available at module level
if _PROTOCOLS_AVAILABLE:
    globals().update(_PROTOCOL_CLASSES)

if _CONNECTORS_AVAILABLE:
    globals().update(_CONNECTOR_CLASSES)

if _PROCESSORS_AVAILABLE:
    globals().update(_PROCESSOR_CLASSES)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",

    # Core classes
    "OutlookIngestor",
    "Settings",
    "get_settings",

    # Data models
    "EmailMessage",
    "EmailAddress",
    "EmailAttachment",
    "OutlookFolder",
    "ProcessingResult",
    "ProcessingStatus",

    # Exceptions
    "OutlookIngestorError",
    "ProtocolError",
    "DatabaseError",
    "ConfigurationError",
    "AuthenticationError",
]

# Add protocol adapters to __all__ if available
if _PROTOCOLS_AVAILABLE:
    __all__.extend([
        "BaseProtocol",
        "GraphAPIAdapter",
        "ExchangeWebServicesAdapter",
        "IMAPAdapter",
    ])

# Add database connectors to __all__ if available
if _CONNECTORS_AVAILABLE:
    __all__.extend([
        "BaseConnector",
        "PostgreSQLConnector",
        "MongoDBConnector",
    ])

# Add processors to __all__ if available
if _PROCESSORS_AVAILABLE:
    __all__.extend([
        "EmailProcessor",
        "AttachmentProcessor",
    ])

# Package metadata
__package_name__ = "evolvishub-outlook-ingestor"
__description__ = "Professional Python library for comprehensive Outlook data ingestion and database storage"
__url__ = "https://github.com/evolvisai/metcal"
__classifiers__ = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: Other/Proprietary License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Communications :: Email",
    "Topic :: Database",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Archiving",
    "Typing :: Typed",
]
