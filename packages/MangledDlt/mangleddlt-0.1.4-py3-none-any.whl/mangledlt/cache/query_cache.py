"""QueryCache entity for LRU caching of query results."""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import OrderedDict
import threading


class QueryCache:
    """LRU cache for query results to improve development performance."""

    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        """Initialize the cache."""
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.entries: OrderedDict[Any, tuple[Any, datetime]] = OrderedDict()
        self.access_times: Dict[Any, datetime] = {}
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key: Any) -> Optional[Any]:
        """Get value from cache if exists and not expired."""
        with self.lock:
            if key in self.entries:
                value, timestamp = self.entries[key]

                # Check if expired
                if datetime.now() - timestamp > timedelta(seconds=self.ttl_seconds):
                    del self.entries[key]
                    self.misses += 1
                    return None

                # Move to end (most recently used)
                self.entries.move_to_end(key)
                self.access_times[key] = datetime.now()
                self.hits += 1
                return value

            self.misses += 1
            return None

    def put(self, key: Any, value: Any):
        """Put value in cache, evicting LRU if necessary."""
        with self.lock:
            # Remove if already exists
            if key in self.entries:
                del self.entries[key]

            # Evict LRU if at capacity
            if len(self.entries) >= self.max_size:
                self.entries.popitem(last=False)

            # Add new entry
            self.entries[key] = (value, datetime.now())
            self.access_times[key] = datetime.now()

    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.entries.clear()
            self.access_times.clear()
            self.hits = 0
            self.misses = 0

    def invalidate_on_config_change(self):
        """Invalidate cache when configuration changes."""
        self.clear()

    def get_memory_usage(self) -> int:
        """Estimate memory usage in MB."""
        # Rough estimate: 10MB per cached DataFrame
        return len(self.entries) * 10

    def evict_if_needed(self):
        """Evict entries if memory limit exceeded."""
        with self.lock:
            memory_limit_mb = 1000  # 1GB default limit
            while self.get_memory_usage() > memory_limit_mb and self.entries:
                # Evict oldest entry
                self.entries.popitem(last=False)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0

            return {
                "enabled": True,
                "entries": len(self.entries),
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "max_size": self.max_size,
                "ttl_seconds": self.ttl_seconds,
                "memory_mb": self.get_memory_usage()
            }