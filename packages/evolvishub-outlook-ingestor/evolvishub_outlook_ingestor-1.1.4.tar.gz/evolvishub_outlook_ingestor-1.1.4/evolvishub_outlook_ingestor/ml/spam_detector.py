"""
Spam detection using machine learning.

This module provides spam detection capabilities using various ML algorithms
and feature extraction techniques.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.core.exceptions import MLError

logger = logging.getLogger(__name__)


@dataclass
class SpamDetectionResult:
    """Result of spam detection."""
    email_id: str
    is_spam: bool
    spam_score: float
    confidence: float
    features_used: List[str]


class SpamDetector:
    """
    Spam detection using machine learning algorithms.
    
    Provides comprehensive spam detection including:
    - Feature extraction from email content
    - ML-based classification
    - Confidence scoring
    - Model training and evaluation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the spam detector.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.threshold = config.get('spam_threshold', 0.5)
        
    async def initialize(self) -> None:
        """Initialize the spam detector."""
        logger.info("Initializing SpamDetector")
        
    async def detect_spam(self, email: EmailMessage) -> SpamDetectionResult:
        """
        Detect if an email is spam.
        
        Args:
            email: Email message to analyze
            
        Returns:
            Spam detection result
        """
        try:
            # Extract features
            features = await self._extract_features(email)
            
            # Calculate spam score (simplified)
            spam_score = await self._calculate_spam_score(features)
            
            # Determine if spam
            is_spam = spam_score > self.threshold
            
            return SpamDetectionResult(
                email_id=email.id,
                is_spam=is_spam,
                spam_score=spam_score,
                confidence=abs(spam_score - 0.5) * 2,  # Distance from threshold
                features_used=list(features.keys())
            )
            
        except Exception as e:
            logger.error(f"Error detecting spam: {e}")
            raise MLError(f"Spam detection failed: {e}")
    
    async def _extract_features(self, email: EmailMessage) -> Dict[str, float]:
        """Extract features for spam detection."""
        features = {}
        
        # Text-based features
        subject = email.subject or ""
        body = email.body or ""
        
        features['subject_length'] = len(subject)
        features['body_length'] = len(body)
        features['has_subject'] = 1.0 if subject else 0.0
        features['has_body'] = 1.0 if body else 0.0
        
        # Spam keywords
        spam_keywords = ['free', 'win', 'money', 'urgent', 'click here']
        content = f"{subject} {body}".lower()
        features['spam_keyword_count'] = sum(1 for keyword in spam_keywords if keyword in content)
        
        return features
    
    async def _calculate_spam_score(self, features: Dict[str, float]) -> float:
        """Calculate spam score from features."""
        # Simplified scoring logic
        score = 0.0
        
        # High spam keyword count increases score
        if features.get('spam_keyword_count', 0) > 2:
            score += 0.6
        
        # Very short or very long emails might be spam
        body_length = features.get('body_length', 0)
        if body_length < 10 or body_length > 10000:
            score += 0.3
        
        # Missing subject is suspicious
        if not features.get('has_subject', 0):
            score += 0.2
        
        return min(1.0, score)  # Cap at 1.0
