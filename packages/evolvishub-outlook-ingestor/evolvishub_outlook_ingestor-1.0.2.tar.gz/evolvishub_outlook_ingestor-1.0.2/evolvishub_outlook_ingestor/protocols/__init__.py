"""
Protocol adapters for Evolvishub Outlook Ingestor.

This module contains protocol adapters for different Outlook connection methods:
- Exchange Web Services (EWS)
- Microsoft Graph API
- IMAP/POP3

All protocol adapters implement a common interface defined by BaseProtocol
to ensure consistent behavior and easy switching between protocols.
"""

from evolvishub_outlook_ingestor.protocols.base_protocol import BaseProtocol
from evolvishub_outlook_ingestor.protocols.microsoft_graph import GraphAPIAdapter
from evolvishub_outlook_ingestor.protocols.exchange_web_services import ExchangeWebServicesAdapter
from evolvishub_outlook_ingestor.protocols.imap_pop3 import IMAPAdapter

__all__ = [
    "BaseProtocol",
    "GraphAPIAdapter",
    "ExchangeWebServicesAdapter",
    "IMAPAdapter",
]
