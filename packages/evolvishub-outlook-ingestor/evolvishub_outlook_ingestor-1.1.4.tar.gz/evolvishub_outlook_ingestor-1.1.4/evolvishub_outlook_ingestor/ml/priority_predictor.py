"""
Email priority prediction using machine learning.

This module provides priority prediction capabilities for email messages
using various ML algorithms and feature extraction techniques.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.core.exceptions import MLError

logger = logging.getLogger(__name__)


class PriorityLevel(Enum):
    """Email priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class PriorityPrediction:
    """Priority prediction result."""
    email_id: str
    predicted_priority: PriorityLevel
    confidence: float
    features_used: List[str]
    reasoning: str


class PriorityPredictor:
    """
    Predicts email priority using machine learning.
    
    Provides comprehensive priority prediction including:
    - Feature extraction from email content and metadata
    - ML-based priority classification
    - Confidence scoring and reasoning
    - Model training and evaluation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the priority predictor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.model = None
        
    async def initialize(self) -> None:
        """Initialize the priority predictor."""
        logger.info("Initializing PriorityPredictor")
        
    async def predict_priority(self, email: EmailMessage) -> PriorityPrediction:
        """
        Predict the priority of an email.
        
        Args:
            email: Email message to analyze
            
        Returns:
            Priority prediction result
        """
        try:
            # Extract features
            features = await self._extract_features(email)
            
            # Predict priority (simplified logic)
            priority, confidence, reasoning = await self._predict(features)
            
            return PriorityPrediction(
                email_id=email.id,
                predicted_priority=priority,
                confidence=confidence,
                features_used=list(features.keys()),
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Error predicting priority: {e}")
            raise MLError(f"Priority prediction failed: {e}")
    
    async def _extract_features(self, email: EmailMessage) -> Dict[str, float]:
        """Extract features for priority prediction."""
        features = {}
        
        # Sender features
        if email.sender:
            sender = email.sender.email if hasattr(email.sender, 'email') else str(email.sender)
            features['sender_is_internal'] = 1.0 if '@company.com' in sender else 0.0
        
        # Subject features
        subject = email.subject or ""
        urgent_keywords = ['urgent', 'asap', 'immediate', 'critical', 'emergency']
        features['urgent_keywords'] = sum(1 for keyword in urgent_keywords if keyword.lower() in subject.lower())
        
        # Recipient features
        recipient_count = len(email.to_recipients or []) + len(email.cc_recipients or [])
        features['recipient_count'] = recipient_count
        features['is_broadcast'] = 1.0 if recipient_count > 5 else 0.0
        
        # Time features
        if email.received_date:
            hour = email.received_date.hour
            features['is_business_hours'] = 1.0 if 9 <= hour <= 17 else 0.0
            features['is_weekend'] = 1.0 if email.received_date.weekday() >= 5 else 0.0
        
        # Content features
        features['has_attachments'] = 1.0 if email.has_attachments else 0.0
        features['body_length'] = len(email.body or '')
        
        return features
    
    async def _predict(self, features: Dict[str, float]) -> Tuple[PriorityLevel, float, str]:
        """Predict priority from features."""
        # Simplified rule-based prediction
        score = 0.0
        reasoning_parts = []
        
        # Urgent keywords strongly indicate high priority
        if features.get('urgent_keywords', 0) > 0:
            score += 0.8
            reasoning_parts.append("Contains urgent keywords")
        
        # Internal senders might be higher priority
        if features.get('sender_is_internal', 0) > 0:
            score += 0.3
            reasoning_parts.append("Internal sender")
        
        # Business hours emails might be more important
        if features.get('is_business_hours', 0) > 0:
            score += 0.2
            reasoning_parts.append("Sent during business hours")
        
        # Attachments might indicate importance
        if features.get('has_attachments', 0) > 0:
            score += 0.1
            reasoning_parts.append("Has attachments")
        
        # Broadcast emails might be less urgent
        if features.get('is_broadcast', 0) > 0:
            score -= 0.2
            reasoning_parts.append("Broadcast email")
        
        # Determine priority level
        if score >= 0.7:
            priority = PriorityLevel.URGENT
            confidence = min(1.0, score)
        elif score >= 0.5:
            priority = PriorityLevel.HIGH
            confidence = min(1.0, score)
        elif score >= 0.3:
            priority = PriorityLevel.MEDIUM
            confidence = min(1.0, score)
        else:
            priority = PriorityLevel.LOW
            confidence = 1.0 - score
        
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "No specific indicators"
        
        return priority, confidence, reasoning
