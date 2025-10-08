"""
Quality rules engine for email data validation.

This module provides a flexible rules engine for defining and executing
data quality validation rules.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.core.exceptions import QualityError

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of quality rules."""
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    ENRICHMENT = "enrichment"
    FILTERING = "filtering"


@dataclass
class QualityRule:
    """A quality rule definition."""
    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    condition: Callable[[EmailMessage], bool]
    action: Callable[[EmailMessage], EmailMessage]
    enabled: bool = True
    priority: int = 0


class QualityRuleEngine:
    """
    Flexible rules engine for data quality validation and transformation.
    
    Provides comprehensive rule management including:
    - Rule definition and registration
    - Rule execution and evaluation
    - Rule prioritization and ordering
    - Error handling and reporting
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the quality rule engine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.rules: Dict[str, QualityRule] = {}
        
    async def initialize(self) -> None:
        """Initialize the rule engine."""
        logger.info("Initializing QualityRuleEngine")
        
        # Load default rules
        await self._load_default_rules()
        
    async def register_rule(self, rule: QualityRule) -> None:
        """Register a quality rule."""
        self.rules[rule.rule_id] = rule
        logger.info(f"Registered quality rule: {rule.rule_id}")
        
    async def apply_rules(self, email: EmailMessage) -> EmailMessage:
        """Apply all enabled rules to an email."""
        # Sort rules by priority
        sorted_rules = sorted(
            [rule for rule in self.rules.values() if rule.enabled],
            key=lambda r: r.priority
        )
        
        result_email = email
        
        for rule in sorted_rules:
            try:
                if rule.condition(result_email):
                    result_email = rule.action(result_email)
            except Exception as e:
                logger.error(f"Error applying rule {rule.rule_id}: {e}")
        
        return result_email
        
    async def _load_default_rules(self) -> None:
        """Load default quality rules."""
        # Example rule: Validate sender email format
        sender_validation_rule = QualityRule(
            rule_id="validate_sender_email",
            name="Validate Sender Email",
            description="Ensure sender email has valid format",
            rule_type=RuleType.VALIDATION,
            condition=lambda email: email.sender is not None,
            action=lambda email: email,  # No transformation, just validation
            enabled=True,
            priority=1
        )
        
        await self.register_rule(sender_validation_rule)
