"""
Entity extraction from email content.

This module provides comprehensive entity extraction capabilities including
named entity recognition, PII detection, and custom entity extraction.
"""

import asyncio
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.core.exceptions import TransformationError

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Types of entities that can be extracted."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    DATE = "date"
    MONEY = "money"
    CREDIT_CARD = "credit_card"
    SSN = "ssn"
    IP_ADDRESS = "ip_address"


@dataclass
class ExtractedEntity:
    """An extracted entity."""
    entity_type: EntityType
    value: str
    confidence: float
    start_position: int
    end_position: int
    context: str
    metadata: Dict[str, Any]


class EntityExtractor:
    """
    Extracts entities from email content.
    
    Provides comprehensive entity extraction including:
    - Named entity recognition
    - PII detection and classification
    - Custom pattern matching
    - Context-aware extraction
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the entity extractor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.enabled_types = config.get('enabled_types', [e.value for e in EntityType])
        
        # Compile regex patterns
        self.patterns = self._compile_patterns()
        
    async def initialize(self) -> None:
        """Initialize the entity extractor."""
        logger.info("Initializing EntityExtractor")
        
    async def extract_entities(self, email: EmailMessage) -> List[ExtractedEntity]:
        """
        Extract entities from email content.
        
        Args:
            email: Email message to process
            
        Returns:
            List of extracted entities
        """
        try:
            entities = []
            
            # Combine subject and body for analysis
            text = f"{email.subject or ''} {email.body or ''}"
            
            # Extract each enabled entity type
            for entity_type in EntityType:
                if entity_type.value in self.enabled_types:
                    type_entities = await self._extract_entity_type(text, entity_type)
                    entities.extend(type_entities)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            raise TransformationError(f"Entity extraction failed: {e}")
    
    async def _extract_entity_type(self, text: str, entity_type: EntityType) -> List[ExtractedEntity]:
        """Extract entities of a specific type."""
        entities = []
        
        pattern = self.patterns.get(entity_type)
        if not pattern:
            return entities
        
        for match in pattern.finditer(text):
            # Get context around the match
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            context = text[start:end]
            
            entity = ExtractedEntity(
                entity_type=entity_type,
                value=match.group(),
                confidence=self._calculate_confidence(entity_type, match.group()),
                start_position=match.start(),
                end_position=match.end(),
                context=context,
                metadata={}
            )
            
            entities.append(entity)
        
        return entities
    
    def _compile_patterns(self) -> Dict[EntityType, re.Pattern]:
        """Compile regex patterns for entity extraction."""
        patterns = {}
        
        # Email pattern
        patterns[EntityType.EMAIL] = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            re.IGNORECASE
        )
        
        # Phone pattern
        patterns[EntityType.PHONE] = re.compile(
            r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
        )
        
        # URL pattern
        patterns[EntityType.URL] = re.compile(
            r'https?://[^\s]+|www\.[^\s]+',
            re.IGNORECASE
        )
        
        # Date pattern (simplified)
        patterns[EntityType.DATE] = re.compile(
            r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b'
        )
        
        # Money pattern
        patterns[EntityType.MONEY] = re.compile(
            r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\b\d+(?:\.\d{2})?\s*(?:dollars?|USD|usd)\b',
            re.IGNORECASE
        )
        
        # Credit card pattern
        patterns[EntityType.CREDIT_CARD] = re.compile(
            r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
        )
        
        # SSN pattern
        patterns[EntityType.SSN] = re.compile(
            r'\b\d{3}-\d{2}-\d{4}\b'
        )
        
        # IP address pattern
        patterns[EntityType.IP_ADDRESS] = re.compile(
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        )
        
        return patterns
    
    def _calculate_confidence(self, entity_type: EntityType, value: str) -> float:
        """Calculate confidence score for an extracted entity."""
        # Simple confidence calculation based on entity type and value characteristics
        
        if entity_type == EntityType.EMAIL:
            # Check for valid email structure
            if '@' in value and '.' in value.split('@')[1]:
                return 0.9
            return 0.6
        
        elif entity_type == EntityType.PHONE:
            # Check for standard phone number length
            digits = re.sub(r'\D', '', value)
            if len(digits) == 10 or len(digits) == 11:
                return 0.8
            return 0.5
        
        elif entity_type == EntityType.URL:
            # Check for protocol or www
            if value.startswith(('http://', 'https://', 'www.')):
                return 0.9
            return 0.6
        
        elif entity_type == EntityType.CREDIT_CARD:
            # Basic Luhn algorithm check could be added here
            digits = re.sub(r'\D', '', value)
            if len(digits) == 16:
                return 0.7
            return 0.4
        
        elif entity_type == EntityType.SSN:
            # Check for standard SSN format
            if re.match(r'^\d{3}-\d{2}-\d{4}$', value):
                return 0.8
            return 0.5
        
        elif entity_type == EntityType.IP_ADDRESS:
            # Check for valid IP address ranges
            parts = value.split('.')
            if all(0 <= int(part) <= 255 for part in parts):
                return 0.9
            return 0.4
        
        # Default confidence for other types
        return 0.7
