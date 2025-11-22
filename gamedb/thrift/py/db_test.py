import sys
sys.path.append('../gen-py')

from db import DB

# Import setup/teardown and test functions from submodules
from dbinc.item_test import (
    setup_database,
    teardown_database,
    test_item_blueprint,
    test_attribute,
    test_item,
)
from dbinc.inventory_test import test_inventory
from dbinc.mobile_test import test_mobile
from dbinc.player_test import test_player


def test_unified_dispatchers(db: DB, database_name: str):
    """Test unified dispatcher functions (save, load, create, update, destroy)."""
    from game.ttypes import (
        Item,
        ItemType,
        Attribute,
        AttributeType,
        Mobile,
        MobileType,
    )

    print("Testing unified dispatchers...")

    # Test unified save with Item
    item = Item(
        id=None,
        internal_name="test_unified_item",
        attributes={},
        max_stack_size=50,
        item_type=ItemType.RAWMATERIAL,
        blueprint=None,
    )

    save_results = db.save(database_name, item)
    from common import is_ok
    assert is_ok(save_results), f"Failed to save Item via unified save: {save_results[0].message}"
    print(f"  ✓ Saved Item via unified save: {save_results[0].message}")

    # Test unified load
    load_result, loaded_item = db.load(database_name, item.id, 'Item')
    from common import is_true
    assert is_true(load_result), f"Failed to load Item via unified load: {load_result.message}"
    assert loaded_item.internal_name == item.internal_name, "Item internal_name mismatch"
    print(f"  ✓ Loaded Item via unified load: {load_result.message}")

    # Test unified update
    loaded_item.internal_name = "test_unified_item_updated"
    update_results = db.update(database_name, loaded_item)
    assert is_ok(update_results), f"Failed to update Item via unified update: {update_results[0].message}"
    print(f"  ✓ Updated Item via unified update: {update_results[0].message}")

    # Test unified destroy
    destroy_results = db.destroy(database_name, loaded_item)
    assert is_ok(destroy_results), f"Failed to destroy Item via unified destroy: {destroy_results[0].message}"
    print(f"  ✓ Destroyed Item via unified destroy: {destroy_results[0].message}")

    # Test unified create with Mobile
    mobile = Mobile(
        id=None,
        mobile_type=MobileType.NPC,
        attributes={},
        owner=None,
    )

    create_results = db.create(database_name, mobile)
    assert is_ok(create_results), f"Failed to create Mobile via unified create: {create_results[0].message}"
    print(f"  ✓ Created Mobile via unified create: {create_results[0].message}")

    # Clean up
    db.destroy(database_name, mobile)

    print("  ✓ All assertions passed for unified dispatchers\n")


def main():
    # Database connection details
    db_host = "localhost"
    db_user = "gamedbadmin"
    db_password = "gamedbadmin"
    database_name = "test_game_db"

    # Create DB instance
    db = DB(db_host, db_user, db_password)

    try:
        # Setup database
        setup_database(db, database_name)

        # Run all tests
        test_item_blueprint(db, database_name)
        test_attribute(db, database_name)
        test_item(db, database_name)
        test_inventory(db, database_name)
        test_mobile(db, database_name)
        test_player(db, database_name)
        test_unified_dispatchers(db, database_name)

        print("=" * 50)
        print("All tests passed!")
        print("=" * 50)

    finally:
        # Cleanup
        teardown_database(db, database_name)


if __name__ == "__main__":
    main()
