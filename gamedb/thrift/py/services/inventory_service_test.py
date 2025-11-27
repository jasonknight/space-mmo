#!/usr/bin/env python3
"""Simplified tests for InventoryService."""

import sys

sys.path.append("../../gen-py")
sys.path.append("..")

import mysql.connector
from services.inventory_service import InventoryServiceHandler
from models.inventory_model import InventoryModel
from models.item_model import ItemModel
from game.ttypes import (
    InventoryRequest,
    InventoryRequestData,
    CreateInventoryRequestData,
    LoadInventoryRequestData,
    SaveInventoryRequestData,
    Inventory,
    InventoryEntry,
    Item,
    ItemType,
    Owner,
    StatusType,
)
from common import is_ok, is_true
from db_tables import get_table_sql


def setup_database(host, user, password, database_name):
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

    cursor.execute(f"DROP DATABASE IF EXISTS {database_name}")
    cursor.execute(f"CREATE DATABASE {database_name}")

    # Create tables using centralized schemas
    cursor.execute(get_table_sql("items", database_name))
    cursor.execute(get_table_sql("attributes", database_name))
    cursor.execute(get_table_sql("attribute_owners", database_name))
    cursor.execute(get_table_sql("inventories", database_name))
    cursor.execute(get_table_sql("inventory_entries", database_name))
    cursor.execute(get_table_sql("inventory_owners", database_name))

    connection.commit()
    cursor.close()
    connection.close()


def teardown_database(host, user, password, database_name):
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
    cursor.execute(f"DROP DATABASE IF EXISTS {database_name}")
    connection.commit()
    cursor.close()
    connection.close()


def run_all_tests():
    """Run all InventoryService tests."""
    print("=" * 60)
    print("Running InventoryService Tests")
    print("=" * 60 + "\n")

    host = "localhost"
    user = "admin"
    password = "minda"
    database_name = "test_inventory_service_db"

    print("Setting up test database...")
    setup_database(host, user, password, database_name)
    print("✓ Test database ready\n")

    service = InventoryServiceHandler(
        host, user, password, database_name, cache_size=1000
    )
    inventory_model = InventoryModel(host, user, password, database_name)
    print("✓ InventoryService handler created\n")

    try:
        # Test create
        print("Testing InventoryService.create()...")
        owner = Owner(mobile_id=100)
        inventory = Inventory(
            id=None,
            max_entries=10,
            max_volume=500.0,
            entries=[],
            owner=owner,
        )

        request = InventoryRequest(
            data=InventoryRequestData(
                create_inventory=CreateInventoryRequestData(inventory=inventory),
            ),
        )

        response = service.create(request)
        assert is_ok(response.results), f"Create failed: {response.results[0].message}"
        assert response.response_data is not None
        created_inventory = response.response_data.create_inventory.inventory
        assert created_inventory.id is not None
        print(f"  ✓ Created inventory with ID: {created_inventory.id}\n")

        # Test load
        print("Testing InventoryService.load()...")
        service.cache.clear()

        load_request = InventoryRequest(
            data=InventoryRequestData(
                load_inventory=LoadInventoryRequestData(
                    inventory_id=created_inventory.id
                ),
            ),
        )

        response = service.load(load_request)
        assert is_ok(response.results), f"Load failed: {response.results[0].message}"
        loaded_inventory = response.response_data.load_inventory.inventory
        assert loaded_inventory.id == created_inventory.id
        print(f"  ✓ Loaded inventory (cache miss)\n")

        # Test load from cache
        response2 = service.load(load_request)
        assert is_ok(response2.results)
        assert "cache" in response2.results[0].message.lower()
        print(f"  ✓ Loaded inventory (cache hit)\n")

        # Test save
        print("Testing InventoryService.save()...")
        loaded_inventory.max_entries = 20
        loaded_inventory.max_volume = 1000.0

        save_request = InventoryRequest(
            data=InventoryRequestData(
                save_inventory=SaveInventoryRequestData(inventory=loaded_inventory),
            ),
        )

        response = service.save(save_request)
        assert is_ok(response.results), f"Save failed: {response.results[0].message}"
        print(f"  ✓ Saved inventory\n")

        # Verify save
        result, updated_inventory = inventory_model.load(created_inventory.id)
        assert is_true(result)
        assert updated_inventory.max_entries == 20
        assert updated_inventory.max_volume == 1000.0
        print(f"  ✓ Verified updates in database\n")

        print("=" * 60)
        print("✓ All InventoryService tests passed!")
        print("=" * 60)

    finally:
        print("\nCleaning up test database...")
        teardown_database(host, user, password, database_name)
        print("✓ Test database removed")


if __name__ == "__main__":
    run_all_tests()
