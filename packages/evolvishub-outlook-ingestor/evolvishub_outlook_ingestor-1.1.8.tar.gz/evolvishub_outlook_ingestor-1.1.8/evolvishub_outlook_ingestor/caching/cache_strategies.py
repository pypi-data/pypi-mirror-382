"""
Cache strategies and implementations.

This module provides various caching strategies including LRU, LFU, TTL,
and custom strategies for different use cases.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
from collections import OrderedDict
import threading

from evolvishub_outlook_ingestor.core.exceptions import CacheError

logger = logging.getLogger(__name__)


class CacheStrategy(ABC):
    """Abstract base class for cache strategies."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache entries."""
        pass


@dataclass
class CacheEntry:
    """A cache entry with metadata."""
    value: Any
    created_at: float
    last_accessed: float
    access_count: int
    ttl: Optional[int] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl


class LRUCache(CacheStrategy):
    """Least Recently Used cache strategy."""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of entries
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired:
                del self.cache[key]
                return None
            
            # Update access info
            entry.last_accessed = time.time()
            entry.access_count += 1
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        with self.lock:
            current_time = time.time()
            
            entry = CacheEntry(
                value=value,
                created_at=current_time,
                last_accessed=current_time,
                access_count=0,
                ttl=ttl
            )
            
            # Remove existing entry if present
            if key in self.cache:
                del self.cache[key]
            
            # Add new entry
            self.cache[key] = entry
            
            # Evict oldest entries if over capacity
            while len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()


class LFUCache(CacheStrategy):
    """Least Frequently Used cache strategy."""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize LFU cache.
        
        Args:
            max_size: Maximum number of entries
        """
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = threading.RLock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired:
                del self.cache[key]
                return None
            
            # Update access info
            entry.last_accessed = time.time()
            entry.access_count += 1
            
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        with self.lock:
            current_time = time.time()
            
            entry = CacheEntry(
                value=value,
                created_at=current_time,
                last_accessed=current_time,
                access_count=0,
                ttl=ttl
            )
            
            # Remove existing entry if present
            if key in self.cache:
                del self.cache[key]
            
            # Add new entry
            self.cache[key] = entry
            
            # Evict least frequently used entries if over capacity
            while len(self.cache) > self.max_size:
                lfu_key = min(self.cache.keys(), key=lambda k: self.cache[k].access_count)
                del self.cache[lfu_key]
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()


class TTLCache(CacheStrategy):
    """Time-To-Live cache strategy."""
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize TTL cache.
        
        Args:
            default_ttl: Default TTL in seconds
        """
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = threading.RLock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired:
                del self.cache[key]
                return None
            
            # Update access info
            entry.last_accessed = time.time()
            entry.access_count += 1
            
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        with self.lock:
            current_time = time.time()
            effective_ttl = ttl if ttl is not None else self.default_ttl
            
            entry = CacheEntry(
                value=value,
                created_at=current_time,
                last_accessed=current_time,
                access_count=0,
                ttl=effective_ttl
            )
            
            self.cache[key] = entry
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
    
    async def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)


class CacheStrategyFactory:
    """Factory for creating cache strategies."""
    
    @staticmethod
    def create_strategy(strategy_type: str, **kwargs) -> CacheStrategy:
        """
        Create a cache strategy.
        
        Args:
            strategy_type: Type of strategy ('lru', 'lfu', 'ttl')
            **kwargs: Strategy-specific parameters
            
        Returns:
            Cache strategy instance
        """
        if strategy_type.lower() == 'lru':
            return LRUCache(max_size=kwargs.get('max_size', 1000))
        elif strategy_type.lower() == 'lfu':
            return LFUCache(max_size=kwargs.get('max_size', 1000))
        elif strategy_type.lower() == 'ttl':
            return TTLCache(default_ttl=kwargs.get('default_ttl', 3600))
        else:
            raise CacheError(f"Unknown cache strategy: {strategy_type}")
    
    @staticmethod
    def get_available_strategies() -> List[str]:
        """Get list of available cache strategies."""
        return ['lru', 'lfu', 'ttl']
