"""
Natural Language Processing for email content.

This module provides comprehensive NLP capabilities including
text analysis, entity extraction, sentiment analysis, and content classification.
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


class SentimentType(Enum):
    """Sentiment analysis types."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class EntityExtraction:
    """Extracted entity information."""
    entity_type: str
    entity_value: str
    confidence: float
    start_position: int
    end_position: int


@dataclass
class SentimentAnalysis:
    """Sentiment analysis result."""
    sentiment: SentimentType
    confidence: float
    positive_score: float
    negative_score: float
    neutral_score: float


@dataclass
class NLPResult:
    """NLP processing result."""
    email_id: str
    language: str
    sentiment: SentimentAnalysis
    entities: List[EntityExtraction]
    keywords: List[str]
    topics: List[str]
    summary: str
    word_count: int
    readability_score: float


class NLPProcessor:
    """
    Natural Language Processing for email content.
    
    Provides comprehensive NLP capabilities including:
    - Language detection
    - Sentiment analysis
    - Named entity recognition
    - Keyword extraction
    - Topic modeling
    - Text summarization
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the NLP processor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.enabled_features = config.get('enabled_features', [
            'language_detection', 'sentiment_analysis', 'entity_extraction',
            'keyword_extraction', 'topic_modeling', 'summarization'
        ])
        
        # Simple word lists for basic processing
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'perfect'
        }
        
        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike',
            'angry', 'frustrated', 'disappointed', 'upset', 'problem', 'issue'
        }
        
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
            'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
    async def initialize(self) -> None:
        """Initialize the NLP processor."""
        logger.info("Initializing NLPProcessor")
        
    async def process_email(self, email: EmailMessage) -> NLPResult:
        """
        Process email content with NLP.
        
        Args:
            email: Email message to process
            
        Returns:
            NLP processing result
        """
        try:
            # Combine subject and body for analysis
            text = f"{email.subject or ''} {email.body or ''}"
            
            # Language detection (simplified)
            language = await self._detect_language(text)
            
            # Sentiment analysis
            sentiment = await self._analyze_sentiment(text)
            
            # Entity extraction
            entities = await self._extract_entities(text)
            
            # Keyword extraction
            keywords = await self._extract_keywords(text)
            
            # Topic modeling (simplified)
            topics = await self._extract_topics(text)
            
            # Text summarization
            summary = await self._summarize_text(text)
            
            # Basic metrics
            word_count = len(text.split())
            readability_score = await self._calculate_readability(text)
            
            return NLPResult(
                email_id=email.id,
                language=language,
                sentiment=sentiment,
                entities=entities,
                keywords=keywords,
                topics=topics,
                summary=summary,
                word_count=word_count,
                readability_score=readability_score
            )
            
        except Exception as e:
            logger.error(f"Error processing email with NLP: {e}")
            raise TransformationError(f"NLP processing failed: {e}")
    
    async def _detect_language(self, text: str) -> str:
        """Detect text language (simplified implementation)."""
        # Very basic language detection
        # In a real implementation, you'd use a proper language detection library
        
        if not text.strip():
            return "unknown"
        
        # Simple heuristics
        english_indicators = ['the', 'and', 'is', 'to', 'of', 'a', 'in', 'that']
        spanish_indicators = ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es']
        french_indicators = ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et']
        
        text_lower = text.lower()
        
        english_score = sum(1 for word in english_indicators if word in text_lower)
        spanish_score = sum(1 for word in spanish_indicators if word in text_lower)
        french_score = sum(1 for word in french_indicators if word in text_lower)
        
        if english_score >= spanish_score and english_score >= french_score:
            return "en"
        elif spanish_score >= french_score:
            return "es"
        elif french_score > 0:
            return "fr"
        else:
            return "en"  # Default to English
    
    async def _analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """Analyze text sentiment (simplified implementation)."""
        if not text.strip():
            return SentimentAnalysis(
                sentiment=SentimentType.NEUTRAL,
                confidence=0.0,
                positive_score=0.0,
                negative_score=0.0,
                neutral_score=1.0
            )
        
        words = text.lower().split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        total_words = len(words)
        
        if total_words == 0:
            return SentimentAnalysis(
                sentiment=SentimentType.NEUTRAL,
                confidence=0.0,
                positive_score=0.0,
                negative_score=0.0,
                neutral_score=1.0
            )
        
        positive_score = positive_count / total_words
        negative_score = negative_count / total_words
        neutral_score = 1.0 - positive_score - negative_score
        
        # Determine overall sentiment
        if positive_score > negative_score and positive_score > 0.1:
            sentiment = SentimentType.POSITIVE
            confidence = positive_score
        elif negative_score > positive_score and negative_score > 0.1:
            sentiment = SentimentType.NEGATIVE
            confidence = negative_score
        else:
            sentiment = SentimentType.NEUTRAL
            confidence = neutral_score
        
        return SentimentAnalysis(
            sentiment=sentiment,
            confidence=min(1.0, confidence * 5),  # Scale confidence
            positive_score=positive_score,
            negative_score=negative_score,
            neutral_score=neutral_score
        )
    
    async def _extract_entities(self, text: str) -> List[EntityExtraction]:
        """Extract named entities (simplified implementation)."""
        entities = []
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entities.append(EntityExtraction(
                entity_type="EMAIL",
                entity_value=match.group(),
                confidence=0.9,
                start_position=match.start(),
                end_position=match.end()
            ))
        
        # Phone pattern
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        for match in re.finditer(phone_pattern, text):
            entities.append(EntityExtraction(
                entity_type="PHONE",
                entity_value=match.group(),
                confidence=0.8,
                start_position=match.start(),
                end_position=match.end()
            ))
        
        # URL pattern
        url_pattern = r'https?://[^\s]+'
        for match in re.finditer(url_pattern, text):
            entities.append(EntityExtraction(
                entity_type="URL",
                entity_value=match.group(),
                confidence=0.9,
                start_position=match.start(),
                end_position=match.end()
            ))
        
        return entities
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords (simplified implementation)."""
        if not text.strip():
            return []
        
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out stop words and short words
        keywords = [
            word for word in words 
            if word not in self.stop_words and len(word) > 3
        ]
        
        # Count frequency and return top keywords
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top 10
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_keywords[:10]]
    
    async def _extract_topics(self, text: str) -> List[str]:
        """Extract topics (simplified implementation)."""
        # Very basic topic extraction based on keywords
        business_keywords = {'meeting', 'project', 'deadline', 'report', 'budget', 'client'}
        technical_keywords = {'system', 'database', 'server', 'code', 'bug', 'feature'}
        personal_keywords = {'family', 'vacation', 'birthday', 'lunch', 'weekend'}
        
        text_lower = text.lower()
        topics = []
        
        if any(keyword in text_lower for keyword in business_keywords):
            topics.append("business")
        
        if any(keyword in text_lower for keyword in technical_keywords):
            topics.append("technical")
        
        if any(keyword in text_lower for keyword in personal_keywords):
            topics.append("personal")
        
        return topics if topics else ["general"]
    
    async def _summarize_text(self, text: str) -> str:
        """Summarize text (simplified implementation)."""
        if not text.strip():
            return ""
        
        # Very basic summarization - return first sentence or first 100 characters
        sentences = re.split(r'[.!?]+', text)
        if sentences and len(sentences[0].strip()) > 10:
            return sentences[0].strip()[:100] + "..."
        
        return text[:100] + "..." if len(text) > 100 else text
    
    async def _calculate_readability(self, text: str) -> float:
        """Calculate readability score (simplified implementation)."""
        if not text.strip():
            return 0.0
        
        # Very basic readability calculation
        words = text.split()
        sentences = len(re.split(r'[.!?]+', text))
        
        if sentences == 0:
            return 0.0
        
        avg_words_per_sentence = len(words) / sentences
        
        # Simple scoring: lower is more readable
        if avg_words_per_sentence <= 10:
            return 0.9  # Very readable
        elif avg_words_per_sentence <= 15:
            return 0.7  # Readable
        elif avg_words_per_sentence <= 20:
            return 0.5  # Moderately readable
        else:
            return 0.3  # Difficult to read
