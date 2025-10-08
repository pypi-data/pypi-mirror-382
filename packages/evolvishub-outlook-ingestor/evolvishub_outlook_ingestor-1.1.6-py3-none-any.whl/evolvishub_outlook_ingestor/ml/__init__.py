"""
Machine learning integration for email data processing.

This module provides comprehensive ML capabilities including
email classification, spam detection, priority prediction, and feature extraction.
"""

from .ml_service import MLService
from .email_classifier import EmailClassifier
from .spam_detector import SpamDetector
from .priority_predictor import PriorityPredictor

__all__ = [
    'MLService',
    'EmailClassifier',
    'SpamDetector',
    'PriorityPredictor'
]
