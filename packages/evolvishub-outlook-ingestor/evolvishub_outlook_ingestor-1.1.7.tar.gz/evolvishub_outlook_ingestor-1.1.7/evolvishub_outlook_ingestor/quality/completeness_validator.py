"""
Email data completeness validation and scoring.

This module provides comprehensive validation of email data completeness,
including field-level scoring, data quality metrics, and validation rules.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import re

from evolvishub_outlook_ingestor.core.data_models import EmailMessage, EmailAddress
from evolvishub_outlook_ingestor.core.exceptions import QualityError

logger = logging.getLogger(__name__)


class FieldImportance(Enum):
    """Importance levels for email fields."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"


@dataclass
class FieldValidation:
    """Validation result for a single field."""
    field_name: str
    is_present: bool
    is_valid: bool
    completeness_score: float  # 0.0 to 1.0
    validation_errors: List[str]
    field_importance: FieldImportance


@dataclass
class ValidationResult:
    """Complete validation result for an email."""
    email_id: str
    overall_completeness_score: float  # 0.0 to 1.0
    field_validations: List[FieldValidation]
    critical_issues: List[str]
    warnings: List[str]
    is_valid: bool
    validation_timestamp: datetime


@dataclass
class CompletenessReport:
    """Completeness analysis report for a set of emails."""
    total_emails: int
    average_completeness_score: float
    field_completeness_stats: Dict[str, Dict[str, float]]
    validation_summary: Dict[str, int]
    top_issues: List[Tuple[str, int]]
    recommendations: List[str]


class CompletenessValidator:
    """
    Validates email data completeness and calculates quality scores.
    
    Provides comprehensive validation including:
    - Field-level completeness scoring
    - Data quality metrics calculation
    - Configurable validation rules
    - Importance-weighted scoring
    - Detailed reporting and recommendations
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the completeness validator.
        
        Args:
            config: Configuration dictionary containing:
                - field_weights: Weights for different fields in scoring
                - validation_rules: Custom validation rules
                - required_fields: List of required fields
                - min_completeness_threshold: Minimum acceptable completeness (default: 0.7)
        """
        self.config = config
        self.field_weights = config.get('field_weights', self._get_default_field_weights())
        self.validation_rules = config.get('validation_rules', {})
        self.required_fields = config.get('required_fields', ['id', 'sender', 'received_date'])
        self.min_completeness_threshold = config.get('min_completeness_threshold', 0.7)
        
        # Field importance mapping
        self.field_importance = self._get_field_importance_mapping()
        
    async def initialize(self) -> None:
        """Initialize the completeness validator."""
        logger.info("Initializing CompletenessValidator")
        
    async def validate_completeness(self, email: EmailMessage) -> ValidationResult:
        """
        Validate completeness of a single email.
        
        Args:
            email: Email message to validate
            
        Returns:
            Validation result with completeness score and details
            
        Raises:
            QualityError: If validation fails
        """
        try:
            field_validations = []
            critical_issues = []
            warnings = []
            
            # Validate each field
            for field_name, weight in self.field_weights.items():
                field_validation = await self._validate_field(email, field_name)
                field_validations.append(field_validation)
                
                # Collect issues
                if not field_validation.is_present and field_name in self.required_fields:
                    critical_issues.append(f"Required field '{field_name}' is missing")
                elif not field_validation.is_valid:
                    if field_validation.field_importance in [FieldImportance.CRITICAL, FieldImportance.HIGH]:
                        critical_issues.extend(field_validation.validation_errors)
                    else:
                        warnings.extend(field_validation.validation_errors)
            
            # Calculate overall completeness score
            overall_score = await self._calculate_overall_score(field_validations)
            
            # Determine if email is valid
            is_valid = (
                len(critical_issues) == 0 and 
                overall_score >= self.min_completeness_threshold
            )
            
            return ValidationResult(
                email_id=email.id,
                overall_completeness_score=overall_score,
                field_validations=field_validations,
                critical_issues=critical_issues,
                warnings=warnings,
                is_valid=is_valid,
                validation_timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error validating email completeness: {e}")
            raise QualityError(f"Completeness validation failed: {e}")
    
    async def validate_batch(self, emails: List[EmailMessage]) -> List[ValidationResult]:
        """
        Validate completeness for a batch of emails.
        
        Args:
            emails: List of email messages to validate
            
        Returns:
            List of validation results
        """
        try:
            validation_results = []
            
            for email in emails:
                result = await self.validate_completeness(email)
                validation_results.append(result)
            
            logger.info(f"Validated completeness for {len(emails)} emails")
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating email batch: {e}")
            raise QualityError(f"Batch validation failed: {e}")
    
    def calculate_completeness_score(self, email: EmailMessage) -> float:
        """
        Calculate completeness score for an email (synchronous version).
        
        Args:
            email: Email message to score
            
        Returns:
            Completeness score between 0.0 and 1.0
        """
        try:
            total_weight = 0
            weighted_score = 0
            
            for field_name, weight in self.field_weights.items():
                field_score = self._calculate_field_score(email, field_name)
                weighted_score += field_score * weight
                total_weight += weight
            
            return weighted_score / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating completeness score: {e}")
            return 0.0
    
    async def generate_completeness_report(self, emails: List[EmailMessage]) -> CompletenessReport:
        """
        Generate comprehensive completeness report for a set of emails.
        
        Args:
            emails: List of email messages to analyze
            
        Returns:
            Completeness analysis report
        """
        try:
            if not emails:
                return CompletenessReport(
                    total_emails=0,
                    average_completeness_score=0.0,
                    field_completeness_stats={},
                    validation_summary={},
                    top_issues=[],
                    recommendations=[]
                )
            
            # Validate all emails
            validation_results = await self.validate_batch(emails)
            
            # Calculate statistics
            total_emails = len(emails)
            scores = [result.overall_completeness_score for result in validation_results]
            average_score = sum(scores) / len(scores)
            
            # Field-level statistics
            field_stats = await self._calculate_field_statistics(emails)
            
            # Validation summary
            validation_summary = {
                'valid_emails': sum(1 for r in validation_results if r.is_valid),
                'invalid_emails': sum(1 for r in validation_results if not r.is_valid),
                'emails_with_critical_issues': sum(1 for r in validation_results if r.critical_issues),
                'emails_with_warnings': sum(1 for r in validation_results if r.warnings)
            }
            
            # Top issues
            issue_counts = {}
            for result in validation_results:
                for issue in result.critical_issues + result.warnings:
                    issue_counts[issue] = issue_counts.get(issue, 0) + 1
            
            top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(field_stats, validation_summary, top_issues)
            
            return CompletenessReport(
                total_emails=total_emails,
                average_completeness_score=average_score,
                field_completeness_stats=field_stats,
                validation_summary=validation_summary,
                top_issues=top_issues,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error generating completeness report: {e}")
            raise QualityError(f"Report generation failed: {e}")
    
    async def _validate_field(self, email: EmailMessage, field_name: str) -> FieldValidation:
        """Validate a specific field of an email."""
        field_value = getattr(email, field_name, None)
        is_present = field_value is not None
        validation_errors = []
        
        # Basic presence check
        if not is_present:
            validation_errors.append(f"Field '{field_name}' is missing")
            return FieldValidation(
                field_name=field_name,
                is_present=False,
                is_valid=False,
                completeness_score=0.0,
                validation_errors=validation_errors,
                field_importance=self.field_importance.get(field_name, FieldImportance.MEDIUM)
            )
        
        # Field-specific validation
        is_valid = True
        
        if field_name == 'sender':
            is_valid = await self._validate_email_address(field_value)
            if not is_valid:
                validation_errors.append("Invalid sender email address format")
        
        elif field_name == 'to_recipients':
            if isinstance(field_value, list):
                for recipient in field_value:
                    if not await self._validate_email_address(recipient):
                        validation_errors.append("Invalid recipient email address format")
                        is_valid = False
                        break
            else:
                validation_errors.append("Recipients field should be a list")
                is_valid = False
        
        elif field_name == 'subject':
            if isinstance(field_value, str):
                if len(field_value.strip()) == 0:
                    validation_errors.append("Subject is empty")
                    is_valid = False
                elif len(field_value) > 1000:  # Reasonable subject length limit
                    validation_errors.append("Subject is unusually long")
            else:
                validation_errors.append("Subject should be a string")
                is_valid = False
        
        elif field_name == 'body':
            if isinstance(field_value, str):
                if len(field_value.strip()) == 0:
                    validation_errors.append("Email body is empty")
                    is_valid = False
            else:
                validation_errors.append("Body should be a string")
                is_valid = False
        
        elif field_name in ['sent_date', 'received_date', 'created_date', 'modified_date']:
            if not isinstance(field_value, datetime):
                validation_errors.append(f"{field_name} should be a datetime object")
                is_valid = False
            elif field_value > datetime.utcnow():
                validation_errors.append(f"{field_name} is in the future")
                is_valid = False
        
        elif field_name == 'id':
            if not isinstance(field_value, str) or len(field_value.strip()) == 0:
                validation_errors.append("Email ID should be a non-empty string")
                is_valid = False
        
        # Apply custom validation rules
        if field_name in self.validation_rules:
            custom_validation = await self._apply_custom_validation(field_value, self.validation_rules[field_name])
            if not custom_validation['is_valid']:
                validation_errors.extend(custom_validation['errors'])
                is_valid = False
        
        # Calculate field completeness score
        completeness_score = self._calculate_field_score(email, field_name)
        
        return FieldValidation(
            field_name=field_name,
            is_present=is_present,
            is_valid=is_valid,
            completeness_score=completeness_score,
            validation_errors=validation_errors,
            field_importance=self.field_importance.get(field_name, FieldImportance.MEDIUM)
        )
    
    async def _validate_email_address(self, email_address: Any) -> bool:
        """Validate email address format."""
        if isinstance(email_address, EmailAddress):
            email_str = email_address.email
        elif isinstance(email_address, str):
            email_str = email_address
        else:
            return False
        
        # Basic email regex validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email_str))
    
    async def _apply_custom_validation(self, field_value: Any, validation_rule: Dict[str, Any]) -> Dict[str, Any]:
        """Apply custom validation rule to a field value."""
        errors = []
        is_valid = True
        
        # Example custom validation rules
        if 'min_length' in validation_rule:
            if isinstance(field_value, str) and len(field_value) < validation_rule['min_length']:
                errors.append(f"Field length is below minimum ({validation_rule['min_length']})")
                is_valid = False
        
        if 'max_length' in validation_rule:
            if isinstance(field_value, str) and len(field_value) > validation_rule['max_length']:
                errors.append(f"Field length exceeds maximum ({validation_rule['max_length']})")
                is_valid = False
        
        if 'pattern' in validation_rule:
            if isinstance(field_value, str) and not re.match(validation_rule['pattern'], field_value):
                errors.append(f"Field does not match required pattern")
                is_valid = False
        
        return {'is_valid': is_valid, 'errors': errors}
    
    def _calculate_field_score(self, email: EmailMessage, field_name: str) -> float:
        """Calculate completeness score for a specific field."""
        field_value = getattr(email, field_name, None)
        
        if field_value is None:
            return 0.0
        
        # Field-specific scoring logic
        if field_name in ['subject', 'body']:
            if isinstance(field_value, str):
                content_length = len(field_value.strip())
                if content_length == 0:
                    return 0.0
                elif content_length < 10:
                    return 0.5  # Very short content
                else:
                    return 1.0
            return 0.0
        
        elif field_name in ['to_recipients', 'cc_recipients', 'bcc_recipients']:
            if isinstance(field_value, list):
                if len(field_value) == 0:
                    return 0.0 if field_name == 'to_recipients' else 1.0  # CC/BCC can be empty
                else:
                    return 1.0
            return 0.0
        
        elif field_name in ['sender', 'from_address']:
            if isinstance(field_value, (EmailAddress, str)):
                return 1.0
            return 0.0
        
        elif field_name in ['sent_date', 'received_date', 'created_date', 'modified_date']:
            if isinstance(field_value, datetime):
                return 1.0
            return 0.0
        
        else:
            # For other fields, simple presence check
            return 1.0 if field_value is not None else 0.0
    
    async def _calculate_overall_score(self, field_validations: List[FieldValidation]) -> float:
        """Calculate overall completeness score from field validations."""
        total_weight = 0
        weighted_score = 0
        
        for validation in field_validations:
            weight = self.field_weights.get(validation.field_name, 1.0)
            weighted_score += validation.completeness_score * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    async def _calculate_field_statistics(self, emails: List[EmailMessage]) -> Dict[str, Dict[str, float]]:
        """Calculate field-level completeness statistics."""
        field_stats = {}
        
        for field_name in self.field_weights.keys():
            present_count = 0
            valid_count = 0
            total_score = 0
            
            for email in emails:
                field_value = getattr(email, field_name, None)
                
                if field_value is not None:
                    present_count += 1
                    
                    # Simple validation check
                    if field_name == 'sender':
                        if await self._validate_email_address(field_value):
                            valid_count += 1
                    elif field_name in ['subject', 'body']:
                        if isinstance(field_value, str) and len(field_value.strip()) > 0:
                            valid_count += 1
                    else:
                        valid_count += 1
                
                field_score = self._calculate_field_score(email, field_name)
                total_score += field_score
            
            field_stats[field_name] = {
                'presence_rate': present_count / len(emails),
                'validity_rate': valid_count / len(emails),
                'average_score': total_score / len(emails)
            }
        
        return field_stats
    
    async def _generate_recommendations(
        self, 
        field_stats: Dict[str, Dict[str, float]], 
        validation_summary: Dict[str, int],
        top_issues: List[Tuple[str, int]]
    ) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        # Check for fields with low presence rates
        for field_name, stats in field_stats.items():
            if stats['presence_rate'] < 0.8:
                recommendations.append(
                    f"Improve data collection for '{field_name}' field "
                    f"(currently {stats['presence_rate']:.1%} present)"
                )
        
        # Check for fields with low validity rates
        for field_name, stats in field_stats.items():
            if stats['validity_rate'] < 0.9 and stats['presence_rate'] > 0.5:
                recommendations.append(
                    f"Implement validation for '{field_name}' field "
                    f"(currently {stats['validity_rate']:.1%} valid)"
                )
        
        # General recommendations based on validation summary
        invalid_percentage = validation_summary['invalid_emails'] / (
            validation_summary['valid_emails'] + validation_summary['invalid_emails']
        ) if (validation_summary['valid_emails'] + validation_summary['invalid_emails']) > 0 else 0
        
        if invalid_percentage > 0.2:
            recommendations.append(
                "Consider implementing data quality checks at ingestion time "
                f"({invalid_percentage:.1%} of emails have quality issues)"
            )
        
        # Recommendations based on top issues
        if top_issues:
            most_common_issue = top_issues[0][0]
            recommendations.append(f"Priority fix: Address '{most_common_issue}' issue")
        
        return recommendations
    
    def _get_default_field_weights(self) -> Dict[str, float]:
        """Get default field weights for scoring."""
        return {
            'id': 2.0,
            'sender': 2.0,
            'subject': 1.5,
            'body': 1.5,
            'to_recipients': 2.0,
            'received_date': 1.5,
            'sent_date': 1.0,
            'cc_recipients': 0.5,
            'bcc_recipients': 0.3,
            'reply_to': 0.5,
            'importance': 0.5,
            'is_read': 0.3,
            'has_attachments': 0.5,
            'conversation_id': 0.8,
            'message_id': 0.8
        }
    
    def _get_field_importance_mapping(self) -> Dict[str, FieldImportance]:
        """Get field importance mapping."""
        return {
            'id': FieldImportance.CRITICAL,
            'sender': FieldImportance.CRITICAL,
            'to_recipients': FieldImportance.CRITICAL,
            'subject': FieldImportance.HIGH,
            'body': FieldImportance.HIGH,
            'received_date': FieldImportance.HIGH,
            'sent_date': FieldImportance.MEDIUM,
            'cc_recipients': FieldImportance.MEDIUM,
            'bcc_recipients': FieldImportance.LOW,
            'reply_to': FieldImportance.LOW,
            'importance': FieldImportance.LOW,
            'is_read': FieldImportance.OPTIONAL,
            'has_attachments': FieldImportance.MEDIUM,
            'conversation_id': FieldImportance.MEDIUM,
            'message_id': FieldImportance.MEDIUM
        }
