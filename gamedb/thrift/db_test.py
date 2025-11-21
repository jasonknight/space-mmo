import sys
sys.path.append('gen-py')

from db import DB
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
    Inventory,
    InventoryEntry,
    Mobile,
    MobileType,
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
    for stmt in db.get_item_blueprints_table_sql(database_name):
        cursor.execute(stmt)

    for stmt in db.get_item_blueprint_components_table_sql(database_name):
        cursor.execute(stmt)

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

    for stmt in db.get_mobiles_table_sql(database_name):
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


def test_item_blueprint(db: DB, database_name: str):
    """Test ItemBlueprint save and load."""
    print("Testing ItemBlueprint...")

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
    save_results = db.save_item_blueprint(database_name, blueprint)
    assert is_ok(save_results), f"Failed to save ItemBlueprint: {save_results[0].message}"
    print(f"  ✓ Saved: {save_results[0].message}")

    # Load blueprint
    load_result, loaded_blueprint = db.load_item_blueprint(database_name, blueprint.id)
    assert is_true(load_result), f"Failed to load ItemBlueprint: {load_result.message}"
    print(f"  ✓ Loaded: {load_result.message}")

    # Compare
    assert loaded_blueprint.id == blueprint.id, "ID mismatch"
    assert loaded_blueprint.bake_time_ms == blueprint.bake_time_ms, "bake_time_ms mismatch"
    assert len(loaded_blueprint.components) == len(blueprint.components), "Components count mismatch"

    for item_id, component in blueprint.components.items():
        assert item_id in loaded_blueprint.components, f"Component {item_id} missing"
        loaded_comp = loaded_blueprint.components[item_id]
        assert loaded_comp.ratio == component.ratio, f"Component {item_id} ratio mismatch"
        assert loaded_comp.item_id == component.item_id, f"Component {item_id} item_id mismatch"

    # Test update
    print("  Testing update...")
    loaded_blueprint.bake_time_ms = 7500
    loaded_blueprint.components = {
        104: ItemBlueprintComponent(ratio=0.9, item_id=104),
        105: ItemBlueprintComponent(ratio=0.6, item_id=105),
    }

    update_results = db.save_item_blueprint(database_name, loaded_blueprint)
    assert is_ok(update_results), f"Failed to update ItemBlueprint: {update_results[0].message}"
    print(f"  ✓ Updated: {update_results[0].message}")

    # Load again and verify updates
    load_result2, updated_blueprint = db.load_item_blueprint(database_name, blueprint.id)
    assert is_true(load_result2), f"Failed to load updated ItemBlueprint: {load_result2.message}"
    assert updated_blueprint.bake_time_ms == 7500, "Updated bake_time_ms mismatch"
    assert len(updated_blueprint.components) == 2, "Updated components count mismatch"
    assert 104 in updated_blueprint.components, "Component 104 missing after update"
    assert 105 in updated_blueprint.components, "Component 105 missing after update"
    print("  ✓ Update verified")

    # Test destroy
    print("  Testing destroy...")
    destroy_results = db.destroy_item_blueprint(database_name, blueprint.id)
    assert is_ok(destroy_results), f"Failed to destroy ItemBlueprint: {destroy_results[0].message}"
    print(f"  ✓ Destroyed: {destroy_results[0].message}")

    # Verify load fails after destroy
    load_result3, destroyed_blueprint = db.load_item_blueprint(database_name, blueprint.id)
    assert not is_true(load_result3), "Load should fail after destroy"
    assert destroyed_blueprint is None, "Destroyed blueprint should be None"
    assert load_result3.error_code == GameError.DB_RECORD_NOT_FOUND, f"Expected DB_RECORD_NOT_FOUND, got {load_result3.error_code}"
    print("  ✓ Destroy verified: load failed with DB_RECORD_NOT_FOUND")

    print("  ✓ All assertions passed for ItemBlueprint\n")


def test_attribute(db: DB, database_name: str):
    """Test Attribute save and load with different value types."""
    print("Testing Attribute...")

    # Test with double value
    from game.ttypes import Owner

    owner1 = Owner()
    owner1.mobile_id = 12345

    attribute1 = Attribute(
        id=None,
        internal_name="test_purity",
        visible=True,
        value=0.95,
        attribute_type=AttributeType.PURITY,
        owner=owner1,
    )

    save_results = db.save_attribute(database_name, attribute1)
    assert is_ok(save_results), f"Failed to save Attribute: {save_results[0].message}"
    print(f"  ✓ Saved attribute1: {save_results[0].message}")

    load_result, loaded_attr1 = db.load_attribute(database_name, attribute1.id)
    assert is_true(load_result), f"Failed to load Attribute: {load_result.message}"
    print(f"  ✓ Loaded attribute1: {load_result.message}")

    assert loaded_attr1.internal_name == attribute1.internal_name, "internal_name mismatch"
    assert loaded_attr1.visible == attribute1.visible, "visible mismatch"
    assert loaded_attr1.attribute_type == attribute1.attribute_type, "attribute_type mismatch"
    print(f"    Debug: Original value={attribute1.value} ({type(attribute1.value)}), Loaded value={loaded_attr1.value} ({type(loaded_attr1.value)})")
    assert loaded_attr1.value == attribute1.value, f"value mismatch: {loaded_attr1.value} != {attribute1.value}"

    # Test with Vector3
    owner2 = Owner()
    owner2.item_it = 67890

    attribute2 = Attribute(
        id=None,
        internal_name="test_position",
        visible=False,
        value=ItemVector3(x=10.5, y=20.3, z=30.7),
        attribute_type=AttributeType.LOCAL_POSITION,
        owner=owner2,
    )

    save_results = db.save_attribute(database_name, attribute2)
    assert is_ok(save_results), f"Failed to save Attribute: {save_results[0].message}"
    print(f"  ✓ Saved attribute2: {save_results[0].message}")

    load_result, loaded_attr2 = db.load_attribute(database_name, attribute2.id)
    assert is_true(load_result), f"Failed to load Attribute: {load_result.message}"
    print(f"  ✓ Loaded attribute2: {load_result.message}")

    assert loaded_attr2.internal_name == attribute2.internal_name, "internal_name mismatch"
    assert loaded_attr2.value.x == attribute2.value.x, "vector3.x mismatch"
    assert loaded_attr2.value.y == attribute2.value.y, "vector3.y mismatch"
    assert loaded_attr2.value.z == attribute2.value.z, "vector3.z mismatch"

    # Test update
    print("  Testing update...")
    loaded_attr2.internal_name = "updated_position"
    loaded_attr2.value = ItemVector3(x=200.0, y=300.0, z=400.0)
    loaded_attr2.visible = True

    update_results = db.save_attribute(database_name, loaded_attr2)
    assert is_ok(update_results), f"Failed to update Attribute: {update_results[0].message}"
    print(f"  ✓ Updated: {update_results[0].message}")

    # Load again and verify updates
    load_result3, updated_attr = db.load_attribute(database_name, loaded_attr2.id)
    assert is_true(load_result3), f"Failed to load updated Attribute: {load_result3.message}"
    assert updated_attr.internal_name == "updated_position", "Updated internal_name mismatch"
    assert updated_attr.visible == True, "Updated visible mismatch"
    assert updated_attr.value.x == 200.0, "Updated vector3.x mismatch"
    print("  ✓ Update verified")

    # Test destroy
    print("  Testing destroy...")
    destroy_results = db.destroy_attribute(database_name, loaded_attr2.id)
    assert is_ok(destroy_results), f"Failed to destroy Attribute: {destroy_results[0].message}"
    print(f"  ✓ Destroyed: {destroy_results[0].message}")

    # Verify load fails after destroy
    load_result4, destroyed_attr = db.load_attribute(database_name, loaded_attr2.id)
    assert not is_true(load_result4), "Load should fail after destroy"
    assert destroyed_attr is None, "Destroyed attribute should be None"
    assert load_result4.error_code == GameError.DB_RECORD_NOT_FOUND, f"Expected DB_RECORD_NOT_FOUND, got {load_result4.error_code}"
    print("  ✓ Destroy verified: load failed with DB_RECORD_NOT_FOUND")

    print("  ✓ All assertions passed for Attribute\n")


def test_item(db: DB, database_name: str):
    """Test Item save and load."""
    print("Testing Item...")

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
    save_results = db.save_item(database_name, item)
    assert is_ok(save_results), f"Failed to save Item: {save_results[0].message}"
    print(f"  ✓ Saved: {save_results[0].message}")

    # Load item
    load_result, loaded_item = db.load_item(database_name, item.id)
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
    assert loaded_item.blueprint.bake_time_ms == blueprint.bake_time_ms, "Blueprint bake_time_ms mismatch"

    # Compare attributes
    assert len(loaded_item.attributes) == len(item.attributes), "Attributes count mismatch"

    # Test update
    print("  Testing update...")
    loaded_item.internal_name = "silver_ore"
    loaded_item.max_stack_size = 1000
    loaded_item.attributes[AttributeType.QUANTITY].value = 200.0

    update_results = db.save_item(database_name, loaded_item)
    assert is_ok(update_results), f"Failed to update Item: {update_results[0].message}"
    print(f"  ✓ Updated: {update_results[0].message}")

    # Load again and verify updates
    load_result2, updated_item = db.load_item(database_name, loaded_item.id)
    assert is_true(load_result2), f"Failed to load updated Item: {load_result2.message}"
    assert updated_item.internal_name == "silver_ore", "Updated internal_name mismatch"
    assert updated_item.max_stack_size == 1000, "Updated max_stack_size mismatch"
    print("  ✓ Update verified")

    # Test destroy
    print("  Testing destroy...")
    destroy_results = db.destroy_item(database_name, loaded_item.id)
    assert is_ok(destroy_results), f"Failed to destroy Item: {destroy_results[0].message}"
    print(f"  ✓ Destroyed: {destroy_results[0].message}")

    # Verify load fails after destroy
    load_result3, destroyed_item = db.load_item(database_name, loaded_item.id)
    assert not is_true(load_result3), "Load should fail after destroy"
    assert destroyed_item is None, "Destroyed item should be None"
    assert load_result3.error_code == GameError.DB_RECORD_NOT_FOUND, f"Expected DB_RECORD_NOT_FOUND, got {load_result3.error_code}"
    print("  ✓ Destroy verified: load failed with DB_RECORD_NOT_FOUND")

    print("  ✓ All assertions passed for Item\n")


def test_inventory(db: DB, database_name: str):
    """Test Inventory save and load."""
    print("Testing Inventory...")

    # Create inventory with 3 entries
    from game.ttypes import Owner

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
    save_results = db.save_inventory(database_name, inventory)
    assert is_ok(save_results), f"Failed to save Inventory: {save_results[0].message}"
    print(f"  ✓ Saved: {save_results[0].message}")

    # Load inventory
    load_result, loaded_inv = db.load_inventory(database_name, inventory.id)
    assert is_true(load_result), f"Failed to load Inventory: {load_result.message}"
    print(f"  ✓ Loaded: {load_result.message}")

    # Compare
    assert loaded_inv.id == inventory.id, "ID mismatch"
    assert loaded_inv.max_entries == inventory.max_entries, "max_entries mismatch"
    assert loaded_inv.max_volume == inventory.max_volume, "max_volume mismatch"
    assert loaded_inv.last_calculated_volume == inventory.last_calculated_volume, "last_calculated_volume mismatch"
    assert len(loaded_inv.entries) == len(inventory.entries), "Entries count mismatch"

    # Compare entries
    for i, entry in enumerate(inventory.entries):
        loaded_entry = loaded_inv.entries[i]
        assert loaded_entry.item_id == entry.item_id, f"Entry {i} item_id mismatch"
        assert loaded_entry.quantity == entry.quantity, f"Entry {i} quantity mismatch"
        assert loaded_entry.is_max_stacked == entry.is_max_stacked, f"Entry {i} is_max_stacked mismatch"

    # Test update
    print("  Testing update...")
    loaded_inv.max_entries = 200
    loaded_inv.max_volume = 2000.0
    loaded_inv.entries = [
        InventoryEntry(item_id=401, quantity=15.0, is_max_stacked=True),
        InventoryEntry(item_id=402, quantity=30.0, is_max_stacked=False),
    ]

    update_results = db.save_inventory(database_name, loaded_inv)
    assert is_ok(update_results), f"Failed to update Inventory: {update_results[0].message}"
    print(f"  ✓ Updated: {update_results[0].message}")

    # Load again and verify updates
    load_result2, updated_inv = db.load_inventory(database_name, loaded_inv.id)
    assert is_true(load_result2), f"Failed to load updated Inventory: {load_result2.message}"
    assert updated_inv.max_entries == 200, "Updated max_entries mismatch"
    assert updated_inv.max_volume == 2000.0, "Updated max_volume mismatch"
    assert len(updated_inv.entries) == 2, "Updated entries count mismatch"
    print("  ✓ Update verified")

    # Test destroy
    print("  Testing destroy...")
    destroy_results = db.destroy_inventory(database_name, loaded_inv.id)
    assert is_ok(destroy_results), f"Failed to destroy Inventory: {destroy_results[0].message}"
    print(f"  ✓ Destroyed: {destroy_results[0].message}")

    # Verify load fails after destroy
    load_result3, destroyed_inv = db.load_inventory(database_name, loaded_inv.id)
    assert not is_true(load_result3), "Load should fail after destroy"
    assert destroyed_inv is None, "Destroyed inventory should be None"
    assert load_result3.error_code == GameError.DB_RECORD_NOT_FOUND, f"Expected DB_RECORD_NOT_FOUND, got {load_result3.error_code}"
    print("  ✓ Destroy verified: load failed with DB_RECORD_NOT_FOUND")

    print("  ✓ All assertions passed for Inventory\n")


def test_mobile(db: DB, database_name: str):
    """Test Mobile save and load."""
    print("Testing Mobile...")

    # Create mobile with attributes
    attributes = {
        AttributeType.TRANSLATED_NAME: Attribute(
            id=None,
            internal_name="player_name",
            visible=True,
            value=12345,
            attribute_type=AttributeType.TRANSLATED_NAME,
            owner=7000,
        ),
        AttributeType.LOCAL_POSITION: Attribute(
            id=None,
            internal_name="player_position",
            visible=False,
            value=ItemVector3(x=100.0, y=50.0, z=200.0),
            attribute_type=AttributeType.LOCAL_POSITION,
            owner=7000,
        ),
    }

    mobile = Mobile(
        id=None,
        mobile_type=MobileType.PLAYER,
        attributes=attributes,
    )

    # Save mobile
    save_results = db.save_mobile(database_name, mobile)
    assert is_ok(save_results), f"Failed to save Mobile: {save_results[0].message}"
    print(f"  ✓ Saved: {save_results[0].message}")

    # Load mobile
    load_result, loaded_mobile = db.load_mobile(database_name, mobile.id)
    assert is_true(load_result), f"Failed to load Mobile: {load_result.message}"
    print(f"  ✓ Loaded: {load_result.message}")

    # Compare
    assert loaded_mobile.id == mobile.id, "ID mismatch"
    assert loaded_mobile.mobile_type == mobile.mobile_type, "mobile_type mismatch"
    assert len(loaded_mobile.attributes) == len(mobile.attributes), "Attributes count mismatch"

    # Test update
    print("  Testing update...")
    loaded_mobile.mobile_type = MobileType.NPC
    loaded_mobile.attributes[AttributeType.LOCAL_POSITION].value = ItemVector3(x=500.0, y=600.0, z=700.0)

    update_results = db.save_mobile(database_name, loaded_mobile)
    assert is_ok(update_results), f"Failed to update Mobile: {update_results[0].message}"
    print(f"  ✓ Updated: {update_results[0].message}")

    # Load again and verify updates
    load_result2, updated_mobile = db.load_mobile(database_name, loaded_mobile.id)
    assert is_true(load_result2), f"Failed to load updated Mobile: {load_result2.message}"
    assert updated_mobile.mobile_type == MobileType.NPC, "Updated mobile_type mismatch"
    print("  ✓ Update verified")

    # Test destroy
    print("  Testing destroy...")
    destroy_results = db.destroy_mobile(database_name, loaded_mobile.id)
    assert is_ok(destroy_results), f"Failed to destroy Mobile: {destroy_results[0].message}"
    print(f"  ✓ Destroyed: {destroy_results[0].message}")

    # Verify load fails after destroy
    load_result3, destroyed_mobile = db.load_mobile(database_name, loaded_mobile.id)
    assert not is_true(load_result3), "Load should fail after destroy"
    assert destroyed_mobile is None, "Destroyed mobile should be None"
    assert load_result3.error_code == GameError.DB_RECORD_NOT_FOUND, f"Expected DB_RECORD_NOT_FOUND, got {load_result3.error_code}"
    print("  ✓ Destroy verified: load failed with DB_RECORD_NOT_FOUND")

    print("  ✓ All assertions passed for Mobile\n")


def test_unified_dispatchers(db: DB, database_name: str):
    """Test unified dispatcher functions (save, create, update, destroy, load)."""
    print("Testing Unified Dispatchers...")

    # Test with ItemBlueprint using unified save
    components = {
        501: ItemBlueprintComponent(ratio=0.8, item_id=501),
    }
    blueprint = ItemBlueprint(
        id=None,
        components=components,
        bake_time_ms=4000,
    )

    # Use unified save (should call save_item_blueprint internally)
    save_results = db.save(database_name, blueprint)
    assert is_ok(save_results), f"Unified save failed: {save_results[0].message}"
    print(f"  ✓ Unified save: {save_results[0].message}")

    # Use unified load (should call load_item_blueprint internally)
    load_result, loaded_blueprint = db.load(database_name, blueprint.id, 'ItemBlueprint')
    assert is_true(load_result), f"Unified load failed: {load_result.message}"
    assert loaded_blueprint.id == blueprint.id, "ID mismatch after unified load"
    print(f"  ✓ Unified load: {load_result.message}")

    # Use unified update (should call update_item_blueprint internally)
    loaded_blueprint.bake_time_ms = 5500
    update_results = db.update(database_name, loaded_blueprint)
    assert is_ok(update_results), f"Unified update failed: {update_results[0].message}"
    print(f"  ✓ Unified update: {update_results[0].message}")

    # Verify update worked
    load_result2, updated_blueprint = db.load(database_name, blueprint.id, 'ItemBlueprint')
    assert updated_blueprint.bake_time_ms == 5500, "Update didn't persist"

    # Use unified destroy (should call destroy_item_blueprint internally)
    destroy_results = db.destroy(database_name, loaded_blueprint)
    assert is_ok(destroy_results), f"Unified destroy failed: {destroy_results[0].message}"
    print(f"  ✓ Unified destroy: {destroy_results[0].message}")

    # Verify destroy worked
    load_result3, destroyed_blueprint = db.load(database_name, blueprint.id, 'ItemBlueprint')
    assert not is_true(load_result3), "Load should fail after unified destroy"
    assert destroyed_blueprint is None, "Destroyed blueprint should be None"
    print("  ✓ Verified destroy worked")

    print("  ✓ All assertions passed for Unified Dispatchers\n")


def main():
    """Run all tests."""
    # Database configuration
    host = "localhost"
    user = "admin"
    password = "minda"
    database_name = "test_run_db"

    print("=" * 60)
    print("Database Seeding Script Test Suite")
    print("=" * 60)
    print()

    # Initialize database connection
    db = DB(host, user, password)

    try:
        # Setup database and tables
        print("Setting up test database...")
        setup_database(db, database_name)
        print("✓ Database setup complete\n")

        # Run tests
        test_item_blueprint(db, database_name)
        test_attribute(db, database_name)
        test_item(db, database_name)
        test_inventory(db, database_name)
        test_mobile(db, database_name)
        test_unified_dispatchers(db, database_name)

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
        teardown_database(db, database_name)
        print("✓ Cleanup complete")


if __name__ == "__main__":
    main()
