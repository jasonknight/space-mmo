import sys
import os
import mysql.connector

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../gen-py"))

from models.inventory_model import InventoryModel
from game.ttypes import (
    Inventory,
    InventoryEntry,
    Owner,
    GameError,
)
from common import is_ok, is_true
from db_tables import get_table_sql


def setup_database(host: str, user: str, password: str, database_name: str):
    """Create all necessary tables for testing."""
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        auth_plugin="mysql_native_password",
        ssl_disabled=True,
        use_pure=True,
    )
    cursor = connection.cursor()

    # Create database
    cursor.execute(f"DROP DATABASE IF EXISTS {database_name};")
    cursor.execute(f"CREATE DATABASE {database_name};")

    # Create tables using centralized schemas
    cursor.execute(get_table_sql("inventories", database_name))
    cursor.execute(get_table_sql("inventory_entries", database_name))
    cursor.execute(get_table_sql("inventory_owners", database_name))

    connection.commit()
    cursor.close()
    connection.close()


def teardown_database(host: str, user: str, password: str, database_name: str):
    """Delete the test database."""
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        auth_plugin="mysql_native_password",
        ssl_disabled=True,
        use_pure=True,
    )
    cursor = connection.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {database_name};")
    connection.commit()
    cursor.close()
    connection.close()


def test_inventory(
    host: str,
    user: str,
    password: str,
    database_name: str,
):
    """Test Inventory save and load."""
    print("Testing Inventory...")

    # Create inventory model
    inventory_model = InventoryModel(host, user, password, database_name)

    # Create inventory with 3 entries
    entries = [
        InventoryEntry(item_id=301, quantity=10.0, is_max_stacked=False),
        InventoryEntry(item_id=302, quantity=25.5, is_max_stacked=True),
        InventoryEntry(item_id=303, quantity=5.0, is_max_stacked=False),
    ]

    owner = Owner()
    owner.mobile_id = 9999

    inventory = Inventory(
        id=None,
        max_entries=100,
        max_volume=1000.0,
        entries=entries,
        last_calculated_volume=250.5,
        owner=owner,
    )

    # Save inventory
    save_results = inventory_model.save(inventory)
    assert is_ok(save_results), f"Failed to save Inventory: {save_results[0].message}"
    print(f"  ✓ Saved: {save_results[0].message}")

    # Load inventory
    load_result, loaded_inv = inventory_model.load(inventory.id)
    assert is_true(load_result), f"Failed to load Inventory: {load_result.message}"
    print(f"  ✓ Loaded: {load_result.message}")

    # Compare
    assert loaded_inv.id == inventory.id, "ID mismatch"
    assert loaded_inv.max_entries == inventory.max_entries, "max_entries mismatch"
    assert loaded_inv.max_volume == inventory.max_volume, "max_volume mismatch"
    assert loaded_inv.last_calculated_volume == inventory.last_calculated_volume, (
        "last_calculated_volume mismatch"
    )
    assert len(loaded_inv.entries) == len(inventory.entries), "Entries count mismatch"

    # Compare entries
    for i, entry in enumerate(inventory.entries):
        loaded_entry = loaded_inv.entries[i]
        assert loaded_entry.item_id == entry.item_id, f"Entry {i} item_id mismatch"
        assert loaded_entry.quantity == entry.quantity, f"Entry {i} quantity mismatch"
        assert loaded_entry.is_max_stacked == entry.is_max_stacked, (
            f"Entry {i} is_max_stacked mismatch"
        )

    # Test update
    print("  Testing update...")
    loaded_inv.max_entries = 200
    loaded_inv.max_volume = 2000.0
    loaded_inv.entries = [
        InventoryEntry(item_id=401, quantity=15.0, is_max_stacked=True),
        InventoryEntry(item_id=402, quantity=30.0, is_max_stacked=False),
    ]

    update_results = inventory_model.save(loaded_inv)
    assert is_ok(update_results), (
        f"Failed to update Inventory: {update_results[0].message}"
    )
    print(f"  ✓ Updated: {update_results[0].message}")

    # Load again and verify updates
    load_result2, updated_inv = inventory_model.load(loaded_inv.id)
    assert is_true(load_result2), (
        f"Failed to load updated Inventory: {load_result2.message}"
    )
    assert updated_inv.max_entries == 200, "Updated max_entries mismatch"
    assert updated_inv.max_volume == 2000.0, "Updated max_volume mismatch"
    assert len(updated_inv.entries) == 2, "Updated entries count mismatch"
    print("  ✓ Update verified")

    # Test destroy
    print("  Testing destroy...")
    destroy_results = inventory_model.destroy(loaded_inv.id)
    assert is_ok(destroy_results), (
        f"Failed to destroy Inventory: {destroy_results[0].message}"
    )
    print(f"  ✓ Destroyed: {destroy_results[0].message}")

    # Verify load fails after destroy
    load_result3, destroyed_inv = inventory_model.load(loaded_inv.id)
    assert not is_true(load_result3), "Load should fail after destroy"
    assert destroyed_inv is None, "Destroyed inventory should be None"
    assert load_result3.error_code == GameError.DB_RECORD_NOT_FOUND, (
        f"Expected DB_RECORD_NOT_FOUND, got {load_result3.error_code}"
    )
    print("  ✓ Destroy verified: load failed with DB_RECORD_NOT_FOUND")

    print("  ✓ All assertions passed for Inventory\n")

    # Disconnect
    inventory_model.disconnect()


def test_list_inventory(
    host: str,
    user: str,
    password: str,
    database_name: str,
):
    """Test Inventory list functionality with pagination."""
    print("Testing Inventory list functionality...")

    import random

    # Create inventory model
    inventory_model = InventoryModel(host, user, password, database_name)

    # Create 100 inventories with random data
    print("  Creating 100 inventories...")
    created_inventories = []

    for i in range(100):
        # Create owner (using mobile_id for simplicity)
        owner = Owner()
        owner.mobile_id = i + 1

        inventory = Inventory(
            id=None,
            max_entries=random.randint(10, 100),
            max_volume=random.uniform(100.0, 1000.0),
            entries=[],
            last_calculated_volume=0.0,
            owner=owner,
        )

        save_results = inventory_model.save(inventory)
        assert is_ok(save_results), (
            f"Failed to save inventory {i}: {save_results[0].message}"
        )
        created_inventories.append(inventory)

    print(f"  ✓ Created {len(created_inventories)} inventories")

    # Test pagination - iterate through all pages with 10 results per page
    print("  Testing pagination (10 results per page)...")
    all_paginated_inventories = []
    page = 0
    results_per_page = 10

    while True:
        result, inventories, total_count = inventory_model.search(
            page,
            results_per_page,
        )
        assert is_true(result), (
            f"Failed to list inventories page {page}: {result.message}"
        )

        if not inventories:
            break

        all_paginated_inventories.extend(inventories)
        print(
            f"    Page {page}: retrieved {len(inventories)} inventories (total: {total_count})"
        )

        # Check if this is the last page
        if len(all_paginated_inventories) >= total_count:
            break

        page += 1

    assert len(all_paginated_inventories) == 100, (
        f"Expected 100 inventories, got {len(all_paginated_inventories)}"
    )
    print(
        f"  ✓ Pagination test passed: retrieved all {len(all_paginated_inventories)} inventories across {page + 1} pages"
    )

    # Note: search_string is not tested for inventories as there are no searchable text fields
    print("  ✓ All list tests passed for Inventory\n")

    # Disconnect
    inventory_model.disconnect()


def main():
    """Run all tests."""
    # Database configuration
    host = "localhost"
    user = "admin"
    password = "minda"
    database_name = "test_inventory_db"

    print("=" * 60)
    print("Inventory Test Suite")
    print("=" * 60)
    print()

    try:
        # Setup database and tables
        print("Setting up test database...")
        setup_database(host, user, password, database_name)
        print("✓ Database setup complete\n")

        # Run tests
        test_inventory(host, user, password, database_name)
        test_list_inventory(host, user, password, database_name)

        print("=" * 60)
        print("All tests passed successfully!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
    finally:
        # Teardown database
        print("\nCleaning up test database...")
        teardown_database(host, user, password, database_name)
        print("✓ Cleanup complete")


if __name__ == "__main__":
    main()
