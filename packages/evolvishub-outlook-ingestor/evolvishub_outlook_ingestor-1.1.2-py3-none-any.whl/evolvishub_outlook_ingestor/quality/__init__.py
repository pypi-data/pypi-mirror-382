"""
Data quality validation and assessment framework.

This module provides comprehensive data quality validation capabilities
for email data, ensuring reliability and consistency across the platform.
"""

from .data_quality_validator import DataQualityValidator
from .quality_rules import QualityRuleEngine
from .quality_metrics import QualityMetricsCollector

__all__ = [
    'DataQualityValidator',
    'QualityRuleEngine',
    'QualityMetricsCollector'
]
