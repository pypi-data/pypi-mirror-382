"""
Caching layer for statistical computations and expensive operations.

This module provides intelligent caching mechanisms to avoid recomputing
expensive statistical operations, improving performance for repeated analyses.
"""

import hashlib
import pickle
import json
import time
from typing import Any, Dict, Optional, Union, Callable, Tuple, List
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd
import numpy as np
from functools import wraps, lru_cache
import sqlite3
import threading
from abc import ABC, abstractmethod
import weakref
import gc

from .utils.logging import get_logger
from .exceptions import ComputationError, ConfigurationError


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata."""
    key: str
    value: Any
    timestamp: float
    access_count: int
    data_hash: str
    computation_time: float
    memory_size: int


@dataclass
class CacheStats:
    """Cache statistics for monitoring and optimization."""
    hit_rate: float
    miss_rate: float
    total_requests: int
    total_hits: int
    total_misses: int
    cache_size: int
    memory_usage_mb: float
    average_computation_time: float


class CacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        pass


class MemoryCache(CacheBackend):
    """In-memory cache with LRU eviction and TTL support."""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0
        }
        self.logger = get_logger("causallm.memory_cache", level="INFO")
    
    def _hash_key(self, key: str) -> str:
        """Generate hash for the key."""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        if self.default_ttl is None:
            return False
        return time.time() - entry.timestamp > self.default_ttl
    
    def _evict_lru(self) -> None:
        """Evict least recently used entries."""
        while len(self.cache) >= self.max_size and self.access_order:
            lru_key = self.access_order.pop(0)
            if lru_key in self.cache:
                del self.cache[lru_key]
    
    def _update_access(self, key: str) -> None:
        """Update access order for LRU."""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        with self.lock:
            self.stats['total_requests'] += 1
            hashed_key = self._hash_key(key)
            
            if hashed_key in self.cache:
                entry = self.cache[hashed_key]
                
                # Check expiration
                if self._is_expired(entry):
                    del self.cache[hashed_key]
                    if hashed_key in self.access_order:
                        self.access_order.remove(hashed_key)
                    self.stats['misses'] += 1
                    return None
                
                # Update access
                entry.access_count += 1
                self._update_access(hashed_key)
                self.stats['hits'] += 1
                
                return entry.value
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in cache."""
        with self.lock:
            hashed_key = self._hash_key(key)
            
            # Evict if necessary
            self._evict_lru()
            
            # Calculate memory size (rough estimate)
            try:
                memory_size = len(pickle.dumps(value))
            except:
                memory_size = 0
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                access_count=0,
                data_hash=self._hash_key(str(value)),
                computation_time=0.0,
                memory_size=memory_size
            )
            
            self.cache[hashed_key] = entry
            self._update_access(hashed_key)
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        with self.lock:
            hashed_key = self._hash_key(key)
            if hashed_key in self.cache:
                del self.cache[hashed_key]
                if hashed_key in self.access_order:
                    self.access_order.remove(hashed_key)
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
            self.stats = {'hits': 0, 'misses': 0, 'total_requests': 0}
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.stats['total_requests']
            if total_requests == 0:
                hit_rate = miss_rate = 0.0
            else:
                hit_rate = self.stats['hits'] / total_requests
                miss_rate = self.stats['misses'] / total_requests
            
            memory_usage = sum(entry.memory_size for entry in self.cache.values()) / (1024**2)
            avg_computation_time = np.mean([entry.computation_time for entry in self.cache.values()]) if self.cache else 0.0
            
            return CacheStats(
                hit_rate=hit_rate,
                miss_rate=miss_rate,
                total_requests=total_requests,
                total_hits=self.stats['hits'],
                total_misses=self.stats['misses'],
                cache_size=len(self.cache),
                memory_usage_mb=memory_usage,
                average_computation_time=avg_computation_time
            )


class DiskCache(CacheBackend):
    """Disk-based cache for persistent storage."""
    
    def __init__(self, cache_dir: Union[str, Path], max_size_mb: int = 1000):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_mb = max_size_mb
        self.db_path = self.cache_dir / "cache_metadata.db"
        self.logger = get_logger("causallm.disk_cache", level="INFO")
        
        # Initialize SQLite database for metadata
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize SQLite database for cache metadata."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key_hash TEXT PRIMARY KEY,
                    original_key TEXT,
                    file_path TEXT,
                    timestamp REAL,
                    access_count INTEGER,
                    data_hash TEXT,
                    computation_time REAL,
                    file_size INTEGER
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON cache_entries(timestamp)
            """)
    
    def _hash_key(self, key: str) -> str:
        """Generate hash for the key."""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def _get_file_path(self, key_hash: str) -> Path:
        """Get file path for cache entry."""
        return self.cache_dir / f"{key_hash}.pkl"
    
    def _cleanup_old_entries(self) -> None:
        """Remove old entries if cache size exceeds limit."""
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.pkl")) / (1024**2)
        
        if total_size > self.max_size_mb:
            with sqlite3.connect(self.db_path) as conn:
                # Get entries sorted by timestamp (oldest first)
                cursor = conn.execute("""
                    SELECT key_hash, file_path FROM cache_entries 
                    ORDER BY timestamp ASC
                """)
                
                for key_hash, file_path in cursor:
                    file_path = Path(file_path)
                    if file_path.exists():
                        file_path.unlink()
                    
                    conn.execute("DELETE FROM cache_entries WHERE key_hash = ?", (key_hash,))
                    
                    # Check if we're under the limit
                    remaining_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.pkl")) / (1024**2)
                    if remaining_size <= self.max_size_mb * 0.8:  # Leave some buffer
                        break
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        key_hash = self._hash_key(key)
        file_path = self._get_file_path(key_hash)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT original_key, timestamp, access_count FROM cache_entries 
                    WHERE key_hash = ?
                """, (key_hash,))
                
                result = cursor.fetchone()
                if not result or not file_path.exists():
                    return None
                
                # Load from disk
                with open(file_path, 'rb') as f:
                    value = pickle.load(f)
                
                # Update access count
                conn.execute("""
                    UPDATE cache_entries SET access_count = access_count + 1 
                    WHERE key_hash = ?
                """, (key_hash,))
                
                return value
        
        except Exception as e:
            self.logger.error(f"Error retrieving from disk cache: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in cache."""
        key_hash = self._hash_key(key)
        file_path = self._get_file_path(key_hash)
        
        try:
            # Clean up old entries if necessary
            self._cleanup_old_entries()
            
            # Save to disk
            with open(file_path, 'wb') as f:
                pickle.dump(value, f)
            
            file_size = file_path.stat().st_size
            
            # Update metadata
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO cache_entries 
                    (key_hash, original_key, file_path, timestamp, access_count, 
                     data_hash, computation_time, file_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    key_hash, key, str(file_path), time.time(), 0,
                    self._hash_key(str(value)), 0.0, file_size
                ))
        
        except Exception as e:
            self.logger.error(f"Error storing to disk cache: {e}")
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        key_hash = self._hash_key(key)
        file_path = self._get_file_path(key_hash)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM cache_entries WHERE key_hash = ?", (key_hash,))
                deleted = cursor.rowcount > 0
            
            if file_path.exists():
                file_path.unlink()
            
            return deleted
        
        except Exception as e:
            self.logger.error(f"Error deleting from disk cache: {e}")
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        try:
            # Remove all pickle files
            for file_path in self.cache_dir.glob("*.pkl"):
                file_path.unlink()
            
            # Clear database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache_entries")
        
        except Exception as e:
            self.logger.error(f"Error clearing disk cache: {e}")
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT COUNT(*), SUM(access_count), SUM(file_size), AVG(computation_time)
                    FROM cache_entries
                """)
                result = cursor.fetchone()
                
                if result and result[0]:
                    cache_size, total_accesses, total_size, avg_time = result
                    
                    return CacheStats(
                        hit_rate=0.0,  # Would need to track separately
                        miss_rate=0.0,
                        total_requests=total_accesses or 0,
                        total_hits=0,
                        total_misses=0,
                        cache_size=cache_size,
                        memory_usage_mb=(total_size or 0) / (1024**2),
                        average_computation_time=avg_time or 0.0
                    )
                
                return CacheStats(0.0, 0.0, 0, 0, 0, 0, 0.0, 0.0)
        
        except Exception as e:
            self.logger.error(f"Error getting disk cache stats: {e}")
            return CacheStats(0.0, 0.0, 0, 0, 0, 0, 0.0, 0.0)


class StatisticalComputationCache:
    """High-level cache for statistical computations with intelligent key generation."""
    
    def __init__(self, 
                 backend: Optional[CacheBackend] = None,
                 cache_dir: Optional[Union[str, Path]] = None):
        
        if backend is None:
            if cache_dir:
                backend = DiskCache(cache_dir)
            else:
                backend = MemoryCache()
        
        self.backend = backend
        self.logger = get_logger("causallm.stat_cache", level="INFO")
    
    def _generate_data_key(self, data: pd.DataFrame) -> str:
        """Generate a key based on DataFrame content and structure."""
        # Create a hash based on data characteristics
        key_components = [
            str(data.shape),
            str(sorted(data.columns.tolist())),
            str(data.dtypes.to_dict()),
        ]
        
        # Sample a few rows for content-based hashing
        if len(data) > 1000:
            sample_data = data.sample(n=100, random_state=42)
        else:
            sample_data = data
        
        # Add hash of sample data
        try:
            data_hash = hashlib.md5(
                pd.util.hash_pandas_object(sample_data, index=True).values
            ).hexdigest()
            key_components.append(data_hash)
        except:
            # Fallback if hashing fails
            key_components.append(str(sample_data.sum(numeric_only=True).sum()))
        
        return hashlib.sha256('|'.join(key_components).encode()).hexdigest()
    
    def _generate_computation_key(self, 
                                 operation: str,
                                 data_key: str,
                                 **params) -> str:
        """Generate a key for a specific computation."""
        # Sort parameters for consistent key generation
        sorted_params = sorted(params.items())
        param_str = json.dumps(sorted_params, sort_keys=True, default=str)
        
        key_components = [operation, data_key, param_str]
        return hashlib.sha256('|'.join(key_components).encode()).hexdigest()
    
    def cached_computation(self, 
                          operation: str,
                          data: pd.DataFrame,
                          computation_func: Callable,
                          **params) -> Any:
        """
        Perform cached computation.
        
        Args:
            operation: Name of the operation
            data: Input DataFrame
            computation_func: Function to compute the result
            **params: Parameters for the computation
            
        Returns:
            Computation result (cached or computed)
        """
        # Generate cache keys
        data_key = self._generate_data_key(data)
        comp_key = self._generate_computation_key(operation, data_key, **params)
        
        # Try to get from cache
        cached_result = self.backend.get(comp_key)
        if cached_result is not None:
            self.logger.debug(f"Cache hit for {operation}")
            return cached_result
        
        # Compute and cache result
        self.logger.debug(f"Cache miss for {operation}, computing...")
        start_time = time.time()
        
        try:
            result = computation_func(data, **params)
            computation_time = time.time() - start_time
            
            # Store in cache
            self.backend.set(comp_key, result)
            
            self.logger.info(f"Computed and cached {operation} in {computation_time:.2f}s")
            return result
        
        except Exception as e:
            raise ComputationError(
                f"Failed during cached computation of {operation}",
                operation=operation,
                cause=e
            )
    
    def get_cache_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self.backend.get_stats()
    
    def clear_cache(self) -> None:
        """Clear all cache entries."""
        self.backend.clear()
        self.logger.info("Cache cleared")


# Decorators for automatic caching

def cached_method(cache_key_func: Optional[Callable] = None,
                 ttl: Optional[int] = None):
    """
    Decorator for automatic method caching.
    
    Args:
        cache_key_func: Function to generate cache key
        ttl: Time to live for cache entries
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Get or create cache instance
            if not hasattr(self, '_method_cache'):
                self._method_cache = MemoryCache()
            
            # Generate cache key
            if cache_key_func:
                key = cache_key_func(self, *args, **kwargs)
            else:
                key = f"{func.__name__}_{hash((args, tuple(sorted(kwargs.items()))))}"
            
            # Try cache first
            result = self._method_cache.get(key)
            if result is not None:
                return result
            
            # Compute and cache
            result = func(self, *args, **kwargs)
            self._method_cache.set(key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


@lru_cache(maxsize=128)
def cached_statistical_function(data_hash: str, 
                               operation: str,
                               computation_func: Callable,
                               **params) -> Any:
    """LRU cached statistical function (for pure functions)."""
    return computation_func(**params)


# Global cache instance
_global_cache = None

def get_global_cache() -> StatisticalComputationCache:
    """Get global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = StatisticalComputationCache()
    return _global_cache

def set_global_cache(cache: StatisticalComputationCache) -> None:
    """Set global cache instance."""
    global _global_cache
    _global_cache = cache


# Cache-aware utility functions

def cached_correlation_matrix(data: pd.DataFrame, method: str = 'pearson') -> pd.DataFrame:
    """Compute correlation matrix with caching."""
    cache = get_global_cache()
    
    def _compute_correlation(df: pd.DataFrame, method: str) -> pd.DataFrame:
        return df.corr(method=method)
    
    return cache.cached_computation(
        'correlation_matrix',
        data,
        _compute_correlation,
        method=method
    )


def cached_pca_analysis(data: pd.DataFrame, n_components: Optional[int] = None) -> Dict[str, Any]:
    """Perform PCA analysis with caching."""
    from sklearn.decomposition import PCA
    
    cache = get_global_cache()
    
    def _compute_pca(df: pd.DataFrame, n_components: Optional[int]) -> Dict[str, Any]:
        numeric_data = df.select_dtypes(include=[np.number]).fillna(0)
        
        pca = PCA(n_components=n_components)
        components = pca.fit_transform(numeric_data)
        
        return {
            'components': components,
            'explained_variance_ratio': pca.explained_variance_ratio_,
            'feature_names': numeric_data.columns.tolist(),
            'n_components': pca.n_components_
        }
    
    return cache.cached_computation(
        'pca_analysis',
        data,
        _compute_pca,
        n_components=n_components
    )