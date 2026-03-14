"""
Basit memory cache implementasyonu
Redis olmadan hafif cache çözümü
"""
from typing import Any, Optional
from datetime import datetime, timedelta
import hashlib
import json


class SimpleCache:
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from data"""
        data_str = json.dumps(data, sort_keys=True)
        hash_key = hashlib.md5(data_str.encode()).hexdigest()
        return f"{prefix}:{hash_key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key not in self._cache:
            return None
        
        # Check expiry
        if key in self._expiry and datetime.now() > self._expiry[key]:
            # Expired, remove from cache
            del self._cache[key]
            del self._expiry[key]
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set value in cache with TTL (default 5 minutes)"""
        self._cache[key] = value
        self._expiry[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()
        self._expiry.clear()
    
    def size(self) -> int:
        """Get cache size"""
        return len(self._cache)


# Global cache instance
cache = SimpleCache()

