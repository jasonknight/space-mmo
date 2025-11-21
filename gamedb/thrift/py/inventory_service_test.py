#!/usr/bin/env python3
"""Tests for InventoryService with cache validation."""

import sys
sys.path.append('../gen-py')

from db import DB
from inventory_service import InventoryServiceHandler, LRUCache
from game.ttypes import (
    Request,
    Response,
    RequestData,
    ResponseData,
    LoadInventoryRequestData,
    CreateInventoryRequestData,
    SaveInventoryRequestData,
    SplitStackRequestData,
    TransferItemRequestData,
    Inventory,
    InventoryEntry,
    Item,
    ItemType,
    Attribute,
    AttributeType,
    Owner,
    StatusType,
    GameError,
)
from common import is_ok, is_true


def setup_database(db: DB, database_name: str):
    """Create all necessary tables for testing."""
    db.connect()
    cursor = db.connection.cursor()

    # Create database
    cursor.execute(f"DROP DATABASE IF EXISTS {database_name};")
    cursor.execute(f"CREATE DATABASE {database_name};")

    # Create all tables
    for stmt in db.get_items_table_sql(database_name):
        cursor.execute(stmt)

    for stmt in db.get_attributes_table_sql(database_name):
        cursor.execute(stmt)

    for stmt in db.get_attribute_owners_table_sql(database_name):
        cursor.execute(stmt)

    for stmt in db.get_inventories_table_sql(database_name):
        cursor.execute(stmt)

    for stmt in db.get_inventory_entries_table_sql(database_name):
        cursor.execute(stmt)

    for stmt in db.get_inventory_owners_table_sql(database_name):
        cursor.execute(stmt)

    db.connection.commit()
    cursor.close()


def teardown_database(db: DB, database_name: str):
    """Delete the test database."""
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {database_name};")
    db.connection.commit()
    cursor.close()
    db.disconnect()


def create_test_item(db: DB, database_name: str, item_id: int, internal_name: str) -> Item:
    """Helper to create a test item in the database."""
    item = Item(
        id=None,
        internal_name=internal_name,
        attributes={},
        max_stack_size=100,
        item_type=ItemType.RAWMATERIAL,
    )

    results = db.save_item(database_name, item)
    assert is_ok(results), f"Failed to create test item: {results[0].message}"
    return item


def test_create_inventory(service: InventoryServiceHandler, db: DB, database_name: str):
    """Test creating a new inventory via service."""
    print("Testing InventoryService.create()...")

    # Create inventory
    owner = Owner(mobile_id=100)
    inventory = Inventory(
        id=None,
        max_entries=10,
        max_volume=500.0,
        entries=[],
        owner=owner,
    )

    request = Request(
        data=RequestData(
            create_inventory=CreateInventoryRequestData(
                inventory=inventory,
            ),
        ),
    )

    response = service.create(request)
    assert is_ok(response.results), f"Create failed: {response.results[0].message}"
    assert response.response_data is not None, "Response data should not be None"
    assert response.response_data.create_inventory is not None, "create_inventory data missing"

    created_inventory = response.response_data.create_inventory.inventory
    assert created_inventory.id is not None, "Created inventory should have an ID"
    print(f"  ✓ Created inventory with ID: {created_inventory.id}")

    # Verify it was saved to DB
    load_result, db_inventory = db.load_inventory(database_name, created_inventory.id)
    assert is_true(load_result), "Failed to load inventory from DB"
    assert db_inventory.max_entries == 10, "max_entries mismatch"
    assert db_inventory.max_volume == 500.0, "max_volume mismatch"
    print("  ✓ Verified inventory in database")

    # Verify it's in cache
    cached_inventory = service.cache.get(created_inventory.id)
    assert cached_inventory is not None, "Inventory should be in cache"
    assert cached_inventory.id == created_inventory.id, "Cached inventory ID mismatch"
    print("  ✓ Verified inventory in cache")

    print("  ✓ All create tests passed\n")
    return created_inventory


def test_load_inventory(service: InventoryServiceHandler, db: DB, database_name: str, inventory_id: int):
    """Test loading an inventory via service (cache miss and cache hit)."""
    print("Testing InventoryService.load()...")

    # Clear cache to test cache miss
    service.cache.clear()
    print("  Cache cleared for testing cache miss")

    # First load - cache miss
    request = Request(
        data=RequestData(
            load_inventory=LoadInventoryRequestData(
                inventory_id=inventory_id,
            ),
        ),
    )

    response = service.load(request)
    assert is_ok(response.results), f"Load failed: {response.results[0].message}"
    assert response.response_data is not None, "Response data should not be None"
    assert response.response_data.load_inventory is not None, "load_inventory data missing"

    loaded_inventory = response.response_data.load_inventory.inventory
    assert loaded_inventory.id == inventory_id, "Loaded inventory ID mismatch"
    print(f"  ✓ Loaded inventory (cache miss): {response.results[0].message}")

    # Verify it's now in cache
    cached_inventory = service.cache.get(inventory_id)
    assert cached_inventory is not None, "Inventory should be in cache after load"
    print("  ✓ Inventory cached after load")

    # Second load - cache hit
    response2 = service.load(request)
    assert is_ok(response2.results), f"Second load failed: {response2.results[0].message}"
    assert "cache" in response2.results[0].message, "Second load should mention cache"
    print(f"  ✓ Loaded inventory (cache hit): {response2.results[0].message}")

    # Test loading non-existent inventory
    request_bad = Request(
        data=RequestData(
            load_inventory=LoadInventoryRequestData(
                inventory_id=99999,
            ),
        ),
    )

    response_bad = service.load(request_bad)
    assert not is_ok(response_bad.results), "Loading non-existent inventory should fail"
    assert response_bad.response_data is None, "Response data should be None for failure"
    print("  ✓ Non-existent inventory load properly failed")

    print("  ✓ All load tests passed\n")


def test_save_inventory(service: InventoryServiceHandler, db: DB, database_name: str, inventory_id: int):
    """Test saving/updating an inventory via service."""
    print("Testing InventoryService.save()...")

    # Load the inventory
    load_result, inventory = db.load_inventory(database_name, inventory_id)
    assert is_true(load_result), "Failed to load inventory from DB"

    # Modify it
    inventory.max_entries = 20
    inventory.max_volume = 1000.0

    request = Request(
        data=RequestData(
            save_inventory=SaveInventoryRequestData(
                inventory=inventory,
            ),
        ),
    )

    response = service.save(request)
    assert is_ok(response.results), f"Save failed: {response.results[0].message}"
    print(f"  ✓ Saved inventory: {response.results[0].message}")

    # Verify changes in DB
    load_result2, updated_inventory = db.load_inventory(database_name, inventory_id)
    assert is_true(load_result2), "Failed to load updated inventory from DB"
    assert updated_inventory.max_entries == 20, "max_entries not updated in DB"
    assert updated_inventory.max_volume == 1000.0, "max_volume not updated in DB"
    print("  ✓ Verified updates in database")

    # Verify cache was updated
    cached_inventory = service.cache.get(inventory_id)
    assert cached_inventory is not None, "Inventory should be in cache"
    assert cached_inventory.max_entries == 20, "max_entries not updated in cache"
    assert cached_inventory.max_volume == 1000.0, "max_volume not updated in cache"
    print("  ✓ Verified cache was updated")

    print("  ✓ All save tests passed\n")


def test_split_stack(service: InventoryServiceHandler, db: DB, database_name: str):
    """Test splitting a stack of items via service."""
    print("Testing InventoryService.split_stack()...")

    # Create a test item
    item = create_test_item(db, database_name, 1, "test_steel")
    print(f"  Created test item: {item.internal_name} (ID: {item.id})")

    # Create inventory with one entry
    owner = Owner(mobile_id=200)
    inventory = Inventory(
        id=None,
        max_entries=10,
        max_volume=500.0,
        entries=[
            InventoryEntry(
                item_id=item.id,
                quantity=100.0,
                is_max_stacked=False,
            ),
        ],
        owner=owner,
    )

    # Save inventory to DB
    save_results = db.save_inventory(database_name, inventory)
    assert is_ok(save_results), "Failed to save test inventory"
    print(f"  ✓ Created test inventory with 1 entry (ID: {inventory.id})")

    # Clear cache
    service.cache.clear()

    # Split the stack
    request = Request(
        data=RequestData(
            split_stack=SplitStackRequestData(
                inventory_id=inventory.id,
                item_id=item.id,
                quantity_to_split=40.0,
            ),
        ),
    )

    response = service.split_stack(request)
    assert is_ok(response.results), f"Split stack failed: {response.results}"
    assert response.response_data is not None, "Response data should not be None"

    split_inventory = response.response_data.split_stack.inventory
    assert len(split_inventory.entries) == 2, f"Should have 2 entries after split, got {len(split_inventory.entries)}"
    print(f"  ✓ Split stack successful: {len(split_inventory.entries)} entries")

    # Verify in DB
    load_result, db_inventory = db.load_inventory(database_name, inventory.id)
    assert is_true(load_result), "Failed to load inventory from DB"
    assert len(db_inventory.entries) == 2, "Should have 2 entries in DB"

    # Check quantities (order might vary)
    quantities = sorted([entry.quantity for entry in db_inventory.entries])
    assert quantities == [40.0, 60.0], f"Expected quantities [40.0, 60.0], got {quantities}"
    print(f"  ✓ Verified split in database: quantities {quantities}")

    # Verify cache was updated
    cached_inventory = service.cache.get(inventory.id)
    assert cached_inventory is not None, "Inventory should be in cache"
    assert len(cached_inventory.entries) == 2, "Should have 2 entries in cache"
    print("  ✓ Verified cache was updated")

    # Test splitting non-existent item
    request_bad = Request(
        data=RequestData(
            split_stack=SplitStackRequestData(
                inventory_id=inventory.id,
                item_id=99999,
                quantity_to_split=10.0,
            ),
        ),
    )

    response_bad = service.split_stack(request_bad)
    assert not is_ok(response_bad.results), "Split with non-existent item should fail"
    assert response_bad.results[0].error_code == GameError.INV_ITEM_NOT_FOUND, "Should return INV_ITEM_NOT_FOUND"
    print("  ✓ Non-existent item split properly failed")

    print("  ✓ All split_stack tests passed\n")


def test_transfer_item(service: InventoryServiceHandler, db: DB, database_name: str):
    """Test transferring items between inventories via service."""
    print("Testing InventoryService.transfer_item()...")

    # Create a test item
    item = create_test_item(db, database_name, 2, "test_copper")
    print(f"  Created test item: {item.internal_name} (ID: {item.id})")

    # Create source inventory with item
    owner1 = Owner(mobile_id=300)
    source_inventory = Inventory(
        id=None,
        max_entries=10,
        max_volume=500.0,
        entries=[
            InventoryEntry(
                item_id=item.id,
                quantity=80.0,
                is_max_stacked=False,
            ),
        ],
        owner=owner1,
    )

    # Create destination inventory (empty)
    owner2 = Owner(mobile_id=400)
    dest_inventory = Inventory(
        id=None,
        max_entries=10,
        max_volume=500.0,
        entries=[],
        owner=owner2,
    )

    # Save both to DB
    save_results1 = db.save_inventory(database_name, source_inventory)
    assert is_ok(save_results1), "Failed to save source inventory"
    save_results2 = db.save_inventory(database_name, dest_inventory)
    assert is_ok(save_results2), "Failed to save dest inventory"
    print(f"  ✓ Created source (ID: {source_inventory.id}) and dest (ID: {dest_inventory.id}) inventories")

    # Clear cache
    service.cache.clear()

    # Transfer item
    request = Request(
        data=RequestData(
            transfer_item=TransferItemRequestData(
                source_inventory_id=source_inventory.id,
                destination_inventory_id=dest_inventory.id,
                item_id=item.id,
                quantity=30.0,
            ),
        ),
    )

    response = service.transfer_item(request)
    assert is_ok(response.results), f"Transfer failed: {response.results}"
    assert response.response_data is not None, "Response data should not be None"

    transfer_data = response.response_data.transfer_item
    assert transfer_data.source_inventory is not None, "Source inventory missing"
    assert transfer_data.destination_inventory is not None, "Destination inventory missing"
    print(f"  ✓ Transfer successful")

    # Verify in DB
    load_result1, db_source = db.load_inventory(database_name, source_inventory.id)
    load_result2, db_dest = db.load_inventory(database_name, dest_inventory.id)
    assert is_true(load_result1), "Failed to load source from DB"
    assert is_true(load_result2), "Failed to load dest from DB"

    # Check source has 50 remaining
    source_quantity = sum([entry.quantity for entry in db_source.entries if entry.item_id == item.id])
    assert source_quantity == 50.0, f"Source should have 50.0, got {source_quantity}"

    # Check dest has 30
    dest_quantity = sum([entry.quantity for entry in db_dest.entries if entry.item_id == item.id])
    assert dest_quantity == 30.0, f"Dest should have 30.0, got {dest_quantity}"
    print(f"  ✓ Verified transfer in database: source={source_quantity}, dest={dest_quantity}")

    # Verify both in cache
    cached_source = service.cache.get(source_inventory.id)
    cached_dest = service.cache.get(dest_inventory.id)
    assert cached_source is not None, "Source should be in cache"
    assert cached_dest is not None, "Dest should be in cache"
    print("  ✓ Verified both inventories cached")

    # Test transferring non-existent item
    request_bad = Request(
        data=RequestData(
            transfer_item=TransferItemRequestData(
                source_inventory_id=source_inventory.id,
                destination_inventory_id=dest_inventory.id,
                item_id=99999,
                quantity=10.0,
            ),
        ),
    )

    response_bad = service.transfer_item(request_bad)
    assert not is_ok(response_bad.results), "Transfer with non-existent item should fail"
    print("  ✓ Non-existent item transfer properly failed")

    print("  ✓ All transfer_item tests passed\n")


def test_cache_eviction(service: InventoryServiceHandler, db: DB, database_name: str):
    """Test that LRU cache eviction works properly."""
    print("Testing cache eviction...")

    # Create a service with small cache
    small_cache_service = InventoryServiceHandler(db, database_name, cache_size=3)

    # Create 4 inventories
    inventories = []
    for i in range(4):
        owner = Owner(mobile_id=500 + i)
        inventory = Inventory(
            id=None,
            max_entries=10,
            max_volume=500.0,
            entries=[],
            owner=owner,
        )
        save_results = db.save_inventory(database_name, inventory)
        assert is_ok(save_results), f"Failed to create inventory {i}"
        inventories.append(inventory)
        print(f"  Created inventory {i} (ID: {inventory.id})")

    # Load first 3 into cache
    for i in range(3):
        request = Request(
            data=RequestData(
                load_inventory=LoadInventoryRequestData(
                    inventory_id=inventories[i].id,
                ),
            ),
        )
        response = small_cache_service.load(request)
        assert is_ok(response.results), f"Failed to load inventory {i}"

    assert small_cache_service.cache.size() == 3, f"Cache should have 3 items, got {small_cache_service.cache.size()}"
    print("  ✓ Loaded 3 inventories into cache")

    # Access inventory 0 to make it recently used
    small_cache_service.cache.get(inventories[0].id)

    # Load inventory 3 - should evict inventory 1 (least recently used)
    request = Request(
        data=RequestData(
            load_inventory=LoadInventoryRequestData(
                inventory_id=inventories[3].id,
            ),
        ),
    )
    response = small_cache_service.load(request)
    assert is_ok(response.results), "Failed to load inventory 3"

    assert small_cache_service.cache.size() == 3, f"Cache should still have 3 items, got {small_cache_service.cache.size()}"

    # Verify inventory 1 was evicted
    assert small_cache_service.cache.get(inventories[1].id) is None, "Inventory 1 should have been evicted"

    # Verify others are still in cache
    assert small_cache_service.cache.get(inventories[0].id) is not None, "Inventory 0 should still be in cache"
    assert small_cache_service.cache.get(inventories[2].id) is not None, "Inventory 2 should still be in cache"
    assert small_cache_service.cache.get(inventories[3].id) is not None, "Inventory 3 should be in cache"
    print("  ✓ LRU eviction working correctly")

    print("  ✓ All cache eviction tests passed\n")


def test_invalid_requests(service: InventoryServiceHandler):
    """Test that invalid requests are handled properly."""
    print("Testing invalid request handling...")

    # Test load without data
    request = Request(data=RequestData())
    response = service.load(request)
    assert not is_ok(response.results), "Load without data should fail"
    assert response.results[0].error_code == GameError.DB_INVALID_DATA, "Should return DB_INVALID_DATA"
    print("  ✓ Load without data properly failed")

    # Test create without data
    response = service.create(request)
    assert not is_ok(response.results), "Create without data should fail"
    print("  ✓ Create without data properly failed")

    # Test save without data
    response = service.save(request)
    assert not is_ok(response.results), "Save without data should fail"
    print("  ✓ Save without data properly failed")

    # Test split_stack without data
    response = service.split_stack(request)
    assert not is_ok(response.results), "Split_stack without data should fail"
    print("  ✓ Split_stack without data properly failed")

    # Test transfer_item without data
    response = service.transfer_item(request)
    assert not is_ok(response.results), "Transfer_item without data should fail"
    print("  ✓ Transfer_item without data properly failed")

    print("  ✓ All invalid request tests passed\n")


def run_all_tests():
    """Run all InventoryService tests."""
    print("=" * 60)
    print("Running InventoryService Tests")
    print("=" * 60 + "\n")

    # Setup
    db = DB(host="localhost", user="admin", password="minda")
    database_name = "test_inventory_service_db"

    print("Setting up test database...")
    setup_database(db, database_name)
    print("✓ Test database ready\n")

    # Create service instance
    service = InventoryServiceHandler(db, database_name, cache_size=1000)
    print("✓ InventoryService handler created\n")

    try:
        # Run tests
        created_inventory = test_create_inventory(service, db, database_name)
        test_load_inventory(service, db, database_name, created_inventory.id)
        test_save_inventory(service, db, database_name, created_inventory.id)
        test_split_stack(service, db, database_name)
        test_transfer_item(service, db, database_name)
        test_cache_eviction(service, db, database_name)
        test_invalid_requests(service)

        print("=" * 60)
        print("✓ All InventoryService tests passed!")
        print("=" * 60)

    finally:
        # Cleanup
        print("\nCleaning up test database...")
        teardown_database(db, database_name)
        print("✓ Test database removed")


if __name__ == "__main__":
    run_all_tests()
