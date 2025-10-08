"""
Advanced analytics and insights engine for email data.

This module provides comprehensive analytics capabilities including
communication pattern analysis, trend detection, and business insights.
"""

from .analytics_engine import AnalyticsEngine
from .communication_analyzer import CommunicationAnalyzer
from .trend_detector import TrendDetector
from .insights_generator import InsightsGenerator

__all__ = [
    'AnalyticsEngine',
    'CommunicationAnalyzer',
    'TrendDetector',
    'InsightsGenerator'
]
