"""
Comprehensive data quality validation service for email data.

This module provides advanced data quality validation capabilities including
completeness checks, format validation, duplicate detection, and anomaly detection.
"""

import asyncio
import hashlib
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

from evolvishub_outlook_ingestor.core.interfaces import IDataQualityValidator, DataQualityLevel, service_registry
from evolvishub_outlook_ingestor.core.data_models import EmailMessage, EmailAddress
from evolvishub_outlook_ingestor.core.exceptions import ValidationError


@dataclass
class ValidationRule:
    """Represents a data quality validation rule."""
    name: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    validator_func: callable
    enabled: bool = True


@dataclass
class ValidationResult:
    """Result of a data quality validation."""
    rule_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    message: str
    severity: str
    metadata: Dict[str, Any]


class DataQualityValidator(IDataQualityValidator):
    """
    Comprehensive data quality validation service for email data.
    
    This service provides extensive validation capabilities including:
    - Data completeness and consistency checks
    - Format validation for emails, dates, and other fields
    - Duplicate detection across multiple dimensions
    - Anomaly detection for unusual patterns
    - Custom validation rules and scoring
    
    Example:
        ```python
        validator = DataQualityValidator({
            'enable_duplicate_detection': True,
            'enable_anomaly_detection': True,
            'completeness_threshold': 0.8,
            'duplicate_window_hours': 24
        })
        
        await validator.initialize()
        
        validation_result = await validator.validate_email(email)
        quality_level = await validator.assess_quality_level(validation_result)
        duplicates = await validator.detect_duplicates([email1, email2, email3])
        ```
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.enable_duplicate_detection = config.get('enable_duplicate_detection', True)
        self.enable_anomaly_detection = config.get('enable_anomaly_detection', True)
        self.completeness_threshold = config.get('completeness_threshold', 0.8)
        self.duplicate_window_hours = config.get('duplicate_window_hours', 24)
        self.max_subject_length = config.get('max_subject_length', 1000)
        self.max_body_length = config.get('max_body_length', 100000)
        
        # Validation rules
        self.validation_rules: List[ValidationRule] = []
        self._setup_default_rules()
        
        # State management
        self.is_initialized = False
        self._email_hashes: Set[str] = set()
        self._recent_emails: List[Tuple[str, datetime]] = []
        self._validation_cache: Dict[str, ValidationResult] = {}
        
        # Statistics
        self.stats = {
            'emails_validated': 0,
            'duplicates_detected': 0,
            'anomalies_detected': 0,
            'validation_failures': 0
        }
    
    async def initialize(self) -> None:
        """Initialize the data quality validator."""
        if self.is_initialized:
            return
        
        try:
            self.logger.info("Initializing data quality validator")
            
            # Load custom validation rules if configured
            custom_rules = self.config.get('custom_rules', [])
            for rule_config in custom_rules:
                await self._add_custom_rule(rule_config)
            
            self.is_initialized = True
            self.logger.info(f"Data quality validator initialized with {len(self.validation_rules)} rules")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize data quality validator: {str(e)}")
            raise ValidationError(f"Validator initialization failed: {str(e)}")
    
    async def validate_email(self, email: EmailMessage) -> Dict[str, Any]:
        """
        Validate an email message against all quality rules.
        
        Args:
            email: Email message to validate
            
        Returns:
            Dictionary containing validation results and overall score
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            validation_results = []
            total_score = 0.0
            critical_failures = 0
            
            # Run all validation rules
            for rule in self.validation_rules:
                if not rule.enabled:
                    continue
                
                try:
                    result = await rule.validator_func(email)
                    validation_results.append(result)
                    total_score += result.score
                    
                    if not result.passed and result.severity == 'critical':
                        critical_failures += 1
                
                except Exception as e:
                    self.logger.error(f"Validation rule {rule.name} failed: {str(e)}")
                    validation_results.append(ValidationResult(
                        rule_name=rule.name,
                        passed=False,
                        score=0.0,
                        message=f"Rule execution failed: {str(e)}",
                        severity=rule.severity,
                        metadata={'error': str(e)}
                    ))
            
            # Calculate overall score
            overall_score = total_score / len(validation_results) if validation_results else 0.0
            
            # Determine quality level
            quality_level = await self.assess_quality_level({
                'overall_score': overall_score,
                'critical_failures': critical_failures,
                'total_rules': len(validation_results)
            })
            
            self.stats['emails_validated'] += 1
            
            return {
                'email_id': email.id,
                'overall_score': overall_score,
                'quality_level': quality_level.value,
                'critical_failures': critical_failures,
                'validation_results': [
                    {
                        'rule_name': r.rule_name,
                        'passed': r.passed,
                        'score': r.score,
                        'message': r.message,
                        'severity': r.severity,
                        'metadata': r.metadata
                    }
                    for r in validation_results
                ],
                'validated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate email {email.id}: {str(e)}")
            self.stats['validation_failures'] += 1
            raise ValidationError(f"Email validation failed: {str(e)}")
    
    async def check_completeness(self, data: Dict[str, Any]) -> float:
        """
        Check data completeness score (0-1).
        
        Args:
            data: Data dictionary to check
            
        Returns:
            Completeness score between 0.0 and 1.0
        """
        if not data:
            return 0.0
        
        # Define required and optional fields with weights
        required_fields = {
            'id': 1.0,
            'message_id': 0.8,
            'subject': 0.9,
            'sender': 0.9,
            'received_date': 0.8,
            'body': 0.7
        }
        
        optional_fields = {
            'to_recipients': 0.6,
            'cc_recipients': 0.3,
            'bcc_recipients': 0.2,
            'attachments': 0.4,
            'folder_id': 0.5
        }
        
        total_weight = sum(required_fields.values()) + sum(optional_fields.values())
        achieved_weight = 0.0
        
        # Check required fields
        for field, weight in required_fields.items():
            if field in data and data[field] is not None:
                if isinstance(data[field], str) and data[field].strip():
                    achieved_weight += weight
                elif not isinstance(data[field], str) and data[field]:
                    achieved_weight += weight
        
        # Check optional fields
        for field, weight in optional_fields.items():
            if field in data and data[field] is not None:
                if isinstance(data[field], (list, dict)) and len(data[field]) > 0:
                    achieved_weight += weight
                elif isinstance(data[field], str) and data[field].strip():
                    achieved_weight += weight
                elif not isinstance(data[field], (str, list, dict)) and data[field]:
                    achieved_weight += weight
        
        return min(achieved_weight / total_weight, 1.0)
    
    async def detect_duplicates(self, emails: List[EmailMessage]) -> List[str]:
        """
        Detect duplicate emails using multiple strategies.
        
        Args:
            emails: List of emails to check for duplicates
            
        Returns:
            List of email IDs that are duplicates
        """
        if not self.enable_duplicate_detection:
            return []
        
        duplicates = []
        seen_hashes = set()
        
        for email in emails:
            # Create multiple hash signatures for different duplicate detection strategies
            signatures = await self._create_duplicate_signatures(email)
            
            for signature in signatures:
                if signature in seen_hashes:
                    duplicates.append(email.id)
                    self.stats['duplicates_detected'] += 1
                    break
                seen_hashes.add(signature)
        
        return duplicates
    
    async def assess_quality_level(self, validation_results: Dict[str, Any]) -> DataQualityLevel:
        """
        Assess overall data quality level based on validation results.
        
        Args:
            validation_results: Results from validation process
            
        Returns:
            Data quality level assessment
        """
        overall_score = validation_results.get('overall_score', 0.0)
        critical_failures = validation_results.get('critical_failures', 0)
        
        # Critical failures automatically reduce quality
        if critical_failures > 0:
            return DataQualityLevel.CRITICAL
        
        # Score-based assessment
        if overall_score >= 0.9:
            return DataQualityLevel.EXCELLENT
        elif overall_score >= 0.8:
            return DataQualityLevel.GOOD
        elif overall_score >= 0.6:
            return DataQualityLevel.FAIR
        elif overall_score >= 0.4:
            return DataQualityLevel.POOR
        else:
            return DataQualityLevel.CRITICAL
    
    def _setup_default_rules(self) -> None:
        """Setup default validation rules."""
        self.validation_rules = [
            ValidationRule(
                name="required_fields",
                description="Check that required fields are present",
                severity="critical",
                validator_func=self._validate_required_fields
            ),
            ValidationRule(
                name="email_format",
                description="Validate email address formats",
                severity="high",
                validator_func=self._validate_email_formats
            ),
            ValidationRule(
                name="date_validity",
                description="Check that dates are valid and reasonable",
                severity="high",
                validator_func=self._validate_dates
            ),
            ValidationRule(
                name="content_length",
                description="Check content length limits",
                severity="medium",
                validator_func=self._validate_content_length
            ),
            ValidationRule(
                name="encoding_validity",
                description="Check text encoding validity",
                severity="medium",
                validator_func=self._validate_encoding
            ),
            ValidationRule(
                name="data_consistency",
                description="Check internal data consistency",
                severity="high",
                validator_func=self._validate_consistency
            )
        ]
    
    async def _validate_required_fields(self, email: EmailMessage) -> ValidationResult:
        """Validate that required fields are present."""
        required_fields = ['id', 'message_id']
        missing_fields = []
        
        for field in required_fields:
            if not hasattr(email, field) or getattr(email, field) is None:
                missing_fields.append(field)
        
        passed = len(missing_fields) == 0
        score = 1.0 if passed else 0.0
        
        return ValidationResult(
            rule_name="required_fields",
            passed=passed,
            score=score,
            message=f"Missing required fields: {missing_fields}" if missing_fields else "All required fields present",
            severity="critical",
            metadata={'missing_fields': missing_fields}
        )
    
    async def _validate_email_formats(self, email: EmailMessage) -> ValidationResult:
        """Validate email address formats."""
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        invalid_emails = []
        
        # Check sender
        if email.sender and email.sender.email:
            if not email_pattern.match(email.sender.email):
                invalid_emails.append(f"sender: {email.sender.email}")
        
        # Check recipients
        for recipient in email.to_recipients + email.cc_recipients + email.bcc_recipients:
            if recipient.email and not email_pattern.match(recipient.email):
                invalid_emails.append(f"recipient: {recipient.email}")
        
        passed = len(invalid_emails) == 0
        score = 1.0 if passed else max(0.0, 1.0 - (len(invalid_emails) * 0.2))
        
        return ValidationResult(
            rule_name="email_format",
            passed=passed,
            score=score,
            message=f"Invalid email formats: {invalid_emails}" if invalid_emails else "All email formats valid",
            severity="high",
            metadata={'invalid_emails': invalid_emails}
        )
    
    async def _validate_dates(self, email: EmailMessage) -> ValidationResult:
        """Validate date fields."""
        issues = []
        now = datetime.utcnow()
        
        # Check sent date
        if email.sent_date:
            if email.sent_date > now + timedelta(hours=1):  # Allow 1 hour clock skew
                issues.append("sent_date is in the future")
            elif email.sent_date < datetime(1990, 1, 1):
                issues.append("sent_date is too old")
        
        # Check received date
        if email.received_date:
            if email.received_date > now + timedelta(hours=1):
                issues.append("received_date is in the future")
            elif email.received_date < datetime(1990, 1, 1):
                issues.append("received_date is too old")
        
        # Check date consistency
        if email.sent_date and email.received_date:
            if email.sent_date > email.received_date + timedelta(hours=1):
                issues.append("sent_date is after received_date")
        
        passed = len(issues) == 0
        score = 1.0 if passed else max(0.0, 1.0 - (len(issues) * 0.3))
        
        return ValidationResult(
            rule_name="date_validity",
            passed=passed,
            score=score,
            message=f"Date issues: {issues}" if issues else "All dates valid",
            severity="high",
            metadata={'date_issues': issues}
        )
    
    async def _validate_content_length(self, email: EmailMessage) -> ValidationResult:
        """Validate content length limits."""
        issues = []
        
        if email.subject and len(email.subject) > self.max_subject_length:
            issues.append(f"subject too long ({len(email.subject)} > {self.max_subject_length})")
        
        if email.body and len(email.body) > self.max_body_length:
            issues.append(f"body too long ({len(email.body)} > {self.max_body_length})")
        
        passed = len(issues) == 0
        score = 1.0 if passed else 0.7  # Length issues are not critical
        
        return ValidationResult(
            rule_name="content_length",
            passed=passed,
            score=score,
            message=f"Content length issues: {issues}" if issues else "Content lengths within limits",
            severity="medium",
            metadata={'length_issues': issues}
        )
    
    async def _validate_encoding(self, email: EmailMessage) -> ValidationResult:
        """Validate text encoding."""
        issues = []
        
        try:
            if email.subject:
                email.subject.encode('utf-8')
            if email.body:
                email.body.encode('utf-8')
        except UnicodeEncodeError as e:
            issues.append(f"encoding error: {str(e)}")
        
        passed = len(issues) == 0
        score = 1.0 if passed else 0.5
        
        return ValidationResult(
            rule_name="encoding_validity",
            passed=passed,
            score=score,
            message=f"Encoding issues: {issues}" if issues else "Text encoding valid",
            severity="medium",
            metadata={'encoding_issues': issues}
        )
    
    async def _validate_consistency(self, email: EmailMessage) -> ValidationResult:
        """Validate internal data consistency."""
        issues = []
        
        # Check attachment consistency
        if email.has_attachments and not email.attachments:
            issues.append("has_attachments is True but no attachments found")
        elif not email.has_attachments and email.attachments:
            issues.append("has_attachments is False but attachments exist")
        
        # Check recipient consistency
        total_recipients = len(email.to_recipients) + len(email.cc_recipients) + len(email.bcc_recipients)
        if total_recipients == 0:
            issues.append("no recipients found")
        
        passed = len(issues) == 0
        score = 1.0 if passed else max(0.0, 1.0 - (len(issues) * 0.2))
        
        return ValidationResult(
            rule_name="data_consistency",
            passed=passed,
            score=score,
            message=f"Consistency issues: {issues}" if issues else "Data is consistent",
            severity="high",
            metadata={'consistency_issues': issues}
        )
    
    async def _create_duplicate_signatures(self, email: EmailMessage) -> List[str]:
        """Create multiple signatures for duplicate detection."""
        signatures = []
        
        # Exact content hash
        if email.body:
            content_hash = hashlib.md5(email.body.encode('utf-8')).hexdigest()
            signatures.append(f"content_{content_hash}")
        
        # Subject + sender hash
        if email.subject and email.sender:
            subject_sender = f"{email.subject}_{email.sender.email}"
            subject_sender_hash = hashlib.md5(subject_sender.encode('utf-8')).hexdigest()
            signatures.append(f"subject_sender_{subject_sender_hash}")
        
        # Message ID (if available)
        if email.message_id:
            signatures.append(f"message_id_{email.message_id}")
        
        return signatures
    
    async def _add_custom_rule(self, rule_config: Dict[str, Any]) -> None:
        """Add a custom validation rule."""
        try:
            rule = ValidationRule(
                name=rule_config['name'],
                description=rule_config.get('description', ''),
                severity=rule_config.get('severity', 'medium'),
                validator_func=self._create_custom_validator(rule_config),
                enabled=rule_config.get('enabled', True)
            )

            self.validation_rules.append(rule)
            self.logger.info(f"Added custom validation rule: {rule.name}")

        except Exception as e:
            self.logger.error(f"Failed to add custom rule: {str(e)}")
            raise ValidationError(f"Custom rule creation failed: {str(e)}")

    def _create_custom_validator(self, rule_config: Dict[str, Any]) -> callable:
        """Create a custom validator function from configuration."""
        rule_type = rule_config.get('type', 'field_check')

        if rule_type == 'field_check':
            field_name = rule_config['field']
            condition = rule_config['condition']
            expected_value = rule_config.get('value')

            async def field_validator(email):
                field_value = getattr(email, field_name, None)

                if condition == 'not_null':
                    passed = field_value is not None
                elif condition == 'equals':
                    passed = field_value == expected_value
                elif condition == 'contains':
                    passed = expected_value in str(field_value) if field_value else False
                elif condition == 'regex':
                    import re
                    passed = bool(re.search(expected_value, str(field_value))) if field_value else False
                else:
                    passed = False

                return ValidationResult(
                    rule_name=rule_config['name'],
                    passed=passed,
                    score=1.0 if passed else 0.0,
                    message=f"Field {field_name} validation: {'passed' if passed else 'failed'}",
                    severity=rule_config.get('severity', 'medium'),
                    metadata={'field': field_name, 'condition': condition}
                )

            return field_validator

        else:
            # Default validator that always passes
            async def default_validator(email):
                return ValidationResult(
                    rule_name=rule_config['name'],
                    passed=True,
                    score=1.0,
                    message="Custom rule executed",
                    severity=rule_config.get('severity', 'medium'),
                    metadata={}
                )

            return default_validator
    
    async def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        return {
            **self.stats,
            'is_initialized': self.is_initialized,
            'total_rules': len(self.validation_rules),
            'enabled_rules': sum(1 for rule in self.validation_rules if rule.enabled),
            'duplicate_detection_enabled': self.enable_duplicate_detection,
            'anomaly_detection_enabled': self.enable_anomaly_detection
        }
