import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheManager:
    """Simple file-based cache manager"""
    
    def __init__(self, cache_dir: str = "./.cache"):
        """Initialize cache manager"""
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_cache_key(self, key: str) -> str:
        """Generate a cache key using MD5 hash"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        """Get the file path for a cache key"""
        cache_key = self._get_cache_key(key)
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, key: str, ttl: int = 3600) -> Optional[Any]:
        """
        Get value from cache
        ttl: time to live in seconds (default 1 hour)
        """
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            # Check if cache is expired
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
            if datetime.now() - file_time > timedelta(seconds=ttl):
                # Cache expired, remove it
                os.remove(cache_path)
                return None
            
            # Read cached data
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
            
            logger.debug(f"Cache hit for key: {key}")
            return cached_data['value']
        except Exception as e:
            logger.warning(f"Error reading cache for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set value in cache
        """
        cache_path = self._get_cache_path(key)
        
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, (datetime, pd.Timestamp)):
                    return o.isoformat()
                return json.JSONEncoder.default(self, o)

        try:
            # Create cache data with timestamp
            cache_data = {
                'key': key,
                'value': value,
                'timestamp': datetime.now().isoformat()
            }
            
            # Write to cache file
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, cls=DateTimeEncoder)
            
            logger.debug(f"Cache set for key: {key}")
            return True
        except Exception as e:
            logger.warning(f"Error writing cache for key {key}: {e}")
            return False
    
    def clear(self, key: str = None) -> bool:
        """
        Clear cache for a specific key or all cache
        """
        try:
            if key:
                # Clear specific key
                cache_path = self._get_cache_path(key)
                if os.path.exists(cache_path):
                    os.remove(cache_path)
            else:
                # Clear all cache
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.json'):
                        os.remove(os.path.join(self.cache_dir, filename))
            
            return True
        except Exception as e:
            logger.warning(f"Error clearing cache: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        """
        try:
            files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
            total_size = sum(os.path.getsize(os.path.join(self.cache_dir, f)) for f in files)
            
            return {
                'cache_dir': self.cache_dir,
                'total_items': len(files),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        except Exception as e:
            logger.warning(f"Error getting cache stats: {e}")
            return {}

# Global cache manager instance
cache_manager = CacheManager()

# Example usage
if __name__ == "__main__":
    # Test cache manager
    cache = CacheManager()
    
    # Test setting and getting values
    cache.set("test_key", {"name": "Test", "value": 123})
    cached_value = cache.get("test_key")
    print(f"Cached value: {cached_value}")
    
    # Test cache stats
    stats = cache.get_stats()
    print(f"Cache stats: {stats}")
    
    # Test clearing cache
    cache.clear("test_key")
    cached_value = cache.get("test_key")
    print(f"After clearing, cached value: {cached_value}")