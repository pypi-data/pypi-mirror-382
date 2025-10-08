"""
Machine learning service for email data processing.

This module provides comprehensive ML capabilities including
classification, prediction, and feature extraction for email data.
"""

import asyncio
import logging
import pickle
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
import numpy as np

from evolvishub_outlook_ingestor.core.interfaces import IMLService, service_registry
from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.core.exceptions import MLError


@dataclass
class MLModelInfo:
    """Information about an ML model."""
    name: str
    version: str
    model_type: str
    accuracy: float
    trained_at: datetime
    feature_count: int
    metadata: Dict[str, Any]


@dataclass
class PredictionResult:
    """Result of an ML prediction."""
    model_name: str
    prediction: Any
    confidence: float
    features_used: List[str]
    processing_time: float
    metadata: Dict[str, Any]


class MLService(IMLService):
    """
    Machine learning service for email data processing.
    
    This service provides comprehensive ML capabilities including:
    - Email classification (category, priority, sentiment)
    - Spam and phishing detection
    - Priority prediction and scoring
    - Feature extraction and engineering
    - Model training and evaluation
    - Real-time inference and batch processing
    
    Example:
        ```python
        ml_service = MLService({
            'model_storage_path': '/models',
            'enable_online_learning': True,
            'feature_cache_size': 10000,
            'models': {
                'spam_detector': {'type': 'sklearn', 'algorithm': 'random_forest'},
                'priority_predictor': {'type': 'sklearn', 'algorithm': 'gradient_boosting'},
                'category_classifier': {'type': 'sklearn', 'algorithm': 'svm'}
            }
        })
        
        await ml_service.initialize()
        
        # Classify email
        classification = await ml_service.classify_email(email)
        
        # Detect spam
        spam_score = await ml_service.detect_spam(email)
        
        # Predict priority
        priority_score = await ml_service.predict_priority(email)
        ```
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.model_storage_path = config.get('model_storage_path', '/tmp/ml_models')
        self.enable_online_learning = config.get('enable_online_learning', False)
        self.feature_cache_size = config.get('feature_cache_size', 10000)
        self.model_configs = config.get('models', {})
        self.batch_size = config.get('batch_size', 100)
        
        # State management
        self.is_initialized = False
        self._models: Dict[str, Any] = {}
        self._model_info: Dict[str, MLModelInfo] = {}
        self._feature_cache: Dict[str, Dict[str, Any]] = {}
        self._vectorizers: Dict[str, Any] = {}
        self._historical_emails: List[Any] = []
        
        # Statistics
        self.stats = {
            'predictions_made': 0,
            'models_loaded': 0,
            'features_extracted': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    async def initialize(self) -> None:
        """Initialize the ML service."""
        if self.is_initialized:
            return
        
        try:
            self.logger.info("Initializing ML service")
            
            # Create model storage directory
            import os
            os.makedirs(self.model_storage_path, exist_ok=True)
            
            # Load or train models
            await self._load_models()
            
            # Initialize feature extractors
            await self._initialize_feature_extractors()
            
            self.is_initialized = True
            self.logger.info(f"ML service initialized with {len(self._models)} models")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML service: {str(e)}")
            raise MLError(f"ML service initialization failed: {str(e)}")
    
    async def classify_email(self, email: EmailMessage) -> Dict[str, float]:
        """
        Classify email content into categories.
        
        Args:
            email: Email message to classify
            
        Returns:
            Dictionary of category probabilities
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            start_time = datetime.now(timezone.utc)
            
            # Extract features
            features = await self.extract_features(email)
            
            # Get classification model
            classifier = self._models.get('category_classifier')
            if not classifier:
                return {'unknown': 1.0}
            
            # Prepare feature vector
            feature_vector = await self._prepare_feature_vector(features, 'classification')
            
            # Make prediction
            if hasattr(classifier, 'predict_proba'):
                probabilities = classifier.predict_proba([feature_vector])[0]
                classes = classifier.classes_
                
                result = dict(zip(classes, probabilities))
            else:
                prediction = classifier.predict([feature_vector])[0]
                result = {prediction: 1.0}
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.stats['predictions_made'] += 1
            
            self.logger.debug(f"Classified email {email.id} in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to classify email {email.id}: {str(e)}")
            return {'error': 1.0}
    
    async def extract_features(self, email: EmailMessage) -> Dict[str, Any]:
        """
        Extract ML features from email.
        
        Args:
            email: Email message to extract features from
            
        Returns:
            Dictionary of extracted features
        """
        try:
            # Check cache first
            cache_key = f"features_{email.id}"
            if cache_key in self._feature_cache:
                self.stats['cache_hits'] += 1
                return self._feature_cache[cache_key]
            
            features = {}
            
            # Basic features
            features.update(await self._extract_basic_features(email))
            
            # Text features
            features.update(await self._extract_text_features(email))
            
            # Metadata features
            features.update(await self._extract_metadata_features(email))
            
            # Temporal features
            features.update(await self._extract_temporal_features(email))
            
            # Network features
            features.update(await self._extract_network_features(email))
            
            # Cache features
            if len(self._feature_cache) < self.feature_cache_size:
                self._feature_cache[cache_key] = features
            
            self.stats['cache_misses'] += 1
            self.stats['features_extracted'] += 1
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract features from email {email.id}: {str(e)}")
            return {}
    
    async def predict_priority(self, email: EmailMessage) -> float:
        """
        Predict email priority score.
        
        Args:
            email: Email message to analyze
            
        Returns:
            Priority score between 0.0 and 1.0
        """
        try:
            # Extract features
            features = await self.extract_features(email)
            
            # Get priority model
            predictor = self._models.get('priority_predictor')
            if not predictor:
                # Fallback to rule-based priority
                return await self._rule_based_priority(email)
            
            # Prepare feature vector
            feature_vector = await self._prepare_feature_vector(features, 'priority')
            
            # Make prediction
            if hasattr(predictor, 'predict_proba'):
                # Classification model (high/medium/low priority)
                probabilities = predictor.predict_proba([feature_vector])[0]
                # Assume classes are ordered: low, medium, high
                priority_score = np.average([0.2, 0.5, 0.9], weights=probabilities)
            else:
                # Regression model
                priority_score = predictor.predict([feature_vector])[0]
                priority_score = max(0.0, min(1.0, priority_score))  # Clamp to [0,1]
            
            self.stats['predictions_made'] += 1
            return float(priority_score)
            
        except Exception as e:
            self.logger.error(f"Failed to predict priority for email {email.id}: {str(e)}")
            return 0.5  # Default medium priority
    
    async def detect_spam(self, email: EmailMessage) -> float:
        """
        Detect spam probability.
        
        Args:
            email: Email message to analyze
            
        Returns:
            Spam probability between 0.0 and 1.0
        """
        try:
            # Extract features
            features = await self.extract_features(email)
            
            # Get spam detection model
            spam_detector = self._models.get('spam_detector')
            if not spam_detector:
                # Fallback to rule-based detection
                return await self._rule_based_spam_detection(email)
            
            # Prepare feature vector
            feature_vector = await self._prepare_feature_vector(features, 'spam')
            
            # Make prediction
            if hasattr(spam_detector, 'predict_proba'):
                # Get probability of spam class (assuming binary classification)
                probabilities = spam_detector.predict_proba([feature_vector])[0]
                spam_prob = probabilities[1] if len(probabilities) > 1 else probabilities[0]
            else:
                # Binary prediction
                prediction = spam_detector.predict([feature_vector])[0]
                spam_prob = 1.0 if prediction else 0.0
            
            self.stats['predictions_made'] += 1
            return float(spam_prob)
            
        except Exception as e:
            self.logger.error(f"Failed to detect spam for email {email.id}: {str(e)}")
            return 0.0  # Default to not spam
    
    async def _load_models(self) -> None:
        """Load or train ML models."""
        for model_name, model_config in self.model_configs.items():
            try:
                model_path = f"{self.model_storage_path}/{model_name}.pkl"
                
                # Try to load existing model
                try:
                    with open(model_path, 'rb') as f:
                        model = pickle.load(f)
                    self._models[model_name] = model
                    self.logger.info(f"Loaded model: {model_name}")
                except FileNotFoundError:
                    # Train new model
                    model = await self._train_model(model_name, model_config)
                    self._models[model_name] = model
                    
                    # Save model
                    with open(model_path, 'wb') as f:
                        pickle.dump(model, f)
                    self.logger.info(f"Trained and saved model: {model_name}")
                
                self.stats['models_loaded'] += 1
                
            except Exception as e:
                self.logger.error(f"Failed to load model {model_name}: {str(e)}")
    
    async def _train_model(self, model_name: str, model_config: Dict[str, Any]) -> Any:
        """Train a new ML model."""
        try:
            model_type = model_config.get('type', 'sklearn')
            algorithm = model_config.get('algorithm', 'random_forest')
            
            if model_type == 'sklearn':
                return await self._train_sklearn_model(model_name, algorithm, model_config)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to train model {model_name}: {str(e)}")
            raise
    
    async def _train_sklearn_model(self, model_name: str, algorithm: str, config: Dict[str, Any]) -> Any:
        """Train a scikit-learn model."""
        try:
            from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
            from sklearn.svm import SVC
            from sklearn.naive_bayes import MultinomialNB
            from sklearn.linear_model import LogisticRegression
            
            # Create model based on algorithm
            if algorithm == 'random_forest':
                model = RandomForestClassifier(
                    n_estimators=config.get('n_estimators', 100),
                    random_state=42
                )
            elif algorithm == 'gradient_boosting':
                model = GradientBoostingClassifier(
                    n_estimators=config.get('n_estimators', 100),
                    random_state=42
                )
            elif algorithm == 'svm':
                model = SVC(
                    probability=True,
                    random_state=42
                )
            elif algorithm == 'naive_bayes':
                model = MultinomialNB()
            elif algorithm == 'logistic_regression':
                model = LogisticRegression(random_state=42)
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Load or generate training data from real email features
            X_train, y_train = await self._load_training_data(model_name)

            if X_train is not None and y_train is not None:
                # Train model with real data
                model.fit(X_train, y_train)
                self.logger.info(f"Trained {model_name} with {len(X_train)} samples")
            else:
                # Use pre-trained model if no training data available
                model = await self._load_pretrained_model(model_name)
                if model is None:
                    raise MLError(f"No training data or pre-trained model available for {model_name}")
            
            return model
            
        except ImportError:
            self.logger.error("scikit-learn not available for model training")
            raise MLError("scikit-learn is required for ML functionality. Install with: pip install scikit-learn")
    
    async def _load_training_data(self, model_name: str) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Load training data from storage or generate from historical email data."""
        try:
            # Try to load pre-existing training data
            training_data_path = f"{self.model_storage_path}/{model_name}_training_data.npz"

            import os
            if os.path.exists(training_data_path):
                data = np.load(training_data_path)
                X_train = data['X']
                y_train = data['y']
                self.logger.info(f"Loaded training data for {model_name}: {len(X_train)} samples")
                return X_train, y_train

            # If no pre-existing data, try to generate from historical emails
            if hasattr(self, '_historical_emails') and self._historical_emails:
                return await self._generate_training_data_from_emails(model_name, self._historical_emails)

            # No training data available
            self.logger.warning(f"No training data available for {model_name}")
            return None, None

        except Exception as e:
            self.logger.error(f"Failed to load training data for {model_name}: {str(e)}")
            return None, None

    async def _generate_training_data_from_emails(self, model_name: str, emails: List[Any]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Generate training data from historical email data."""
        try:
            features_list = []
            labels_list = []

            for email in emails:
                # Extract features from email
                features = await self.extract_features(email)
                feature_vector = await self._prepare_feature_vector(features, model_name)

                # Generate labels based on model type and email properties
                label = await self._generate_label_for_email(model_name, email)
                if label is not None:
                    features_list.append(feature_vector)
                    labels_list.append(label)

            if len(features_list) > 0:
                X = np.array(features_list)
                y = np.array(labels_list)

                # Save training data for future use
                training_data_path = f"{self.model_storage_path}/{model_name}_training_data.npz"
                np.savez(training_data_path, X=X, y=y)

                self.logger.info(f"Generated training data for {model_name}: {len(X)} samples")
                return X, y

            return None, None

        except Exception as e:
            self.logger.error(f"Failed to generate training data from emails: {str(e)}")
            return None, None

    async def _generate_label_for_email(self, model_name: str, email: Any) -> Optional[Any]:
        """Generate appropriate label for an email based on model type."""
        try:
            if model_name == 'spam_detector':
                # Use folder information or subject patterns to infer spam
                if hasattr(email, 'folder_name'):
                    return 1 if 'spam' in email.folder_name.lower() or 'junk' in email.folder_name.lower() else 0
                # Use subject patterns as heuristic
                if hasattr(email, 'subject') and email.subject:
                    spam_keywords = ['free', 'urgent', 'limited time', 'act now', 'winner', 'congratulations']
                    return 1 if any(keyword in email.subject.lower() for keyword in spam_keywords) else 0
                return 0  # Default to not spam

            elif model_name == 'priority_predictor':
                # Use importance flag or subject patterns
                if hasattr(email, 'importance'):
                    if email.importance and email.importance.value == 'high':
                        return 2  # High priority
                    elif email.importance and email.importance.value == 'low':
                        return 0  # Low priority
                    else:
                        return 1  # Medium priority
                # Use subject patterns
                if hasattr(email, 'subject') and email.subject:
                    high_priority_keywords = ['urgent', 'asap', 'important', 'critical']
                    if any(keyword in email.subject.lower() for keyword in high_priority_keywords):
                        return 2
                return 1  # Default to medium priority

            elif model_name == 'category_classifier':
                # Use folder information or sender patterns
                if hasattr(email, 'folder_name'):
                    folder = email.folder_name.lower()
                    if 'work' in folder or 'business' in folder:
                        return 'work'
                    elif 'personal' in folder:
                        return 'personal'
                    elif 'promotion' in folder or 'marketing' in folder:
                        return 'promotional'
                    elif 'social' in folder:
                        return 'social'
                # Use sender domain patterns
                if hasattr(email, 'sender') and email.sender and hasattr(email.sender, 'email'):
                    domain = email.sender.email.split('@')[-1].lower()
                    if domain in ['linkedin.com', 'facebook.com', 'twitter.com']:
                        return 'social'
                    elif domain in ['noreply.com', 'marketing.com', 'promo.com']:
                        return 'promotional'
                return 'work'  # Default category

            return None

        except Exception as e:
            self.logger.warning(f"Failed to generate label for {model_name}: {str(e)}")
            return None

    async def _load_pretrained_model(self, model_name: str) -> Optional[Any]:
        """Load a pre-trained model if available."""
        try:
            pretrained_path = f"{self.model_storage_path}/{model_name}_pretrained.pkl"
            import os
            if os.path.exists(pretrained_path):
                with open(pretrained_path, 'rb') as f:
                    model = pickle.load(f)
                self.logger.info(f"Loaded pre-trained model for {model_name}")
                return model
            return None
        except Exception as e:
            self.logger.error(f"Failed to load pre-trained model for {model_name}: {str(e)}")
            return None
    
    async def _initialize_feature_extractors(self) -> None:
        """Initialize feature extraction components."""
        try:
            # Initialize text vectorizers
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            self._vectorizers['tfidf'] = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Initialize with empty vocabulary - will be fitted on real data
            # The vectorizer will be fitted when first real email data is processed
            self._vectorizers['tfidf_fitted'] = False
            
        except ImportError:
            self.logger.warning("scikit-learn not available for feature extraction")

    async def _fit_vectorizer_on_corpus(self, texts: List[str]) -> None:
        """Fit the TF-IDF vectorizer on a corpus of texts."""
        try:
            if 'tfidf' in self._vectorizers and len(texts) > 0:
                # If we have historical emails, use them for fitting
                if hasattr(self, '_historical_emails') and self._historical_emails:
                    corpus_texts = []
                    for email in self._historical_emails[:1000]:  # Use up to 1000 emails for fitting
                        email_text = ""
                        if hasattr(email, 'subject') and email.subject:
                            email_text += email.subject + " "
                        if hasattr(email, 'body') and email.body:
                            email_text += email.body
                        if email_text.strip():
                            corpus_texts.append(email_text)

                    if len(corpus_texts) > 10:  # Need minimum corpus size
                        self._vectorizers['tfidf'].fit(corpus_texts)
                        self._vectorizers['tfidf_fitted'] = True
                        self.logger.info(f"Fitted TF-IDF vectorizer on {len(corpus_texts)} emails")
                        return

                # Fallback: fit on provided texts
                self._vectorizers['tfidf'].fit(texts)
                self._vectorizers['tfidf_fitted'] = True
                self.logger.info(f"Fitted TF-IDF vectorizer on {len(texts)} texts")

        except Exception as e:
            self.logger.error(f"Failed to fit TF-IDF vectorizer: {str(e)}")
    
    async def _extract_basic_features(self, email: EmailMessage) -> Dict[str, Any]:
        """Extract basic email features."""
        features = {}
        
        # Length features
        features['subject_length'] = len(email.subject) if email.subject else 0
        features['body_length'] = len(email.body) if email.body else 0
        features['has_attachments'] = int(email.has_attachments)
        features['attachment_count'] = len(email.attachments)
        
        # Recipient features
        features['to_count'] = len(email.to_recipients)
        features['cc_count'] = len(email.cc_recipients)
        features['bcc_count'] = len(email.bcc_recipients)
        features['total_recipients'] = features['to_count'] + features['cc_count'] + features['bcc_count']
        
        # Boolean features
        features['is_reply'] = int(bool(email.in_reply_to))
        features['is_html'] = int(email.is_html)
        features['is_read'] = int(email.is_read)
        features['is_flagged'] = int(email.is_flagged)
        
        return features
    
    async def _extract_text_features(self, email: EmailMessage) -> Dict[str, Any]:
        """Extract text-based features."""
        features = {}
        
        # Combine subject and body
        text = ""
        if email.subject:
            text += email.subject + " "
        if email.body:
            text += email.body
        
        if text and 'tfidf' in self._vectorizers:
            try:
                # Fit vectorizer on first use if not already fitted
                if not self._vectorizers.get('tfidf_fitted', False):
                    await self._fit_vectorizer_on_corpus([text])

                # TF-IDF features
                tfidf_vector = self._vectorizers['tfidf'].transform([text])
                tfidf_features = tfidf_vector.toarray()[0]

                # Add top TF-IDF features
                for i, score in enumerate(tfidf_features[:20]):  # Top 20 features
                    features[f'tfidf_{i}'] = score

            except Exception as e:
                self.logger.warning(f"Failed to extract TF-IDF features: {str(e)}")
        
        # Simple text statistics
        if text:
            words = text.split()
            features['word_count'] = len(words)
            features['avg_word_length'] = np.mean([len(word) for word in words]) if words else 0
            features['exclamation_count'] = text.count('!')
            features['question_count'] = text.count('?')
            features['uppercase_ratio'] = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        return features
    
    async def _extract_metadata_features(self, email: EmailMessage) -> Dict[str, Any]:
        """Extract metadata features."""
        features = {}
        
        # Importance and sensitivity
        if email.importance:
            features['importance_high'] = int(email.importance.value == 'high')
            features['importance_low'] = int(email.importance.value == 'low')
        
        if email.sensitivity:
            features['sensitivity_confidential'] = int(email.sensitivity.value == 'confidential')
            features['sensitivity_private'] = int(email.sensitivity.value == 'private')
        
        # Domain features
        if email.sender and email.sender.email:
            domain = email.sender.email.split('@')[-1] if '@' in email.sender.email else ''
            features['sender_domain_length'] = len(domain)
            features['sender_is_common_domain'] = int(domain in ['gmail.com', 'outlook.com', 'yahoo.com'])
        
        return features
    
    async def _extract_temporal_features(self, email: EmailMessage) -> Dict[str, Any]:
        """Extract temporal features."""
        features = {}
        
        if email.sent_date:
            features['sent_hour'] = email.sent_date.hour
            features['sent_day_of_week'] = email.sent_date.weekday()
            features['sent_is_weekend'] = int(email.sent_date.weekday() >= 5)
            features['sent_is_business_hours'] = int(9 <= email.sent_date.hour <= 17)
        
        if email.received_date:
            features['received_hour'] = email.received_date.hour
            features['received_day_of_week'] = email.received_date.weekday()
        
        # Response time if it's a reply
        if email.sent_date and email.received_date and email.in_reply_to:
            response_time = (email.sent_date - email.received_date).total_seconds()
            features['response_time_hours'] = response_time / 3600
            features['quick_response'] = int(response_time < 3600)  # Less than 1 hour
        
        return features
    
    async def _extract_network_features(self, email: EmailMessage) -> Dict[str, Any]:
        """Extract network/relationship features."""
        features = {}
        
        # This would typically involve analyzing communication patterns
        # For now, just basic features
        if email.sender and email.sender.email:
            features['sender_email_length'] = len(email.sender.email)
        
        # Recipient diversity
        if email.to_recipients:
            domains = set()
            for recipient in email.to_recipients:
                if recipient.email and '@' in recipient.email:
                    domains.add(recipient.email.split('@')[-1])
            features['recipient_domain_diversity'] = len(domains)
        
        return features
    
    async def _prepare_feature_vector(self, features: Dict[str, Any], model_type: str) -> np.ndarray:
        """Prepare feature vector for model input."""
        # This would typically involve feature selection and scaling
        # For now, just convert to array with fixed size
        feature_vector = []
        
        # Define expected features for each model type
        expected_features = {
            'spam': ['subject_length', 'body_length', 'exclamation_count', 'uppercase_ratio', 'sender_is_common_domain'],
            'priority': ['importance_high', 'total_recipients', 'has_attachments', 'is_reply', 'sent_is_business_hours'],
            'classification': ['word_count', 'to_count', 'cc_count', 'is_html', 'attachment_count']
        }
        
        model_features = expected_features.get(model_type, list(features.keys())[:10])
        
        for feature_name in model_features:
            value = features.get(feature_name, 0)
            if isinstance(value, (int, float)):
                feature_vector.append(value)
            else:
                feature_vector.append(0)
        
        # Pad or truncate to fixed size
        target_size = 50
        if len(feature_vector) < target_size:
            feature_vector.extend([0] * (target_size - len(feature_vector)))
        else:
            feature_vector = feature_vector[:target_size]
        
        return np.array(feature_vector)
    
    async def _rule_based_priority(self, email: EmailMessage) -> float:
        """Fallback rule-based priority scoring."""
        score = 0.5  # Default medium priority
        
        if email.importance and email.importance.value == 'high':
            score += 0.3
        
        if email.is_flagged:
            score += 0.2
        
        if email.sender and 'urgent' in (email.subject or '').lower():
            score += 0.2
        
        return min(1.0, score)
    
    async def _rule_based_spam_detection(self, email: EmailMessage) -> float:
        """Fallback rule-based spam detection."""
        spam_indicators = 0
        
        if email.subject:
            spam_words = ['free', 'urgent', 'limited time', 'act now', 'winner']
            for word in spam_words:
                if word.lower() in email.subject.lower():
                    spam_indicators += 1
        
        if email.body:
            if email.body.count('!') > 5:
                spam_indicators += 1
            if sum(1 for c in email.body if c.isupper()) / len(email.body) > 0.3:
                spam_indicators += 1
        
        return min(1.0, spam_indicators * 0.2)
    
    async def set_historical_emails(self, emails: List[Any]) -> None:
        """Set historical emails for training data generation."""
        self._historical_emails = emails
        self.logger.info(f"Set {len(emails)} historical emails for training")

    async def retrain_model(self, model_name: str, emails: List[Any]) -> bool:
        """Retrain a model with new email data."""
        try:
            if model_name not in self.model_configs:
                raise ValueError(f"Unknown model: {model_name}")

            # Set historical emails for training
            await self.set_historical_emails(emails)

            # Retrain the model
            model_config = self.model_configs[model_name]
            new_model = await self._train_model(model_name, model_config)

            if new_model is not None:
                self._models[model_name] = new_model

                # Save the retrained model
                model_path = f"{self.model_storage_path}/{model_name}.pkl"
                with open(model_path, 'wb') as f:
                    pickle.dump(new_model, f)

                self.logger.info(f"Successfully retrained model: {model_name}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to retrain model {model_name}: {str(e)}")
            return False

    async def get_ml_stats(self) -> Dict[str, Any]:
        """Get ML service statistics."""
        return {
            **self.stats,
            'is_initialized': self.is_initialized,
            'models_available': list(self._models.keys()),
            'feature_cache_size': len(self._feature_cache),
            'online_learning_enabled': self.enable_online_learning,
            'historical_emails_count': len(self._historical_emails),
            'vectorizer_fitted': self._vectorizers.get('tfidf_fitted', False)
        }



