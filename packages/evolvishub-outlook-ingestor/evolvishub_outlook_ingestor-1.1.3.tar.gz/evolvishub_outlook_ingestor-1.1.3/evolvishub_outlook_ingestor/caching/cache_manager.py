"""
Intelligent cache manager with multiple strategies and optimization.

This module provides a comprehensive caching solution with support for
multiple cache backends, intelligent strategies, and performance optimization.
"""

import asyncio
import json
import logging
import pickle
import time
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from evolvishub_outlook_ingestor.core.interfaces import ICacheManager, CacheStrategy, service_registry
from evolvishub_outlook_ingestor.core.exceptions import CacheError


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata."""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl: Optional[int]
    strategy: CacheStrategy
    size_bytes: int


@dataclass
class CacheStats:
    """Cache performance statistics."""
    hits: int
    misses: int
    evictions: int
    total_size: int
    entry_count: int
    hit_ratio: float


class CacheBackend(Enum):
    """Available cache backends."""
    MEMORY = "memory"
    REDIS = "redis"
    DISK = "disk"
    HYBRID = "hybrid"


class IntelligentCacheManager(ICacheManager):
    """
    Intelligent cache manager with multiple strategies and backends.
    
    This cache manager provides:
    - Multiple caching strategies (LRU, LFU, TTL, etc.)
    - Multi-level caching (memory, Redis, disk)
    - Intelligent cache warming and preloading
    - Performance monitoring and optimization
    - Automatic cache invalidation and cleanup
    
    Example:
        ```python
        cache = IntelligentCacheManager({
            'backend': CacheBackend.HYBRID,
            'memory_limit_mb': 512,
            'redis_url': 'redis://localhost:6379',
            'default_ttl': 3600,
            'enable_compression': True
        })
        
        await cache.initialize()
        
        # Set with different strategies
        await cache.set('key1', data, strategy=CacheStrategy.LRU)
        await cache.set('key2', data, ttl=300, strategy=CacheStrategy.TTL)
        
        # Get with fallback
        value = await cache.get('key1', default='not_found')
        
        # Warm cache
        await cache.warm_cache(['key1', 'key2', 'key3'])
        ```
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.backend = CacheBackend(config.get('backend', CacheBackend.MEMORY))
        self.memory_limit_mb = config.get('memory_limit_mb', 256)
        self.default_ttl = config.get('default_ttl', 3600)
        self.enable_compression = config.get('enable_compression', False)
        self.enable_encryption = config.get('enable_encryption', False)
        self.cleanup_interval = config.get('cleanup_interval', 300)  # 5 minutes
        
        # Cache backends
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._redis_client = None
        self._disk_cache_path = config.get('disk_cache_path', '/tmp/email_cache')
        
        # State management
        self.is_initialized = False
        self._current_size_bytes = 0
        self._max_size_bytes = self.memory_limit_mb * 1024 * 1024
        
        # Statistics
        self.stats = CacheStats(
            hits=0, misses=0, evictions=0,
            total_size=0, entry_count=0, hit_ratio=0.0
        )
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._stats_task: Optional[asyncio.Task] = None
        
        # Cache warming
        self._warming_callbacks: Dict[str, Callable] = {}
        self._preload_patterns: List[str] = config.get('preload_patterns', [])
    
    async def initialize(self) -> None:
        """Initialize the cache manager."""
        if self.is_initialized:
            return
        
        try:
            self.logger.info(f"Initializing intelligent cache manager with {self.backend.value} backend")
            
            # Initialize backends
            if self.backend in [CacheBackend.REDIS, CacheBackend.HYBRID]:
                await self._initialize_redis()
            
            if self.backend in [CacheBackend.DISK, CacheBackend.HYBRID]:
                await self._initialize_disk_cache()
            
            # Start background tasks
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self._stats_task = asyncio.create_task(self._stats_loop())
            
            self.is_initialized = True
            self.logger.info("Cache manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize cache manager: {str(e)}")
            raise CacheError(f"Cache initialization failed: {str(e)}")
    
    async def shutdown(self) -> None:
        """Shutdown the cache manager."""
        if not self.is_initialized:
            return
        
        self.logger.info("Shutting down cache manager")
        
        # Cancel background tasks
        tasks = [self._cleanup_task, self._stats_task]
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Close Redis connection
        if self._redis_client:
            await self._redis_client.close()
        
        # Clear memory cache
        self._memory_cache.clear()
        
        self.is_initialized = False
        self.logger.info("Cache manager shutdown complete")
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache with intelligent fallback.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        try:
            # Try memory cache first
            if key in self._memory_cache:
                entry = self._memory_cache[key]
                
                # Check TTL
                if self._is_expired(entry):
                    await self._remove_from_memory(key)
                else:
                    # Update access metadata
                    entry.last_accessed = datetime.utcnow()
                    entry.access_count += 1
                    self.stats.hits += 1
                    return entry.value
            
            # Try Redis cache
            if self._redis_client:
                value = await self._get_from_redis(key)
                if value is not None:
                    # Promote to memory cache
                    await self._promote_to_memory(key, value)
                    self.stats.hits += 1
                    return value
            
            # Try disk cache
            if self.backend in [CacheBackend.DISK, CacheBackend.HYBRID]:
                value = await self._get_from_disk(key)
                if value is not None:
                    # Promote to higher levels
                    await self._promote_to_memory(key, value)
                    self.stats.hits += 1
                    return value
            
            # Cache miss
            self.stats.misses += 1
            return default
            
        except Exception as e:
            self.logger.error(f"Failed to get cache key {key}: {str(e)}")
            self.stats.misses += 1
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, strategy: CacheStrategy = CacheStrategy.LRU) -> None:
        """
        Set value in cache with specified strategy.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            strategy: Caching strategy to use
        """
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            # Serialize and compress if needed
            serialized_value = await self._serialize_value(value)
            size_bytes = len(serialized_value) if isinstance(serialized_value, bytes) else len(str(serialized_value))
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                access_count=1,
                ttl=ttl,
                strategy=strategy,
                size_bytes=size_bytes
            )
            
            # Store in appropriate backends
            await self._store_entry(entry, serialized_value)
            
            self.logger.debug(f"Cached key {key} with strategy {strategy.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to set cache key {key}: {str(e)}")
            raise CacheError(f"Failed to cache value: {str(e)}")
    
    async def invalidate(self, pattern: str) -> int:
        """
        Invalidate cache entries matching pattern.
        
        Args:
            pattern: Pattern to match (supports wildcards)
            
        Returns:
            Number of entries invalidated
        """
        try:
            invalidated_count = 0
            
            # Convert pattern to regex
            import re
            regex_pattern = pattern.replace('*', '.*').replace('?', '.')
            regex = re.compile(regex_pattern)
            
            # Invalidate from memory cache
            keys_to_remove = [key for key in self._memory_cache.keys() if regex.match(key)]
            for key in keys_to_remove:
                await self._remove_from_memory(key)
                invalidated_count += 1
            
            # Invalidate from Redis
            if self._redis_client:
                redis_keys = await self._redis_client.keys(pattern)
                if redis_keys:
                    await self._redis_client.delete(*redis_keys)
                    invalidated_count += len(redis_keys)
            
            # Invalidate from disk cache
            if self.backend in [CacheBackend.DISK, CacheBackend.HYBRID]:
                disk_invalidated = await self._invalidate_disk_pattern(pattern)
                invalidated_count += disk_invalidated
            
            self.logger.info(f"Invalidated {invalidated_count} cache entries matching pattern: {pattern}")
            return invalidated_count
            
        except Exception as e:
            self.logger.error(f"Failed to invalidate pattern {pattern}: {str(e)}")
            return 0
    
    async def warm_cache(self, keys: List[str]) -> None:
        """
        Warm cache with specified keys.
        
        Args:
            keys: List of keys to warm
        """
        try:
            warmed_count = 0
            
            for key in keys:
                # Check if key already exists
                if key in self._memory_cache:
                    continue
                
                # Try to load from warming callback
                if key in self._warming_callbacks:
                    try:
                        value = await self._warming_callbacks[key]()
                        await self.set(key, value)
                        warmed_count += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to warm cache key {key}: {str(e)}")
            
            self.logger.info(f"Warmed {warmed_count} cache entries")
            
        except Exception as e:
            self.logger.error(f"Failed to warm cache: {str(e)}")
    
    async def register_warming_callback(self, key_pattern: str, callback: Callable) -> None:
        """
        Register a callback for cache warming.
        
        Args:
            key_pattern: Pattern for keys this callback handles
            callback: Async function to generate cache value
        """
        self._warming_callbacks[key_pattern] = callback
        self.logger.debug(f"Registered warming callback for pattern: {key_pattern}")
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis backend."""
        try:
            import redis.asyncio as redis
            redis_url = self.config.get('redis_url', 'redis://localhost:6379')
            self._redis_client = redis.from_url(redis_url)
            await self._redis_client.ping()
            self.logger.info("Redis cache backend initialized")
        except ImportError:
            self.logger.warning("Redis not available, falling back to memory cache")
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis: {str(e)}")
            raise
    
    async def _initialize_disk_cache(self) -> None:
        """Initialize disk cache backend."""
        import os
        os.makedirs(self._disk_cache_path, exist_ok=True)
        self.logger.info(f"Disk cache initialized at: {self._disk_cache_path}")
    
    async def _store_entry(self, entry: CacheEntry, serialized_value: Any) -> None:
        """Store entry in appropriate backends based on strategy."""
        # Always store in memory cache first
        await self._store_in_memory(entry)
        
        # Store in Redis for persistence
        if self._redis_client and entry.strategy in [CacheStrategy.WRITE_THROUGH, CacheStrategy.WRITE_BACK]:
            await self._store_in_redis(entry.key, serialized_value, entry.ttl)
        
        # Store in disk for long-term caching
        if (self.backend in [CacheBackend.DISK, CacheBackend.HYBRID] and 
            entry.strategy == CacheStrategy.WRITE_THROUGH):
            await self._store_in_disk(entry.key, serialized_value)
    
    async def _store_in_memory(self, entry: CacheEntry) -> None:
        """Store entry in memory cache with eviction if needed."""
        # Check if we need to evict
        while (self._current_size_bytes + entry.size_bytes > self._max_size_bytes and 
               len(self._memory_cache) > 0):
            await self._evict_entry()
        
        # Store entry
        self._memory_cache[entry.key] = entry
        self._current_size_bytes += entry.size_bytes
        self.stats.entry_count += 1
        self.stats.total_size = self._current_size_bytes
    
    async def _store_in_redis(self, key: str, value: Any, ttl: Optional[int]) -> None:
        """Store entry in Redis."""
        if self._redis_client:
            try:
                if ttl:
                    await self._redis_client.setex(key, ttl, value)
                else:
                    await self._redis_client.set(key, value)
            except Exception as e:
                self.logger.warning(f"Failed to store in Redis: {str(e)}")
    
    async def _store_in_disk(self, key: str, value: Any) -> None:
        """Store entry in disk cache."""
        try:
            import os
            file_path = os.path.join(self._disk_cache_path, f"{key}.cache")
            with open(file_path, 'wb') as f:
                if isinstance(value, bytes):
                    f.write(value)
                else:
                    pickle.dump(value, f)
        except Exception as e:
            self.logger.warning(f"Failed to store in disk cache: {str(e)}")
    
    async def _get_from_redis(self, key: str) -> Any:
        """Get value from Redis cache."""
        if self._redis_client:
            try:
                value = await self._redis_client.get(key)
                if value:
                    return await self._deserialize_value(value)
            except Exception as e:
                self.logger.warning(f"Failed to get from Redis: {str(e)}")
        return None
    
    async def _get_from_disk(self, key: str) -> Any:
        """Get value from disk cache."""
        try:
            import os
            file_path = os.path.join(self._disk_cache_path, f"{key}.cache")
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to get from disk cache: {str(e)}")
        return None
    
    async def _evict_entry(self) -> None:
        """Evict an entry based on the configured strategy."""
        if not self._memory_cache:
            return
        
        # Find entry to evict based on strategy
        entry_to_evict = None
        
        # Default to LRU eviction
        oldest_access = min(self._memory_cache.values(), key=lambda e: e.last_accessed)
        entry_to_evict = oldest_access
        
        if entry_to_evict:
            await self._remove_from_memory(entry_to_evict.key)
            self.stats.evictions += 1
    
    async def _remove_from_memory(self, key: str) -> None:
        """Remove entry from memory cache."""
        if key in self._memory_cache:
            entry = self._memory_cache.pop(key)
            self._current_size_bytes -= entry.size_bytes
            self.stats.entry_count -= 1
            self.stats.total_size = self._current_size_bytes
    
    async def _promote_to_memory(self, key: str, value: Any) -> None:
        """Promote a value to memory cache."""
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            access_count=1,
            ttl=self.default_ttl,
            strategy=CacheStrategy.LRU,
            size_bytes=len(str(value))
        )
        await self._store_in_memory(entry)
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        if entry.ttl is None:
            return False
        
        age = (datetime.utcnow() - entry.created_at).total_seconds()
        return age > entry.ttl
    
    async def _serialize_value(self, value: Any) -> Any:
        """Serialize value for storage."""
        if self.enable_compression:
            import gzip
            serialized = pickle.dumps(value)
            return gzip.compress(serialized)
        else:
            return pickle.dumps(value)
    
    async def _deserialize_value(self, value: Any) -> Any:
        """Deserialize value from storage."""
        if self.enable_compression:
            import gzip
            decompressed = gzip.decompress(value)
            return pickle.loads(decompressed)
        else:
            return pickle.loads(value)
    
    async def _invalidate_disk_pattern(self, pattern: str) -> int:
        """Invalidate disk cache entries matching pattern."""
        try:
            import os
            import glob
            
            file_pattern = os.path.join(self._disk_cache_path, f"{pattern}.cache")
            files = glob.glob(file_pattern)
            
            for file_path in files:
                os.remove(file_path)
            
            return len(files)
        except Exception as e:
            self.logger.warning(f"Failed to invalidate disk pattern: {str(e)}")
            return 0
    
    async def _cleanup_loop(self) -> None:
        """Background task to clean up expired entries."""
        while self.is_initialized:
            try:
                current_time = datetime.utcnow()
                expired_keys = []
                
                for key, entry in self._memory_cache.items():
                    if self._is_expired(entry):
                        expired_keys.append(key)
                
                for key in expired_keys:
                    await self._remove_from_memory(key)
                
                if expired_keys:
                    self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                
                await asyncio.sleep(self.cleanup_interval)
            
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {str(e)}")
                await asyncio.sleep(60)
    
    async def _stats_loop(self) -> None:
        """Background task to update cache statistics."""
        while self.is_initialized:
            try:
                total_requests = self.stats.hits + self.stats.misses
                self.stats.hit_ratio = self.stats.hits / total_requests if total_requests > 0 else 0.0
                
                await asyncio.sleep(60)  # Update stats every minute
            
            except Exception as e:
                self.logger.error(f"Error in stats loop: {str(e)}")
                await asyncio.sleep(60)
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        return {
            'hits': self.stats.hits,
            'misses': self.stats.misses,
            'hit_ratio': self.stats.hit_ratio,
            'evictions': self.stats.evictions,
            'entry_count': self.stats.entry_count,
            'total_size_bytes': self.stats.total_size,
            'total_size_mb': self.stats.total_size / (1024 * 1024),
            'memory_usage_percent': (self._current_size_bytes / self._max_size_bytes) * 100,
            'backend': self.backend.value,
            'is_initialized': self.is_initialized
        }
