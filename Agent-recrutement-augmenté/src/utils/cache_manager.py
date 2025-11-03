"""
Caching system for the recruitment agent to improve performance.
"""
import os
import json
import hashlib
import pickle
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages caching of CV analyses and rankings."""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live for cache entries in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """Load cache metadata."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache metadata: {e}")
                self.metadata = {}
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """Save cache metadata."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")
    
    def _generate_key(self, *args) -> str:
        """
        Generate a unique cache key from arguments.
        
        Args:
            *args: Arguments to hash
            
        Returns:
            MD5 hash as hex string
        """
        # Combine all arguments into a string
        content = ''.join(str(arg) for arg in args)
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{key}.pkl"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        try:
            # Check metadata
            if key not in self.metadata:
                return None
            
            # Check expiration
            created_at = datetime.fromisoformat(self.metadata[key]['created_at'])
            if datetime.now() - created_at > self.ttl:
                logger.debug(f"Cache expired for key: {key}")
                self.delete(key)
                return None
            
            # Load cached data
            cache_path = self._get_cache_path(key)
            if not cache_path.exists():
                logger.warning(f"Cache file missing for key: {key}")
                del self.metadata[key]
                self._save_metadata()
                return None
            
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            
            logger.debug(f"Cache hit for key: {key}")
            return data
            
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
            return None
    
    def set(self, key: str, value: Any, description: str = ""):
        """
        Store a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            description: Optional description of cached data
        """
        try:
            # Save data
            cache_path = self._get_cache_path(key)
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            
            # Update metadata
            self.metadata[key] = {
                'created_at': datetime.now().isoformat(),
                'description': description,
                'size_bytes': cache_path.stat().st_size
            }
            self._save_metadata()
            
            logger.debug(f"Cached data with key: {key}")
            
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
    
    def delete(self, key: str):
        """
        Delete a cache entry.
        
        Args:
            key: Cache key to delete
        """
        try:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
            
            if key in self.metadata:
                del self.metadata[key]
                self._save_metadata()
            
            logger.debug(f"Deleted cache entry: {key}")
            
        except Exception as e:
            logger.error(f"Error deleting cache entry: {e}")
    
    def clear(self):
        """Clear all cache entries."""
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            
            self.metadata = {}
            self._save_metadata()
            
            logger.info("Cache cleared")
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total_entries = len(self.metadata)
        total_size = sum(entry.get('size_bytes', 0) for entry in self.metadata.values())
        
        # Count expired entries
        expired = 0
        for key, entry in self.metadata.items():
            created_at = datetime.fromisoformat(entry['created_at'])
            if datetime.now() - created_at > self.ttl:
                expired += 1
        
        return {
            'total_entries': total_entries,
            'expired_entries': expired,
            'active_entries': total_entries - expired,
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir),
            'ttl_hours': self.ttl.total_seconds() / 3600
        }
    
    def cleanup_expired(self):
        """Remove expired cache entries."""
        expired_keys = []
        for key, entry in self.metadata.items():
            created_at = datetime.fromisoformat(entry['created_at'])
            if datetime.now() - created_at > self.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)
        
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        return len(expired_keys)

# Global cache instance
_cache_manager = None

def get_cache_manager(cache_dir: str = "cache", ttl_hours: int = 24) -> CacheManager:
    """Get or create the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager(cache_dir, ttl_hours)
    return _cache_manager
