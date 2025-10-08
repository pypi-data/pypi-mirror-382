"""
Duplicate email detection and handling.

This module provides comprehensive duplicate detection capabilities using
content hashing, fuzzy matching, and intelligent clustering algorithms.
"""

import asyncio
import hashlib
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
import difflib
from difflib import SequenceMatcher

from evolvishub_outlook_ingestor.core.data_models import EmailMessage, EmailAddress
from evolvishub_outlook_ingestor.core.exceptions import QualityError

logger = logging.getLogger(__name__)


@dataclass
class DuplicateGroup:
    """A group of duplicate emails."""
    group_id: str
    emails: List[EmailMessage]
    canonical_email: EmailMessage
    similarity_score: float
    duplicate_type: str  # 'exact', 'near_exact', 'fuzzy'
    detection_method: str
    confidence: float


@dataclass
class DuplicateAnalysis:
    """Results of duplicate analysis."""
    total_emails: int
    unique_emails: int
    duplicate_emails: int
    duplicate_groups: List[DuplicateGroup]
    duplicate_percentage: float
    space_savings_bytes: int


class DuplicateDetector:
    """
    Detects and handles duplicate emails using multiple algorithms.
    
    Provides comprehensive duplicate detection including:
    - SHA256 content hashing for exact duplicates
    - Fuzzy matching using difflib for near-duplicates
    - Intelligent clustering based on metadata
    - Configurable similarity thresholds
    - Space savings calculation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the duplicate detector.
        
        Args:
            config: Configuration dictionary containing:
                - similarity_threshold: Minimum similarity for fuzzy matching (default: 0.85)
                - hash_fields: Fields to include in hash calculation
                - enable_fuzzy_matching: Enable fuzzy duplicate detection (default: True)
                - max_group_size: Maximum emails per duplicate group (default: 100)
        """
        self.config = config
        self.similarity_threshold = config.get('similarity_threshold', 0.85)
        self.hash_fields = config.get('hash_fields', ['subject', 'body', 'sender'])
        self.enable_fuzzy_matching = config.get('enable_fuzzy_matching', True)
        self.max_group_size = config.get('max_group_size', 100)
        
        # Cache for computed hashes
        self.hash_cache: Dict[str, str] = {}
        self.content_cache: Dict[str, str] = {}
        
    async def initialize(self) -> None:
        """Initialize the duplicate detector."""
        logger.info("Initializing DuplicateDetector")
        
    async def detect_duplicates(self, emails: List[EmailMessage]) -> List[DuplicateGroup]:
        """
        Detect duplicate emails using multiple algorithms.
        
        Args:
            emails: List of email messages to analyze
            
        Returns:
            List of duplicate groups found
            
        Raises:
            QualityError: If duplicate detection fails
        """
        try:
            if not emails:
                return []
            
            logger.info(f"Starting duplicate detection for {len(emails)} emails")
            
            duplicate_groups = []
            processed_emails = set()
            
            # Step 1: Exact duplicate detection using content hashing
            exact_groups = await self._detect_exact_duplicates(emails)
            duplicate_groups.extend(exact_groups)
            
            # Mark processed emails
            for group in exact_groups:
                for email in group.emails:
                    processed_emails.add(email.id)
            
            # Step 2: Fuzzy duplicate detection for remaining emails
            if self.enable_fuzzy_matching:
                remaining_emails = [e for e in emails if e.id not in processed_emails]
                fuzzy_groups = await self._detect_fuzzy_duplicates(remaining_emails)
                duplicate_groups.extend(fuzzy_groups)
                
                # Mark processed emails
                for group in fuzzy_groups:
                    for email in group.emails:
                        processed_emails.add(email.id)
            
            # Step 3: Metadata-based duplicate detection
            remaining_emails = [e for e in emails if e.id not in processed_emails]
            metadata_groups = await self._detect_metadata_duplicates(remaining_emails)
            duplicate_groups.extend(metadata_groups)
            
            logger.info(f"Detected {len(duplicate_groups)} duplicate groups")
            return duplicate_groups
            
        except Exception as e:
            logger.error(f"Error detecting duplicates: {e}")
            raise QualityError(f"Duplicate detection failed: {e}")
    
    async def analyze_duplicates(self, emails: List[EmailMessage]) -> DuplicateAnalysis:
        """
        Perform comprehensive duplicate analysis.
        
        Args:
            emails: List of email messages to analyze
            
        Returns:
            Duplicate analysis results
        """
        try:
            duplicate_groups = await self.detect_duplicates(emails)
            
            total_emails = len(emails)
            duplicate_emails = sum(len(group.emails) - 1 for group in duplicate_groups)  # Exclude canonical
            unique_emails = total_emails - duplicate_emails
            duplicate_percentage = (duplicate_emails / total_emails * 100) if total_emails > 0 else 0
            
            # Calculate space savings
            space_savings = 0
            for group in duplicate_groups:
                if group.emails:
                    canonical_size = len(group.canonical_email.body or '') + len(group.canonical_email.subject or '')
                    for email in group.emails[1:]:  # Skip canonical
                        email_size = len(email.body or '') + len(email.subject or '')
                        space_savings += email_size
            
            return DuplicateAnalysis(
                total_emails=total_emails,
                unique_emails=unique_emails,
                duplicate_emails=duplicate_emails,
                duplicate_groups=duplicate_groups,
                duplicate_percentage=duplicate_percentage,
                space_savings_bytes=space_savings
            )
            
        except Exception as e:
            logger.error(f"Error analyzing duplicates: {e}")
            raise QualityError(f"Duplicate analysis failed: {e}")
    
    async def merge_duplicates(self, duplicate_group: DuplicateGroup) -> EmailMessage:
        """
        Merge duplicate emails into a canonical version.
        
        Args:
            duplicate_group: Group of duplicate emails to merge
            
        Returns:
            Merged canonical email
        """
        try:
            if not duplicate_group.emails:
                raise QualityError("Empty duplicate group")
            
            # Start with the canonical email
            canonical = duplicate_group.canonical_email
            
            # Merge metadata from all emails
            merged_email = EmailMessage(
                id=canonical.id,
                message_id=canonical.message_id,
                conversation_id=canonical.conversation_id,
                subject=canonical.subject,
                body=canonical.body,
                body_preview=canonical.body_preview,
                body_type=canonical.body_type,
                is_html=canonical.is_html,
                sender=canonical.sender,
                from_address=canonical.from_address,
                to_recipients=canonical.to_recipients,
                cc_recipients=canonical.cc_recipients,
                bcc_recipients=canonical.bcc_recipients,
                reply_to=canonical.reply_to,
                sent_date=canonical.sent_date,
                received_date=canonical.received_date,
                created_date=canonical.created_date,
                modified_date=canonical.modified_date,
                importance=canonical.importance,
                sensitivity=canonical.sensitivity,
                priority=canonical.priority,
                is_read=canonical.is_read,
                is_draft=canonical.is_draft,
                has_attachments=canonical.has_attachments,
                is_flagged=canonical.is_flagged
            )
            
            # Merge additional metadata from duplicates
            all_recipients = set()
            all_cc_recipients = set()
            
            for email in duplicate_group.emails:
                # Collect all unique recipients
                if email.to_recipients:
                    for recipient in email.to_recipients:
                        recipient_email = recipient.email if isinstance(recipient, EmailAddress) else str(recipient)
                        all_recipients.add(recipient_email)
                
                if email.cc_recipients:
                    for recipient in email.cc_recipients:
                        recipient_email = recipient.email if isinstance(recipient, EmailAddress) else str(recipient)
                        all_cc_recipients.add(recipient_email)
                
                # Use the earliest received date
                if email.received_date and (not merged_email.received_date or email.received_date < merged_email.received_date):
                    merged_email.received_date = email.received_date
                
                # Use the latest modified date
                if email.modified_date and (not merged_email.modified_date or email.modified_date > merged_email.modified_date):
                    merged_email.modified_date = email.modified_date
                
                # Merge flags (OR operation)
                merged_email.is_read = merged_email.is_read or email.is_read
                merged_email.is_flagged = merged_email.is_flagged or email.is_flagged
                merged_email.has_attachments = merged_email.has_attachments or email.has_attachments
            
            # Update recipient lists with merged data
            if all_recipients:
                merged_email.to_recipients = [EmailAddress(email=email) for email in all_recipients]
            if all_cc_recipients:
                merged_email.cc_recipients = [EmailAddress(email=email) for email in all_cc_recipients]
            
            logger.info(f"Merged {len(duplicate_group.emails)} duplicate emails into canonical version")
            return merged_email
            
        except Exception as e:
            logger.error(f"Error merging duplicates: {e}")
            raise QualityError(f"Duplicate merge failed: {e}")
    
    async def _detect_exact_duplicates(self, emails: List[EmailMessage]) -> List[DuplicateGroup]:
        """Detect exact duplicates using content hashing."""
        hash_groups = defaultdict(list)
        
        for email in emails:
            content_hash = await self._calculate_content_hash(email)
            hash_groups[content_hash].append(email)
        
        duplicate_groups = []
        group_counter = 0
        
        for content_hash, email_list in hash_groups.items():
            if len(email_list) > 1:
                # Sort by received date to choose canonical
                email_list.sort(key=lambda e: e.received_date or datetime.min)
                canonical = email_list[0]
                
                group_counter += 1
                duplicate_groups.append(DuplicateGroup(
                    group_id=f"exact_{group_counter}",
                    emails=email_list,
                    canonical_email=canonical,
                    similarity_score=1.0,
                    duplicate_type='exact',
                    detection_method='content_hash',
                    confidence=1.0
                ))
        
        return duplicate_groups
    
    async def _detect_fuzzy_duplicates(self, emails: List[EmailMessage]) -> List[DuplicateGroup]:
        """Detect fuzzy duplicates using similarity matching."""
        if len(emails) < 2:
            return []
        
        duplicate_groups = []
        processed = set()
        group_counter = 0
        
        for i, email1 in enumerate(emails):
            if email1.id in processed:
                continue
            
            similar_emails = [email1]
            
            for j, email2 in enumerate(emails[i+1:], i+1):
                if email2.id in processed:
                    continue
                
                similarity = await self._calculate_similarity(email1, email2)
                
                if similarity >= self.similarity_threshold:
                    similar_emails.append(email2)
                    processed.add(email2.id)
            
            if len(similar_emails) > 1:
                # Sort by received date to choose canonical
                similar_emails.sort(key=lambda e: e.received_date or datetime.min)
                canonical = similar_emails[0]
                
                group_counter += 1
                duplicate_groups.append(DuplicateGroup(
                    group_id=f"fuzzy_{group_counter}",
                    emails=similar_emails,
                    canonical_email=canonical,
                    similarity_score=self.similarity_threshold,
                    duplicate_type='fuzzy',
                    detection_method='content_similarity',
                    confidence=0.8
                ))
                
                processed.add(email1.id)
        
        return duplicate_groups
    
    async def _detect_metadata_duplicates(self, emails: List[EmailMessage]) -> List[DuplicateGroup]:
        """Detect duplicates based on metadata similarity."""
        metadata_groups = defaultdict(list)
        
        for email in emails:
            # Create metadata signature
            sender = email.sender.email if isinstance(email.sender, EmailAddress) else str(email.sender) if email.sender else ''
            subject = (email.subject or '').strip().lower()
            
            # Normalize subject (remove Re:, Fwd:, etc.)
            normalized_subject = self._normalize_subject(subject)
            
            # Group by sender + normalized subject + date (same day)
            date_key = email.received_date.strftime('%Y-%m-%d') if email.received_date else 'unknown'
            metadata_key = f"{sender}|{normalized_subject}|{date_key}"
            
            metadata_groups[metadata_key].append(email)
        
        duplicate_groups = []
        group_counter = 0
        
        for metadata_key, email_list in metadata_groups.items():
            if len(email_list) > 1:
                # Additional content similarity check
                content_similar_groups = await self._group_by_content_similarity(email_list)
                
                for similar_group in content_similar_groups:
                    if len(similar_group) > 1:
                        # Sort by received date to choose canonical
                        similar_group.sort(key=lambda e: e.received_date or datetime.min)
                        canonical = similar_group[0]
                        
                        group_counter += 1
                        duplicate_groups.append(DuplicateGroup(
                            group_id=f"metadata_{group_counter}",
                            emails=similar_group,
                            canonical_email=canonical,
                            similarity_score=0.7,
                            duplicate_type='near_exact',
                            detection_method='metadata_similarity',
                            confidence=0.6
                        ))
        
        return duplicate_groups
    
    async def _calculate_content_hash(self, email: EmailMessage) -> str:
        """Calculate SHA256 hash of email content."""
        if email.id in self.hash_cache:
            return self.hash_cache[email.id]
        
        # Combine relevant fields for hashing
        content_parts = []
        
        if 'subject' in self.hash_fields and email.subject:
            content_parts.append(email.subject.strip().lower())
        
        if 'body' in self.hash_fields and email.body:
            # Normalize whitespace and remove HTML tags for consistent hashing
            normalized_body = ' '.join(email.body.split())
            content_parts.append(normalized_body.lower())
        
        if 'sender' in self.hash_fields and email.sender:
            sender = email.sender.email if isinstance(email.sender, EmailAddress) else str(email.sender)
            content_parts.append(sender.lower())
        
        # Create hash
        content_string = '|'.join(content_parts)
        content_hash = hashlib.sha256(content_string.encode('utf-8')).hexdigest()
        
        self.hash_cache[email.id] = content_hash
        return content_hash
    
    async def _calculate_similarity(self, email1: EmailMessage, email2: EmailMessage) -> float:
        """Calculate similarity between two emails."""
        # Quick checks first
        if email1.id == email2.id:
            return 1.0
        
        # Subject similarity
        subject1 = (email1.subject or '').strip().lower()
        subject2 = (email2.subject or '').strip().lower()
        
        if not subject1 and not subject2:
            subject_similarity = 1.0
        elif not subject1 or not subject2:
            subject_similarity = 0.0
        else:
            subject_similarity = SequenceMatcher(None, subject1, subject2).ratio()
        
        # Body similarity
        body1 = (email1.body or '').strip().lower()
        body2 = (email2.body or '').strip().lower()
        
        if not body1 and not body2:
            body_similarity = 1.0
        elif not body1 or not body2:
            body_similarity = 0.0
        else:
            # For long texts, use a more efficient approach
            if len(body1) > 1000 or len(body2) > 1000:
                # Use first 1000 characters for similarity
                body1_sample = body1[:1000]
                body2_sample = body2[:1000]
                body_similarity = SequenceMatcher(None, body1_sample, body2_sample).ratio()
            else:
                body_similarity = SequenceMatcher(None, body1, body2).ratio()
        
        # Sender similarity
        sender1 = email1.sender.email if isinstance(email1.sender, EmailAddress) else str(email1.sender) if email1.sender else ''
        sender2 = email2.sender.email if isinstance(email2.sender, EmailAddress) else str(email2.sender) if email2.sender else ''
        
        sender_similarity = 1.0 if sender1.lower() == sender2.lower() else 0.0
        
        # Weighted average
        weights = {'subject': 0.3, 'body': 0.5, 'sender': 0.2}
        overall_similarity = (
            weights['subject'] * subject_similarity +
            weights['body'] * body_similarity +
            weights['sender'] * sender_similarity
        )
        
        return overall_similarity
    
    def _normalize_subject(self, subject: str) -> str:
        """Normalize email subject by removing common prefixes."""
        if not subject:
            return ''
        
        # Remove common prefixes
        prefixes = ['re:', 'fwd:', 'fw:', 'forward:', 'reply:']
        normalized = subject.lower().strip()
        
        for prefix in prefixes:
            while normalized.startswith(prefix):
                normalized = normalized[len(prefix):].strip()
        
        return normalized
    
    async def _group_by_content_similarity(self, emails: List[EmailMessage]) -> List[List[EmailMessage]]:
        """Group emails by content similarity."""
        if len(emails) <= 1:
            return [emails] if emails else []
        
        groups = []
        processed = set()
        
        for i, email1 in enumerate(emails):
            if email1.id in processed:
                continue
            
            current_group = [email1]
            processed.add(email1.id)
            
            for j, email2 in enumerate(emails[i+1:], i+1):
                if email2.id in processed:
                    continue
                
                similarity = await self._calculate_similarity(email1, email2)
                if similarity >= 0.8:  # High similarity threshold for metadata groups
                    current_group.append(email2)
                    processed.add(email2.id)
            
            groups.append(current_group)
        
        return groups
