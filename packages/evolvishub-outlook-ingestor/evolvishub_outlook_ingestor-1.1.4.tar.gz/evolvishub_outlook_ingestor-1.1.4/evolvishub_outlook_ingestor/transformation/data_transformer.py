"""
Advanced data transformation service for email data.

This module provides comprehensive data transformation capabilities including
NLP processing, entity extraction, sentiment analysis, and content enrichment.
"""

import asyncio
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from evolvishub_outlook_ingestor.core.interfaces import IDataTransformer, service_registry
from evolvishub_outlook_ingestor.core.data_models import EmailMessage, EmailAddress
from evolvishub_outlook_ingestor.core.exceptions import TransformationError


@dataclass
class TransformationResult:
    """Result of data transformation operation."""
    original_email: EmailMessage
    transformed_email: EmailMessage
    extracted_entities: Dict[str, List[str]]
    sentiment_analysis: Dict[str, float]
    language: str
    metadata: Dict[str, Any]
    processing_time: float


class DataTransformer(IDataTransformer):
    """
    Advanced data transformation service for email data.
    
    This service provides comprehensive transformation capabilities including:
    - NLP processing and entity extraction
    - Sentiment analysis and language detection
    - Content cleaning and standardization
    - PII detection and masking
    - Data enrichment and augmentation
    
    Example:
        ```python
        transformer = DataTransformer({
            'enable_nlp': True,
            'enable_sentiment': True,
            'enable_pii_detection': True,
            'language_models': ['en', 'es', 'fr']
        })
        
        await transformer.initialize()
        
        transformed_email = await transformer.transform_email(email)
        entities = await transformer.extract_entities(email.body)
        sentiment = await transformer.analyze_sentiment(email.body)
        ```
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.enable_nlp = config.get('enable_nlp', True)
        self.enable_sentiment = config.get('enable_sentiment', True)
        self.enable_pii_detection = config.get('enable_pii_detection', True)
        self.enable_language_detection = config.get('enable_language_detection', True)
        self.language_models = config.get('language_models', ['en'])
        self.max_text_length = config.get('max_text_length', 10000)
        
        # NLP components (lazy loaded)
        self._nlp_models = {}
        self._sentiment_analyzer = None
        self._language_detector = None
        self._is_initialized = False
        
        # PII patterns
        self._pii_patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'),
            'ssn': re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
            'credit_card': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            'ip_address': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
        }
    
    async def initialize(self) -> None:
        """Initialize the data transformer with NLP models."""
        if self._is_initialized:
            return
        
        try:
            self.logger.info("Initializing data transformer")
            
            if self.enable_nlp:
                await self._load_nlp_models()
            
            if self.enable_sentiment:
                await self._load_sentiment_analyzer()
            
            if self.enable_language_detection:
                await self._load_language_detector()
            
            self._is_initialized = True
            self.logger.info("Data transformer initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize data transformer: {str(e)}")
            raise TransformationError(f"Initialization failed: {str(e)}")
    
    async def transform_email(self, email: EmailMessage) -> EmailMessage:
        """
        Transform an email message with comprehensive processing.
        
        Args:
            email: Email message to transform
            
        Returns:
            Transformed email message with enriched data
        """
        start_time = datetime.utcnow()
        
        try:
            if not self._is_initialized:
                await self.initialize()
            
            # Create a copy for transformation
            transformed_email = EmailMessage(
                id=email.id,
                message_id=email.message_id,
                conversation_id=email.conversation_id,
                subject=email.subject,
                body=email.body,
                body_preview=email.body_preview,
                body_type=email.body_type,
                is_html=email.is_html,
                sender=email.sender,
                from_address=email.from_address,
                to_recipients=email.to_recipients,
                cc_recipients=email.cc_recipients,
                bcc_recipients=email.bcc_recipients,
                reply_to=email.reply_to,
                sent_date=email.sent_date,
                received_date=email.received_date,
                created_date=email.created_date,
                modified_date=email.modified_date,
                importance=email.importance,
                sensitivity=email.sensitivity,
                priority=email.priority,
                is_read=email.is_read,
                is_draft=email.is_draft,
                has_attachments=email.has_attachments,
                is_flagged=email.is_flagged,
                folder_id=email.folder_id,
                folder_path=email.folder_path,
                attachments=email.attachments,
                headers=email.headers.copy(),
                internet_headers=email.internet_headers.copy(),
                categories=email.categories.copy(),
                in_reply_to=email.in_reply_to,
                references=email.references.copy(),
                size=email.size,
                extended_properties=email.extended_properties.copy()
            )
            
            # Clean and standardize content
            transformed_email = await self._clean_content(transformed_email)
            
            # Extract entities
            entities = await self.extract_entities(transformed_email.body or "")
            
            # Analyze sentiment
            sentiment = await self.analyze_sentiment(transformed_email.body or "")
            
            # Detect language
            language = await self.detect_language(transformed_email.body or "")
            
            # Detect and mask PII
            if self.enable_pii_detection:
                transformed_email = await self._mask_pii(transformed_email)
            
            # Add enriched data to extended properties
            transformed_email.extended_properties.update({
                'transformation': {
                    'entities': entities,
                    'sentiment': sentiment,
                    'language': language,
                    'processed_at': datetime.utcnow().isoformat(),
                    'transformer_version': '1.0'
                }
            })
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.debug(f"Transformed email {email.id} in {processing_time:.2f}s")
            
            return transformed_email
            
        except Exception as e:
            self.logger.error(f"Failed to transform email {email.id}: {str(e)}")
            raise TransformationError(f"Email transformation failed: {str(e)}")
    
    async def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from text using NLP models.
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Dictionary of entity types and their values
        """
        if not text or not self.enable_nlp:
            return {}
        
        try:
            # Truncate text if too long
            if len(text) > self.max_text_length:
                text = text[:self.max_text_length]
            
            entities = {
                'persons': [],
                'organizations': [],
                'locations': [],
                'dates': [],
                'emails': [],
                'phones': [],
                'urls': []
            }
            
            # Use spaCy for NLP if available
            if 'en' in self._nlp_models:
                doc = self._nlp_models['en'](text)
                
                for ent in doc.ents:
                    if ent.label_ in ['PERSON']:
                        entities['persons'].append(ent.text)
                    elif ent.label_ in ['ORG']:
                        entities['organizations'].append(ent.text)
                    elif ent.label_ in ['GPE', 'LOC']:
                        entities['locations'].append(ent.text)
                    elif ent.label_ in ['DATE', 'TIME']:
                        entities['dates'].append(ent.text)
            
            # Extract emails and phones using regex
            entities['emails'].extend(self._pii_patterns['email'].findall(text))
            entities['phones'].extend(self._pii_patterns['phone'].findall(text))
            
            # Extract URLs
            url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
            entities['urls'].extend(url_pattern.findall(text))
            
            # Remove duplicates and empty strings
            for key in entities:
                entities[key] = list(set(filter(None, entities[key])))
            
            return entities
            
        except Exception as e:
            self.logger.error(f"Failed to extract entities: {str(e)}")
            return {}
    
    async def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores
        """
        if not text or not self.enable_sentiment:
            return {'polarity': 0.0, 'subjectivity': 0.0}
        
        try:
            # Truncate text if too long
            if len(text) > self.max_text_length:
                text = text[:self.max_text_length]
            
            if self._sentiment_analyzer:
                blob = self._sentiment_analyzer(text)
                return {
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity
                }
            
            return {'polarity': 0.0, 'subjectivity': 0.0}
            
        except Exception as e:
            self.logger.error(f"Failed to analyze sentiment: {str(e)}")
            return {'polarity': 0.0, 'subjectivity': 0.0}
    
    async def detect_language(self, text: str) -> str:
        """
        Detect the language of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (e.g., 'en', 'es', 'fr')
        """
        if not text or not self.enable_language_detection:
            return 'unknown'
        
        try:
            # Truncate text if too long
            if len(text) > 1000:  # Language detection doesn't need full text
                text = text[:1000]
            
            if self._language_detector:
                return self._language_detector.detect(text)
            
            return 'unknown'
            
        except Exception as e:
            self.logger.error(f"Failed to detect language: {str(e)}")
            return 'unknown'
    
    async def _load_nlp_models(self) -> None:
        """Load NLP models for entity extraction."""
        try:
            import spacy
            
            for lang in self.language_models:
                try:
                    model_name = f"{lang}_core_web_sm"
                    self._nlp_models[lang] = spacy.load(model_name)
                    self.logger.info(f"Loaded spaCy model: {model_name}")
                except OSError:
                    self.logger.warning(f"spaCy model {model_name} not found, skipping")
            
        except ImportError:
            self.logger.warning("spaCy not available, entity extraction will be limited")
    
    async def _load_sentiment_analyzer(self) -> None:
        """Load sentiment analysis model."""
        try:
            from textblob import TextBlob
            self._sentiment_analyzer = TextBlob
            self.logger.info("Loaded TextBlob for sentiment analysis")
        except ImportError:
            self.logger.warning("TextBlob not available, sentiment analysis disabled")
    
    async def _load_language_detector(self) -> None:
        """Load language detection model."""
        try:
            from langdetect import detect
            self._language_detector = type('LanguageDetector', (), {'detect': lambda self, text: detect(text)})()
            self.logger.info("Loaded langdetect for language detection")
        except ImportError:
            self.logger.warning("langdetect not available, language detection disabled")
    
    async def _clean_content(self, email: EmailMessage) -> EmailMessage:
        """Clean and standardize email content."""
        if email.body:
            # Remove excessive whitespace
            email.body = re.sub(r'\s+', ' ', email.body).strip()
            
            # Remove HTML tags if it's HTML content
            if email.is_html:
                email.body = re.sub(r'<[^>]+>', '', email.body)
            
            # Normalize line endings
            email.body = email.body.replace('\r\n', '\n').replace('\r', '\n')
        
        if email.subject:
            # Clean subject line
            email.subject = email.subject.strip()
            # Remove common prefixes
            email.subject = re.sub(r'^(RE:|FW:|FWD:)\s*', '', email.subject, flags=re.IGNORECASE)
        
        return email
    
    async def _mask_pii(self, email: EmailMessage) -> EmailMessage:
        """Detect and mask PII in email content."""
        if not email.body:
            return email
        
        masked_body = email.body
        
        # Mask different types of PII
        for pii_type, pattern in self._pii_patterns.items():
            if pii_type == 'email':
                masked_body = pattern.sub('[EMAIL_MASKED]', masked_body)
            elif pii_type == 'phone':
                masked_body = pattern.sub('[PHONE_MASKED]', masked_body)
            elif pii_type == 'ssn':
                masked_body = pattern.sub('[SSN_MASKED]', masked_body)
            elif pii_type == 'credit_card':
                masked_body = pattern.sub('[CARD_MASKED]', masked_body)
            elif pii_type == 'ip_address':
                masked_body = pattern.sub('[IP_MASKED]', masked_body)
        
        # Store original body in extended properties for audit
        if masked_body != email.body:
            email.extended_properties['original_body_hash'] = hash(email.body)
            email.body = masked_body
        
        return email
    
    async def get_transformation_stats(self) -> Dict[str, Any]:
        """Get transformation service statistics."""
        return {
            'is_initialized': self._is_initialized,
            'nlp_enabled': self.enable_nlp,
            'sentiment_enabled': self.enable_sentiment,
            'pii_detection_enabled': self.enable_pii_detection,
            'language_detection_enabled': self.enable_language_detection,
            'loaded_models': list(self._nlp_models.keys()),
            'max_text_length': self.max_text_length
        }
