#!/usr/bin/env python3
"""
Simple test script for ItemService to verify basic functionality.
"""
import sys
sys.path.append('../../gen-py')
sys.path.append('..')

from services.item_service import ItemServiceHandler
from db import DB
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

def test_item_service():
    print("=" * 60)
    print("ItemService Test Suite")
    print("=" * 60)

    # Initialize database connection
    db = DB(host='localhost', user='admin', password='minda')
    db.connect()
    database = 'gamedb_test_itemservice'

    # Setup test database
    print("\nSetting up test database...")
    cursor = db.connection.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {database}")

    for stmt in db.get_items_table_sql(database):
        cursor.execute(stmt)
    for stmt in db.get_item_blueprints_table_sql(database):
        cursor.execute(stmt)
    for stmt in db.get_item_blueprint_components_table_sql(database):
        cursor.execute(stmt)
    for stmt in db.get_attributes_table_sql(database):
        cursor.execute(stmt)
    for stmt in db.get_attribute_owners_table_sql(database):
        cursor.execute(stmt)

    db.connection.commit()
    cursor.close()
    print("✓ Database setup complete\n")

    # Initialize service
    service = ItemServiceHandler(db, database)

    # Test describe()
    print("Testing describe() method...")
    metadata = service.describe()
    assert metadata.service_name == "ItemService"
    assert metadata.version == "1.0"
    assert len(metadata.methods) == 4  # create, load, save, destroy
    assert len(metadata.enums) > 0
    print(f"✓ Service metadata: {metadata.service_name} v{metadata.version}")
    print(f"✓ Methods: {', '.join([m.method_name for m in metadata.methods])}\n")

    # Test create()
    print("Testing create() method...")
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
    assert is_ok(create_response.results), f"Create failed: {create_response.results[0].message}"
    assert create_response.response_data is not None
    assert create_response.response_data.create_item.item.id is not None
    item_id = create_response.response_data.create_item.item.id
    print(f"✓ Created item with id={item_id}\n")

    # Test load()
    print("Testing load() method...")
    load_request = ItemRequest(
        data=ItemRequestData(
            load_item=LoadItemRequestData(item_id=item_id),
        ),
    )

    load_response = service.load(load_request)
    assert is_ok(load_response.results), f"Load failed: {load_response.results[0].message}"
    assert load_response.response_data is not None
    loaded_item = load_response.response_data.load_item.item
    assert loaded_item.id == item_id
    assert loaded_item.internal_name == "test_iron_ore"
    assert loaded_item.item_type == ItemType.RAWMATERIAL
    print(f"✓ Loaded item: {loaded_item.internal_name}\n")

    # Test save() (update)
    print("Testing save() method (update)...")
    loaded_item.internal_name = "test_iron_ore_refined"
    loaded_item.item_type = ItemType.REFINEDMATERIAL
    loaded_item.max_stack_size = 500

    save_request = ItemRequest(
        data=ItemRequestData(
            save_item=SaveItemRequestData(item=loaded_item),
        ),
    )

    save_response = service.save(save_request)
    assert is_ok(save_response.results), f"Save failed: {save_response.results[0].message}"
    assert save_response.response_data is not None
    print(f"✓ Updated item: {save_response.response_data.save_item.item.internal_name}\n")

    # Verify update
    print("Verifying update...")
    load_response2 = service.load(load_request)
    assert is_ok(load_response2.results)
    updated_item = load_response2.response_data.load_item.item
    assert updated_item.internal_name == "test_iron_ore_refined"
    assert updated_item.item_type == ItemType.REFINEDMATERIAL
    assert updated_item.max_stack_size == 500
    print("✓ Update verified\n")

    # Test destroy()
    print("Testing destroy() method...")
    destroy_request = ItemRequest(
        data=ItemRequestData(
            destroy_item=DestroyItemRequestData(item_id=item_id),
        ),
    )

    destroy_response = service.destroy(destroy_request)
    assert is_ok(destroy_response.results), f"Destroy failed: {destroy_response.results[0].message}"
    print(f"✓ Destroyed item id={item_id}\n")

    # Verify destroy
    print("Verifying destroy...")
    load_response3 = service.load(load_request)
    assert load_response3.results[0].status == StatusType.FAILURE
    assert load_response3.response_data is None
    print("✓ Destroy verified: item no longer exists\n")

    # Cleanup
    print("Cleaning up test database...")
    cursor = db.connection.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {database}")
    db.connection.commit()
    cursor.close()
    print("✓ Cleanup complete\n")

    print("=" * 60)
    print("All ItemService tests passed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_item_service()
