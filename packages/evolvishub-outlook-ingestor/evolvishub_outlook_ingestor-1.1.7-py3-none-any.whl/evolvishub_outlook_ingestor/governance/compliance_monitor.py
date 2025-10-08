"""
GDPR/CCPA compliance monitoring and enforcement.

This module provides comprehensive compliance monitoring capabilities including
GDPR Article 5 validation, CCPA compliance checking, and violation reporting.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import re

from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.core.exceptions import GovernanceError

logger = logging.getLogger(__name__)


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"
    CCPA = "ccpa"
    PIPEDA = "pipeda"
    LGPD = "lgpd"


class ViolationSeverity(Enum):
    """Severity levels for compliance violations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplianceViolation:
    """A compliance violation."""
    violation_id: str
    framework: ComplianceFramework
    article_section: str
    description: str
    severity: ViolationSeverity
    entity_id: str
    detected_at: datetime
    remediation_required: bool
    remediation_deadline: Optional[datetime]
    metadata: Dict[str, Any]


@dataclass
class ComplianceResult:
    """Result of compliance check."""
    is_compliant: bool
    framework: ComplianceFramework
    violations: List[ComplianceViolation]
    checked_at: datetime
    recommendations: List[str]


@dataclass
class ComplianceReport:
    """Comprehensive compliance audit report."""
    timeframe: str
    frameworks_checked: List[str]
    total_operations: int
    compliant_operations: int
    violation_count: int
    violations_by_severity: Dict[str, int]
    violations_by_framework: Dict[str, int]
    top_violations: List[ComplianceViolation]
    recommendations: List[str]
    generated_at: datetime


class ComplianceMonitor:
    """
    GDPR/CCPA compliance monitoring and enforcement.
    
    Provides comprehensive compliance monitoring including:
    - GDPR Article 5 principle validation
    - CCPA consumer rights compliance
    - Automated violation detection
    - Compliance reporting and audit trails
    - Remediation recommendations
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the compliance monitor.
        
        Args:
            config: Configuration dictionary containing compliance settings
        """
        self.config = config
        self.enabled_frameworks = config.get('compliance_frameworks', ['GDPR', 'CCPA'])
        self.violation_threshold = config.get('violation_threshold', 10)
        self.auto_remediation = config.get('auto_remediation', False)
        
        # PII detection patterns
        self.pii_patterns = self._load_pii_patterns()
        
        # Violation tracking
        self.violations: List[ComplianceViolation] = []
        self.violation_counter = 0
        
    async def initialize(self) -> None:
        """Initialize the compliance monitor."""
        logger.info("Initializing ComplianceMonitor")
        
    async def check_gdpr_compliance(self, operation: Dict[str, Any]) -> ComplianceResult:
        """
        Check GDPR compliance for data operations.
        
        Args:
            operation: Data operation to check
            
        Returns:
            GDPR compliance result
            
        Raises:
            GovernanceError: If compliance check fails
        """
        try:
            violations = []
            
            # Article 5(1)(a) - Lawfulness, fairness and transparency
            if not await self._check_lawful_basis(operation):
                violations.append(self._create_violation(
                    ComplianceFramework.GDPR,
                    "Article 5(1)(a)",
                    "No lawful basis for processing personal data",
                    ViolationSeverity.CRITICAL,
                    operation.get('entity_id', 'unknown')
                ))
            
            # Article 5(1)(b) - Purpose limitation
            if not await self._check_purpose_limitation(operation):
                violations.append(self._create_violation(
                    ComplianceFramework.GDPR,
                    "Article 5(1)(b)",
                    "Data processed for purposes incompatible with original purpose",
                    ViolationSeverity.HIGH,
                    operation.get('entity_id', 'unknown')
                ))
            
            # Article 5(1)(c) - Data minimization
            if not await self._check_data_minimization(operation):
                violations.append(self._create_violation(
                    ComplianceFramework.GDPR,
                    "Article 5(1)(c)",
                    "Data processing exceeds what is necessary for the purpose",
                    ViolationSeverity.HIGH,
                    operation.get('entity_id', 'unknown')
                ))
            
            # Article 5(1)(d) - Accuracy
            if not await self._check_data_accuracy(operation):
                violations.append(self._create_violation(
                    ComplianceFramework.GDPR,
                    "Article 5(1)(d)",
                    "Inaccurate or outdated personal data detected",
                    ViolationSeverity.MEDIUM,
                    operation.get('entity_id', 'unknown')
                ))
            
            # Article 5(1)(e) - Storage limitation
            if not await self._check_retention_limits(operation):
                violations.append(self._create_violation(
                    ComplianceFramework.GDPR,
                    "Article 5(1)(e)",
                    "Data retained longer than necessary for the purpose",
                    ViolationSeverity.MEDIUM,
                    operation.get('entity_id', 'unknown')
                ))
            
            # Article 5(1)(f) - Integrity and confidentiality
            if not await self._check_security_measures(operation):
                violations.append(self._create_violation(
                    ComplianceFramework.GDPR,
                    "Article 5(1)(f)",
                    "Inadequate security measures for personal data",
                    ViolationSeverity.HIGH,
                    operation.get('entity_id', 'unknown')
                ))
            
            # Generate recommendations
            recommendations = await self._generate_gdpr_recommendations(violations)
            
            return ComplianceResult(
                is_compliant=len(violations) == 0,
                framework=ComplianceFramework.GDPR,
                violations=violations,
                checked_at=datetime.utcnow(),
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error checking GDPR compliance: {e}")
            raise GovernanceError(f"GDPR compliance check failed: {e}")
    
    async def check_ccpa_compliance(self, operation: Dict[str, Any]) -> ComplianceResult:
        """
        Check CCPA compliance for data operations.
        
        Args:
            operation: Data operation to check
            
        Returns:
            CCPA compliance result
        """
        try:
            violations = []
            
            # Right to know
            if not await self._check_transparency_requirements(operation):
                violations.append(self._create_violation(
                    ComplianceFramework.CCPA,
                    "Section 1798.100",
                    "Insufficient transparency about data collection and use",
                    ViolationSeverity.HIGH,
                    operation.get('entity_id', 'unknown')
                ))
            
            # Right to delete
            if not await self._check_deletion_capability(operation):
                violations.append(self._create_violation(
                    ComplianceFramework.CCPA,
                    "Section 1798.105",
                    "No mechanism for consumer data deletion requests",
                    ViolationSeverity.HIGH,
                    operation.get('entity_id', 'unknown')
                ))
            
            # Right to opt-out
            if not await self._check_opt_out_mechanism(operation):
                violations.append(self._create_violation(
                    ComplianceFramework.CCPA,
                    "Section 1798.120",
                    "No opt-out mechanism for data sale",
                    ViolationSeverity.MEDIUM,
                    operation.get('entity_id', 'unknown')
                ))
            
            # Non-discrimination
            if not await self._check_non_discrimination(operation):
                violations.append(self._create_violation(
                    ComplianceFramework.CCPA,
                    "Section 1798.125",
                    "Discriminatory practices against consumers exercising rights",
                    ViolationSeverity.HIGH,
                    operation.get('entity_id', 'unknown')
                ))
            
            # Generate recommendations
            recommendations = await self._generate_ccpa_recommendations(violations)
            
            return ComplianceResult(
                is_compliant=len(violations) == 0,
                framework=ComplianceFramework.CCPA,
                violations=violations,
                checked_at=datetime.utcnow(),
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error checking CCPA compliance: {e}")
            raise GovernanceError(f"CCPA compliance check failed: {e}")
    
    async def monitor_email_compliance(self, email: EmailMessage) -> List[ComplianceViolation]:
        """
        Monitor email for compliance violations.
        
        Args:
            email: Email message to monitor
            
        Returns:
            List of detected violations
        """
        try:
            violations = []
            
            # Check for PII in email content
            pii_violations = await self._detect_pii_violations(email)
            violations.extend(pii_violations)
            
            # Check retention compliance
            retention_violations = await self._check_email_retention(email)
            violations.extend(retention_violations)
            
            # Check consent requirements
            consent_violations = await self._check_consent_requirements(email)
            violations.extend(consent_violations)
            
            # Store violations
            self.violations.extend(violations)
            
            return violations
            
        except Exception as e:
            logger.error(f"Error monitoring email compliance: {e}")
            return []
    
    async def generate_compliance_report(self, timeframe: str) -> ComplianceReport:
        """
        Generate comprehensive compliance audit report.
        
        Args:
            timeframe: Timeframe for the report (e.g., "30d", "1y")
            
        Returns:
            Compliance audit report
        """
        try:
            start_date, end_date = self._parse_timeframe(timeframe)
            
            # Filter violations by timeframe
            relevant_violations = [
                v for v in self.violations
                if start_date <= v.detected_at <= end_date
            ]
            
            # Calculate statistics
            violations_by_severity = {}
            violations_by_framework = {}
            
            for violation in relevant_violations:
                severity = violation.severity.value
                framework = violation.framework.value
                
                violations_by_severity[severity] = violations_by_severity.get(severity, 0) + 1
                violations_by_framework[framework] = violations_by_framework.get(framework, 0) + 1
            
            # Get top violations
            top_violations = sorted(
                relevant_violations,
                key=lambda v: (v.severity.value, v.detected_at),
                reverse=True
            )[:10]
            
            # Generate recommendations
            recommendations = await self._generate_report_recommendations(relevant_violations)
            
            return ComplianceReport(
                timeframe=timeframe,
                frameworks_checked=self.enabled_frameworks,
                total_operations=1000,  # Placeholder
                compliant_operations=1000 - len(relevant_violations),
                violation_count=len(relevant_violations),
                violations_by_severity=violations_by_severity,
                violations_by_framework=violations_by_framework,
                top_violations=top_violations,
                recommendations=recommendations,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            raise GovernanceError(f"Compliance report generation failed: {e}")
    
    def _create_violation(
        self,
        framework: ComplianceFramework,
        article_section: str,
        description: str,
        severity: ViolationSeverity,
        entity_id: str
    ) -> ComplianceViolation:
        """Create a compliance violation."""
        self.violation_counter += 1
        
        # Calculate remediation deadline based on severity
        remediation_deadline = None
        if severity == ViolationSeverity.CRITICAL:
            remediation_deadline = datetime.utcnow() + timedelta(days=1)
        elif severity == ViolationSeverity.HIGH:
            remediation_deadline = datetime.utcnow() + timedelta(days=7)
        elif severity == ViolationSeverity.MEDIUM:
            remediation_deadline = datetime.utcnow() + timedelta(days=30)
        
        return ComplianceViolation(
            violation_id=f"violation_{self.violation_counter:06d}",
            framework=framework,
            article_section=article_section,
            description=description,
            severity=severity,
            entity_id=entity_id,
            detected_at=datetime.utcnow(),
            remediation_required=severity in [ViolationSeverity.CRITICAL, ViolationSeverity.HIGH],
            remediation_deadline=remediation_deadline,
            metadata={}
        )
    
    async def _check_lawful_basis(self, operation: Dict[str, Any]) -> bool:
        """Check if there's a lawful basis for processing."""
        # Check if lawful basis is documented
        return operation.get('lawful_basis') is not None
    
    async def _check_purpose_limitation(self, operation: Dict[str, Any]) -> bool:
        """Check purpose limitation compliance."""
        original_purpose = operation.get('original_purpose')
        current_purpose = operation.get('current_purpose')
        
        if not original_purpose or not current_purpose:
            return False
        
        # Check if purposes are compatible
        return original_purpose == current_purpose or self._are_purposes_compatible(original_purpose, current_purpose)
    
    async def _check_data_minimization(self, operation: Dict[str, Any]) -> bool:
        """Check data minimization compliance."""
        # Check if only necessary data is being processed
        data_fields = operation.get('data_fields', [])
        necessary_fields = operation.get('necessary_fields', [])
        
        # All processed fields should be necessary
        return all(field in necessary_fields for field in data_fields)
    
    async def _check_data_accuracy(self, operation: Dict[str, Any]) -> bool:
        """Check data accuracy requirements."""
        # Check if data accuracy is maintained
        last_updated = operation.get('last_updated')
        if last_updated:
            # Data should be updated within reasonable timeframe
            cutoff = datetime.utcnow() - timedelta(days=365)
            return last_updated > cutoff
        
        return True  # Assume accurate if no timestamp
    
    async def _check_retention_limits(self, operation: Dict[str, Any]) -> bool:
        """Check storage limitation compliance."""
        retention_period = operation.get('retention_period_days')
        data_age_days = operation.get('data_age_days', 0)
        
        if retention_period:
            return data_age_days <= retention_period
        
        return True  # No specific limit set
    
    async def _check_security_measures(self, operation: Dict[str, Any]) -> bool:
        """Check security measures compliance."""
        # Check if appropriate security measures are in place
        security_measures = operation.get('security_measures', [])
        required_measures = ['encryption', 'access_control', 'audit_logging']
        
        return all(measure in security_measures for measure in required_measures)
    
    async def _check_transparency_requirements(self, operation: Dict[str, Any]) -> bool:
        """Check CCPA transparency requirements."""
        # Check if privacy notice is provided
        return operation.get('privacy_notice_provided', False)
    
    async def _check_deletion_capability(self, operation: Dict[str, Any]) -> bool:
        """Check CCPA deletion capability."""
        # Check if deletion mechanism exists
        return operation.get('deletion_mechanism_available', False)
    
    async def _check_opt_out_mechanism(self, operation: Dict[str, Any]) -> bool:
        """Check CCPA opt-out mechanism."""
        # Check if opt-out mechanism is available
        return operation.get('opt_out_mechanism_available', False)
    
    async def _check_non_discrimination(self, operation: Dict[str, Any]) -> bool:
        """Check CCPA non-discrimination requirements."""
        # Check if non-discriminatory practices are followed
        return operation.get('non_discriminatory_practices', True)
    
    async def _detect_pii_violations(self, email: EmailMessage) -> List[ComplianceViolation]:
        """Detect PII-related compliance violations in email."""
        violations = []
        
        # Check email content for PII
        content = f"{email.subject or ''} {email.body or ''}"
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = pattern.findall(content)
            if matches:
                violations.append(self._create_violation(
                    ComplianceFramework.GDPR,
                    "Article 5(1)(f)",
                    f"Unprotected {pii_type} detected in email content",
                    ViolationSeverity.HIGH,
                    email.id
                ))
        
        return violations
    
    async def _check_email_retention(self, email: EmailMessage) -> List[ComplianceViolation]:
        """Check email retention compliance."""
        violations = []
        
        if email.received_date:
            # Check if email is older than maximum retention period
            max_retention_days = self.config.get('max_retention_days', 2555)  # 7 years
            cutoff_date = datetime.utcnow() - timedelta(days=max_retention_days)
            
            if email.received_date < cutoff_date:
                violations.append(self._create_violation(
                    ComplianceFramework.GDPR,
                    "Article 5(1)(e)",
                    f"Email retained beyond maximum retention period",
                    ViolationSeverity.MEDIUM,
                    email.id
                ))
        
        return violations
    
    async def _check_consent_requirements(self, email: EmailMessage) -> List[ComplianceViolation]:
        """Check consent requirements for email processing."""
        violations = []
        
        # Check if consent is required and available
        # This is a simplified check - real implementation would be more complex
        if not self.config.get('consent_obtained', True):
            violations.append(self._create_violation(
                ComplianceFramework.GDPR,
                "Article 6(1)(a)",
                "No valid consent for email processing",
                ViolationSeverity.CRITICAL,
                email.id
            ))
        
        return violations
    
    def _load_pii_patterns(self) -> Dict[str, re.Pattern]:
        """Load PII detection patterns."""
        return {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
        }
    
    def _are_purposes_compatible(self, original: str, current: str) -> bool:
        """Check if two purposes are compatible."""
        # Simplified compatibility check
        compatible_purposes = {
            'email_processing': ['analytics', 'quality_improvement'],
            'analytics': ['reporting', 'insights'],
        }
        
        return current in compatible_purposes.get(original, [])
    
    def _parse_timeframe(self, timeframe: str) -> tuple[datetime, datetime]:
        """Parse timeframe string into start and end dates."""
        end_date = datetime.utcnow()
        
        if timeframe.endswith('d'):
            days = int(timeframe[:-1])
            start_date = end_date - timedelta(days=days)
        elif timeframe.endswith('m'):
            months = int(timeframe[:-1])
            start_date = end_date - timedelta(days=months * 30)
        elif timeframe.endswith('y'):
            years = int(timeframe[:-1])
            start_date = end_date - timedelta(days=years * 365)
        else:
            # Default to 30 days
            start_date = end_date - timedelta(days=30)
        
        return start_date, end_date
    
    async def _generate_gdpr_recommendations(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate GDPR-specific recommendations."""
        recommendations = []
        
        violation_types = [v.article_section for v in violations]
        
        if "Article 5(1)(a)" in violation_types:
            recommendations.append("Establish and document lawful basis for all data processing activities")
        
        if "Article 5(1)(c)" in violation_types:
            recommendations.append("Implement data minimization practices to collect only necessary data")
        
        if "Article 5(1)(e)" in violation_types:
            recommendations.append("Review and update data retention policies")
        
        if "Article 5(1)(f)" in violation_types:
            recommendations.append("Enhance security measures including encryption and access controls")
        
        return recommendations
    
    async def _generate_ccpa_recommendations(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate CCPA-specific recommendations."""
        recommendations = []
        
        violation_sections = [v.article_section for v in violations]
        
        if "Section 1798.100" in violation_sections:
            recommendations.append("Improve transparency in privacy notices and data collection practices")
        
        if "Section 1798.105" in violation_sections:
            recommendations.append("Implement consumer data deletion request mechanisms")
        
        if "Section 1798.120" in violation_sections:
            recommendations.append("Provide clear opt-out mechanisms for data sale")
        
        return recommendations
    
    async def _generate_report_recommendations(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate general recommendations based on violations."""
        recommendations = []
        
        if len(violations) > self.violation_threshold:
            recommendations.append("High number of violations detected - conduct comprehensive compliance review")
        
        critical_violations = [v for v in violations if v.severity == ViolationSeverity.CRITICAL]
        if critical_violations:
            recommendations.append("Address critical violations immediately to avoid regulatory penalties")
        
        frameworks = set(v.framework for v in violations)
        if len(frameworks) > 1:
            recommendations.append("Implement unified compliance framework to address multiple regulations")
        
        return recommendations
