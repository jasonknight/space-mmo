import sys
import os
import mysql.connector

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../gen-py"))

from models.mobile_item_model import MobileItemModel
from game.ttypes import (
    ItemBlueprint,
    ItemBlueprintComponent,
    MobileItem,
    ItemType,
    Attribute,
    AttributeType,
    ItemVector3,
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

    # Create mobile_item_blueprints table
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS {database_name}.mobile_item_blueprints ("
        f"id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        f"bake_time_ms BIGINT NOT NULL"
        f");"
    )

    # Create mobile_item_blueprint_components table
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS {database_name}.mobile_item_blueprint_components ("
        f"id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        f"mobile_item_blueprint_id BIGINT NOT NULL, "
        f"component_item_id BIGINT NOT NULL, "
        f"ratio DOUBLE NOT NULL, "
        f"FOREIGN KEY (mobile_item_blueprint_id) REFERENCES {database_name}.mobile_item_blueprints(id)"
        f");"
    )

    # Create mobile_items table
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS {database_name}.mobile_items ("
        f"id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        f"item_id BIGINT NOT NULL, "
        f"mobile_id BIGINT NOT NULL, "
        f"internal_name VARCHAR(255) NOT NULL, "
        f"max_stack_size BIGINT, "
        f"item_type VARCHAR(50) NOT NULL, "
        f"blueprint_id BIGINT"
        f");"
    )

    # Create mobile_item_attributes table
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS {database_name}.mobile_item_attributes ("
        f"id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        f"mobile_item_id BIGINT NOT NULL, "
        f"internal_name VARCHAR(255) NOT NULL, "
        f"visible BOOLEAN NOT NULL, "
        f"attribute_type VARCHAR(50) NOT NULL, "
        f"bool_value BOOLEAN, "
        f"double_value DOUBLE, "
        f"vector3_x DOUBLE, "
        f"vector3_y DOUBLE, "
        f"vector3_z DOUBLE, "
        f"asset_id BIGINT, "
        f"FOREIGN KEY (mobile_item_id) REFERENCES {database_name}.mobile_items(id)"
        f");"
    )

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


def test_mobile_item(
    host: str,
    user: str,
    password: str,
    database_name: str,
):
    """Test MobileItem save and load."""
    print("Testing MobileItem...")

    # Create mobile item model
    mobile_item_model = MobileItemModel(host, user, password, database_name)

    # Create blueprint
    components = {
        201: ItemBlueprintComponent(ratio=0.6, item_id=201),
        202: ItemBlueprintComponent(ratio=0.8, item_id=202),
    }
    blueprint = ItemBlueprint(
        id=None,
        components=components,
        bake_time_ms=3000,
    )

    # Create mobile item with attributes
    attributes = {
        AttributeType.QUANTITY: Attribute(
            id=None,
            internal_name="item_quantity",
            visible=True,
            value=100.0,
            attribute_type=AttributeType.QUANTITY,
            owner=None,
        ),
        AttributeType.VOLUME: Attribute(
            id=None,
            internal_name="item_volume",
            visible=True,
            value=50.5,
            attribute_type=AttributeType.VOLUME,
            owner=None,
        ),
    }

    mobile_item = MobileItem(
        id=None,
        item_id=1001,
        mobile_id=5001,
        internal_name="iron_ore_instance",
        attributes=attributes,
        max_stack_size=500,
        item_type=ItemType.RAWMATERIAL,
        blueprint=blueprint,
    )

    # Save mobile item
    save_results = mobile_item_model.save(mobile_item)
    assert is_ok(save_results), f"Failed to save MobileItem: {save_results[0].message}"
    print(f"  ✓ Saved: {save_results[0].message}")

    # Load mobile item
    load_result, loaded_mobile_item = mobile_item_model.load(mobile_item.id)
    assert is_true(load_result), f"Failed to load MobileItem: {load_result.message}"
    print(f"  ✓ Loaded: {load_result.message}")

    # Compare
    assert loaded_mobile_item.id == mobile_item.id, "ID mismatch"
    assert loaded_mobile_item.item_id == mobile_item.item_id, "item_id mismatch"
    assert loaded_mobile_item.mobile_id == mobile_item.mobile_id, "mobile_id mismatch"
    assert loaded_mobile_item.internal_name == mobile_item.internal_name, (
        "internal_name mismatch"
    )
    assert loaded_mobile_item.max_stack_size == mobile_item.max_stack_size, (
        "max_stack_size mismatch"
    )
    assert loaded_mobile_item.item_type == mobile_item.item_type, "item_type mismatch"

    # Compare blueprint
    assert loaded_mobile_item.blueprint is not None, "Blueprint is None"
    assert loaded_mobile_item.blueprint.id == blueprint.id, "Blueprint ID mismatch"
    assert loaded_mobile_item.blueprint.bake_time_ms == blueprint.bake_time_ms, (
        "Blueprint bake_time_ms mismatch"
    )

    # Compare attributes
    assert len(loaded_mobile_item.attributes) == len(mobile_item.attributes), (
        "Attributes count mismatch"
    )

    # Test update
    print("  Testing update...")
    loaded_mobile_item.internal_name = "silver_ore_instance"
    loaded_mobile_item.max_stack_size = 1000
    loaded_mobile_item.attributes[AttributeType.QUANTITY].value = 200.0

    update_results = mobile_item_model.save(loaded_mobile_item)
    assert is_ok(update_results), (
        f"Failed to update MobileItem: {update_results[0].message}"
    )
    print(f"  ✓ Updated: {update_results[0].message}")

    # Load again and verify updates
    load_result2, updated_mobile_item = mobile_item_model.load(loaded_mobile_item.id)
    assert is_true(load_result2), (
        f"Failed to load updated MobileItem: {load_result2.message}"
    )
    assert updated_mobile_item.internal_name == "silver_ore_instance", (
        "Updated internal_name mismatch"
    )
    assert updated_mobile_item.max_stack_size == 1000, "Updated max_stack_size mismatch"
    print("  ✓ Update verified")

    # Test destroy
    print("  Testing destroy...")
    destroy_results = mobile_item_model.destroy(loaded_mobile_item.id)
    assert is_ok(destroy_results), (
        f"Failed to destroy MobileItem: {destroy_results[0].message}"
    )
    print(f"  ✓ Destroyed: {destroy_results[0].message}")

    # Verify load fails after destroy
    load_result3, destroyed_mobile_item = mobile_item_model.load(loaded_mobile_item.id)
    assert not is_true(load_result3), "Load should fail after destroy"
    assert destroyed_mobile_item is None, "Destroyed mobile item should be None"
    assert load_result3.error_code == GameError.DB_RECORD_NOT_FOUND, (
        f"Expected DB_RECORD_NOT_FOUND, got {load_result3.error_code}"
    )
    print("  ✓ Destroy verified: load failed with DB_RECORD_NOT_FOUND")

    print("  ✓ All assertions passed for MobileItem\n")

    # Disconnect
    mobile_item_model.disconnect()


def test_search_mobile_item(
    host: str,
    user: str,
    password: str,
    database_name: str,
):
    """Test MobileItem search functionality with pagination and search."""
    print("Testing MobileItem search functionality...")

    import random
    import string

    # Create mobile item model
    mobile_item_model = MobileItemModel(host, user, password, database_name)

    # Generate random string helper
    def random_string(length=10):
        return "".join(random.choices(string.ascii_letters, k=length))

    # Create 100 mobile items with random data
    print("  Creating 100 mobile items...")
    created_mobile_items = []
    search_test_names = []

    for i in range(100):
        internal_name = f"mobile_item_{random_string(8)}"

        # Save some names for search testing
        if i < 5:
            search_test_names.append(internal_name)

        mobile_item = MobileItem(
            id=None,
            item_id=1000 + i,
            mobile_id=5000 + i,
            internal_name=internal_name,
            attributes={},
            max_stack_size=random.randint(1, 100),
            item_type=random.choice(
                [ItemType.VIRTUAL, ItemType.WEAPON, ItemType.RAWMATERIAL],
            ),
            blueprint=None,
        )

        save_results = mobile_item_model.save(mobile_item)
        assert is_ok(save_results), (
            f"Failed to save mobile item {i}: {save_results[0].message}"
        )
        created_mobile_items.append(mobile_item)

    print(f"  ✓ Created {len(created_mobile_items)} mobile items")

    # Test pagination - iterate through all pages with 10 results per page
    print("  Testing pagination (10 results per page)...")
    all_paginated_mobile_items = []
    page = 0
    results_per_page = 10

    while True:
        result, mobile_items, total_count = mobile_item_model.search(
            page,
            results_per_page,
        )
        assert is_true(result), (
            f"Failed to search mobile items page {page}: {result.message}"
        )

        if not mobile_items:
            break

        all_paginated_mobile_items.extend(mobile_items)
        print(
            f"    Page {page}: retrieved {len(mobile_items)} mobile items (total: {total_count})"
        )

        # Check if this is the last page
        if len(all_paginated_mobile_items) >= total_count:
            break

        page += 1

    assert len(all_paginated_mobile_items) == 100, (
        f"Expected 100 mobile items, got {len(all_paginated_mobile_items)}"
    )
    print(
        f"  ✓ Pagination test passed: retrieved all {len(all_paginated_mobile_items)} mobile items across {page + 1} pages"
    )

    # Test search on internal_name
    print("  Testing search on internal_name...")
    search_name = search_test_names[0]
    result, mobile_items, total_count = mobile_item_model.search(
        0,
        100,
        search_string=search_name,
    )
    assert is_true(result), f"Failed to search mobile items: {result.message}"
    assert len(mobile_items) >= 1, (
        f"Expected at least 1 mobile item matching '{search_name}', got {len(mobile_items)}"
    )
    assert any(mi.internal_name == search_name for mi in mobile_items), (
        f"Expected to find mobile item with internal_name '{search_name}'"
    )
    print(
        f"  ✓ Search on internal_name '{search_name}' found {len(mobile_items)} mobile item(s)"
    )

    # Test partial search
    print("  Testing partial search...")
    partial_search = "mobile_item_"
    result, mobile_items, total_count = mobile_item_model.search(
        0,
        100,
        search_string=partial_search,
    )
    assert is_true(result), f"Failed to search mobile items: {result.message}"
    assert len(mobile_items) == 100, (
        f"Expected 100 mobile items matching '{partial_search}', got {len(mobile_items)}"
    )
    print(
        f"  ✓ Partial search '{partial_search}' found {len(mobile_items)} mobile item(s)"
    )

    print("  ✓ All search tests passed for MobileItem\n")

    # Disconnect
    mobile_item_model.disconnect()


def main():
    """Run all tests."""
    # Database configuration
    host = "localhost"
    user = "admin"
    password = "minda"
    database_name = "test_mobile_item_db"

    print("=" * 60)
    print("MobileItem Test Suite")
    print("=" * 60)
    print()

    try:
        # Setup database and tables
        print("Setting up test database...")
        setup_database(host, user, password, database_name)
        print("✓ Database setup complete\n")

        # Run tests
        test_mobile_item(host, user, password, database_name)
        test_search_mobile_item(host, user, password, database_name)

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
