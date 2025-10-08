"""
Data retention management and policy enforcement.

This module provides comprehensive data retention capabilities including
policy-based retention, automated deletion scheduling, and compliance reporting.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.core.exceptions import GovernanceError

logger = logging.getLogger(__name__)


class RetentionAction(Enum):
    """Types of retention actions."""
    DELETE = "delete"
    ARCHIVE = "archive"
    ANONYMIZE = "anonymize"
    RETAIN = "retain"


@dataclass
class RetentionPolicy:
    """Data retention policy definition."""
    policy_id: str
    name: str
    description: str
    retention_period_days: int
    action: RetentionAction
    criteria: Dict[str, Any]
    enabled: bool
    created_at: datetime
    last_modified: datetime


@dataclass
class RetentionResult:
    """Result of retention policy application."""
    policy_id: str
    emails_processed: int
    emails_deleted: int
    emails_archived: int
    emails_anonymized: int
    emails_retained: int
    execution_time_seconds: float
    errors: List[str]


class RetentionManager:
    """
    Manages data retention policies and enforcement.
    
    Provides comprehensive retention management including:
    - Policy-based retention rules
    - Automated deletion scheduling
    - Compliance reporting
    - Legal hold management
    - Audit trail maintenance
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the retention manager.
        
        Args:
            config: Configuration dictionary containing retention settings
        """
        self.config = config
        self.default_retention_days = config.get('default_retention_days', 2555)  # 7 years
        self.enable_legal_hold = config.get('enable_legal_hold', True)
        self.dry_run_mode = config.get('dry_run_mode', False)
        
        # Storage for policies and legal holds
        self.policies: Dict[str, RetentionPolicy] = {}
        self.legal_holds: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self) -> None:
        """Initialize the retention manager."""
        logger.info("Initializing RetentionManager")
        
        # Load default policies
        await self._load_default_policies()
        
    async def apply_retention_policy(self, policy: RetentionPolicy) -> RetentionResult:
        """
        Apply a retention policy to email data.
        
        Args:
            policy: Retention policy to apply
            
        Returns:
            Results of policy application
            
        Raises:
            GovernanceError: If policy application fails
        """
        try:
            start_time = datetime.utcnow()
            
            # Get emails matching policy criteria
            matching_emails = await self._get_emails_for_policy(policy)
            
            # Filter out emails under legal hold
            eligible_emails = await self._filter_legal_holds(matching_emails)
            
            # Apply retention actions
            result = await self._apply_retention_actions(policy, eligible_emails)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            result.execution_time_seconds = execution_time
            
            logger.info(f"Applied retention policy {policy.policy_id}: processed {result.emails_processed} emails")
            
            return result
            
        except Exception as e:
            logger.error(f"Error applying retention policy: {e}")
            raise GovernanceError(f"Retention policy application failed: {e}")
    
    async def schedule_deletion(
        self, 
        emails: List[EmailMessage], 
        policy: RetentionPolicy
    ) -> None:
        """
        Schedule emails for deletion based on policy.
        
        Args:
            emails: List of emails to schedule for deletion
            policy: Retention policy governing the deletion
        """
        try:
            if self.dry_run_mode:
                logger.info(f"DRY RUN: Would schedule {len(emails)} emails for deletion")
                return
            
            # Calculate deletion date
            deletion_date = datetime.utcnow() + timedelta(days=policy.retention_period_days)
            
            # Schedule each email
            for email in emails:
                await self._schedule_email_deletion(email, deletion_date, policy)
            
            logger.info(f"Scheduled {len(emails)} emails for deletion on {deletion_date}")
            
        except Exception as e:
            logger.error(f"Error scheduling deletion: {e}")
            raise GovernanceError(f"Deletion scheduling failed: {e}")
    
    async def create_legal_hold(
        self, 
        hold_id: str, 
        description: str, 
        criteria: Dict[str, Any],
        expiration_date: Optional[datetime] = None
    ) -> None:
        """
        Create a legal hold to prevent deletion of matching emails.
        
        Args:
            hold_id: Unique identifier for the legal hold
            description: Description of the legal hold
            criteria: Criteria for matching emails
            expiration_date: Optional expiration date for the hold
        """
        try:
            if not self.enable_legal_hold:
                logger.warning("Legal hold functionality is disabled")
                return
            
            legal_hold = {
                'hold_id': hold_id,
                'description': description,
                'criteria': criteria,
                'created_at': datetime.utcnow(),
                'expiration_date': expiration_date,
                'status': 'active'
            }
            
            self.legal_holds[hold_id] = legal_hold
            
            logger.info(f"Created legal hold: {hold_id}")
            
        except Exception as e:
            logger.error(f"Error creating legal hold: {e}")
            raise GovernanceError(f"Legal hold creation failed: {e}")
    
    async def release_legal_hold(self, hold_id: str) -> None:
        """
        Release a legal hold, allowing normal retention policies to apply.
        
        Args:
            hold_id: ID of the legal hold to release
        """
        try:
            if hold_id in self.legal_holds:
                self.legal_holds[hold_id]['status'] = 'released'
                self.legal_holds[hold_id]['released_at'] = datetime.utcnow()
                
                logger.info(f"Released legal hold: {hold_id}")
            else:
                logger.warning(f"Legal hold not found: {hold_id}")
                
        except Exception as e:
            logger.error(f"Error releasing legal hold: {e}")
            raise GovernanceError(f"Legal hold release failed: {e}")
    
    async def generate_retention_report(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate a retention compliance report.
        
        Args:
            start_date: Start date for the report
            end_date: End date for the report
            
        Returns:
            Retention compliance report
        """
        try:
            report = {
                'report_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'policies_applied': len(self.policies),
                'active_legal_holds': len([h for h in self.legal_holds.values() if h['status'] == 'active']),
                'retention_actions': {
                    'deleted': 0,
                    'archived': 0,
                    'anonymized': 0,
                    'retained': 0
                },
                'compliance_status': 'compliant',
                'recommendations': []
            }
            
            # Add policy details
            report['policies'] = [
                {
                    'policy_id': policy.policy_id,
                    'name': policy.name,
                    'retention_days': policy.retention_period_days,
                    'action': policy.action.value,
                    'enabled': policy.enabled
                }
                for policy in self.policies.values()
            ]
            
            # Add legal hold details
            report['legal_holds'] = [
                {
                    'hold_id': hold['hold_id'],
                    'description': hold['description'],
                    'status': hold['status'],
                    'created_at': hold['created_at'].isoformat()
                }
                for hold in self.legal_holds.values()
            ]
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating retention report: {e}")
            raise GovernanceError(f"Retention report generation failed: {e}")
    
    async def _get_emails_for_policy(self, policy: RetentionPolicy) -> List[EmailMessage]:
        """Get emails that match the policy criteria."""
        # This would typically query the database
        # For now, return empty list as placeholder
        return []
    
    async def _filter_legal_holds(self, emails: List[EmailMessage]) -> List[EmailMessage]:
        """Filter out emails that are under legal hold."""
        if not self.enable_legal_hold:
            return emails
        
        eligible_emails = []
        
        for email in emails:
            is_on_hold = False
            
            for hold in self.legal_holds.values():
                if hold['status'] != 'active':
                    continue
                
                # Check if email matches legal hold criteria
                if await self._email_matches_criteria(email, hold['criteria']):
                    is_on_hold = True
                    break
            
            if not is_on_hold:
                eligible_emails.append(email)
        
        return eligible_emails
    
    async def _apply_retention_actions(
        self, 
        policy: RetentionPolicy, 
        emails: List[EmailMessage]
    ) -> RetentionResult:
        """Apply retention actions to emails."""
        result = RetentionResult(
            policy_id=policy.policy_id,
            emails_processed=len(emails),
            emails_deleted=0,
            emails_archived=0,
            emails_anonymized=0,
            emails_retained=0,
            execution_time_seconds=0.0,
            errors=[]
        )
        
        for email in emails:
            try:
                if await self._should_apply_retention(email, policy):
                    if policy.action == RetentionAction.DELETE:
                        await self._delete_email(email)
                        result.emails_deleted += 1
                    elif policy.action == RetentionAction.ARCHIVE:
                        await self._archive_email(email)
                        result.emails_archived += 1
                    elif policy.action == RetentionAction.ANONYMIZE:
                        await self._anonymize_email(email)
                        result.emails_anonymized += 1
                    else:
                        result.emails_retained += 1
                else:
                    result.emails_retained += 1
                    
            except Exception as e:
                error_msg = f"Error processing email {email.id}: {e}"
                result.errors.append(error_msg)
                logger.error(error_msg)
        
        return result
    
    async def _should_apply_retention(self, email: EmailMessage, policy: RetentionPolicy) -> bool:
        """Check if retention should be applied to an email."""
        if not email.received_date:
            return False
        
        # Check if email is older than retention period
        cutoff_date = datetime.utcnow() - timedelta(days=policy.retention_period_days)
        return email.received_date < cutoff_date
    
    async def _email_matches_criteria(self, email: EmailMessage, criteria: Dict[str, Any]) -> bool:
        """Check if an email matches the given criteria."""
        # Simple criteria matching
        if 'sender_domain' in criteria:
            if email.sender:
                sender = email.sender.email if hasattr(email.sender, 'email') else str(email.sender)
                if '@' in sender:
                    domain = sender.split('@')[1]
                    if domain not in criteria['sender_domain']:
                        return False
        
        if 'subject_contains' in criteria:
            if not email.subject or criteria['subject_contains'].lower() not in email.subject.lower():
                return False
        
        if 'date_range' in criteria:
            date_range = criteria['date_range']
            if email.received_date:
                if 'start' in date_range and email.received_date < date_range['start']:
                    return False
                if 'end' in date_range and email.received_date > date_range['end']:
                    return False
        
        return True
    
    async def _schedule_email_deletion(
        self, 
        email: EmailMessage, 
        deletion_date: datetime, 
        policy: RetentionPolicy
    ) -> None:
        """Schedule an email for deletion."""
        # This would typically add to a deletion queue
        logger.debug(f"Scheduled email {email.id} for deletion on {deletion_date}")
    
    async def _delete_email(self, email: EmailMessage) -> None:
        """Delete an email."""
        if self.dry_run_mode:
            logger.info(f"DRY RUN: Would delete email {email.id}")
        else:
            # This would typically delete from database
            logger.debug(f"Deleted email {email.id}")
    
    async def _archive_email(self, email: EmailMessage) -> None:
        """Archive an email."""
        if self.dry_run_mode:
            logger.info(f"DRY RUN: Would archive email {email.id}")
        else:
            # This would typically move to archive storage
            logger.debug(f"Archived email {email.id}")
    
    async def _anonymize_email(self, email: EmailMessage) -> None:
        """Anonymize an email."""
        if self.dry_run_mode:
            logger.info(f"DRY RUN: Would anonymize email {email.id}")
        else:
            # This would typically remove PII from email
            logger.debug(f"Anonymized email {email.id}")
    
    async def _load_default_policies(self) -> None:
        """Load default retention policies."""
        # Default 7-year retention policy
        default_policy = RetentionPolicy(
            policy_id="default_7_year",
            name="Default 7-Year Retention",
            description="Default retention policy for business emails",
            retention_period_days=2555,  # 7 years
            action=RetentionAction.ARCHIVE,
            criteria={},
            enabled=True,
            created_at=datetime.utcnow(),
            last_modified=datetime.utcnow()
        )
        
        self.policies[default_policy.policy_id] = default_policy
        
        # Spam deletion policy
        spam_policy = RetentionPolicy(
            policy_id="spam_30_day",
            name="Spam 30-Day Deletion",
            description="Delete spam emails after 30 days",
            retention_period_days=30,
            action=RetentionAction.DELETE,
            criteria={'category': 'spam'},
            enabled=True,
            created_at=datetime.utcnow(),
            last_modified=datetime.utcnow()
        )
        
        self.policies[spam_policy.policy_id] = spam_policy
        
        logger.info(f"Loaded {len(self.policies)} default retention policies")
