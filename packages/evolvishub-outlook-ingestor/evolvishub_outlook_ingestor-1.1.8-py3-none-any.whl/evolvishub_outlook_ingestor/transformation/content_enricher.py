"""
Content enrichment and augmentation for email data.

This module provides comprehensive content enrichment capabilities including
metadata extraction, content classification, and data augmentation.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib

from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.core.exceptions import TransformationError

logger = logging.getLogger(__name__)


class EnrichmentType(Enum):
    """Types of content enrichment."""
    METADATA = "metadata"
    CLASSIFICATION = "classification"
    SENTIMENT = "sentiment"
    LANGUAGE = "language"
    TOPICS = "topics"
    KEYWORDS = "keywords"
    SUMMARY = "summary"


@dataclass
class EnrichmentResult:
    """Result of content enrichment."""
    enrichment_type: EnrichmentType
    data: Dict[str, Any]
    confidence: float
    processing_time_ms: float


class ContentEnricher:
    """
    Enriches email content with additional metadata and insights.
    
    Provides comprehensive content enrichment including:
    - Metadata extraction and augmentation
    - Content classification and tagging
    - Sentiment and language analysis
    - Topic modeling and keyword extraction
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the content enricher.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.enabled_enrichments = config.get('enabled_enrichments', [
            e.value for e in EnrichmentType
        ])
        
    async def initialize(self) -> None:
        """Initialize the content enricher."""
        logger.info("Initializing ContentEnricher")
        
    async def enrich_email(self, email: EmailMessage) -> Dict[str, EnrichmentResult]:
        """
        Enrich email content with additional metadata and insights.
        
        Args:
            email: Email message to enrich
            
        Returns:
            Dictionary of enrichment results
        """
        try:
            enrichments = {}
            
            # Apply each enabled enrichment
            for enrichment_type in EnrichmentType:
                if enrichment_type.value in self.enabled_enrichments:
                    result = await self._apply_enrichment(email, enrichment_type)
                    if result:
                        enrichments[enrichment_type.value] = result
            
            return enrichments
            
        except Exception as e:
            logger.error(f"Error enriching email content: {e}")
            raise TransformationError(f"Content enrichment failed: {e}")
    
    async def _apply_enrichment(
        self, 
        email: EmailMessage, 
        enrichment_type: EnrichmentType
    ) -> Optional[EnrichmentResult]:
        """Apply a specific type of enrichment."""
        import time
        start_time = time.time()
        
        try:
            if enrichment_type == EnrichmentType.METADATA:
                data = await self._extract_metadata(email)
            elif enrichment_type == EnrichmentType.CLASSIFICATION:
                data = await self._classify_content(email)
            elif enrichment_type == EnrichmentType.SENTIMENT:
                data = await self._analyze_sentiment(email)
            elif enrichment_type == EnrichmentType.LANGUAGE:
                data = await self._detect_language(email)
            elif enrichment_type == EnrichmentType.TOPICS:
                data = await self._extract_topics(email)
            elif enrichment_type == EnrichmentType.KEYWORDS:
                data = await self._extract_keywords(email)
            elif enrichment_type == EnrichmentType.SUMMARY:
                data = await self._generate_summary(email)
            else:
                return None
            
            processing_time = (time.time() - start_time) * 1000
            
            return EnrichmentResult(
                enrichment_type=enrichment_type,
                data=data,
                confidence=data.get('confidence', 0.8),
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error applying {enrichment_type.value} enrichment: {e}")
            return None
    
    async def _extract_metadata(self, email: EmailMessage) -> Dict[str, Any]:
        """Extract additional metadata from email."""
        metadata = {}
        
        # Content statistics
        subject_length = len(email.subject or '')
        body_length = len(email.body or '')
        
        metadata['content_stats'] = {
            'subject_length': subject_length,
            'body_length': body_length,
            'total_length': subject_length + body_length,
            'has_subject': subject_length > 0,
            'has_body': body_length > 0
        }
        
        # Recipient analysis
        to_count = len(email.to_recipients or [])
        cc_count = len(email.cc_recipients or [])
        bcc_count = len(email.bcc_recipients or [])
        
        metadata['recipient_stats'] = {
            'to_count': to_count,
            'cc_count': cc_count,
            'bcc_count': bcc_count,
            'total_recipients': to_count + cc_count + bcc_count,
            'is_broadcast': (to_count + cc_count + bcc_count) > 5
        }
        
        # Attachment analysis
        metadata['attachment_stats'] = {
            'has_attachments': email.has_attachments,
            'attachment_count': len(email.attachments or [])
        }
        
        # Generate content hash for deduplication
        content = f"{email.subject or ''}{email.body or ''}"
        content_hash = hashlib.md5(content.encode()).hexdigest()
        metadata['content_hash'] = content_hash
        
        metadata['confidence'] = 1.0
        return metadata
    
    async def _classify_content(self, email: EmailMessage) -> Dict[str, Any]:
        """Classify email content into categories."""
        content = f"{email.subject or ''} {email.body or ''}"
        content_lower = content.lower()
        
        categories = []
        confidence_scores = {}
        
        # Business categories
        business_keywords = ['meeting', 'project', 'deadline', 'report', 'budget', 'client', 'proposal']
        business_score = sum(1 for keyword in business_keywords if keyword in content_lower)
        if business_score > 0:
            categories.append('business')
            confidence_scores['business'] = min(1.0, business_score / 3)
        
        # Technical categories
        tech_keywords = ['system', 'database', 'server', 'code', 'bug', 'feature', 'deployment']
        tech_score = sum(1 for keyword in tech_keywords if keyword in content_lower)
        if tech_score > 0:
            categories.append('technical')
            confidence_scores['technical'] = min(1.0, tech_score / 3)
        
        # Personal categories
        personal_keywords = ['family', 'vacation', 'birthday', 'lunch', 'weekend', 'personal']
        personal_score = sum(1 for keyword in personal_keywords if keyword in content_lower)
        if personal_score > 0:
            categories.append('personal')
            confidence_scores['personal'] = min(1.0, personal_score / 3)
        
        # Marketing categories
        marketing_keywords = ['sale', 'discount', 'offer', 'promotion', 'deal', 'free', 'limited time']
        marketing_score = sum(1 for keyword in marketing_keywords if keyword in content_lower)
        if marketing_score > 0:
            categories.append('marketing')
            confidence_scores['marketing'] = min(1.0, marketing_score / 3)
        
        if not categories:
            categories = ['general']
            confidence_scores['general'] = 0.5
        
        return {
            'categories': categories,
            'confidence_scores': confidence_scores,
            'primary_category': max(confidence_scores.keys(), key=confidence_scores.get),
            'confidence': max(confidence_scores.values()) if confidence_scores else 0.5
        }
    
    async def _analyze_sentiment(self, email: EmailMessage) -> Dict[str, Any]:
        """Analyze sentiment of email content."""
        # Simplified sentiment analysis
        content = f"{email.subject or ''} {email.body or ''}"
        content_lower = content.lower()
        
        positive_words = ['good', 'great', 'excellent', 'love', 'happy', 'pleased', 'wonderful']
        negative_words = ['bad', 'terrible', 'hate', 'angry', 'frustrated', 'disappointed']
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(1.0, positive_count / 5)
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(1.0, negative_count / 5)
        else:
            sentiment = 'neutral'
            confidence = 0.7
        
        return {
            'sentiment': sentiment,
            'positive_score': positive_count,
            'negative_score': negative_count,
            'confidence': confidence
        }
    
    async def _detect_language(self, email: EmailMessage) -> Dict[str, Any]:
        """Detect language of email content."""
        # Very basic language detection
        content = f"{email.subject or ''} {email.body or ''}"
        
        # Simple heuristics
        if not content.strip():
            return {'language': 'unknown', 'confidence': 0.0}
        
        # Default to English for simplicity
        return {'language': 'en', 'confidence': 0.8}
    
    async def _extract_topics(self, email: EmailMessage) -> Dict[str, Any]:
        """Extract topics from email content."""
        content = f"{email.subject or ''} {email.body or ''}"
        content_lower = content.lower()
        
        topics = []
        
        # Simple topic extraction based on keywords
        topic_keywords = {
            'finance': ['budget', 'cost', 'money', 'payment', 'invoice', 'financial'],
            'technology': ['system', 'software', 'database', 'server', 'code'],
            'management': ['meeting', 'project', 'deadline', 'team', 'manager'],
            'marketing': ['campaign', 'promotion', 'customer', 'sales', 'marketing'],
            'hr': ['employee', 'hiring', 'training', 'benefits', 'policy']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)
        
        return {
            'topics': topics if topics else ['general'],
            'confidence': 0.7 if topics else 0.5
        }
    
    async def _extract_keywords(self, email: EmailMessage) -> Dict[str, Any]:
        """Extract keywords from email content."""
        import re
        
        content = f"{email.subject or ''} {email.body or ''}"
        
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Filter out common stop words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count frequency and return top keywords
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top 10
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        top_keywords = [word for word, freq in sorted_keywords[:10]]
        
        return {
            'keywords': top_keywords,
            'keyword_frequencies': dict(sorted_keywords[:10]),
            'confidence': 0.8 if top_keywords else 0.3
        }
    
    async def _generate_summary(self, email: EmailMessage) -> Dict[str, Any]:
        """Generate summary of email content."""
        content = f"{email.subject or ''} {email.body or ''}"
        
        if not content.strip():
            return {'summary': '', 'confidence': 0.0}
        
        # Very basic summarization - return first sentence or first 100 characters
        import re
        sentences = re.split(r'[.!?]+', content)
        
        if sentences and len(sentences[0].strip()) > 10:
            summary = sentences[0].strip()[:200] + "..."
        else:
            summary = content[:200] + "..." if len(content) > 200 else content
        
        return {
            'summary': summary,
            'original_length': len(content),
            'summary_length': len(summary),
            'compression_ratio': len(summary) / len(content) if content else 0,
            'confidence': 0.6
        }
