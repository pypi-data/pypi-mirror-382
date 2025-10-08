"""
Email classification using machine learning models.

This module provides comprehensive email classification capabilities using
scikit-learn models for spam detection, priority prediction, and categorization.
"""

import asyncio
import logging
import pickle
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import numpy as np

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import classification_report, accuracy_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.core.exceptions import MLError

logger = logging.getLogger(__name__)


@dataclass
class EmailClassification:
    """Email classification results."""
    email_id: str
    spam_score: float
    priority_score: float
    category: str
    category_confidence: float
    sentiment_score: float
    confidence_scores: Dict[str, float]
    classification_timestamp: datetime


@dataclass
class ModelMetrics:
    """Model performance metrics."""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_samples: int
    last_trained: datetime


@dataclass
class TrainingResult:
    """Model training results."""
    model_name: str
    accuracy: float
    training_samples: int
    validation_accuracy: float
    feature_count: int
    training_time_seconds: float
    model_path: Optional[str]


class EmailClassifier:
    """
    Advanced email classification using machine learning.
    
    Provides comprehensive email classification including:
    - Spam detection using RandomForest
    - Priority prediction using GradientBoosting
    - Category classification
    - Sentiment analysis
    - Feature extraction and model training
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the email classifier.
        
        Args:
            config: Configuration dictionary containing ML settings
        """
        if not SKLEARN_AVAILABLE:
            raise MLError("scikit-learn is required for ML functionality. Install with: pip install scikit-learn")
        
        self.config = config
        self.model_dir = Path(config.get('model_dir', 'models'))
        self.model_dir.mkdir(exist_ok=True)
        
        # Model configurations
        self.spam_threshold = config.get('spam_threshold', 0.5)
        self.priority_threshold = config.get('priority_threshold', 0.7)
        self.max_features = config.get('max_features', 10000)
        
        # Initialize models
        self.models = {}
        self.vectorizers = {}
        self.is_trained = {}
        
        # Categories for classification
        self.categories = config.get('categories', [
            'work', 'personal', 'promotional', 'social', 'updates', 'forums'
        ])
        
    async def initialize(self) -> None:
        """Initialize the email classifier."""
        logger.info("Initializing EmailClassifier")
        
        # Initialize spam detection model
        self.models['spam'] = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=self.max_features,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95
            )),
            ('classifier', RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            ))
        ])
        
        # Initialize priority prediction model
        self.models['priority'] = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2)
            )),
            ('classifier', GradientBoostingClassifier(
                n_estimators=100,
                random_state=42
            ))
        ])
        
        # Initialize category classification model
        self.models['category'] = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=8000,
                stop_words='english',
                ngram_range=(1, 3)
            )),
            ('classifier', RandomForestClassifier(
                n_estimators=150,
                random_state=42,
                n_jobs=-1
            ))
        ])
        
        # Load pre-trained models if available
        await self._load_models()
        
    async def classify_email(self, email: EmailMessage) -> EmailClassification:
        """
        Classify an email using all available models.
        
        Args:
            email: Email message to classify
            
        Returns:
            Email classification results
            
        Raises:
            MLError: If classification fails
        """
        try:
            # Extract features
            features = await self._extract_features(email)
            text_content = f"{email.subject or ''} {email.body or ''}"
            
            # Spam detection
            spam_score = await self._predict_spam(text_content)
            
            # Priority prediction
            priority_score = await self._predict_priority(text_content, features)
            
            # Category classification
            category, category_confidence = await self._predict_category(text_content)
            
            # Sentiment analysis (simplified)
            sentiment_score = await self._analyze_sentiment(text_content)
            
            # Compile confidence scores
            confidence_scores = {
                'spam': spam_score,
                'priority': priority_score,
                'category': category_confidence,
                'sentiment': abs(sentiment_score)
            }
            
            return EmailClassification(
                email_id=email.id,
                spam_score=spam_score,
                priority_score=priority_score,
                category=category,
                category_confidence=category_confidence,
                sentiment_score=sentiment_score,
                confidence_scores=confidence_scores,
                classification_timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error classifying email: {e}")
            raise MLError(f"Email classification failed: {e}")
    
    async def train_spam_model(self, training_emails: List[Tuple[EmailMessage, bool]]) -> TrainingResult:
        """
        Train the spam detection model.
        
        Args:
            training_emails: List of (email, is_spam) tuples
            
        Returns:
            Training results
        """
        try:
            if len(training_emails) < 10:
                raise MLError("Insufficient training data for spam model")
            
            start_time = datetime.utcnow()
            
            # Prepare training data
            X = []
            y = []
            
            for email, is_spam in training_emails:
                text_content = f"{email.subject or ''} {email.body or ''}"
                X.append(text_content)
                y.append(1 if is_spam else 0)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train model
            self.models['spam'].fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.models['spam'].predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(self.models['spam'], X_train, y_train, cv=5)
            validation_accuracy = cv_scores.mean()
            
            # Save model
            model_path = await self._save_model('spam')
            
            training_time = (datetime.utcnow() - start_time).total_seconds()
            
            self.is_trained['spam'] = True
            
            logger.info(f"Spam model trained with accuracy: {accuracy:.3f}")
            
            return TrainingResult(
                model_name='spam',
                accuracy=accuracy,
                training_samples=len(training_emails),
                validation_accuracy=validation_accuracy,
                feature_count=self.models['spam'].named_steps['tfidf'].vocabulary_.__len__() if hasattr(self.models['spam'].named_steps['tfidf'], 'vocabulary_') else 0,
                training_time_seconds=training_time,
                model_path=model_path
            )
            
        except Exception as e:
            logger.error(f"Error training spam model: {e}")
            raise MLError(f"Spam model training failed: {e}")
    
    async def train_priority_model(self, training_emails: List[Tuple[EmailMessage, str]]) -> TrainingResult:
        """
        Train the priority prediction model.
        
        Args:
            training_emails: List of (email, priority_level) tuples
            
        Returns:
            Training results
        """
        try:
            if len(training_emails) < 10:
                raise MLError("Insufficient training data for priority model")
            
            start_time = datetime.utcnow()
            
            # Prepare training data
            X = []
            y = []
            
            priority_mapping = {'low': 0, 'medium': 1, 'high': 2}
            
            for email, priority in training_emails:
                text_content = f"{email.subject or ''} {email.body or ''}"
                X.append(text_content)
                y.append(priority_mapping.get(priority.lower(), 1))
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train model
            self.models['priority'].fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.models['priority'].predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(self.models['priority'], X_train, y_train, cv=5)
            validation_accuracy = cv_scores.mean()
            
            # Save model
            model_path = await self._save_model('priority')
            
            training_time = (datetime.utcnow() - start_time).total_seconds()
            
            self.is_trained['priority'] = True
            
            logger.info(f"Priority model trained with accuracy: {accuracy:.3f}")
            
            return TrainingResult(
                model_name='priority',
                accuracy=accuracy,
                training_samples=len(training_emails),
                validation_accuracy=validation_accuracy,
                feature_count=self.models['priority'].named_steps['tfidf'].vocabulary_.__len__() if hasattr(self.models['priority'].named_steps['tfidf'], 'vocabulary_') else 0,
                training_time_seconds=training_time,
                model_path=model_path
            )
            
        except Exception as e:
            logger.error(f"Error training priority model: {e}")
            raise MLError(f"Priority model training failed: {e}")
    
    async def get_model_metrics(self, model_name: str) -> Optional[ModelMetrics]:
        """Get performance metrics for a model."""
        if model_name not in self.models or not self.is_trained.get(model_name, False):
            return None
        
        # This would typically load metrics from storage
        # For now, return placeholder metrics
        return ModelMetrics(
            model_name=model_name,
            accuracy=0.85,  # Placeholder
            precision=0.83,
            recall=0.87,
            f1_score=0.85,
            training_samples=1000,
            last_trained=datetime.utcnow()
        )
    
    async def _extract_features(self, email: EmailMessage) -> Dict[str, Any]:
        """Extract features from email for ML models."""
        features = {}
        
        # Text features
        subject_length = len(email.subject) if email.subject else 0
        body_length = len(email.body) if email.body else 0
        
        features.update({
            'subject_length': subject_length,
            'body_length': body_length,
            'total_length': subject_length + body_length,
            'has_subject': subject_length > 0,
            'has_body': body_length > 0
        })
        
        # Sender features
        if email.sender:
            sender = email.sender.email if hasattr(email.sender, 'email') else str(email.sender)
            features.update({
                'sender_domain': sender.split('@')[1] if '@' in sender else 'unknown',
                'sender_length': len(sender)
            })
        
        # Recipient features
        to_count = len(email.to_recipients) if email.to_recipients else 0
        cc_count = len(email.cc_recipients) if email.cc_recipients else 0
        
        features.update({
            'to_count': to_count,
            'cc_count': cc_count,
            'total_recipients': to_count + cc_count,
            'has_cc': cc_count > 0
        })
        
        # Time features
        if email.received_date:
            features.update({
                'hour_of_day': email.received_date.hour,
                'day_of_week': email.received_date.weekday(),
                'is_weekend': email.received_date.weekday() >= 5
            })
        
        # Attachment features
        features.update({
            'has_attachments': email.has_attachments or False,
            'attachment_count': len(getattr(email, 'attachments', []))
        })
        
        return features
    
    async def _predict_spam(self, text_content: str) -> float:
        """Predict spam probability."""
        if not self.is_trained.get('spam', False):
            # Return default score if model not trained
            return 0.1
        
        try:
            probabilities = self.models['spam'].predict_proba([text_content])
            return float(probabilities[0][1])  # Probability of spam class
        except Exception as e:
            logger.warning(f"Error predicting spam: {e}")
            return 0.1
    
    async def _predict_priority(self, text_content: str, features: Dict[str, Any]) -> float:
        """Predict priority score."""
        if not self.is_trained.get('priority', False):
            # Simple heuristic if model not trained
            if features.get('has_attachments', False):
                return 0.8
            elif features.get('total_recipients', 0) > 5:
                return 0.6
            else:
                return 0.3
        
        try:
            probabilities = self.models['priority'].predict_proba([text_content])
            # Return probability of high priority
            return float(probabilities[0][-1]) if len(probabilities[0]) > 2 else 0.5
        except Exception as e:
            logger.warning(f"Error predicting priority: {e}")
            return 0.5
    
    async def _predict_category(self, text_content: str) -> Tuple[str, float]:
        """Predict email category."""
        if not self.is_trained.get('category', False):
            # Simple keyword-based classification if model not trained
            text_lower = text_content.lower()
            
            if any(word in text_lower for word in ['meeting', 'schedule', 'calendar']):
                return 'work', 0.7
            elif any(word in text_lower for word in ['sale', 'discount', 'offer']):
                return 'promotional', 0.8
            elif any(word in text_lower for word in ['social', 'friend', 'family']):
                return 'personal', 0.6
            else:
                return 'updates', 0.4
        
        try:
            probabilities = self.models['category'].predict_proba([text_content])
            predicted_class = self.models['category'].predict([text_content])[0]
            confidence = float(max(probabilities[0]))
            
            # Map class index to category name
            category_names = self.categories
            if isinstance(predicted_class, (int, np.integer)):
                category = category_names[predicted_class] if predicted_class < len(category_names) else 'unknown'
            else:
                category = str(predicted_class)
            
            return category, confidence
        except Exception as e:
            logger.warning(f"Error predicting category: {e}")
            return 'unknown', 0.1
    
    async def _analyze_sentiment(self, text_content: str) -> float:
        """Analyze sentiment of email content."""
        # Simple sentiment analysis based on keywords
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'worst', 'hate']
        
        text_lower = text_content.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_words = len(words)
        if total_words == 0:
            return 0.0
        
        sentiment_score = (positive_count - negative_count) / total_words
        return max(-1.0, min(1.0, sentiment_score))  # Clamp to [-1, 1]
    
    async def _save_model(self, model_name: str) -> str:
        """Save a trained model to disk."""
        model_path = self.model_dir / f"{model_name}_model.pkl"
        
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(self.models[model_name], f)
            
            logger.info(f"Saved {model_name} model to {model_path}")
            return str(model_path)
            
        except Exception as e:
            logger.error(f"Error saving {model_name} model: {e}")
            return ""
    
    async def _load_models(self) -> None:
        """Load pre-trained models from disk."""
        for model_name in ['spam', 'priority', 'category']:
            model_path = self.model_dir / f"{model_name}_model.pkl"
            
            if model_path.exists():
                try:
                    with open(model_path, 'rb') as f:
                        self.models[model_name] = pickle.load(f)
                    
                    self.is_trained[model_name] = True
                    logger.info(f"Loaded {model_name} model from {model_path}")
                    
                except Exception as e:
                    logger.warning(f"Error loading {model_name} model: {e}")
                    self.is_trained[model_name] = False
            else:
                self.is_trained[model_name] = False
