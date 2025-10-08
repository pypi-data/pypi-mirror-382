"""
Anomaly detection for email data quality.

This module provides comprehensive anomaly detection capabilities using
statistical methods, distribution analysis, and quality scoring algorithms.
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from scipy import stats
import re

from evolvishub_outlook_ingestor.core.data_models import EmailMessage, EmailAddress
from evolvishub_outlook_ingestor.core.exceptions import QualityError

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies that can be detected."""
    STATISTICAL_OUTLIER = "statistical_outlier"
    PATTERN_DEVIATION = "pattern_deviation"
    FORMAT_ANOMALY = "format_anomaly"
    TEMPORAL_ANOMALY = "temporal_anomaly"
    CONTENT_ANOMALY = "content_anomaly"
    METADATA_ANOMALY = "metadata_anomaly"


class AnomalySeverity(Enum):
    """Severity levels for detected anomalies."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class QualityAnomaly:
    """A detected quality anomaly."""
    anomaly_id: str
    email_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    field_name: Optional[str]
    description: str
    actual_value: Any
    expected_range: Optional[Tuple[float, float]]
    confidence_score: float  # 0.0 to 1.0
    detection_method: str
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class AnomalyReport:
    """Comprehensive anomaly detection report."""
    total_emails_analyzed: int
    total_anomalies_detected: int
    anomalies_by_type: Dict[str, int]
    anomalies_by_severity: Dict[str, int]
    anomalies: List[QualityAnomaly]
    quality_score: float  # Overall quality score 0.0 to 1.0
    recommendations: List[str]
    analysis_timestamp: datetime


class AnomalyDetector:
    """
    Detects anomalies in email data quality using statistical analysis.
    
    Provides comprehensive anomaly detection including:
    - Statistical outlier detection using Z-scores and IQR
    - Pattern deviation analysis
    - Format and structure anomalies
    - Temporal anomalies in email patterns
    - Content-based anomaly detection
    - Metadata consistency checks
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the anomaly detector.
        
        Args:
            config: Configuration dictionary containing:
                - z_score_threshold: Z-score threshold for outliers (default: 2.5)
                - iqr_multiplier: IQR multiplier for outlier detection (default: 1.5)
                - min_samples: Minimum samples for statistical analysis (default: 10)
                - anomaly_types: List of anomaly types to detect
                - severity_thresholds: Thresholds for severity classification
        """
        self.config = config
        self.z_score_threshold = config.get('z_score_threshold', 2.5)
        self.iqr_multiplier = config.get('iqr_multiplier', 1.5)
        self.min_samples = config.get('min_samples', 10)
        self.anomaly_types = config.get('anomaly_types', [t.value for t in AnomalyType])
        self.severity_thresholds = config.get('severity_thresholds', {
            'low': 2.0,
            'medium': 3.0,
            'high': 4.0,
            'critical': 5.0
        })
        
        self.anomaly_counter = 0
        
    async def initialize(self) -> None:
        """Initialize the anomaly detector."""
        logger.info("Initializing AnomalyDetector")
        
    async def detect_anomalies(self, emails: List[EmailMessage]) -> List[QualityAnomaly]:
        """
        Detect anomalies in email data quality.
        
        Args:
            emails: List of email messages to analyze
            
        Returns:
            List of detected anomalies
            
        Raises:
            QualityError: If anomaly detection fails
        """
        try:
            if len(emails) < self.min_samples:
                logger.warning(f"Insufficient samples for anomaly detection: {len(emails)} < {self.min_samples}")
                return []
            
            anomalies = []
            
            # Statistical outlier detection
            if AnomalyType.STATISTICAL_OUTLIER.value in self.anomaly_types:
                statistical_anomalies = await self._detect_statistical_outliers(emails)
                anomalies.extend(statistical_anomalies)
            
            # Pattern deviation detection
            if AnomalyType.PATTERN_DEVIATION.value in self.anomaly_types:
                pattern_anomalies = await self._detect_pattern_deviations(emails)
                anomalies.extend(pattern_anomalies)
            
            # Format anomaly detection
            if AnomalyType.FORMAT_ANOMALY.value in self.anomaly_types:
                format_anomalies = await self._detect_format_anomalies(emails)
                anomalies.extend(format_anomalies)
            
            # Temporal anomaly detection
            if AnomalyType.TEMPORAL_ANOMALY.value in self.anomaly_types:
                temporal_anomalies = await self._detect_temporal_anomalies(emails)
                anomalies.extend(temporal_anomalies)
            
            # Content anomaly detection
            if AnomalyType.CONTENT_ANOMALY.value in self.anomaly_types:
                content_anomalies = await self._detect_content_anomalies(emails)
                anomalies.extend(content_anomalies)
            
            # Metadata anomaly detection
            if AnomalyType.METADATA_ANOMALY.value in self.anomaly_types:
                metadata_anomalies = await self._detect_metadata_anomalies(emails)
                anomalies.extend(metadata_anomalies)
            
            # Sort by severity and confidence
            anomalies.sort(key=lambda x: (x.severity.value, x.confidence_score), reverse=True)
            
            logger.info(f"Detected {len(anomalies)} anomalies in {len(emails)} emails")
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            raise QualityError(f"Anomaly detection failed: {e}")
    
    async def generate_anomaly_report(self, emails: List[EmailMessage]) -> AnomalyReport:
        """
        Generate comprehensive anomaly detection report.
        
        Args:
            emails: List of email messages to analyze
            
        Returns:
            Anomaly detection report
        """
        try:
            anomalies = await self.detect_anomalies(emails)
            
            # Calculate statistics
            anomalies_by_type = defaultdict(int)
            anomalies_by_severity = defaultdict(int)
            
            for anomaly in anomalies:
                anomalies_by_type[anomaly.anomaly_type.value] += 1
                anomalies_by_severity[anomaly.severity.value] += 1
            
            # Calculate overall quality score
            quality_score = await self._calculate_quality_score(emails, anomalies)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(anomalies, emails)
            
            return AnomalyReport(
                total_emails_analyzed=len(emails),
                total_anomalies_detected=len(anomalies),
                anomalies_by_type=dict(anomalies_by_type),
                anomalies_by_severity=dict(anomalies_by_severity),
                anomalies=anomalies,
                quality_score=quality_score,
                recommendations=recommendations,
                analysis_timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating anomaly report: {e}")
            raise QualityError(f"Anomaly report generation failed: {e}")
    
    async def _detect_statistical_outliers(self, emails: List[EmailMessage]) -> List[QualityAnomaly]:
        """Detect statistical outliers in numerical fields."""
        anomalies = []
        
        # Analyze email body lengths
        body_lengths = [len(email.body or '') for email in emails]
        if body_lengths:
            outliers = await self._find_outliers(body_lengths, 'body_length')
            for email_idx, z_score in outliers:
                email = emails[email_idx]
                severity = self._determine_severity(abs(z_score))
                
                anomalies.append(QualityAnomaly(
                    anomaly_id=self._generate_anomaly_id(),
                    email_id=email.id,
                    anomaly_type=AnomalyType.STATISTICAL_OUTLIER,
                    severity=severity,
                    field_name='body',
                    description=f"Email body length ({body_lengths[email_idx]} chars) is a statistical outlier",
                    actual_value=body_lengths[email_idx],
                    expected_range=self._calculate_normal_range(body_lengths),
                    confidence_score=min(1.0, abs(z_score) / 5.0),
                    detection_method='z_score',
                    timestamp=datetime.utcnow(),
                    metadata={'z_score': z_score, 'mean': np.mean(body_lengths), 'std': np.std(body_lengths)}
                ))
        
        # Analyze subject lengths
        subject_lengths = [len(email.subject or '') for email in emails]
        if subject_lengths:
            outliers = await self._find_outliers(subject_lengths, 'subject_length')
            for email_idx, z_score in outliers:
                email = emails[email_idx]
                severity = self._determine_severity(abs(z_score))
                
                anomalies.append(QualityAnomaly(
                    anomaly_id=self._generate_anomaly_id(),
                    email_id=email.id,
                    anomaly_type=AnomalyType.STATISTICAL_OUTLIER,
                    severity=severity,
                    field_name='subject',
                    description=f"Email subject length ({subject_lengths[email_idx]} chars) is a statistical outlier",
                    actual_value=subject_lengths[email_idx],
                    expected_range=self._calculate_normal_range(subject_lengths),
                    confidence_score=min(1.0, abs(z_score) / 5.0),
                    detection_method='z_score',
                    timestamp=datetime.utcnow(),
                    metadata={'z_score': z_score}
                ))
        
        # Analyze recipient counts
        recipient_counts = [len(email.to_recipients or []) + len(email.cc_recipients or []) for email in emails]
        if recipient_counts:
            outliers = await self._find_outliers(recipient_counts, 'recipient_count')
            for email_idx, z_score in outliers:
                email = emails[email_idx]
                severity = self._determine_severity(abs(z_score))
                
                anomalies.append(QualityAnomaly(
                    anomaly_id=self._generate_anomaly_id(),
                    email_id=email.id,
                    anomaly_type=AnomalyType.STATISTICAL_OUTLIER,
                    severity=severity,
                    field_name='recipients',
                    description=f"Recipient count ({recipient_counts[email_idx]}) is a statistical outlier",
                    actual_value=recipient_counts[email_idx],
                    expected_range=self._calculate_normal_range(recipient_counts),
                    confidence_score=min(1.0, abs(z_score) / 5.0),
                    detection_method='z_score',
                    timestamp=datetime.utcnow(),
                    metadata={'z_score': z_score}
                ))
        
        return anomalies
    
    async def _detect_pattern_deviations(self, emails: List[EmailMessage]) -> List[QualityAnomaly]:
        """Detect deviations from normal email patterns."""
        anomalies = []
        
        # Analyze sender domain patterns
        sender_domains = defaultdict(int)
        for email in emails:
            if email.sender:
                sender = email.sender.email if isinstance(email.sender, EmailAddress) else str(email.sender)
                if '@' in sender:
                    domain = sender.split('@')[1].lower()
                    sender_domains[domain] += 1
        
        # Detect unusual domains (very low frequency)
        if sender_domains:
            total_emails = sum(sender_domains.values())
            for email in emails:
                if email.sender:
                    sender = email.sender.email if isinstance(email.sender, EmailAddress) else str(email.sender)
                    if '@' in sender:
                        domain = sender.split('@')[1].lower()
                        frequency = sender_domains[domain] / total_emails
                        
                        if frequency < 0.01 and sender_domains[domain] == 1:  # Very rare domain
                            anomalies.append(QualityAnomaly(
                                anomaly_id=self._generate_anomaly_id(),
                                email_id=email.id,
                                anomaly_type=AnomalyType.PATTERN_DEVIATION,
                                severity=AnomalySeverity.LOW,
                                field_name='sender',
                                description=f"Unusual sender domain: {domain}",
                                actual_value=domain,
                                expected_range=None,
                                confidence_score=0.6,
                                detection_method='frequency_analysis',
                                timestamp=datetime.utcnow(),
                                metadata={'domain_frequency': frequency}
                            ))
        
        return anomalies
    
    async def _detect_format_anomalies(self, emails: List[EmailMessage]) -> List[QualityAnomaly]:
        """Detect format and structure anomalies."""
        anomalies = []
        
        for email in emails:
            # Check for malformed email addresses
            if email.sender:
                sender = email.sender.email if isinstance(email.sender, EmailAddress) else str(email.sender)
                if not self._is_valid_email_format(sender):
                    anomalies.append(QualityAnomaly(
                        anomaly_id=self._generate_anomaly_id(),
                        email_id=email.id,
                        anomaly_type=AnomalyType.FORMAT_ANOMALY,
                        severity=AnomalySeverity.HIGH,
                        field_name='sender',
                        description=f"Malformed sender email address: {sender}",
                        actual_value=sender,
                        expected_range=None,
                        confidence_score=0.9,
                        detection_method='regex_validation',
                        timestamp=datetime.utcnow(),
                        metadata={'validation_error': 'invalid_email_format'}
                    ))
            
            # Check for suspicious subject patterns
            if email.subject:
                if self._has_suspicious_subject_pattern(email.subject):
                    anomalies.append(QualityAnomaly(
                        anomaly_id=self._generate_anomaly_id(),
                        email_id=email.id,
                        anomaly_type=AnomalyType.FORMAT_ANOMALY,
                        severity=AnomalySeverity.MEDIUM,
                        field_name='subject',
                        description=f"Suspicious subject pattern detected",
                        actual_value=email.subject,
                        expected_range=None,
                        confidence_score=0.7,
                        detection_method='pattern_matching',
                        timestamp=datetime.utcnow(),
                        metadata={'pattern_type': 'suspicious_subject'}
                    ))
            
            # Check for encoding issues
            if email.body and self._has_encoding_issues(email.body):
                anomalies.append(QualityAnomaly(
                    anomaly_id=self._generate_anomaly_id(),
                    email_id=email.id,
                    anomaly_type=AnomalyType.FORMAT_ANOMALY,
                    severity=AnomalySeverity.MEDIUM,
                    field_name='body',
                    description="Potential encoding issues in email body",
                    actual_value=len(email.body),
                    expected_range=None,
                    confidence_score=0.8,
                    detection_method='encoding_analysis',
                    timestamp=datetime.utcnow(),
                    metadata={'encoding_issue': True}
                ))
        
        return anomalies
    
    async def _detect_temporal_anomalies(self, emails: List[EmailMessage]) -> List[QualityAnomaly]:
        """Detect temporal anomalies in email timestamps."""
        anomalies = []
        
        # Check for future timestamps
        current_time = datetime.utcnow()
        for email in emails:
            if email.received_date and email.received_date > current_time:
                time_diff = (email.received_date - current_time).total_seconds() / 3600  # hours
                
                anomalies.append(QualityAnomaly(
                    anomaly_id=self._generate_anomaly_id(),
                    email_id=email.id,
                    anomaly_type=AnomalyType.TEMPORAL_ANOMALY,
                    severity=AnomalySeverity.HIGH,
                    field_name='received_date',
                    description=f"Email received date is {time_diff:.1f} hours in the future",
                    actual_value=email.received_date.isoformat(),
                    expected_range=None,
                    confidence_score=1.0,
                    detection_method='timestamp_validation',
                    timestamp=datetime.utcnow(),
                    metadata={'hours_in_future': time_diff}
                ))
            
            # Check for very old timestamps (potential data quality issue)
            if email.received_date and email.received_date < datetime(1990, 1, 1):
                anomalies.append(QualityAnomaly(
                    anomaly_id=self._generate_anomaly_id(),
                    email_id=email.id,
                    anomaly_type=AnomalyType.TEMPORAL_ANOMALY,
                    severity=AnomalySeverity.MEDIUM,
                    field_name='received_date',
                    description=f"Email received date is unusually old: {email.received_date}",
                    actual_value=email.received_date.isoformat(),
                    expected_range=None,
                    confidence_score=0.9,
                    detection_method='timestamp_validation',
                    timestamp=datetime.utcnow(),
                    metadata={'year': email.received_date.year}
                ))
        
        return anomalies
    
    async def _detect_content_anomalies(self, emails: List[EmailMessage]) -> List[QualityAnomaly]:
        """Detect content-based anomalies."""
        anomalies = []
        
        for email in emails:
            # Check for empty or very short content
            if email.body is not None and len(email.body.strip()) < 5:
                anomalies.append(QualityAnomaly(
                    anomaly_id=self._generate_anomaly_id(),
                    email_id=email.id,
                    anomaly_type=AnomalyType.CONTENT_ANOMALY,
                    severity=AnomalySeverity.MEDIUM,
                    field_name='body',
                    description="Email body is empty or extremely short",
                    actual_value=len(email.body),
                    expected_range=(10, 10000),
                    confidence_score=0.8,
                    detection_method='content_length_analysis',
                    timestamp=datetime.utcnow(),
                    metadata={'content_length': len(email.body)}
                ))
            
            # Check for missing subject
            if not email.subject or len(email.subject.strip()) == 0:
                anomalies.append(QualityAnomaly(
                    anomaly_id=self._generate_anomaly_id(),
                    email_id=email.id,
                    anomaly_type=AnomalyType.CONTENT_ANOMALY,
                    severity=AnomalySeverity.LOW,
                    field_name='subject',
                    description="Email has no subject line",
                    actual_value="",
                    expected_range=None,
                    confidence_score=1.0,
                    detection_method='content_presence_check',
                    timestamp=datetime.utcnow(),
                    metadata={'missing_subject': True}
                ))
        
        return anomalies
    
    async def _detect_metadata_anomalies(self, emails: List[EmailMessage]) -> List[QualityAnomaly]:
        """Detect metadata consistency anomalies."""
        anomalies = []
        
        for email in emails:
            # Check for missing critical metadata
            if not email.id:
                anomalies.append(QualityAnomaly(
                    anomaly_id=self._generate_anomaly_id(),
                    email_id="unknown",
                    anomaly_type=AnomalyType.METADATA_ANOMALY,
                    severity=AnomalySeverity.CRITICAL,
                    field_name='id',
                    description="Email is missing unique identifier",
                    actual_value=None,
                    expected_range=None,
                    confidence_score=1.0,
                    detection_method='metadata_validation',
                    timestamp=datetime.utcnow(),
                    metadata={'missing_id': True}
                ))
            
            # Check for inconsistent sender information
            if email.sender and email.from_address:
                sender1 = email.sender.email if isinstance(email.sender, EmailAddress) else str(email.sender)
                sender2 = email.from_address.email if isinstance(email.from_address, EmailAddress) else str(email.from_address)
                
                if sender1.lower() != sender2.lower():
                    anomalies.append(QualityAnomaly(
                        anomaly_id=self._generate_anomaly_id(),
                        email_id=email.id,
                        anomaly_type=AnomalyType.METADATA_ANOMALY,
                        severity=AnomalySeverity.MEDIUM,
                        field_name='sender',
                        description="Inconsistent sender information between 'sender' and 'from_address'",
                        actual_value=f"sender: {sender1}, from: {sender2}",
                        expected_range=None,
                        confidence_score=0.9,
                        detection_method='metadata_consistency_check',
                        timestamp=datetime.utcnow(),
                        metadata={'sender': sender1, 'from_address': sender2}
                    ))
        
        return anomalies
    
    async def _find_outliers(self, values: List[float], field_name: str) -> List[Tuple[int, float]]:
        """Find statistical outliers using Z-score method."""
        if len(values) < self.min_samples:
            return []
        
        values_array = np.array(values)
        mean_val = np.mean(values_array)
        std_val = np.std(values_array)
        
        if std_val == 0:
            return []
        
        z_scores = np.abs((values_array - mean_val) / std_val)
        outliers = []
        
        for i, z_score in enumerate(z_scores):
            if z_score > self.z_score_threshold:
                outliers.append((i, z_score))
        
        return outliers
    
    def _calculate_normal_range(self, values: List[float]) -> Tuple[float, float]:
        """Calculate normal range for values using IQR method."""
        if not values:
            return (0.0, 0.0)
        
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - self.iqr_multiplier * iqr
        upper_bound = q3 + self.iqr_multiplier * iqr
        
        return (lower_bound, upper_bound)
    
    def _determine_severity(self, z_score: float) -> AnomalySeverity:
        """Determine anomaly severity based on Z-score."""
        if z_score >= self.severity_thresholds['critical']:
            return AnomalySeverity.CRITICAL
        elif z_score >= self.severity_thresholds['high']:
            return AnomalySeverity.HIGH
        elif z_score >= self.severity_thresholds['medium']:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
    
    def _is_valid_email_format(self, email: str) -> bool:
        """Check if email address has valid format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    def _has_suspicious_subject_pattern(self, subject: str) -> bool:
        """Check for suspicious patterns in email subject."""
        suspicious_patterns = [
            r'^\s*$',  # Empty or whitespace only
            r'^(re:\s*){5,}',  # Too many "Re:" prefixes
            r'[A-Z]{10,}',  # Too many consecutive capitals
            r'[!]{3,}',  # Too many exclamation marks
            r'\$\$\$',  # Money symbols
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, subject, re.IGNORECASE):
                return True
        
        return False
    
    def _has_encoding_issues(self, text: str) -> bool:
        """Check for potential encoding issues in text."""
        # Look for common encoding issue indicators
        encoding_indicators = [
            '�',  # Replacement character
            '\ufffd',  # Unicode replacement character
            '=?',  # MIME encoded word start
            '?=',  # MIME encoded word end
        ]
        
        for indicator in encoding_indicators:
            if indicator in text:
                return True
        
        return False
    
    async def _calculate_quality_score(self, emails: List[EmailMessage], anomalies: List[QualityAnomaly]) -> float:
        """Calculate overall quality score based on anomalies."""
        if not emails:
            return 1.0
        
        # Weight anomalies by severity
        severity_weights = {
            AnomalySeverity.LOW: 0.1,
            AnomalySeverity.MEDIUM: 0.3,
            AnomalySeverity.HIGH: 0.6,
            AnomalySeverity.CRITICAL: 1.0
        }
        
        total_penalty = 0
        for anomaly in anomalies:
            penalty = severity_weights[anomaly.severity] * anomaly.confidence_score
            total_penalty += penalty
        
        # Normalize by number of emails
        normalized_penalty = total_penalty / len(emails)
        
        # Calculate quality score (1.0 - penalty, minimum 0.0)
        quality_score = max(0.0, 1.0 - normalized_penalty)
        
        return quality_score
    
    async def _generate_recommendations(self, anomalies: List[QualityAnomaly], emails: List[EmailMessage]) -> List[str]:
        """Generate recommendations based on detected anomalies."""
        recommendations = []
        
        # Count anomalies by type
        anomaly_counts = defaultdict(int)
        for anomaly in anomalies:
            anomaly_counts[anomaly.anomaly_type] += 1
        
        # Generate type-specific recommendations
        if anomaly_counts[AnomalyType.FORMAT_ANOMALY] > 0:
            recommendations.append("Implement input validation to prevent format anomalies")
        
        if anomaly_counts[AnomalyType.TEMPORAL_ANOMALY] > 0:
            recommendations.append("Review timestamp handling and validation logic")
        
        if anomaly_counts[AnomalyType.CONTENT_ANOMALY] > 0:
            recommendations.append("Implement content quality checks during ingestion")
        
        if anomaly_counts[AnomalyType.STATISTICAL_OUTLIER] > len(emails) * 0.05:
            recommendations.append("High number of statistical outliers detected - review data collection process")
        
        if anomaly_counts[AnomalyType.METADATA_ANOMALY] > 0:
            recommendations.append("Improve metadata consistency and validation")
        
        # General recommendations
        anomaly_rate = len(anomalies) / len(emails) if emails else 0
        if anomaly_rate > 0.1:
            recommendations.append(f"High anomaly rate ({anomaly_rate:.1%}) - consider comprehensive data quality review")
        
        return recommendations
    
    def _generate_anomaly_id(self) -> str:
        """Generate unique anomaly ID."""
        self.anomaly_counter += 1
        return f"anomaly_{datetime.utcnow().strftime('%Y%m%d')}_{self.anomaly_counter:06d}"
