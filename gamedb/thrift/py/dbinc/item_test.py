import sys
import os
import mysql.connector

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../gen-py"))

from models.blueprint_model import BlueprintModel
from models.item_model import ItemModel
from game.ttypes import (
    ItemBlueprint,
    ItemBlueprintComponent,
    Item,
    ItemType,
    Attribute,
    AttributeType,
    AttributeValue,
    ItemVector3,
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
    cursor.execute(get_table_sql("item_blueprints", database_name))
    cursor.execute(get_table_sql("item_blueprint_components", database_name))
    cursor.execute(get_table_sql("items", database_name))
    cursor.execute(get_table_sql("attributes", database_name))
    cursor.execute(get_table_sql("attribute_owners", database_name))

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


def test_item_blueprint(
    host: str,
    user: str,
    password: str,
    database_name: str,
):
    """Test ItemBlueprint save and load."""
    print("Testing ItemBlueprint...")

    # Create blueprint model
    blueprint_model = BlueprintModel(host, user, password, database_name)

    # Create stub with 3 components
    components = {
        101: ItemBlueprintComponent(ratio=0.5, item_id=101),
        102: ItemBlueprintComponent(ratio=0.75, item_id=102),
        103: ItemBlueprintComponent(ratio=1.0, item_id=103),
    }

    blueprint = ItemBlueprint(
        id=None,
        components=components,
        bake_time_ms=5000,
    )

    # Save blueprint
    save_results = blueprint_model.save(blueprint)
    assert is_ok(save_results), (
        f"Failed to save ItemBlueprint: {save_results[0].message}"
    )
    print(f"  ✓ Saved: {save_results[0].message}")

    # Load blueprint
    load_result, loaded_blueprint = blueprint_model.load(blueprint.id)
    assert is_true(load_result), f"Failed to load ItemBlueprint: {load_result.message}"
    print(f"  ✓ Loaded: {load_result.message}")

    # Compare
    assert loaded_blueprint.id == blueprint.id, "ID mismatch"
    assert loaded_blueprint.bake_time_ms == blueprint.bake_time_ms, (
        "bake_time_ms mismatch"
    )
    assert len(loaded_blueprint.components) == len(blueprint.components), (
        "Components count mismatch"
    )

    for item_id, component in blueprint.components.items():
        assert item_id in loaded_blueprint.components, f"Component {item_id} missing"
        loaded_comp = loaded_blueprint.components[item_id]
        assert loaded_comp.ratio == component.ratio, (
            f"Component {item_id} ratio mismatch"
        )
        assert loaded_comp.item_id == component.item_id, (
            f"Component {item_id} item_id mismatch"
        )

    # Test update
    print("  Testing update...")
    loaded_blueprint.bake_time_ms = 7500
    loaded_blueprint.components = {
        104: ItemBlueprintComponent(ratio=0.9, item_id=104),
        105: ItemBlueprintComponent(ratio=0.6, item_id=105),
    }

    update_results = blueprint_model.save(loaded_blueprint)
    assert is_ok(update_results), (
        f"Failed to update ItemBlueprint: {update_results[0].message}"
    )
    print(f"  ✓ Updated: {update_results[0].message}")

    # Load again and verify updates
    load_result2, updated_blueprint = blueprint_model.load(blueprint.id)
    assert is_true(load_result2), (
        f"Failed to load updated ItemBlueprint: {load_result2.message}"
    )
    assert updated_blueprint.bake_time_ms == 7500, "Updated bake_time_ms mismatch"
    assert len(updated_blueprint.components) == 2, "Updated components count mismatch"
    assert 104 in updated_blueprint.components, "Component 104 missing after update"
    assert 105 in updated_blueprint.components, "Component 105 missing after update"
    print("  ✓ Update verified")

    # Test destroy
    print("  Testing destroy...")
    destroy_results = blueprint_model.destroy(blueprint.id)
    assert is_ok(destroy_results), (
        f"Failed to destroy ItemBlueprint: {destroy_results[0].message}"
    )
    print(f"  ✓ Destroyed: {destroy_results[0].message}")

    # Verify load fails after destroy
    load_result3, destroyed_blueprint = blueprint_model.load(blueprint.id)
    assert not is_true(load_result3), "Load should fail after destroy"
    assert destroyed_blueprint is None, "Destroyed blueprint should be None"
    assert load_result3.error_code == GameError.DB_RECORD_NOT_FOUND, (
        f"Expected DB_RECORD_NOT_FOUND, got {load_result3.error_code}"
    )
    print("  ✓ Destroy verified: load failed with DB_RECORD_NOT_FOUND")

    print("  ✓ All assertions passed for ItemBlueprint\n")

    # Disconnect
    blueprint_model.disconnect()


def test_item(
    host: str,
    user: str,
    password: str,
    database_name: str,
):
    """Test Item save and load."""
    print("Testing Item...")

    # Create item model
    item_model = ItemModel(host, user, password, database_name)

    # First create and save a blueprint for the item
    components = {
        201: ItemBlueprintComponent(ratio=0.6, item_id=201),
        202: ItemBlueprintComponent(ratio=0.8, item_id=202),
    }
    blueprint = ItemBlueprint(
        id=None,
        components=components,
        bake_time_ms=3000,
    )

    # Create item with attributes
    attributes = {
        AttributeType.QUANTITY: Attribute(
            id=None,
            internal_name="item_quantity",
            visible=True,
            value=100.0,
            attribute_type=AttributeType.QUANTITY,
            owner=1000,
        ),
        AttributeType.VOLUME: Attribute(
            id=None,
            internal_name="item_volume",
            visible=True,
            value=50.5,
            attribute_type=AttributeType.VOLUME,
            owner=1000,
        ),
    }

    item = Item(
        id=None,
        internal_name="iron_ore",
        attributes=attributes,
        max_stack_size=500,
        item_type=ItemType.RAWMATERIAL,
        blueprint=blueprint,
    )

    # Save item (which will also save blueprint)
    save_results = item_model.save(item)
    assert is_ok(save_results), f"Failed to save Item: {save_results[0].message}"
    print(f"  ✓ Saved: {save_results[0].message}")

    # Load item
    load_result, loaded_item = item_model.load(item.id)
    assert is_true(load_result), f"Failed to load Item: {load_result.message}"
    print(f"  ✓ Loaded: {load_result.message}")

    # Compare
    assert loaded_item.id == item.id, "ID mismatch"
    assert loaded_item.internal_name == item.internal_name, "internal_name mismatch"
    assert loaded_item.max_stack_size == item.max_stack_size, "max_stack_size mismatch"
    assert loaded_item.item_type == item.item_type, "item_type mismatch"

    # Compare blueprint
    assert loaded_item.blueprint is not None, "Blueprint is None"
    assert loaded_item.blueprint.id == blueprint.id, "Blueprint ID mismatch"
    assert loaded_item.blueprint.bake_time_ms == blueprint.bake_time_ms, (
        "Blueprint bake_time_ms mismatch"
    )

    # Compare attributes
    assert len(loaded_item.attributes) == len(item.attributes), (
        "Attributes count mismatch"
    )

    # Test update
    print("  Testing update...")
    loaded_item.internal_name = "silver_ore"
    loaded_item.max_stack_size = 1000
    loaded_item.attributes[AttributeType.QUANTITY].value = 200.0

    update_results = item_model.save(loaded_item)
    assert is_ok(update_results), f"Failed to update Item: {update_results[0].message}"
    print(f"  ✓ Updated: {update_results[0].message}")

    # Load again and verify updates
    load_result2, updated_item = item_model.load(loaded_item.id)
    assert is_true(load_result2), f"Failed to load updated Item: {load_result2.message}"
    assert updated_item.internal_name == "silver_ore", "Updated internal_name mismatch"
    assert updated_item.max_stack_size == 1000, "Updated max_stack_size mismatch"
    print("  ✓ Update verified")

    # Test destroy
    print("  Testing destroy...")
    destroy_results = item_model.destroy(loaded_item.id)
    assert is_ok(destroy_results), (
        f"Failed to destroy Item: {destroy_results[0].message}"
    )
    print(f"  ✓ Destroyed: {destroy_results[0].message}")

    # Verify load fails after destroy
    load_result3, destroyed_item = item_model.load(loaded_item.id)
    assert not is_true(load_result3), "Load should fail after destroy"
    assert destroyed_item is None, "Destroyed item should be None"
    assert load_result3.error_code == GameError.DB_RECORD_NOT_FOUND, (
        f"Expected DB_RECORD_NOT_FOUND, got {load_result3.error_code}"
    )
    print("  ✓ Destroy verified: load failed with DB_RECORD_NOT_FOUND")

    print("  ✓ All assertions passed for Item\n")

    # Disconnect
    item_model.disconnect()


def test_search_item(
    host: str,
    user: str,
    password: str,
    database_name: str,
):
    """Test Item search functionality with pagination and search."""
    print("Testing Item search functionality...")

    import random
    import string

    # Create item model
    item_model = ItemModel(host, user, password, database_name)

    # Generate random string helper
    def random_string(length=10):
        return "".join(random.choices(string.ascii_letters, k=length))

    # Create 100 items with random data
    print("  Creating 100 items...")
    created_items = []
    search_test_names = []

    for i in range(100):
        internal_name = f"item_{random_string(8)}"

        # Save some names for search testing
        if i < 5:
            search_test_names.append(internal_name)

        item = Item(
            id=None,
            internal_name=internal_name,
            attributes={},
            max_stack_size=random.randint(1, 100),
            item_type=random.choice(
                [ItemType.VIRTUAL, ItemType.WEAPON, ItemType.RAWMATERIAL],
            ),
            blueprint=None,
        )

        save_results = item_model.save(item)
        assert is_ok(save_results), (
            f"Failed to save item {i}: {save_results[0].message}"
        )
        created_items.append(item)

    print(f"  ✓ Created {len(created_items)} items")

    # Test pagination - iterate through all pages with 10 results per page
    print("  Testing pagination (10 results per page)...")
    all_paginated_items = []
    page = 0
    results_per_page = 10

    while True:
        result, items, total_count = item_model.search(
            page,
            results_per_page,
        )
        assert is_true(result), f"Failed to search items page {page}: {result.message}"

        if not items:
            break

        all_paginated_items.extend(items)
        print(f"    Page {page}: retrieved {len(items)} items (total: {total_count})")

        # Check if this is the last page
        if len(all_paginated_items) >= total_count:
            break

        page += 1

    assert len(all_paginated_items) == 100, (
        f"Expected 100 items, got {len(all_paginated_items)}"
    )
    print(
        f"  ✓ Pagination test passed: retrieved all {len(all_paginated_items)} items across {page + 1} pages"
    )

    # Test search on internal_name
    print("  Testing search on internal_name...")
    search_name = search_test_names[0]
    result, items, total_count = item_model.search(
        0,
        100,
        search_string=search_name,
    )
    assert is_true(result), f"Failed to search items: {result.message}"
    assert len(items) >= 1, (
        f"Expected at least 1 item matching '{search_name}', got {len(items)}"
    )
    assert any(item.internal_name == search_name for item in items), (
        f"Expected to find item with internal_name '{search_name}'"
    )
    print(f"  ✓ Search on internal_name '{search_name}' found {len(items)} item(s)")

    # Test partial search
    print("  Testing partial search...")
    partial_search = "item_"
    result, items, total_count = item_model.search(
        0,
        100,
        search_string=partial_search,
    )
    assert is_true(result), f"Failed to search items: {result.message}"
    assert len(items) == 100, (
        f"Expected 100 items matching '{partial_search}', got {len(items)}"
    )
    print(f"  ✓ Partial search '{partial_search}' found {len(items)} item(s)")

    print("  ✓ All search tests passed for Item\n")

    # Disconnect
    item_model.disconnect()


def main():
    """Run all tests."""
    # Database configuration
    host = "localhost"
    user = "admin"
    password = "minda"
    database_name = "test_item_db"

    print("=" * 60)
    print("Item Test Suite")
    print("=" * 60)
    print()

    try:
        # Setup database and tables
        print("Setting up test database...")
        setup_database(host, user, password, database_name)
        print("✓ Database setup complete\n")

        # Run tests
        test_item_blueprint(host, user, password, database_name)
        test_item(host, user, password, database_name)
        test_search_item(host, user, password, database_name)

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
