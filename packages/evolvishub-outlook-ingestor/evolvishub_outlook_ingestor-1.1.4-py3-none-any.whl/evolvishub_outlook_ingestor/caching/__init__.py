"""
Intelligent caching and performance optimization system.

This module provides advanced caching capabilities with multiple strategies,
intelligent cache warming, and performance optimization features.
"""

from .cache_manager import IntelligentCacheManager
from .cache_strategies import CacheStrategyFactory
from .cache_warmer import CacheWarmer

# Alias for backward compatibility
CacheManager = IntelligentCacheManager

__all__ = [
    'IntelligentCacheManager',
    'CacheManager',
    'CacheStrategyFactory',
    'CacheWarmer'
]
