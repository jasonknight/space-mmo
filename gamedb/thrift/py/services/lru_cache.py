"""
LRU Cache implementation for service handlers.
Simple LRU (Least Recently Used) cache using OrderedDict.
When the cache reaches max_size, the least recently used item is evicted.
"""

from collections import OrderedDict
from typing import Optional, TypeVar, Generic
from copy import deepcopy
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class LRUCache(Generic[T]):
    """
    Simple LRU (Least Recently Used) cache implementation using OrderedDict.
    When the cache reaches max_size, the least recently used item is evicted.
    """

    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size

    def get(self, key: int) -> Optional[T]:
        """
        Get an item from the cache by ID.
        Returns a deep copy to prevent modifications affecting the cached version.
        Moves the item to the end (most recently used).
        """
        if key not in self.cache:
            logger.debug(f"Cache MISS for key={key}")
            return None

        logger.debug(f"Cache HIT for key={key}")
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        # Return a deep copy to prevent external modifications
        return deepcopy(self.cache[key])

    def put(self, key: int, value: T) -> None:
        """
        Add or update an item in the cache.
        Stores a deep copy to prevent external modifications affecting the cache.
        If cache is full, removes the least recently used item.
        """
        # Store a deep copy to prevent external modifications
        self.cache[key] = deepcopy(value)
        self.cache.move_to_end(key)

        # Evict least recently used if over capacity
        if len(self.cache) > self.max_size:
            evicted_key = next(iter(self.cache))
            self.cache.popitem(last=False)
            logger.debug(f"Cache EVICTED key={evicted_key} (cache full, size={self.max_size})")

        logger.debug(f"Cache PUT key={key} (cache size now {len(self.cache)})")

    def invalidate(self, key: int) -> None:
        """Remove an item from the cache."""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache INVALIDATED key={key}")

    def clear(self) -> None:
        """Clear all entries from the cache."""
        self.cache.clear()

    def size(self) -> int:
        """Return the current size of the cache."""
        return len(self.cache)
