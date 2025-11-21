#!/usr/bin/env python3
"""Simple test to verify LRU cache functionality."""

import sys
sys.path.append('gen-py')

from inventory_service import LRUCache
from game.ttypes import Inventory, Owner

def test_lru_cache():
    """Test basic LRU cache operations."""
    print("Testing LRU cache...")

    # Create cache with small size for testing
    cache = LRUCache(max_size=3)

    # Create test inventories
    inv1 = Inventory(
        id=1,
        max_entries=10,
        max_volume=100.0,
        entries=[],
        owner=Owner(mobile_id=1),
    )

    inv2 = Inventory(
        id=2,
        max_entries=20,
        max_volume=200.0,
        entries=[],
        owner=Owner(mobile_id=2),
    )

    inv3 = Inventory(
        id=3,
        max_entries=30,
        max_volume=300.0,
        entries=[],
        owner=Owner(mobile_id=3),
    )

    inv4 = Inventory(
        id=4,
        max_entries=40,
        max_volume=400.0,
        entries=[],
        owner=Owner(mobile_id=4),
    )

    # Test 1: Put and get
    print("  Test 1: Put and get...")
    cache.put(1, inv1)
    retrieved = cache.get(1)
    assert retrieved is not None, "Failed to retrieve cached inventory"
    assert retrieved.id == 1, "Retrieved wrong inventory"
    assert retrieved.max_entries == 10, "Retrieved inventory has wrong data"
    print("  ✓ Put and get working")

    # Test 2: Cache miss
    print("  Test 2: Cache miss...")
    missing = cache.get(999)
    assert missing is None, "Should return None for cache miss"
    print("  ✓ Cache miss returns None")

    # Test 3: LRU eviction
    print("  Test 3: LRU eviction...")
    cache.put(1, inv1)
    cache.put(2, inv2)
    cache.put(3, inv3)
    assert cache.size() == 3, f"Cache should have 3 items, has {cache.size()}"

    # Access inv1 to make it recently used
    cache.get(1)

    # Add inv4 - should evict inv2 (least recently used)
    cache.put(4, inv4)
    assert cache.size() == 3, f"Cache should still have 3 items, has {cache.size()}"
    assert cache.get(2) is None, "inv2 should have been evicted"
    assert cache.get(1) is not None, "inv1 should still be in cache"
    assert cache.get(3) is not None, "inv3 should still be in cache"
    assert cache.get(4) is not None, "inv4 should be in cache"
    print("  ✓ LRU eviction working correctly")

    # Test 4: Deep copy prevents external modifications
    print("  Test 4: Deep copy isolation...")
    cache.clear()
    cache.put(1, inv1)
    retrieved1 = cache.get(1)
    retrieved1.max_entries = 999  # Modify the retrieved copy
    retrieved2 = cache.get(1)
    assert retrieved2.max_entries == 10, "Cache should return unmodified copy"
    print("  ✓ Deep copy isolation working")

    # Test 5: Invalidate
    print("  Test 5: Invalidate...")
    cache.put(1, inv1)
    assert cache.get(1) is not None, "Should be in cache"
    cache.invalidate(1)
    assert cache.get(1) is None, "Should be removed from cache"
    print("  ✓ Invalidate working")

    print("\n✓ All LRU cache tests passed!")

if __name__ == "__main__":
    test_lru_cache()
