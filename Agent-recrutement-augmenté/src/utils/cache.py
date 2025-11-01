"""
Caching utilities for improved performance.
"""
import os
import json
import hashlib
import pickle
from typing import Any, Optional, Callable
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Cache:
    """Simple file-based cache for CV processing results."""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live in hours for cache entries
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get path to cache file."""
        return self.cache_dir / f"{key}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            # Check if expired
            file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
            if datetime.now() - file_time > self.ttl:
                cache_path.unlink()  # Delete expired cache
                return None
            
            # Load cached data
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            
            logger.debug(f"Cache hit for key: {key}")
            return data
            
        except Exception as e:
            logger.warning(f"Cache read error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            
        Returns:
            True if successful
        """
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            logger.debug(f"Cached data for key: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache write error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cache entry."""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
            return True
        return False
    
    def clear(self) -> int:
        """Clear all cache entries. Returns number of files deleted."""
        count = 0
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
            count += 1
        return count
    
    def clear_expired(self) -> int:
        """Clear expired cache entries. Returns number of files deleted."""
        count = 0
        now = datetime.now()
        
        for cache_file in self.cache_dir.glob("*.cache"):
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if now - file_time > self.ttl:
                cache_file.unlink()
                count += 1
        
        return count
    
    def stats(self) -> dict:
        """Get cache statistics."""
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'total_entries': len(cache_files),
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir),
            'ttl_hours': self.ttl.total_seconds() / 3600
        }


def cached(cache_instance: Cache, key_func: Optional[Callable] = None):
    """
    Decorator for caching function results.
    
    Args:
        cache_instance: Cache instance to use
        key_func: Optional function to generate cache key from arguments
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache_instance._get_cache_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


# Global cache instance
cv_cache = Cache(cache_dir="cache/cv_processing", ttl_hours=24)
llm_cache = Cache(cache_dir="cache/llm_results", ttl_hours=168)  # 1 week for LLM results
