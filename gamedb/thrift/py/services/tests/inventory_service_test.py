#!/usr/bin/env python3
"""Tests for InventoryService using db_models."""

import sys
import os
import uuid

thrift_gen_path = '/vagrant/gamedb/thrift/gen-py'
if thrift_gen_path not in sys.path:
    sys.path.insert(0, thrift_gen_path)

py_path = '/vagrant/gamedb/thrift/py'
if py_path not in sys.path:
    sys.path.insert(0, py_path)

from dotenv import load_dotenv
load_dotenv()

import mysql.connector
from services.inventory_service import InventoryServiceHandler
from db_models.models import Inventory, InventoryEntry, Item, Attribute
from game.ttypes import (
    InventoryRequest,
    InventoryRequestData,
    CreateInventoryRequestData,
    LoadInventoryRequestData,
    SaveInventoryRequestData,
    Inventory as ThriftInventory,
    Owner,
    StatusType,
)
from common import is_ok

TEST_DATABASE = None


def setUpModule():
    """Create unique test database and tables."""
    global TEST_DATABASE
    TEST_DATABASE = f"gamedb_test_{uuid.uuid4().hex[:8]}"

    connection = mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'admin'),
        password=os.environ.get('DB_PASSWORD', 'minda'),
        auth_plugin="mysql_native_password",
        ssl_disabled=True,
        use_pure=True,
    )
    cursor = connection.cursor()

    cursor.execute(f"CREATE DATABASE `{TEST_DATABASE}`")
    connection.database = TEST_DATABASE

    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    cursor.execute(Item.CREATE_TABLE_STATEMENT)
    cursor.execute(Attribute.CREATE_TABLE_STATEMENT)
    cursor.execute(Inventory.CREATE_TABLE_STATEMENT)
    cursor.execute(InventoryEntry.CREATE_TABLE_STATEMENT)
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")

    connection.commit()
    cursor.close()
    connection.close()

    os.environ['DB_DATABASE'] = TEST_DATABASE
    print(f"✓ Test database created: {TEST_DATABASE}")


def tearDownModule():
    """Drop test database."""
    global TEST_DATABASE
    if TEST_DATABASE:
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'admin'),
            password=os.environ.get('DB_PASSWORD', 'minda'),
            auth_plugin="mysql_native_password",
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS `{TEST_DATABASE}`")
        connection.commit()
        cursor.close()
        connection.close()
        print(f"✓ Test database dropped: {TEST_DATABASE}")


def run_all_tests():
    """Run all InventoryService tests."""
    print("=" * 60)
    print("Running InventoryService Tests")
    print("=" * 60 + "\n")

    service = InventoryServiceHandler()
    print("✓ InventoryService handler created\n")

    try:
        # Test create
        print("Testing InventoryService.create()...")
        owner = Owner(mobile_id=100)
        inventory = ThriftInventory(
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
        print(f"  ✓ Loaded inventory\n")

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
        updated_inventory_model = Inventory.find(created_inventory.id)
        assert updated_inventory_model is not None
        results, updated_inventory = updated_inventory_model.into_thrift()
        assert is_ok(results)
        assert updated_inventory.max_entries == 20
        assert updated_inventory.max_volume == 1000.0
        print(f"  ✓ Verified updates in database\n")

        print("=" * 60)
        print("✓ All InventoryService tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed with error:")
        print(f"  {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    setUpModule()
    try:
        run_all_tests()
    finally:
        tearDownModule()
