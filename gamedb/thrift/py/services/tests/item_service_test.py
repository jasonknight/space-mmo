#!/usr/bin/env python3
"""
Simple test script for ItemService to verify basic functionality.
"""

import sys
import os
import uuid

thrift_gen_path = "/vagrant/gamedb/thrift/gen-py"
if thrift_gen_path not in sys.path:
    sys.path.insert(0, thrift_gen_path)

py_path = "/vagrant/gamedb/thrift/py"
if py_path not in sys.path:
    sys.path.insert(0, py_path)

from dotenv import load_dotenv

load_dotenv()

import mysql.connector
from services.item_service import ItemServiceHandler
from game.ttypes import (
    ItemRequest,
    ItemRequestData,
    CreateItemRequestData,
    LoadItemRequestData,
    SaveItemRequestData,
    DestroyItemRequestData,
    Item,
    ItemType,
    StatusType,
)
from common import is_ok
from db_models.models import (
    Item as ItemModel,
    Attribute,
    AttributeOwner,
)

TEST_DATABASE = None


def setUpModule():
    """Set up test database before running tests."""
    global TEST_DATABASE
    TEST_DATABASE = f"gamedb_test_{uuid.uuid4().hex[:8]}"

    connection = mysql.connector.connect(
        host="localhost",
        user="admin",
        password="minda",
        auth_plugin="mysql_native_password",
        ssl_disabled=True,
        use_pure=True,
    )
    cursor = connection.cursor()

    cursor.execute(f"CREATE DATABASE `{TEST_DATABASE}`")
    connection.database = TEST_DATABASE

    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    cursor.execute(ItemModel.CREATE_TABLE_STATEMENT)
    cursor.execute(Attribute.CREATE_TABLE_STATEMENT)
    cursor.execute(AttributeOwner.CREATE_TABLE_STATEMENT)
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")

    connection.commit()
    cursor.close()
    connection.close()

    os.environ["DB_DATABASE"] = TEST_DATABASE
    print(f"\n✓ Test database '{TEST_DATABASE}' created")


def tearDownModule():
    """Tear down test database after running tests."""
    global TEST_DATABASE

    if TEST_DATABASE:
        connection = mysql.connector.connect(
            host="localhost",
            user="admin",
            password="minda",
            auth_plugin="mysql_native_password",
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS `{TEST_DATABASE}`")
        connection.commit()
        cursor.close()
        connection.close()
        print(f"\n✓ Test database '{TEST_DATABASE}' dropped")


def test_item_service():
    print("=" * 60)
    print("ItemService Test Suite")
    print("=" * 60)

    service = ItemServiceHandler()

    print("\nTesting create() method...")
    item = Item(
        id=None,
        internal_name="test_iron_ore",
        attributes={},
        max_stack_size=1000,
        item_type=ItemType.RAWMATERIAL,
    )

    create_request = ItemRequest(
        data=ItemRequestData(
            create_item=CreateItemRequestData(item=item),
        ),
    )

    create_response = service.create(create_request)
    assert is_ok(create_response.results), (
        f"Create failed: {create_response.results[0].message}"
    )
    assert create_response.response_data is not None
    assert create_response.response_data.create_item.item.id is not None
    item_id = create_response.response_data.create_item.item.id
    print(f"✓ Created item with id={item_id}")

    print("\nTesting load() method...")
    load_request = ItemRequest(
        data=ItemRequestData(
            load_item=LoadItemRequestData(item_id=item_id),
        ),
    )

    load_response = service.load(load_request)
    assert is_ok(load_response.results), (
        f"Load failed: {load_response.results[0].message}"
    )
    assert load_response.response_data is not None
    loaded_item = load_response.response_data.load_item.item
    assert loaded_item.id == item_id
    assert loaded_item.internal_name == "test_iron_ore"
    assert loaded_item.item_type == ItemType.RAWMATERIAL
    print(f"✓ Loaded item: {loaded_item.internal_name}")

    print("\nTesting save() method (update)...")
    loaded_item.internal_name = "test_iron_ore_refined"
    loaded_item.item_type = ItemType.REFINEDMATERIAL
    loaded_item.max_stack_size = 500

    save_request = ItemRequest(
        data=ItemRequestData(
            save_item=SaveItemRequestData(item=loaded_item),
        ),
    )

    save_response = service.save(save_request)
    assert is_ok(save_response.results), (
        f"Save failed: {save_response.results[0].message}"
    )
    assert save_response.response_data is not None
    print(
        f"✓ Updated item: {save_response.response_data.save_item.item.internal_name}"
    )

    print("\nVerifying update...")
    load_response2 = service.load(load_request)
    assert is_ok(load_response2.results)
    updated_item = load_response2.response_data.load_item.item
    assert updated_item.internal_name == "test_iron_ore_refined"
    assert updated_item.item_type == ItemType.REFINEDMATERIAL
    assert updated_item.max_stack_size == 500
    print("✓ Update verified")

    print("\nTesting destroy() method...")
    destroy_request = ItemRequest(
        data=ItemRequestData(
            destroy_item=DestroyItemRequestData(item_id=item_id),
        ),
    )

    destroy_response = service.destroy(destroy_request)
    assert is_ok(destroy_response.results), (
        f"Destroy failed: {destroy_response.results[0].message}"
    )
    print(f"✓ Destroyed item id={item_id}")

    print("\nVerifying destroy...")
    load_response3 = service.load(load_request)
    assert load_response3.results[0].status == StatusType.FAILURE
    assert load_response3.response_data is None
    print("✓ Destroy verified: item no longer exists")

    print("\n" + "=" * 60)
    print("All ItemService tests passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    setUpModule()
    try:
        test_item_service()
    finally:
        tearDownModule()
